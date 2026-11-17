"""Söylem ve belgelenmiş uygulamalar için sürümlü iç sözleşme."""
import hashlib
import json
import sqlite3
from pathlib import Path

PRACTICE_TABLES = {
    'practice_contract': 'version INTEGER PRIMARY KEY, taxonomy_version INTEGER NOT NULL, stage TEXT NOT NULL, method_version INTEGER NOT NULL, inventory_digest TEXT NOT NULL',
    'practice_event': 'id TEXT PRIMARY KEY, common_event_key TEXT, event_at TEXT, date_precision TEXT NOT NULL, date_unknown_reason TEXT, scope_context TEXT NOT NULL, title TEXT NOT NULL, occurrence_basis TEXT NOT NULL',
    'practice_event_evidence': 'event_id TEXT NOT NULL REFERENCES practice_event(id), passage_id TEXT NOT NULL REFERENCES passage(id), supported_point TEXT NOT NULL, stage TEXT NOT NULL, concrete_basis TEXT NOT NULL, limitation TEXT NOT NULL, epistemic_type TEXT NOT NULL, PRIMARY KEY(event_id,passage_id,stage)',
    'practice_contribution': 'id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES practice_event(id), party_id TEXT NOT NULL REFERENCES party(id), actor_id TEXT NOT NULL REFERENCES actor(id), contribution_kind TEXT NOT NULL, finding_id TEXT NOT NULL REFERENCES finding(id), authority_passage_id TEXT REFERENCES passage(id), membership_passage_id TEXT REFERENCES passage(id), responsibility_limit TEXT NOT NULL',
    'practice_statement': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, summary_finding_id TEXT NOT NULL REFERENCES finding(id), quote_finding_id TEXT NOT NULL REFERENCES finding(id), statement_at TEXT, date_precision TEXT NOT NULL, version_id TEXT NOT NULL REFERENCES document_version(id), period_basis TEXT NOT NULL, uncertainty_reason TEXT, comparison_row_id TEXT NOT NULL REFERENCES comparison_row(id), FOREIGN KEY(topic_id,taxonomy_version) REFERENCES comparison_topic(topic_id,taxonomy_version)',
    'practice_relation': 'id TEXT PRIMARY KEY, statement_id TEXT NOT NULL REFERENCES practice_statement(id), event_id TEXT NOT NULL REFERENCES practice_event(id), party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, scope_id TEXT, comparability_reason TEXT NOT NULL, target_finding_id TEXT NOT NULL REFERENCES finding(id), result_finding_id TEXT REFERENCES finding(id), explanation_finding_id TEXT NOT NULL REFERENCES finding(id), temporal_context TEXT NOT NULL, authority_context TEXT NOT NULL, uncertainty_reason TEXT',
    'practice_legacy_link': 'legacy_kind TEXT NOT NULL, legacy_id TEXT NOT NULL, event_id TEXT NOT NULL REFERENCES practice_event(id), relation_id TEXT NOT NULL REFERENCES practice_relation(id), overlap_reason TEXT NOT NULL, PRIMARY KEY(legacy_kind,legacy_id,event_id,relation_id)',
    'practice_source_party': 'version_id TEXT NOT NULL REFERENCES document_version(id), party_id TEXT NOT NULL REFERENCES party(id), passage_id TEXT NOT NULL REFERENCES passage(id), scope_reason TEXT NOT NULL, PRIMARY KEY(version_id,party_id,passage_id)',
}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def migrate_practice_workspace(db, backup_path, fail_at=None):
    backup = sqlite3.connect(backup_path)
    try:
        db.backup(backup)
    finally:
        backup.close()
    try:
        db.execute('BEGIN IMMEDIATE')
        for name, definition in PRACTICE_TABLES.items():
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        if fail_at == 'migration':
            raise RuntimeError('Migration hatası')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Migration bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise


