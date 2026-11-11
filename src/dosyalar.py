"""Kaynaklı parti dosyaları ve sıralı teslim sözleşmesi."""
import datetime as dt
import json
from pathlib import Path
import sqlite3
import tempfile
import shutil
import re
from urllib.parse import urlsplit

DOSSIER_TABLES = {
    'party_identity_revision': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), previous_registry_key TEXT NOT NULL, registry_key TEXT NOT NULL, previous_legal_name TEXT NOT NULL, legal_name TEXT NOT NULL, passage_id TEXT NOT NULL REFERENCES passage(id), changed_at TEXT NOT NULL, reason TEXT NOT NULL',
    'dossier_field': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), field TEXT NOT NULL, value TEXT, finding_id TEXT REFERENCES finding(id), missing_id TEXT REFERENCES missing(id), as_of TEXT, date_precision TEXT NOT NULL, date_unknown_reason TEXT, UNIQUE(party_id,field)',
    'dossier_event': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), kind TEXT NOT NULL, event_date_id TEXT NOT NULL REFERENCES event_date(id), summary_finding_id TEXT NOT NULL REFERENCES finding(id)',
    'dossier_identity_note': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), related_party_id TEXT NOT NULL REFERENCES party(id), pair_id TEXT NOT NULL, text TEXT NOT NULL, provenance TEXT NOT NULL, own_passage_id TEXT NOT NULL REFERENCES passage(id), related_passage_id TEXT NOT NULL REFERENCES passage(id)',
    'dossier_source': 'party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, version_id TEXT NOT NULL REFERENCES document_version(id), reason TEXT NOT NULL, PRIMARY KEY(party_id,heading,version_id)',
    'version_context': 'version_id TEXT PRIMARY KEY REFERENCES document_version(id), period_start TEXT, period_end TEXT, date_precision TEXT NOT NULL, date_unknown_reason TEXT, passage_id TEXT REFERENCES passage(id), explanation_finding_id TEXT REFERENCES finding(id)',
    'version_relation': 'id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES document_version(id), previous_version_id TEXT NOT NULL REFERENCES document_version(id), relation TEXT NOT NULL, passage_id TEXT REFERENCES passage(id), explanation_finding_id TEXT REFERENCES finding(id)',
}
SOURCE_TYPE_LABELS = {'registry': 'Birincil belge', 'official': 'Birincil belge', 'party': 'Birincil belge', 'journalism': 'Gazetecilik', 'news': 'Gazetecilik', 'academic': 'Akademik çalışma', 'independent_report': 'Bağımsız rapor', 'unverified': 'Türü doğrulanamadı', 'unknown': 'Türü doğrulanamadı'}
DELIVERY_ORDER = ('tip', 'dem', 'iyi', 'yeni-yol', 'dbp', 'emep', 'saadet', 'demokrat')
HEADINGS = ('Kuruluş', 'Tüzük', 'Program', 'Söylem ve uygulama', 'Finansman ve harcamalar')
FIELDS = ('legal_name', 'abbreviation', 'foundation_date', 'registry_key', 'official_site', 'headquarters', 'chairperson')
FIELD_LABELS = {'legal_name':'Resmî ad', 'abbreviation':'Kısaltma', 'foundation_date':'Kuruluş tarihi', 'registry_key':'Sicil kimliği', 'official_site':'Resmî site', 'headquarters':'Genel merkez', 'chairperson':'Genel başkan'}


