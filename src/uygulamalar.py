"""Söylem ve belgelenmiş uygulamalar için sürümlü iç sözleşme."""
import hashlib
import json
import sqlite3
from datetime import date
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

# Optional extension: absence preserves the original schema-7 serialization.
PRACTICE_VARIANT_TABLES = {
    'practice_variant_contract': 'version INTEGER PRIMARY KEY, inventory_json TEXT NOT NULL',
    'practice_scope': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, period_start TEXT NOT NULL, cutoff_at TEXT NOT NULL, research_kind TEXT NOT NULL, state TEXT NOT NULL, boundary_reason TEXT NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES comparison_topic(topic_id,taxonomy_version)',
    'practice_attempt': 'id TEXT PRIMARY KEY, scope_id TEXT NOT NULL REFERENCES practice_scope(id), attempted_at TEXT NOT NULL, query TEXT NOT NULL, url TEXT, result TEXT NOT NULL, reason TEXT NOT NULL, source_version_id TEXT REFERENCES document_version(id)',
    'practice_unmatched': 'id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES practice_event(id), party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, statement_scope_id TEXT NOT NULL REFERENCES practice_scope(id), statement_search_state TEXT NOT NULL, reason TEXT NOT NULL',
}

# A separate marker keeps version-1 variant snapshots byte-compatible.
PRACTICE_EVIDENCE_TABLES = {
    'practice_evidence_contract': 'version INTEGER PRIMARY KEY',
    'practice_evidence_assessment': 'event_id TEXT NOT NULL, passage_id TEXT NOT NULL, stage TEXT NOT NULL, basis_kind TEXT NOT NULL, PRIMARY KEY(event_id,passage_id,stage), FOREIGN KEY(event_id,passage_id,stage) REFERENCES practice_event_evidence(event_id,passage_id,stage)',
    'practice_actor_period': 'contribution_id TEXT PRIMARY KEY REFERENCES practice_contribution(id), valid_from TEXT NOT NULL, valid_to TEXT NOT NULL, identity_passage_id TEXT NOT NULL REFERENCES passage(id)',
    'practice_dispute': 'id TEXT PRIMARY KEY, event_id TEXT NOT NULL REFERENCES practice_event(id), supported_points TEXT NOT NULL, disputed_points TEXT NOT NULL, unresolved_points TEXT NOT NULL, summary_finding_id TEXT NOT NULL REFERENCES finding(id)',
    'practice_dispute_evidence': 'dispute_id TEXT NOT NULL REFERENCES practice_dispute(id), passage_id TEXT NOT NULL REFERENCES passage(id), point TEXT NOT NULL, source_position TEXT NOT NULL, role TEXT NOT NULL, PRIMARY KEY(dispute_id,passage_id,point,role)',
    'practice_position_change': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, before_statement_id TEXT NOT NULL REFERENCES practice_statement(id), after_statement_id TEXT NOT NULL REFERENCES practice_statement(id), comparison_conditions TEXT NOT NULL, explanation_finding_id TEXT NOT NULL REFERENCES finding(id), uncertainty_reason TEXT NOT NULL',
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
        db.execute('PRAGMA user_version = 7')
        if fail_at == 'migration':
            raise RuntimeError('Migration hatası')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Migration bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise


def validate_practice_evidence(data, findings, passages, events, statements, check_finding, party_sources):
    """Check stage-specific and contested evidence without changing source epistemics."""
    extension = set(data).intersection(PRACTICE_EVIDENCE_TABLES)
    if extension and (extension != set(PRACTICE_EVIDENCE_TABLES) or data['practice_evidence_contract'] != [{'version': 1}] or 'practice_variant_contract' not in data):
        raise ValueError('Uygulama kanıt sözleşmesi eksik veya geçersiz')
    evidence = data['finding_evidence']
    if extension:
        assessments = {(a['event_id'], a['passage_id'], a['stage']): a for a in data['practice_evidence_assessment']}
        for ref in data['practice_event_evidence']:
            assessment = assessments.get((ref['event_id'], ref['passage_id'], ref['stage']))
            if not assessment or assessment['basis_kind'] not in ('observation', 'document', 'independent_report', 'party_announcement'):
                raise ValueError('Olay kanıtının somut dayanak türü gerekli')
            if ref['stage'] != 'initiative' and assessment['basis_kind'] == 'party_announcement':
                raise ValueError('Parti duyurusunun tekrarı oluş kanıtı değildir')
        if len(assessments) != len(data['practice_event_evidence']):
            raise ValueError('Olay kanıtı değerlendirmesi uyuşmuyor')
    for relation in data['practice_relation']:
        fid = relation['result_finding_id']
        if fid:
            refs = {e['passage_id'] for e in evidence if e['finding_id'] == fid}
            if not any(e['event_id'] == relation['event_id'] and e['stage'] == 'result' and e['passage_id'] in refs for e in data['practice_event_evidence']):
                raise ValueError('Sonuç ayrı sonuç aşaması kanıtı gerektirir')
    disputes = {d['id']: d for d in data.get('practice_dispute', [])}
    for dispute in disputes.values():
        if dispute['event_id'] not in events or not all(dispute[k] for k in ('supported_points', 'disputed_points', 'unresolved_points')):
            raise ValueError('İhtilaf noktaları veya olayı eksik')
        parties = {r['party_id'] for r in data['practice_relation'] if r['event_id'] == dispute['event_id']}
        parties |= {u['party_id'] for u in data.get('practice_unmatched', []) if u['event_id'] == dispute['event_id']}
        fid = dispute['summary_finding_id']
        if fid not in findings or findings[fid]['party_id'] not in parties:
            raise ValueError('İhtilaf özeti olay kapsamıyla uyuşmuyor')
        check_finding(fid, findings[fid]['party_id'])
        refs = [e for e in data['practice_dispute_evidence'] if e['dispute_id'] == dispute['id']]
        if not refs or not any(e['role'] == 'conflict' for e in refs):
            raise ValueError('İhtilaf karşıt pasaj gerektirir')
    for ref in data.get('practice_dispute_evidence', []):
        dispute = disputes.get(ref['dispute_id'])
        passage = passages.get(ref['passage_id'])
        if not dispute or not passage or ref['role'] not in ('support', 'conflict', 'reply') or not ref['point'] or not ref['source_position']:
            raise ValueError('İhtilaf kanıtı geçersiz')
        version = passage['version_id']
        versions = {v['id']: v for v in data['document_version']}
        documents = {d['id']: d for d in data['document']}
        parties = {r['party_id'] for r in data['practice_relation'] if r['event_id'] == dispute['event_id']}
        parties |= {u['party_id'] for u in data.get('practice_unmatched', []) if u['event_id'] == dispute['event_id']}
        if any(documents[versions[version]['document_id']]['party_id'] != party and (version, party, ref['passage_id']) not in party_sources for party in parties):
            raise ValueError('İhtilaf kaynağı parti kapsamı dışında')


def validate_practice_temporality(data, statements, check_finding):
    """Compare only dated statements in the same party and topic."""
    evidence = data['finding_evidence']
    for change in data.get('practice_position_change', []):
        before = statements.get(change['before_statement_id'])
        after = statements.get(change['after_statement_id'])
        if (not before or not after or before['id'] == after['id'] or
                any((s['party_id'], s['topic_id']) != (change['party_id'], change['topic_id']) for s in (before, after)) or before['taxonomy_version'] != after['taxonomy_version'] or
                not before['statement_at'] or not after['statement_at'] or before['statement_at'] >= after['statement_at'] or
                not change['comparison_conditions'] or not change['uncertainty_reason']):
            raise ValueError('Tutum değişimi dönem veya kapsamı geçersiz')
        check_finding(change['explanation_finding_id'], change['party_id'])
        refs = {e['passage_id'] for e in evidence if e['finding_id'] == change['explanation_finding_id']}
        before_quotes = {e['passage_id'] for e in evidence if e['finding_id'] == before['quote_finding_id']}
        after_quotes = {e['passage_id'] for e in evidence if e['finding_id'] == after['quote_finding_id']}
        findings = {f['id']: f for f in data['finding']}
        if not before_quotes or not after_quotes or before_quotes == after_quotes or findings[before['quote_finding_id']]['text'] == findings[after['quote_finding_id']]['text']:
            raise ValueError('Tutum değişimi ayrı önceki ve sonraki pasajlar gerektirir')
        for statement in (before, after):
            statement_refs = {e['passage_id'] for e in evidence if e['finding_id'] in (statement['summary_finding_id'], statement['quote_finding_id'])}
            if not refs.intersection(statement_refs):
                raise ValueError('Tutum değişimi iki söylem kaynağını gerektirir')


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
    variant = set(data).intersection(PRACTICE_VARIANT_TABLES)
    if variant:
        marker = data.get('practice_variant_contract', [])
        if variant != set(PRACTICE_VARIANT_TABLES) or len(marker) != 1 or marker[0]['version'] != 1:
            raise ValueError('Uygulama varyant sözleşmesi eksik veya geçersiz')
        try:
            inventory = json.loads(marker[0]['inventory_json'])
        except (ValueError, TypeError):
            raise ValueError('Kapsam envanteri geçersiz')
        if not isinstance(inventory, list) or _digest(inventory) != c[0]['inventory_digest']:
            raise ValueError('Kapsam envanteri özeti uyuşmuyor')
        scopes = {s['id']: s for s in data['practice_scope']}
        for s in scopes.values():
            if (s['research_kind'] != 'statement' or s['state'] not in ('not_researched', 'open', 'closed') or not s['boundary_reason'] or
                    not any((r['party_id'], r['topic_id'], r['taxonomy_version']) == (s['party_id'], s['topic_id'], s['taxonomy_version']) for r in data['comparison_row']) or
                    not any(all(cell.get(k) == s[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')) and cell.get('scope_id') == s['id'] for cell in inventory)):
                raise ValueError('Söylem araştırma kapsamı geçersiz')
            aware_time(s['cutoff_at'])
            founding = next((i['valid_from'] for i in data['identity_observation'] if i['entity_id'] == s['party_id'] and i['entity_kind'] == 'party'), None)
            cutoff = max(data['method'], key=lambda m: m['version'])['cutoff_at']
            if not founding or validate_dates(s['period_start'], 'day', founding, cutoff) == 'outside' or aware_time(s['cutoff_at']) > aware_time(cutoff) or s['period_start'] > s['cutoff_at'][:10]:
                raise ValueError('Söylem kapsam dönemi geçersiz')
        for a in data['practice_attempt']:
            if a['scope_id'] not in scopes or not all(a[k] for k in ('query', 'result', 'reason')):
                raise ValueError('Söylem arama girişimi geçersiz')
            aware_time(a['attempted_at'])
        for u in data['practice_unmatched']:
            s = scopes.get(u['statement_scope_id'])
            if (not s or u['event_id'] not in events or (u['party_id'], u['topic_id']) != (s['party_id'], s['topic_id']) or not u['reason']):
                raise ValueError('Söylemsiz olay kapsamı geçersiz')
            if any((r['event_id'], r['party_id'], r['topic_id']) == (u['event_id'], u['party_id'], u['topic_id']) for r in data['practice_relation']):
                raise ValueError('İlişkili olay aynı kapsamda söylemsiz olamaz')
            event = events[u['event_id']]
            if validate_dates(event['event_at'], event['date_precision'], s['period_start'], s['cutoff_at'], event['date_unknown_reason']) == 'outside':
                raise ValueError('Söylemsiz olay araştırma döneminin dışında')
            attempts = [a for a in data['practice_attempt'] if a['scope_id'] == s['id']]
            if u['statement_search_state'] == 'not_researched':
                if s['state'] != 'not_researched' or attempts:
                    raise ValueError('İncelenmemiş kapsamda arama girişimi olamaz')
            elif u['statement_search_state'] == 'missing':
                linked = {a['id']: a for a in data.get('attempt', [])}
                missing = data.get('missing', [])
                allowed = {'Bulunamadı': ('search', 'no_result'), 'Erişilemedi': ('access', 'failure'), 'Doğrulanamadı': ('verification', 'inconclusive')}
                if s['state'] == 'not_researched' or not attempts or not any(a['id'] in linked and (linked[a['id']]['party_id'], linked[a['id']]['topic_id']) == (s['party_id'], s['topic_id']) and all(linked[a['id']][k] == a[k] for k in ('query', 'attempted_at', 'result', 'reason', 'source_version_id')) and any(m['attempt_id'] == a['id'] and (m['party_id'], m['topic_id'], m['heading']) == (s['party_id'], s['topic_id'], linked[a['id']]['heading']) and allowed.get(m['status']) == (linked[a['id']]['type'], linked[a['id']]['result']) and m['reason'] for m in missing) for a in attempts):
                    raise ValueError('Eksik söylem için gerçek arama gerekli')
            else:
                raise ValueError('Söylem arama durumu geçersiz')
    if data.get('comparison_completion_revision'):
        selected = json.loads(max(data['comparison_completion_revision'], key=lambda x: x['epoch'])['selection'])
        selected_rows = {x['id'] for x in selected['rows']}
    else:
        selected_rows = set(rows)
    evidence = data['finding_evidence']
    verified = {(x['finding_id'], x['passage_id']): x for x in data['verification'] if x['result'] == 'confirmed' and x['reason']}
    reviewed = {x['subject_id']: x for x in data['review'] if x['kind'] == 'finding' and x['reviewer_kind'] == 'agent' and x['result'] == 'reviewed' and x['reason']}
    party_sources = {(x['version_id'], x['party_id'], x['passage_id']) for x in data['practice_source_party'] if x['scope_reason']}
    for version, party, passage in party_sources:
        if passage not in passages or passages[passage]['version_id'] != version or party not in {p['id'] for p in data['party']}:
            raise ValueError('Kaynak parti kapsamı geçersiz')
    def source_allowed(passage_id, party):
        passage = passages[passage_id]
        version = passage['version_id']
        return documents[versions[version]['document_id']]['party_id'] == party or (version, party, passage_id) in party_sources
    for item in data.get('practice_unmatched', []):
        refs = [e for e in data['practice_event_evidence'] if e['event_id'] == item['event_id']]
        if not refs or any(e['passage_id'] not in passages or not source_allowed(e['passage_id'], item['party_id']) for e in refs):
            raise ValueError('Söylemsiz olay için parti kapsamlı kaynak gerekli')
        founding = next((i['valid_from'] for i in data['identity_observation'] if i['entity_id'] == item['party_id'] and i['entity_kind'] == 'party'), None)
        event = events[item['event_id']]
        cutoff = max(data['method'], key=lambda m: m['version'])['cutoff_at']
        if not founding or validate_dates(event['event_at'], event['date_precision'], founding, cutoff, event['date_unknown_reason']) == 'outside':
            raise ValueError('Söylemsiz olay tarihi kapsam dışında')
    def check_finding(fid, party):
        f = findings.get(fid)
        refs = [x['passage_id'] for x in evidence if x['finding_id'] == fid]
        if not f or f['party_id'] != party or not refs or any((fid, p) not in verified for p in refs):
            raise ValueError('Partiyle eşleşen doğrulanmış bulgu gerekli')
        if fid not in reviewed:
            raise ValueError('Bulgu için kaynak incelemesi eksik: ' + fid)
        aware_time(reviewed[fid]['reviewed_at'])
        for p in refs:
            aware_time(verified[(fid, p)]['checked_at'])
            if p not in passages or not source_allowed(p, party):
                raise ValueError('Bulgu kaynağı parti kapsamı dışında')
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
        founding = next((i['valid_from'] for i in data['identity_observation'] if i['entity_id'] == s['party_id'] and i['entity_kind'] == 'party'), None)
        cutoff = max(data['method'], key=lambda m: m['version'])['cutoff_at']
        if not founding or validate_dates(s['statement_at'], s['date_precision'], founding, cutoff, s['uncertainty_reason']) == 'outside':
            raise ValueError('Söylem tarihi kapsam dışında')
        if s['statement_at'] and versions[s['version_id']]['document_date'] and s['statement_at'][:10] > versions[s['version_id']]['document_date']:
            raise ValueError('Söylem kaynak tarihinden sonra olamaz')
    for x in data['practice_event_evidence']:
        p = passages.get(x['passage_id'])
        if not p or x['event_id'] not in events or x['stage'] not in ('initiative', 'action', 'result') or x['epistemic_type'] not in ('claim', 'comment', 'fact') or not all(x[k] for k in ('supported_point', 'concrete_basis', 'limitation')):
            raise ValueError('Olay kanıtı geçersiz')
        doc = documents[versions[p['version_id']]['document_id']]
        if doc['source_kind'] == 'party' and x['stage'] != 'initiative':
            raise ValueError('Salt parti kaynağı oluş kanıtı değildir')
        if doc['source_kind'] in ('news', 'journalism', 'party', 'social') and x['epistemic_type'] == 'fact':
            raise ValueError('Haber veya parti iddiası doğrulanmış olguya dönüştürülemez')
        event_date = events[x['event_id']]['event_at']
        source_date = versions[p['version_id']]['document_date']
        if x['stage'] != 'initiative' and event_date and source_date and source_date < event_date[:10]:
            raise ValueError('Olay kaynağı olaydan önce yayımlanmış')
    if any(not any(x['event_id'] == event_id for x in data['practice_event_evidence']) for event_id in events):
        raise ValueError('Her olay için kaynaklı kanıt gerekli')
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
        if any(not source_allowed(x['passage_id'], r['party_id']) for x in data['practice_event_evidence'] if x['event_id'] == e['id']):
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
        if not actor or actor['party_id'] != x['party_id'] or actor['kind'] not in ('institution', 'authorized_representative', 'individual_mp') or x['contribution_kind'] not in ('support', 'objection', 'task', 'unknown') or not x['responsibility_limit']:
            raise ValueError('Aktör veya katkı sınırı geçersiz')
        if actor['kind'] in ('authorized_representative', 'individual_mp'):
            period = next((p for p in data.get('practice_actor_period', []) if p['contribution_id'] == x['id']), None)
            person = next((p for p in data['person'] if p['id'] == actor['person_id']), None)
            identity = passages.get(period['identity_passage_id']) if period else None
            event = events.get(x['event_id'])
            if not period or not person or not identity or person['name'] not in identity['exact'] or not source_allowed(identity['id'], x['party_id']) or not event or (not event['event_at'] and not event['date_unknown_reason']):
                raise ValueError('Aktör kimliği ve dönemsel yetki veya üyelik gerekli')
            start, end = date.fromisoformat(period['valid_from']), date.fromisoformat(period['valid_to'])
            if start > end or (event['event_at'] and not start <= date.fromisoformat(event['event_at'][:10]) <= end):
                raise ValueError('Aktör yetkisi olay dönemini kapsamıyor')
            if actor['kind'] == 'individual_mp':
                membership = passages.get(x['membership_passage_id'])
                party_name = next(p['legal_name'] for p in data['party'] if p['id'] == x['party_id'])
                if not membership or person['name'] not in membership['exact'] or party_name not in membership['exact'] or x['membership_passage_id'] == period['identity_passage_id'] or (documents[versions[membership['version_id']]['document_id']]['party_id'] != x['party_id'] and (membership['version_id'], x['party_id'], membership['id']) not in party_sources):
                    raise ValueError('Milletvekili kimliği ve üyeliği ayrı kanıt gerektirir')
        if actor['kind'] == 'authorized_representative' and (not x['authority_passage_id'] or x['authority_passage_id'] != actor['authorization_passage_id']):
            raise ValueError('Yetki kanıtı gerekli')
        if actor['kind'] == 'authorized_representative':
            person = next((p for p in data['person'] if p['id'] == actor['person_id']), None)
            authority = passages.get(x['authority_passage_id'])
            if not person or not authority or person['name'] not in authority['exact'] or not source_allowed(authority['id'], x['party_id']):
                raise ValueError('Temsil yetkisi kişi ve partiyle uyuşmuyor')
        event = events.get(x['event_id'])
        founding = next((i['valid_from'] for i in data['identity_observation'] if i['entity_id'] == x['party_id'] and i['entity_kind'] == 'party'), None)
        cutoff = max(data['method'], key=lambda m: m['version'])['cutoff_at']
        if not event or not founding or validate_dates(event['event_at'], event['date_precision'], founding, cutoff, event['date_unknown_reason']) == 'outside':
            raise ValueError('Katkı tarihi parti kapsamı dışında')
        finding = check_finding(x['finding_id'], x['party_id'])
        refs = {r['passage_id'] for r in evidence if r['finding_id'] == finding['id']}
        event_refs = {r['passage_id'] for r in data['practice_event_evidence'] if r['event_id'] == x['event_id']}
        if not refs.intersection(event_refs):
            raise ValueError('Katkı olay kanıtıyla uyuşmuyor')
        if finding['epistemic_type'] == 'fact' and any(documents[versions[passages[p]['version_id']]['document_id']]['source_kind'] in ('news', 'journalism', 'party', 'social') for p in refs):
            raise ValueError('Haber kaynaklı katkı iddia olarak korunmalı')
    contributions = {x['id']: x for x in data['practice_contribution']}
    for period in data.get('practice_actor_period', []):
        contribution = contributions.get(period['contribution_id'])
        if not contribution or actors[contribution['actor_id']]['kind'] not in ('authorized_representative', 'individual_mp'):
            raise ValueError('Aktör dönemi katkıya bağlı olmalı')
    for link in data['practice_legacy_link']:
        if link['legacy_kind'] not in ('action', 'match', 'candidate') or not link['overlap_reason']:
            raise ValueError('Eski kayıt köprüsü geçersiz')
        table = {'action': 'action', 'match': 'match', 'candidate': 'match_candidate'}[link['legacy_kind']]
        key = 'finding_id' if table == 'action' else 'id'
        if not any(x[key] == link['legacy_id'] for x in data[table]):
            raise ValueError('Eski kayıt bulunamadı')
    validate_practice_evidence(data, findings, passages, events, statements, check_finding, party_sources)
    validate_practice_temporality(data, statements, check_finding)
    linked = {value for name in ('practice_statement', 'practice_relation', 'practice_contribution', 'practice_dispute', 'practice_position_change') for row in data.get(name, []) for key, value in row.items() if key.endswith('finding_id') and value}
    pairs = {findings[fid]['pair_id'] for fid in linked if fid in findings}
    for finding in findings.values():
        if finding['pair_id'] in pairs:
            check_finding(finding['id'], finding['party_id'])
    return True


def practice_manifest_fields(data):
    c = data['practice_contract'][0]
    result = dict(practice_validation_version=c['version'], practice_stage=c['stage'], practice_inventory_sha256=c['inventory_digest'], practice_selection_sha256=_digest({k: data[k] for k in PRACTICE_TABLES}))
    if 'practice_variant_contract' in data:
        result['practice_variant_sha256'] = _digest({k: data[k] for k in PRACTICE_VARIANT_TABLES})
    if 'practice_evidence_contract' in data:
        result['practice_evidence_sha256'] = _digest({k: data[k] for k in PRACTICE_EVIDENCE_TABLES})
    return result


def validate_practice_descent(base, candidate):
    if 'practice_evidence_contract' in base:
        for name in PRACTICE_EVIDENCE_TABLES:
            if name not in candidate or any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki uygulama kanıt sözleşmesi değiştirilemez')
    if 'practice_variant_contract' in base:
        if any(k not in candidate for k in PRACTICE_VARIANT_TABLES):
            raise ValueError('Uygulama varyant sözleşmesi kaldırılamaz')
        for name in PRACTICE_VARIANT_TABLES:
            if any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki uygulama varyantı değiştirilemez')
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
    from arsiv import connect, validate_phase_one_workspace, aware_time
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
        input_findings = {entry['values']['id'] for entry in payload['entries'] if entry.get('kind') == 'finding' and isinstance(entry.get('values'), dict) and entry['values'].get('id')}
        for entry in payload['entries']:
            kind, values = entry['kind'], entry['values']
            if kind not in ('finding', 'finding_evidence', 'verification', 'source_attribution', 'review') or not values:
                raise ValueError('Uygulama girdi türü geçersiz')
            if kind == 'review' and (values.get('kind'), values.get('reviewer_kind'), values.get('result')) != ('finding', 'agent', 'reviewed'):
                raise ValueError('Yalnız ajan bulgu incelemesi eklenebilir')
            if kind == 'review':
                if values.get('subject_id') not in input_findings or not values.get('reason'):
                    raise ValueError('İnceleme yeni bir bulguya ve gerekçeye bağlı olmalı')
                aware_time(values.get('reviewed_at'))
            cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
            if not set(values) <= cols:
                raise ValueError('Bilinmeyen alan')
            db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
        records = payload['practice_records']
        variant = set(records).intersection(PRACTICE_VARIANT_TABLES)
        if variant and variant != set(PRACTICE_VARIANT_TABLES):
            raise ValueError('Uygulama varyant tabloları eksik')
        tables = dict(PRACTICE_TABLES)
        if variant:
            tables.update(PRACTICE_VARIANT_TABLES)
            for name, definition in PRACTICE_VARIANT_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        extension = set(records).intersection(PRACTICE_EVIDENCE_TABLES)
        if extension:
            if extension != set(PRACTICE_EVIDENCE_TABLES) or not variant:
                raise ValueError('Uygulama kanıt tabloları eksik')
            tables.update(PRACTICE_EVIDENCE_TABLES)
            for name, definition in PRACTICE_EVIDENCE_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        if set(records) != set(tables):
            raise ValueError('Uygulama tabloları eksik')
        for kind in tables:
            for values in records[kind]:
                cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
                if set(values) != cols:
                    raise ValueError('Uygulama alanları uyuşmuyor')
                db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
        # Validate a transaction-consistent snapshot before the commit.
        data = {name: [dict(x) for x in db.execute(f'SELECT * FROM {name}')] for name in list(tables) + ['finding', 'finding_evidence', 'verification', 'review', 'passage', 'document_version', 'document', 'actor', 'person', 'comparison_contract', 'comparison_row', 'comparison_completion_revision', 'identity_observation', 'method', 'party', 'action', 'match', 'match_candidate', 'attempt', 'missing']}
        validate_practices(data)
        if db.execute('PRAGMA foreign_key_check').fetchall() or db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Uygulama bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    validate_phase_one_workspace(work)


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
        del current_data
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