def validate_practices(data):
    """Validate the complete snapshot, including evidence and party boundaries."""
    from arsiv import validate_dates, aware_time
    c = data.get('practice_contract', [])
    if len(c) != 1 or (c[0]['version'], c[0]['taxonomy_version'], c[0]['method_version']) != (1, 4, 1) or c[0]['stage'] not in ('tracer', 'partial', 'complete'):
        raise ValueError('Uygulama sözleşmesi geçersiz')
    if len(c[0]['inventory_digest']) != 64 or any(x not in '0123456789abcdef' for x in c[0]['inventory_digest']):
        raise ValueError('Envanter özeti geçersiz')
    if not data.get('comparison_contract') or data['comparison_contract'][0]['stage'] != 'complete' or data['comparison_contract'][0]['taxonomy_version'] != 4:
        raise ValueError('Tam Faz 3 tabanı gerekli')
    findings = {x['id']: x for x in data['finding']}
    passages = {x['id']: x for x in data['passage']}
    versions = {x['id']: x for x in data['document_version']}
    documents = {x['id']: x for x in data['document']}
    actors = {x['id']: x for x in data['actor']}
    events = {x['id']: x for x in data['practice_event']}
    statements = {x['id']: x for x in data['practice_statement']}
    rows = {x['id']: x for x in data['comparison_row']}
    if data.get('comparison_completion_revision'):
        selected = json.loads(max(data['comparison_completion_revision'], key=lambda x: x['epoch'])['selection'])
        selected_rows = {x['id'] for x in selected['rows']}
    else:
        selected_rows = set(rows)
    evidence = data['finding_evidence']
    verified = {(x['finding_id'], x['passage_id']): x for x in data['verification'] if x['result'] == 'confirmed' and x['reason']}
    party_sources = {(x['version_id'], x['party_id'], x['passage_id']) for x in data['practice_source_party'] if x['scope_reason']}
    for version, party, passage in party_sources:
        if passage not in passages or passages[passage]['version_id'] != version or party not in {p['id'] for p in data['party']}:
            raise ValueError('Kaynak parti kapsamı geçersiz')
    def check_finding(fid, party):
        f = findings.get(fid)
        refs = [x['passage_id'] for x in evidence if x['finding_id'] == fid]
        if not f or f['party_id'] != party or not refs or any((fid, p) not in verified for p in refs):
            raise ValueError('Partiyle eşleşen doğrulanmış bulgu gerekli')
        for p in refs:
            aware_time(verified[(fid, p)]['checked_at'])
        return f
    for s in statements.values():
        row = rows.get(s['comparison_row_id'])
        if not row or row['id'] not in selected_rows or (row['party_id'], row['topic_id'], row['taxonomy_version']) != (s['party_id'], s['topic_id'], s['taxonomy_version']):
            raise ValueError('Faz 3 satırı uyuşmuyor')
        for key in ('summary_finding_id', 'quote_finding_id'):
            f = check_finding(s[key], s['party_id'])
            if not any(passages[e['passage_id']]['version_id'] == s['version_id'] for e in evidence if e['finding_id'] == f['id']):
                raise ValueError('Söylem sürümü uyuşmuyor')
        if findings[s['quote_finding_id']]['provenance'] != 'quote' or not s['period_basis']:
            raise ValueError('Söylem alıntısı veya dönem dayanağı eksik')
        if s['date_precision'] == 'unknown' and not s['uncertainty_reason']:
            raise ValueError('Bilinmeyen söylem tarihi açıklanmalı')
        if s['date_precision'] not in ('day', 'instant', 'unknown') or (s['date_precision'] == 'unknown') != (s['statement_at'] is None):
            raise ValueError('Söylem tarihi ve kesinliği uyuşmuyor')
    for x in data['practice_event_evidence']:
        p = passages.get(x['passage_id'])
        if not p or x['event_id'] not in events or x['stage'] not in ('initiative', 'action', 'result') or x['epistemic_type'] not in ('claim', 'comment', 'fact') or not all(x[k] for k in ('supported_point', 'concrete_basis', 'limitation')):
            raise ValueError('Olay kanıtı geçersiz')
        doc = documents[versions[p['version_id']]['document_id']]
        if doc['source_kind'] == 'party':
            raise ValueError('Salt parti kaynağı oluş kanıtı değildir')
        if doc['source_kind'] == 'news' and x['epistemic_type'] == 'fact':
            raise ValueError('Haber iddiası doğrulanmış olguya dönüştürülemez')
        event_date = events[x['event_id']]['event_at']
        source_date = versions[p['version_id']]['document_date']
        if event_date and source_date and source_date < event_date[:10]:
            raise ValueError('Olay kaynağı olaydan önce yayımlanmış')
    for r in data['practice_relation']:
        s, e = statements.get(r['statement_id']), events.get(r['event_id'])
        if not s or not e or (r['party_id'], r['topic_id']) != (s['party_id'], s['topic_id']) or not all(r[k] for k in ('comparability_reason', 'temporal_context', 'authority_context')):
            raise ValueError('İlişki kapsamı geçersiz')
        for key in ('target_finding_id', 'result_finding_id', 'explanation_finding_id'):
            if r[key]: check_finding(r[key], r['party_id'])
            elif key != 'result_finding_id': raise ValueError('İlişki bulgusu gerekli')
        if r['target_finding_id'] != s['summary_finding_id']:
            raise ValueError('Hedef söylemle uyuşmuyor')
        result_refs = {x['passage_id'] for x in evidence if x['finding_id'] == r['result_finding_id']} if r['result_finding_id'] else set()
        event_refs = {x['passage_id'] for x in data['practice_event_evidence'] if x['event_id'] == e['id']}
        statement_refs = {x['passage_id'] for x in evidence if x['finding_id'] in (s['summary_finding_id'], s['quote_finding_id'])}
        if (result_refs and not result_refs.intersection(event_refs)) or event_refs.intersection(statement_refs):
            raise ValueError('Söylem ve oluş için ayrı bağlı kaynaklar gerekli')
        explanation_refs = {x['passage_id'] for x in evidence if x['finding_id'] == r['explanation_finding_id']}
        if not explanation_refs.intersection(statement_refs) or not explanation_refs.intersection(event_refs):
            raise ValueError('İlişki açıklaması her iki kaynağa dayanmalı')
        if not r['result_finding_id'] and not r['uncertainty_reason']:
            raise ValueError('Bulunmayan sonuç açıklanmalı')
        if s['statement_at'] and e['event_at'] and s['statement_at'][:10] > e['event_at'][:10]:
            raise ValueError('Sonraki söylem geçmiş olaya uygulanamaz')
        if not any(x['event_id'] == e['id'] and (passages[x['passage_id']]['version_id'], r['party_id'], x['passage_id']) in party_sources for x in data['practice_event_evidence']):
            raise ValueError('Olay ve parti kapsamı dayanağı eksik')
        founding = next((i['valid_from'] for i in data['identity_observation'] if i['entity_id'] == r['party_id'] and i['entity_kind'] == 'party'), None)
        cutoff = max(data['method'], key=lambda m: m['version'])['cutoff_at']
        if not founding or validate_dates(e['event_at'], e['date_precision'], founding, cutoff, e['date_unknown_reason']) == 'outside':
            raise ValueError('Olay tarihi kapsam dışında')
        if validate_dates(s['statement_at'], s['date_precision'], founding, cutoff, s['uncertainty_reason']) == 'outside':
            raise ValueError('Söylem tarihi kapsam dışında')
        if s['statement_at'] and versions[s['version_id']]['document_date'] and s['statement_at'][:10] > versions[s['version_id']]['document_date']:
            raise ValueError('Söylem kaynak tarihinden sonra olamaz')
    for x in data['practice_contribution']:
        actor = actors.get(x['actor_id'])
        if not actor or actor['party_id'] != x['party_id'] or actor['kind'] not in ('institution', 'authorized_representative') or x['contribution_kind'] not in ('support', 'objection', 'task', 'unknown') or not x['responsibility_limit']:
            raise ValueError('Aktör veya katkı sınırı geçersiz')
        if actor['kind'] == 'authorized_representative' and (not x['authority_passage_id'] or x['authority_passage_id'] != actor['authorization_passage_id']):
            raise ValueError('Yetki kanıtı gerekli')
        if actor['kind'] == 'authorized_representative':
            person = next((p for p in data['person'] if p['id'] == actor['person_id']), None)
            authority = passages.get(x['authority_passage_id'])
            if not person or not authority or person['name'] not in authority['exact'] or documents[versions[authority['version_id']]['document_id']]['party_id'] != x['party_id']:
                raise ValueError('Temsil yetkisi kişi ve partiyle uyuşmuyor')
        finding = check_finding(x['finding_id'], x['party_id'])
        refs = {r['passage_id'] for r in evidence if r['finding_id'] == finding['id']}
        event_refs = {r['passage_id'] for r in data['practice_event_evidence'] if r['event_id'] == x['event_id']}
        if not refs.intersection(event_refs):
            raise ValueError('Katkı olay kanıtıyla uyuşmuyor')
        if finding['epistemic_type'] == 'fact' and any(documents[versions[passages[p]['version_id']]['document_id']]['source_kind'] == 'news' for p in refs):
            raise ValueError('Haber kaynaklı katkı iddia olarak korunmalı')
    for link in data['practice_legacy_link']:
        if link['legacy_kind'] not in ('action', 'match', 'candidate') or not link['overlap_reason']:
            raise ValueError('Eski kayıt köprüsü geçersiz')
        table = {'action': 'action', 'match': 'match', 'candidate': 'match_candidate'}[link['legacy_kind']]
        key = 'finding_id' if table == 'action' else 'id'
        if not any(x[key] == link['legacy_id'] for x in data[table]):
            raise ValueError('Eski kayıt bulunamadı')
    return True