def migrate_workspace(db, backup_path, fail_at=None):
    """Yalnız kopyayı yedekle ve eklemeli migration'ı tek transaction'da uygula."""
    backup = sqlite3.connect(backup_path)
    try:
        db.backup(backup)
        before = {r[0]: [tuple(row) for row in backup.execute('SELECT * FROM "' + r[0] + '"')]
                  for r in backup.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    finally:
        backup.close()
    try:
        db.execute('BEGIN IMMEDIATE')
        for name, definition in DOSSIER_TABLES.items():
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        if fail_at == 'migration':
            raise RuntimeError('Enjekte edilen migration hatası')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Migration bütünlük denetimi başarısız')
        if any([tuple(row) for row in db.execute('SELECT * FROM "' + name + '"')] != rows for name, rows in before.items()):
            raise ValueError('Migration önceki kayıtları değiştirdi')
        db.commit()
    except Exception:
        db.rollback()
        raise


def foundation_for_party(db, party_id):
    """Partinin sicille doğrulanmış kuruluş tarihini döndür."""
    # Gecikmeli import: arşiv yazıcısı bu modülü de kullanır.
    from arsiv import check_identity

    identities = db.execute(
        "SELECT * FROM identity_observation WHERE entity_id=? AND entity_kind='party' AND valid_from IS NOT NULL",
        (party_id,),
    ).fetchall()
    if len(identities) != 1:
        raise ValueError('Parti için tek doğrulanmış kuruluş tarihi gerekli')
    identity = dict(identities[0])
    check_identity(db, identity)
    return identity['valid_from']


def validate_delivery_prefix(base_manifest, candidate_manifest):
    old = (base_manifest or {}).get('phase2_delivery', {}).get('completed_prefix', [])
    delivery = candidate_manifest.get('phase2_delivery')
    if delivery is None:
        if old or (base_manifest or {}).get('phase2_delivery'):
            raise ValueError('Faz 2 teslim sözleşmesi kaldırılamaz')
        return
    new = delivery.get('completed_prefix')
    party, stage = delivery.get('party_id'), delivery.get('stage')
    if not isinstance(old, list) or not isinstance(new, list) or old != list(DELIVERY_ORDER[:len(old)]) or new != list(DELIVERY_ORDER[:len(new)]):
        raise ValueError('Teslim sırası geçersiz')
    if stage == 'tracer':
        if new != old or len(old) >= len(DELIVERY_ORDER) or party != DELIVERY_ORDER[len(old)]:
            raise ValueError('Tracer tamamlanmamış sıradaki parti olmalı')
    elif stage == 'complete':
        if len(old) >= len(DELIVERY_ORDER) or new != old + [DELIVERY_ORDER[len(old)]] or party != new[-1]:
            raise ValueError('Yalnız sıradaki tek parti tamamlanabilir')
    else:
        raise ValueError('Geçersiz teslim aşaması')


def validate_dossier(data, party_id=None, stage='tracer'):
    """Kayıt ve export yollarında aynı kaynak ve ilişki kurallarını uygula."""
    findings = {x['id']: x for x in data['finding']}
    passages = {x['id']: x for x in data['passage']}
    versions = {x['id']: x for x in data['document_version']}
    documents = {x['id']: x for x in data['document']}
    events = {x['id']: x for x in data['event_date']}
    missing = {x['id']: x for x in data['missing']}
    evidence = data['finding_evidence']
    def owner(pid):
        return documents[versions[passages[pid]['version_id']]['document_id']]['party_id']
    def checked_finding(fid, party, heading=None):
        f = findings.get(fid)
        if not f or f['party_id'] != party or (heading and f['heading'] != heading):
            raise ValueError('Dosya bulgusu parti veya başlıkla uyuşmuyor')
        ev = [e for e in evidence if e['finding_id'] == fid]
        if not ev or any(owner(e['passage_id']) != party for e in ev):
            raise ValueError('Dosya kanıtı partiyle uyuşmuyor')
        if not any(r['kind'] == 'finding' and r['subject_id'] == fid and r['reviewer_kind'] in ('agent', 'human') and r['result'] == 'reviewed' and r['reason'] and r['reviewed_at'] for r in data['review']):
            raise ValueError('Dosya bulgusu incelenmemiş')
        return f
    def pair(fid, party):
        f = checked_finding(fid, party)
        summary_passages = {e['passage_id'] for e in evidence if e['finding_id'] == fid}
        if f['provenance'] != 'summary' or not any(x['pair_id'] == f['pair_id'] and x['party_id'] == party and x['provenance'] == 'quote' and x['heading'] == f['heading'] and checked_finding(x['id'], party) and summary_passages.intersection(e['passage_id'] for e in evidence if e['finding_id'] == x['id']) for x in findings.values()):
            raise ValueError('Kaynaklı özet ve alıntı çifti gerekli')
        return f
    for x in data.get('dossier_field', []):
        if x['field'] not in FIELDS or x['date_precision'] not in ('day','unknown') or (x['date_precision'] == 'unknown' and (x['as_of'] or not x['date_unknown_reason'])) or (x['date_precision'] == 'day' and not x['as_of']): raise ValueError('Kart alanı veya tarih gerekçesi geçersiz')
        if x['as_of']:
            date = dt.date.fromisoformat(x['as_of'])
            methods = data.get('method', [])
            if not methods or date > dt.datetime.fromisoformat(max(methods, key=lambda m:m['version'])['cutoff_at']).date(): raise ValueError('Kart tarihi kesim dışında')
        if x['value'] is not None:
            if not x['value'] or not x['finding_id'] or x['missing_id']: raise ValueError('Kart değeri için bulgu gerekli')
            f = pair(x['finding_id'], x['party_id'])
            if str(x['value']).casefold() not in f['text'].casefold() and not any(str(x['value']).casefold() in passages[e['passage_id']]['exact'].casefold() for e in evidence if e['finding_id'] == f['id']):
                raise ValueError('Kart değeri dayanağında bulunamadı')
            if x['field'] == 'foundation_date':
                identities = [i for i in data['identity_observation'] if i['entity_id'] == x['party_id'] and i['entity_kind'] == 'party' and i['valid_from']]
                if len(identities) != 1 or x['value'] not in (identities[0]['valid_from'], dt.date.fromisoformat(identities[0]['valid_from']).strftime('%d.%m.%Y')):
                    raise ValueError('Kartın kuruluş günü doğrulanmış sicille uyuşmuyor')
        else:
            m = missing.get(x['missing_id'])
            if x['finding_id'] or not m or m['party_id'] != x['party_id'] or m['heading'] != 'Kuruluş': raise ValueError('Kart eksiği girişimli kayıt gerektirir')
    for x in data.get('dossier_event', []):
        e = events.get(x['event_date_id'])
        if x['kind'] not in ('foundation','name_change','abbreviation_change','legal_status','first_congress','first_management') or not e or e['party_id'] != x['party_id'] or owner(e['passage_id']) != x['party_id']:
            raise ValueError('Kronoloji olayı geçersiz')
        f = pair(x['summary_finding_id'], x['party_id'])
        if f['heading'] != 'Kuruluş' or not any(y['finding_id'] == f['id'] and y['passage_id'] == e['passage_id'] for y in evidence): raise ValueError('Olay tarihi ve özeti aynı kaynağa dayanmalı')
        if x['kind'] == 'foundation' and not any(i['entity_id'] == x['party_id'] and i['valid_from'] == e['event_at'] for i in data['identity_observation']): raise ValueError('Kuruluş kronolojisi sicil tarihiyle uyuşmuyor')
    for x in data.get('dossier_source', []):
        v = versions.get(x['version_id'])
        if not v or documents[v['document_id']]['party_id'] != x['party_id'] or x['heading'] not in HEADINGS or not x['reason']: raise ValueError('Kaynak başlığı veya sahibi geçersiz')
        if documents[v['document_id']]['source_kind'] not in SOURCE_TYPE_LABELS: raise ValueError('Kaynak türü geçersiz')
    for x in data.get('version_context', []):
        v = versions[x['version_id']]; party = documents[v['document_id']]['party_id']
        if x['date_precision'] == 'unknown':
            if not x['date_unknown_reason']: raise ValueError('Bilinmeyen dönem için gerekçe gerekli')
        elif x['date_precision'] != 'day' or not x['period_start'] or not x['period_end'] or x['period_start'] > x['period_end'] or not x['passage_id'] or owner(x['passage_id']) != party:
            raise ValueError('Kaynaklı belge dönemi gerekli')
        else:
            text = passages[x['passage_id']]['exact']
            for value in (x['period_start'],x['period_end']):
                date = dt.date.fromisoformat(value)
                if value not in text and date.strftime('%d.%m.%Y') not in text: raise ValueError('Belge dönemi pasajda bulunamadı')
        if x['explanation_finding_id']:
            pair(x['explanation_finding_id'], party)
            if x['passage_id'] and not any(e['finding_id'] == x['explanation_finding_id'] and e['passage_id'] == x['passage_id'] for e in evidence): raise ValueError('Dönem açıklaması kendi kanıtına bağlanmalı')
    graph = {}
    for x in data.get('version_relation', []):
        v, prev = versions[x['version_id']], versions[x['previous_version_id']]
        if v['id'] == prev['id'] or v['document_id'] != prev['document_id'] or x['relation'] not in ('supersedes','related','uncertain'):
            raise ValueError('Belge sürüm ilişkisi geçersiz')
        party = documents[v['document_id']]['party_id']
        if not x['passage_id'] or owner(x['passage_id']) != party or passages[x['passage_id']]['version_id'] not in (v['id'], prev['id']) or not x['explanation_finding_id']: raise ValueError('Sürüm ilişkisi kanıt ve açıklama gerektirir')
        pair(x['explanation_finding_id'], party)
        if not any(e['finding_id'] == x['explanation_finding_id'] and e['passage_id'] == x['passage_id'] for e in evidence): raise ValueError('Sürüm açıklaması kendi kanıtına bağlanmalı')
        graph.setdefault(v['id'], []).append(prev['id'])
    def visit(v, path):
        if v in path: raise ValueError('Sürüm ilişkisi döngüsü')
        for nxt in graph.get(v, []): visit(nxt, path | {v})
    for v in graph: visit(v, set())
    for x in data.get('dossier_identity_note', []):
        if x['party_id'] == x['related_party_id'] or owner(x['own_passage_id']) != x['party_id'] or owner(x['related_passage_id']) != x['related_party_id'] or x['provenance'] not in ('summary','quote') or not x['text']:
            raise ValueError('Kimlik notu iki ayrı kaynak gerektirir')
        if not any(y['id'] != x['id'] and y['pair_id'] == x['pair_id'] and y['party_id'] == x['party_id'] and y['related_party_id'] == x['related_party_id'] and y['own_passage_id'] == x['own_passage_id'] and y['related_passage_id'] == x['related_passage_id'] and y['provenance'] != x['provenance'] for y in data['dossier_identity_note']): raise ValueError('Kimlik notu çifti gerekli')
        if x['provenance'] == 'quote' and x['text'] not in (passages[x['own_passage_id']]['exact'], passages[x['related_passage_id']]['exact']): raise ValueError('Kimlik notu alıntısı kaynakla uyuşmuyor')
        if not any(r['kind'] == 'dossier_identity_note' and r['subject_id'] == x['id'] and r['result'] == 'reviewed' and r['reason'] and r['reviewed_at'] for r in data['review']): raise ValueError('Kimlik notu incelemesi gerekli')
    for x in data.get('party_identity_revision', []):
        if not all(x[k] for k in ('previous_registry_key','registry_key','previous_legal_name','legal_name','changed_at','reason')) or owner(x['passage_id']) != x['party_id']:
            raise ValueError('Kimlik geçişi kaynak ve gerekçe gerektirir')
        v = versions[passages[x['passage_id']]['version_id']]
        url = urlsplit(v['final_url'])
        if not re.fullmatch(r'yargitay-\d+', x['registry_key']) or documents[v['document_id']]['source_kind'] != 'registry' or url.scheme != 'https' or url.hostname not in ('yargitaycb.gov.tr','www.yargitaycb.gov.tr') or url.path != '/sipar/' + x['registry_key'].removeprefix('yargitay-') or x['legal_name'].casefold() not in passages[x['passage_id']]['exact'].casefold():
            raise ValueError('Kimlik geçişi sicille uyuşmuyor')
    for party in {x['party_id'] for x in data.get('party_identity_revision', [])}:
        revisions = sorted((x for x in data['party_identity_revision'] if x['party_id'] == party), key=lambda x:x['changed_at'])
        if any((a['registry_key'],a['legal_name']) != (b['previous_registry_key'],b['previous_legal_name']) for a,b in zip(revisions,revisions[1:])): raise ValueError('Kimlik geçmişi zinciri kopuk')
        current = next(p for p in data['party'] if p['id'] == party)
        if (revisions[-1]['registry_key'],revisions[-1]['legal_name']) != (current['registry_key'],current['legal_name']): raise ValueError('Güncel kimlik geçmişle uyuşmuyor')
    if party_id:
        fs = [x for x in data.get('dossier_field', []) if x['party_id'] == party_id]
        es = [x for x in data.get('dossier_event', []) if x['party_id'] == party_id]
        foundation_fields = [x for x in fs if x['field'] == 'foundation_date']
        has_foundation = bool(foundation_fields and foundation_fields[0]['value'])
        has_event = any(x['kind'] == 'foundation' for x in es)
        if (stage == 'tracer' and not has_foundation) or not foundation_fields or has_foundation != has_event:
            raise ValueError('Kuruluş alanı ile kaynaklı kronoloji veya girişimli eksik gerekli')
        foundation_events = [x for x in es if x['kind'] == 'foundation']
        if not all(any(s['party_id'] == party_id and s['heading'] == 'Kuruluş' and s['version_id'] == passages[events[e['event_date_id']]['passage_id']]['version_id'] for s in data['dossier_source']) for e in foundation_events):
            raise ValueError('Kuruluş kaynağı başlığa bağlanmalı')
        if stage == 'complete':
            if not set(FIELDS[:5]).issubset({x['field'] for x in fs}): raise ValueError('Tam dosya için beş kart alanı gerekli')
            if not set(HEADINGS).issubset({x['heading'] for x in data['research_state'] if x['party_id'] == party_id and x['state'] == 'reviewed'}): raise ValueError('Beş araştırma başlığı incelenmeli')
            for heading in HEADINGS:
                relevant = [f for f in findings.values() if f['party_id'] == party_id and f['heading'] == heading]
                gaps = [m for m in missing.values() if m['party_id'] == party_id and m['heading'] == heading]
                if not relevant and not gaps: raise ValueError('İncelenen başlık için bulgu veya girişimli eksik gerekli')
                for f in relevant:
                    for ev in (e for e in evidence if e['finding_id'] == f['id']):
                        if not any(s['party_id'] == party_id and s['heading'] == heading and s['version_id'] == passages[ev['passage_id']]['version_id'] for s in data['dossier_source']): raise ValueError('Bulgu kaynağı başlığa bağlanmalı')
            context_versions = {c['version_id'] for c in data['version_context']}
            if any(s['version_id'] not in context_versions for s in data['dossier_source'] if s['party_id'] == party_id): raise ValueError('Kaynak dönemi veya gerekçeli belirsizlik gerekli')
    return True


def validate_phase_two_workspace(work, party_id=None, stage='complete'):
    import arsiv
    data = arsiv.validate_phase_one_workspace(work)
    if data['schema_version'] != 4: raise ValueError('Faz 2 için şema 4 gerekli')
    if stage not in ('tracer', 'complete'): raise ValueError('Geçersiz aşama')
    if party_id:
        if party_id not in ('yeni-parti',) + DELIVERY_ORDER: raise ValueError('Kapsam dışı parti')
        validate_dossier(data, party_id, stage)
    else:
        for p in ('yeni-parti',) + DELIVERY_ORDER: validate_dossier(data, p, 'complete')
    return data


def validate_phase_two(release='current', party_id=None, stage='complete'):
    import arsiv
    release = arsiv.audit_release(release)
    folder = arsiv.DATA / 'releases' / release
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    delivery = manifest.get('phase2_delivery')
    if not delivery or (party_id and (delivery['party_id'], delivery['stage']) != (party_id, stage)):
        raise ValueError('İstenen parti ve aşama manifestle uyuşmuyor')
    if party_id is None and delivery['completed_prefix'] != list(DELIVERY_ORDER): raise ValueError('Dokuz dosya henüz tamamlanmadı')
    data = validate_phase_two_workspace(folder, party_id, stage)
    arsiv.validate_phase_one_html(data, (folder / 'index.html').read_text(encoding='utf-8'))
    return release


def identity_confirmation(db, party_id, values):
    import arsiv
    required = {'registry_key','legal_name','valid_from','passage_id','changed_at','reason'}
    if set(values) != required or not all(values.values()): raise ValueError('Kimlik doğrulaması alanları eksik')
    old = db.execute('SELECT * FROM party WHERE id=?', (party_id,)).fetchone()
    if not old: raise ValueError('Parti bulunamadı')
    if old['registry_key'] == values['registry_key'] and old['legal_name'] == values['legal_name']:
        existing = db.execute("SELECT * FROM identity_observation WHERE entity_id=? AND registry_key=?", (party_id, values['registry_key'])).fetchone()
        if existing and existing['valid_from'] == values['valid_from'] and existing['passage_id'] == values['passage_id']:
            arsiv.check_identity(db, dict(existing)); return
        raise ValueError('Mevcut kimlik ile sicil doğrulaması çelişiyor')
    db.execute('UPDATE party SET registry_key=?, legal_name=? WHERE id=?', (values['registry_key'], values['legal_name'], party_id))
    observation = dict(entity_id=party_id, entity_kind='party', registry_key=values['registry_key'], valid_from=values['valid_from'], valid_to=None, passage_id=values['passage_id'])
    arsiv.check_identity(db, observation)
    # The stable party ID and TBMM observations are retained; the former key is recorded.
    db.execute('DELETE FROM identity_observation WHERE entity_id=? AND entity_kind=?', (party_id, 'party'))
    db.execute('INSERT INTO identity_observation VALUES (?,?,?,?,?,?)', tuple(observation[k] for k in ('entity_id','entity_kind','registry_key','valid_from','valid_to','passage_id')))
    rid = 'revision-' + party_id + '-' + values['registry_key']
    db.execute('INSERT INTO party_identity_revision VALUES (?,?,?,?,?,?,?,?,?)', (rid, party_id, old['registry_key'], values['registry_key'], old['legal_name'], values['legal_name'], values['passage_id'], values['changed_at'], values['reason']))


def load_dossier(work, payload):
    import arsiv
    if not isinstance(payload, dict) or payload.get('schema_version') != 1 or payload.get('party_id') not in ('yeni-parti',) + DELIVERY_ORDER or not isinstance(payload.get('records'), list): raise ValueError('Dosya girdisi geçersiz')
    arsiv.assert_lock(work)
    work = Path(work)
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        tmp = Path(tmp)
        shutil.copyfile(work / 'records.sqlite3', tmp / 'records.sqlite3')
        shutil.copyfile(work / 'workspace.json', tmp / 'workspace.json')
        db = arsiv.connect(tmp / 'records.sqlite3')
        method = db.execute('SELECT version,cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
        db.close()
        if not method or (payload.get('method_version'),payload.get('cutoff_at')) != (method['version'],method['cutoff_at']): raise ValueError('Yöntem sürümü veya kesim uyuşmuyor')
        rank = {k:i for i,k in enumerate(('document','document_version','passage','identity_observation','lead','attempt','missing','event_date','accounting_period','finding','finding_evidence','verification','review','dossier_source','dossier_field','dossier_event','version_context','version_relation','dossier_identity_note'))}
        entries = payload['records']
        if any(not isinstance(e,dict) or set(e) != {'kind','values'} or e['kind'] not in arsiv.TABLES or not isinstance(e['values'],dict) for e in entries): raise ValueError('Geçersiz kayıt')
        entries = sorted(entries, key=lambda e: rank.get(e['kind'], 100))
        confirmation_done = False
        notes = []
        for entry in entries:
            kind, values = entry['kind'], entry['values']
            if kind in ('party','scope_party','scope_observation','method','party_identity_revision'): raise ValueError('Bu kayıt yükleme yoluyla değiştirilemez')
            if 'party_id' in values and values['party_id'] != payload['party_id']: raise ValueError('Girdi başka partiye yazamaz')
            if payload.get('identity_confirmation') and not confirmation_done and rank.get(kind,100) >= rank['identity_observation']:
                db = arsiv.connect(tmp / 'records.sqlite3')
                try:
                    with db: identity_confirmation(db, payload['party_id'], payload['identity_confirmation'])
                finally: db.close()
                confirmation_done = True
            db = arsiv.connect(tmp / 'records.sqlite3')
            try:
                info = db.execute(f'PRAGMA table_info({kind})').fetchall()
                pks = [r['name'] for r in sorted(info, key=lambda r:r['pk']) if r['pk']]
                if not pks or not all(k in values for k in pks): raise ValueError('Kayıt anahtarı eksik')
                existing = db.execute(f"SELECT * FROM {kind} WHERE " + ' AND '.join(k+'=?' for k in pks), [values[k] for k in pks]).fetchone()
                if existing:
                    if any(existing[r['name']] != values.get(r['name']) for r in info): raise ValueError('Aynı kimlikle çelişen kayıt')
                    continue
            finally: db.close()
            if kind == 'dossier_identity_note': notes.append(values)
            else: arsiv.record(tmp, kind, values)
        if notes:
            db = arsiv.connect(tmp / 'records.sqlite3')
            try:
                with db:
                    for values in notes:
                        keys = list(values)
                        db.execute('INSERT INTO dossier_identity_note (' + ','.join(keys) + ') VALUES (' + ','.join('?' for _ in keys) + ')', [values[k] for k in keys])
                    data = {name:[dict(row) for row in db.execute(f'SELECT * FROM {name}')] for name in arsiv.TABLES}
                    validate_dossier(data)
            finally: db.close()
        if payload.get('identity_confirmation') and not confirmation_done:
            db = arsiv.connect(tmp / 'records.sqlite3')
            try:
                with db: identity_confirmation(db, payload['party_id'], payload['identity_confirmation'])
            finally: db.close()
        arsiv.export_db(tmp / 'records.sqlite3', 'workspace', strict_identity=True)
        (tmp / 'records.sqlite3').replace(work / 'records.sqlite3')


def check_dossier_input(path):
    import arsiv
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory() as tmp:
        work = arsiv.open_workspace(tmp)
        try:
            load_dossier(work, payload)
            validate_phase_two_workspace(work, payload['party_id'], 'complete')
        finally:
            try: arsiv.assert_lock(work)
            except (ValueError,OSError): pass
            else: (arsiv.DATA / '.write.lock').unlink()
    return True


def make_delivery_receipt(release, party_id, previous=None, _seen=None):
    import arsiv
    release = arsiv.audit_release(release)
    folder = arsiv.DATA / 'releases' / release
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    delivery = manifest.get('phase2_delivery') or {}
    stage = delivery.get('stage')
    validate_phase_two(release, party_id, stage)
    data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
    fields = [x for x in data['dossier_field'] if x['party_id'] == party_id]
    sources = sorted({x['version_id'] for x in data['dossier_source'] if x['party_id'] == party_id})
    added = [f"{FIELD_LABELS[x['field']]}: {x['value']}" for x in fields if x['value'] is not None]
    if any(x['party_id'] == party_id and x['kind'] == 'foundation' for x in data['dossier_event']): added.append('Kaynaklı kuruluş kronolojisi ve sicil pasajına bağlantı')
    gaps = [f"{FIELD_LABELS[name]}: henüz incelenmedi" for name in FIELDS[:5] if not any(f['field'] == name for f in fields)]
    gaps += [f"{FIELD_LABELS[x['field']]}: {next(m['status'] + ' — ' + m['reason'] for m in data['missing'] if m['id'] == x['missing_id'])}" for x in fields if x['value'] is None]
    reviewed = {x['heading'] for x in data['research_state'] if x['party_id'] == party_id and x['state'] == 'reviewed'}
    gaps += [f"{heading}: {'araştırma tamamlanmadı' if any(f['party_id'] == party_id and f['heading'] == heading for f in data['finding']) else 'henüz incelenmedi'}" for heading in HEADINGS if heading not in reviewed]
    if party_id == 'tip' and stage == 'tracer': gaps.append('Arşivli TİP tüzüğünün kesim tarihinde yürürlükteki sürüm olduğu doğrulanmadı; parti dosyası tamamlanmadı.')
    if not added or not gaps or not sources: raise ValueError('Teslim içeriği, kaynak veya önemli açıklar boş')
    if previous:
        previous_path = arsiv.safe_path(arsiv.ROOT, previous)
        check_delivery_receipt(previous_path, _seen)
        previous = str(previous_path.relative_to(arsiv.ROOT))
    method = max(data['method'], key=lambda m:m['version'])
    report = (folder / 'index.html').resolve()
    return dict(schema_version=1, party_id=party_id, stage=stage, completed_prefix=delivery['completed_prefix'], release_id=release,
                report_path=str(report), report_url=report.as_uri(), added_content=added, important_gaps=gaps,
                source_versions=sources, checked_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                audit_result='PHASE2_TRACER_OK' if stage == 'tracer' else 'PHASE2_PARTY_OK', previous_receipt=previous,
                method_version=method['version'], cutoff_at=method['cutoff_at'])


def check_delivery_receipt(path, _seen=None):
    path = Path(path).resolve()
    _seen = set() if _seen is None else _seen
    if path in _seen: raise ValueError('Makbuz zincirinde döngü')
    _seen.add(path)
    receipt = json.loads(path.read_text(encoding='utf-8'))
    expected = make_delivery_receipt(receipt['release_id'], receipt['party_id'], receipt.get('previous_receipt'), _seen)
    if set(receipt) != set(expected) or any(receipt[k] != expected[k] for k in expected if k != 'checked_at'):
        raise ValueError('Makbuz denetlenen sürümle uyuşmuyor')
    try: dt.datetime.fromisoformat(receipt['checked_at'])
    except (ValueError, TypeError): raise ValueError('Makbuz denetim tarihi geçersiz')
    if not Path(receipt['report_path']).is_file(): raise ValueError('Makbuz raporu bulunamadı')
    return receipt