def practice_manifest_fields(data):
    c = data['practice_contract'][0]
    return dict(practice_validation_version=c['version'], practice_stage=c['stage'], practice_inventory_sha256=c['inventory_digest'], practice_selection_sha256=_digest({k: data[k] for k in PRACTICE_TABLES}))


def validate_practice_descent(base, candidate):
    if base.get('practice_contract'):
        if not candidate.get('practice_contract'):
            raise ValueError('Uygulama sözleşmesi kaldırılamaz')
        old, new = base['practice_contract'][0], candidate['practice_contract'][0]
        levels = {'tracer': 0, 'partial': 1, 'complete': 2}
        if (new['version'], new['taxonomy_version'], new['method_version']) != (old['version'], old['taxonomy_version'], old['method_version']) or levels[new['stage']] < levels[old['stage']]:
            raise ValueError('Uygulama sözleşmesi geriletilemez')
        for name in PRACTICE_TABLES:
            if name != 'practice_contract' and any(x not in candidate.get(name, []) for x in base[name]):
                raise ValueError('Önceki uygulama kaydı değiştirilemez')


def load_practice(work, payload):
    import os
    import shutil
    import tempfile
    from arsiv import assert_lock
    work = Path(work)
    metadata = assert_lock(work)
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        scratch = Path(tmp)
        shutil.copyfile(work / 'records.sqlite3', scratch / 'records.sqlite3')
        shutil.copyfile(work / 'records.sqlite3', work / 'pre-practice-migration.sqlite3')
        _load_practice_copy(scratch, payload, metadata['base'])
        assert_lock(work)
        os.replace(scratch / 'records.sqlite3', work / 'records.sqlite3')


def _load_practice_copy(work, payload, base):
    from arsiv import connect, export_db
    if payload.get('base_release') != base or payload.get('contract_version') != 1 or payload.get('stage') not in ('tracer', 'partial', 'complete') or payload.get('taxonomy_version') != 4:
        raise ValueError('Uygulama paketi veya tabanı geçersiz')
    if len(payload.get('practice_records', {}).get('practice_contract', [])) != 1 or payload['practice_records']['practice_contract'][0].get('stage') != payload['stage']:
        raise ValueError('Paket ve uygulama aşaması uyuşmuyor')
    if not isinstance(payload.get('scope_inventory'), list) or payload['practice_records']['practice_contract'][0].get('inventory_digest') != _digest(payload['scope_inventory']):
        raise ValueError('Envanter kapsamı özeti uyuşmuyor')
    db = connect(work / 'records.sqlite3')
    try:
        migrate_practice_workspace(db, work / 'pre-practice-migration.sqlite3')
        db.execute('BEGIN IMMEDIATE')
        for entry in payload['entries']:
            kind, values = entry['kind'], entry['values']
            if kind not in ('finding', 'finding_evidence', 'verification', 'source_attribution') or not values:
                raise ValueError('Uygulama girdi türü geçersiz')
            cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
            if not set(values) <= cols:
                raise ValueError('Bilinmeyen alan')
            db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
        records = payload['practice_records']
        if set(records) != set(PRACTICE_TABLES):
            raise ValueError('Uygulama tabloları eksik')
        for kind in PRACTICE_TABLES:
            for values in records[kind]:
                cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
                if set(values) != cols:
                    raise ValueError('Uygulama alanları uyuşmuyor')
                db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
        # Validate a transaction-consistent snapshot before the commit.
        data = {name: [dict(x) for x in db.execute(f'SELECT * FROM {name}')] for name in list(PRACTICE_TABLES) + ['finding', 'finding_evidence', 'verification', 'passage', 'document_version', 'document', 'actor', 'person', 'comparison_contract', 'comparison_row', 'comparison_completion_revision', 'identity_observation', 'method', 'party', 'action', 'match', 'match_candidate']}
        validate_practices(data)
        if db.execute('PRAGMA foreign_key_check').fetchall() or db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Uygulama bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    export_db(work / 'records.sqlite3', 'practice-validation')


def validate_practice_input(payload, base_release='current'):
    # Read-only validation uses a private copy; it never acquires the global writer lock.
    import shutil
    import tempfile
    import arsiv
    base = arsiv.current() if base_release == 'current' else base_release
    # A published tracer may be checked again after current advances. Accept
    # its declared parent only when current actually contains every submitted
    # record and explicitly names that parent; never silently switch bases.
    if base_release == 'current' and payload.get('base_release') != base:
        current_folder = arsiv.safe_path(arsiv.DATA / 'releases', base)
        current_manifest = json.loads((current_folder / 'manifest.json').read_text(encoding='utf-8'))
        if current_manifest.get('base_release') != payload.get('base_release'):
            raise ValueError('Taban sürüm uyuşmuyor')
        if current_manifest.get('release_id') != base or any(arsiv.sha(arsiv.safe_path(current_folder, name)) != digest for name, digest in current_manifest['files'].items()):
            raise ValueError('Güncel sürüm özeti uyuşmuyor')
        current_data = json.loads((current_folder / 'records.json').read_text(encoding='utf-8'))
        submitted = list(payload.get('entries', []))
        submitted += [{'kind': kind, 'values': row} for kind, rows in payload.get('practice_records', {}).items() for row in rows]
        if not submitted or any(not any(all(existing.get(k) == v for k, v in item['values'].items()) for existing in current_data.get(item['kind'], [])) for item in submitted):
            raise ValueError('Güncel sürüm paket kayıtlarını içermiyor')
        base = payload['base_release']
    if payload.get('base_release') != base:
        raise ValueError('Taban sürüm uyuşmuyor')
    folder = arsiv.safe_path(arsiv.DATA / 'releases', base)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('release_id') != base or any(arsiv.sha(arsiv.safe_path(folder, name)) != digest for name, digest in manifest['files'].items()):
        raise ValueError('Taban sürüm özeti uyuşmuyor')
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copyfile(folder / 'records.sqlite3', work / 'records.sqlite3')
        _load_practice_copy(work, payload, base)
    return True
