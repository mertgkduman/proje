"""Söylem ve belgelenmiş uygulamalar için sürümlü iç sözleşme."""
import hashlib
import json
import sqlite3
from datetime import date
from pathlib import Path
from uygulama_merge_kayit import (ENTRY_KINDS, PRACTICE_ENTRY_ORDER, PRACTICE_MERGE_TABLES,
                                  materialize_practice_merge, practice_entry_matches, validate_practice_merge)

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

# Coverage v2 is append-only: v1 scope rows remain byte-identical while new
# scopes and their transitions can evolve without mutating archived snapshots.
# Extension topic IDs intentionally do not reference comparison_topic: those
# topics belong to practice research and must not change the Phase 3 taxonomy.
PRACTICE_COVERAGE_TABLES = {
    'practice_coverage_contract': 'version INTEGER PRIMARY KEY, inventory_json TEXT NOT NULL',
    'practice_inventory_revision': 'epoch INTEGER PRIMARY KEY, inventory_json TEXT NOT NULL, reason TEXT NOT NULL',
    'practice_scope_v2': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, period_start TEXT NOT NULL, cutoff_at TEXT NOT NULL, research_kind TEXT NOT NULL, boundary_reason TEXT NOT NULL',
    'practice_scope_source': 'scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), version_id TEXT NOT NULL REFERENCES document_version(id), inspected_sections TEXT NOT NULL, inspected_at TEXT NOT NULL, PRIMARY KEY(scope_id,version_id,inspected_at)',
    'practice_lead': 'id TEXT PRIMARY KEY, scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), url TEXT NOT NULL, relevance_reason TEXT NOT NULL, state TEXT NOT NULL, attempt_ids TEXT NOT NULL',
    'practice_lead_revision': 'id TEXT PRIMARY KEY, lead_id TEXT NOT NULL REFERENCES practice_lead(id), recorded_at TEXT NOT NULL, state TEXT NOT NULL, attempt_ids TEXT NOT NULL, reason TEXT NOT NULL',
    'practice_attempt_v2': 'id TEXT PRIMARY KEY, scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), attempted_at TEXT NOT NULL, query TEXT NOT NULL, url TEXT, result TEXT NOT NULL, reason TEXT NOT NULL, source_version_id TEXT REFERENCES document_version(id)',
    'practice_candidate': 'id TEXT PRIMARY KEY, scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), event_id TEXT REFERENCES practice_event(id), relation_id TEXT REFERENCES practice_relation(id), state TEXT NOT NULL, reason TEXT NOT NULL, passage_ids TEXT NOT NULL',
    'practice_candidate_legacy': 'candidate_id TEXT NOT NULL REFERENCES practice_candidate(id), legacy_id TEXT NOT NULL REFERENCES match_candidate(id), reason TEXT NOT NULL, PRIMARY KEY(candidate_id,legacy_id)',
    'practice_candidate_revision': 'id TEXT PRIMARY KEY, candidate_id TEXT NOT NULL REFERENCES practice_candidate(id), recorded_at TEXT NOT NULL, event_id TEXT REFERENCES practice_event(id), relation_id TEXT REFERENCES practice_relation(id), state TEXT NOT NULL, reason TEXT NOT NULL, passage_ids TEXT NOT NULL',
    'practice_closure': 'id TEXT PRIMARY KEY, scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), closed_at TEXT NOT NULL, reason TEXT NOT NULL, residual_lead_ids TEXT NOT NULL',
    'practice_reopen': 'id TEXT PRIMARY KEY, closure_id TEXT NOT NULL REFERENCES practice_closure(id), lead_id TEXT NOT NULL REFERENCES practice_lead(id), opened_at TEXT NOT NULL, reason TEXT NOT NULL',
    'practice_topic_extension': 'id TEXT PRIMARY KEY, parent_topic_id TEXT NOT NULL, definition TEXT NOT NULL, basis_passage_ids TEXT NOT NULL, reason TEXT NOT NULL',
    'practice_legacy_scope': 'scope_id TEXT NOT NULL REFERENCES practice_scope_v2(id), closure_id TEXT NOT NULL REFERENCES closure(id), attempt_id TEXT NOT NULL REFERENCES attempt(id), mapping_reason TEXT NOT NULL, PRIMARY KEY(scope_id,closure_id,attempt_id)',
}

# Optional independent reading extension; older snapshots retain their bytes.
PRACTICE_SOURCE_REVIEW_TABLES = {
    'practice_source_review_contract': 'version INTEGER PRIMARY KEY',
    'practice_source_review': 'subject_kind TEXT NOT NULL, subject_id TEXT NOT NULL, reviewer_kind TEXT NOT NULL, reviewed_at TEXT NOT NULL, source_version_ids TEXT NOT NULL, passage_ids TEXT NOT NULL, inspected_sections TEXT NOT NULL, supported_claim TEXT NOT NULL, limitations TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(subject_kind,subject_id)',
}

# An additive adapter leaves published v1 rows and serialization untouched.
PRACTICE_SOURCE_REVIEW_REVISION_TABLES = {
    'practice_source_review_revision_contract': 'version INTEGER PRIMARY KEY',
    'practice_source_review_revision': 'subject_kind TEXT NOT NULL, subject_id TEXT NOT NULL, revision INTEGER NOT NULL, reviewer_kind TEXT NOT NULL, reviewed_at TEXT NOT NULL, source_version_ids TEXT NOT NULL, passage_ids TEXT NOT NULL, inspected_sections TEXT NOT NULL, supported_claim TEXT NOT NULL, limitations TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(subject_kind,subject_id,revision), FOREIGN KEY(subject_kind,subject_id) REFERENCES practice_source_review(subject_kind,subject_id)',
}


def _unmatched_candidates(data, selection):
    """Yield the retained candidate and revision records with their owner."""
    scopes = {scope['id']: scope for scope in data.get('practice_scope_v2', [])}
    parents = {row['id']: row for row in data.get('practice_candidate', [])}
    for row in selection.get('practice_candidate', []):
        if row['state'] == 'unmatched' and row['scope_id'] in scopes:
            yield 'practice_candidate', row, scopes[row['scope_id']]
    for row in selection.get('practice_candidate_revision', []):
        parent = parents.get(row['candidate_id'])
        if row['state'] == 'unmatched' and parent and parent['scope_id'] in scopes:
            yield 'practice_candidate_revision', row, scopes[parent['scope_id']]


def practice_review_targets(data, selection=None):
    """Map each semantic target to its actual passages and party boundaries."""
    selected = data if selection is None else selection
    targets = {}
    evidence = data.get('finding_evidence', [])
    unmatched_parties = {}
    for _, row, scope in _unmatched_candidates(data, data):
        unmatched_parties.setdefault(row['event_id'], set()).add(scope['party_id'])

    def add(kind, identity, passages, parties=()):
        key = (kind, identity)
        refs = {p for p in passages if p}
        if not refs:
            raise ValueError('İnceleme hedefinin kaynak pasajı eksik: ' + repr(key))
        if key in targets:
            raise ValueError('Tekrarlı inceleme hedefi')
        targets[key] = (refs, {p for p in parties if p})

    for row in selected.get('practice_event_evidence', []):
        event_id = row['event_id']
        parties = [r['party_id'] for name in ('practice_relation', 'practice_contribution', 'practice_unmatched')
                   for r in data.get(name, []) if r['event_id'] == event_id]
        parties.extend(unmatched_parties.get(event_id, ()))
        add('practice_event_evidence', '|'.join((event_id, row['passage_id'], row['stage'])), [row['passage_id']], parties)
    for row in selected.get('practice_event', []):
        event_id = row['id']
        refs = [e['passage_id'] for e in data.get('practice_event_evidence', []) if e['event_id'] == event_id]
        parties = [r['party_id'] for name in ('practice_relation', 'practice_contribution', 'practice_unmatched')
                   for r in data.get(name, []) if r['event_id'] == event_id]
        parties.extend(unmatched_parties.get(event_id, ()))
        add('practice_event', event_id, refs, parties)
    for name, fields in {
        'practice_statement': ('summary_finding_id', 'quote_finding_id'),
        'practice_relation': ('target_finding_id', 'result_finding_id', 'explanation_finding_id'),
        'practice_contribution': ('finding_id',),
        'practice_dispute': ('summary_finding_id',),
        'practice_position_change': ('explanation_finding_id',),
    }.items():
        for row in selected.get(name, []):
            if name in ('practice_statement', 'practice_relation', 'practice_contribution', 'practice_dispute', 'practice_position_change'):
                ids = [row.get(field) for field in fields if row.get(field)]
                refs = [e['passage_id'] for e in evidence if e['finding_id'] in ids]
                if name in ('practice_relation', 'practice_dispute'):
                    refs += [e['passage_id'] for e in data.get('practice_event_evidence', []) if e['event_id'] == row['event_id']]
                if name == 'practice_relation':
                    statement = next((s for s in data.get('practice_statement', []) if s['id'] == row['statement_id']), None)
                    if not statement:
                        raise ValueError('İnceleme ilişkisinin söylemi bulunamadı')
                    refs += [e['passage_id'] for e in evidence if e['finding_id'] in (statement['summary_finding_id'], statement['quote_finding_id'])]
                if name == 'practice_contribution':
                    refs += [row.get('authority_passage_id'), row.get('membership_passage_id')]
                parties = [row.get('party_id')]
                if name == 'practice_dispute':
                    parties += [f['party_id'] for f in data.get('finding', []) if f['id'] in ids]
                add(name, row['id'], refs, parties)
            for field in fields:
                fid = row.get(field)
                if fid:
                    party = row.get('party_id')
                    if not party:
                        party = next((f['party_id'] for f in data.get('finding', []) if f['id'] == fid), None)
                    add(name + '.' + field, row['id'], [e['passage_id'] for e in evidence if e['finding_id'] == fid], [party])
    for row in selected.get('practice_dispute_evidence', []):
        identity = '|'.join((row['dispute_id'], row['passage_id'], row['point'], row['role']))
        dispute = next((d for d in data.get('practice_dispute', []) if d['id'] == row['dispute_id']), None)
        if not dispute:
            raise ValueError('İnceleme uyuşmazlığı bulunamadı')
        parties = [f['party_id'] for f in data.get('finding', []) if f['id'] == dispute['summary_finding_id']]
        add('practice_dispute_evidence', identity, [row['passage_id']], parties)
    for row in selected.get('practice_unmatched', []):
        refs = [e['passage_id'] for e in data.get('practice_event_evidence', []) if e['event_id'] == row['event_id']]
        add('practice_unmatched', row['id'], refs, [row['party_id']])
    for kind, row, scope in _unmatched_candidates(data, selected):
        add(kind, row['id'], json.loads(row['passage_ids']), [scope['party_id']])
    return targets


def practice_review_package_targets(data, records, new_passages, party_id=None):
    """Include existing targets affected by newly attached evidence."""
    targets = practice_review_targets(data, records)
    targets.update({key: value for key, value in practice_review_targets(data).items() if value[0] & set(new_passages)})
    return {key: value for key, value in targets.items() if party_id is None or not value[1] or party_id in value[1]}


def validate_practice_source_review(data, reviews, selection=None, *, require_coverage=True, party_id=None, revisions=None, target_keys=None):
    """Validate recorded agent reading, without claiming to repeat that reading."""
    from arsiv import aware_time
    targets = practice_review_targets(data, selection if target_keys is None else None)
    if target_keys is not None:
        if not set(target_keys) <= set(targets):
            raise ValueError('Kaynak inceleme hedefi bulunamadı')
        targets = {key: targets[key] for key in target_keys}
    if party_id is not None:
        targets = {key: value for key, value in targets.items() if not value[1] or party_id in value[1]}
    passages = {p['id']: p for p in data['passage']}
    versions = {v['id']: v for v in data['document_version']}
    documents = {d['id']: d for d in data['document']}
    shared = {(r['version_id'], r['party_id'], r['passage_id']) for r in data.get('practice_source_party', []) if r.get('scope_reason')}
    seen = set()
    descriptions = set()
    fields = {'subject_kind', 'subject_id', 'reviewer_kind', 'reviewed_at', 'source_version_ids', 'passage_ids', 'inspected_sections', 'supported_claim', 'limitations', 'result', 'reason'}
    if not isinstance(reviews, list) or (revisions is not None and not isinstance(revisions, list)):
        raise ValueError('Kaynak inceleme kayıtları dizi olmalı')
    versioned = revisions is not None
    grouped = {}
    for row in reviews:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError('Kaynak inceleme alanları geçersiz')
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ('subject_kind', 'subject_id', 'reviewer_kind', 'reviewed_at', 'result')):
            raise ValueError('Kaynak inceleme kimliği veya durumu geçersiz')
        key = (row['subject_kind'], row['subject_id'])
        if key in grouped:
            raise ValueError('Kaynak inceleme hedefi tekrarlı')
        grouped[key] = [(1, row)]
    for item in revisions or []:
        if not isinstance(item, dict) or set(item) != fields | {'revision'} or type(item['revision']) is not int or item['revision'] < 2:
            raise ValueError('Kaynak inceleme revizyonu geçersiz')
        row = {k: item[k] for k in fields}
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ('subject_kind', 'subject_id', 'reviewer_kind', 'reviewed_at', 'result')):
            raise ValueError('Kaynak inceleme kimliği veya durumu geçersiz')
        key = (row['subject_kind'], row['subject_id'])
        if key not in grouped:
            raise ValueError('İlk kaynak incelemesi bulunamadı')
        grouped[key].append((item['revision'], row))
    ordered = []
    for key, items in grouped.items():
        items.sort(key=lambda item: item[0])
        if [i for i, _ in items] != list(range(1, len(items) + 1)):
            raise ValueError('Kaynak inceleme revizyon sırası belirsiz')
        previous_time = None
        previous_passages = set()
        for index, (_, row) in enumerate(items):
            when = aware_time(row['reviewed_at'])
            if previous_time is not None and when <= previous_time:
                raise ValueError('Kaynak inceleme revizyon tarihi ilerlemeli')
            previous_time = when
            try:
                passage_set = set(json.loads(row['passage_ids']))
            except (TypeError, ValueError):
                raise ValueError('Kaynak inceleme pasajları geçersiz')
            if not previous_passages <= passage_set:
                raise ValueError('Önceki inceleme kapsamı korunmalı')
            previous_passages = passage_set
            ordered.append((row, index == len(items) - 1))
    for row, latest in ordered:
        if not isinstance(row, dict) or set(row) != fields:
            raise ValueError('Kaynak inceleme alanları geçersiz')
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ('subject_kind', 'subject_id', 'reviewer_kind', 'reviewed_at', 'result')):
            raise ValueError('Kaynak inceleme kimliği veya durumu geçersiz')
        key = (row['subject_kind'], row['subject_id'])
        if (key in seen and not versioned) or key not in targets:
            raise ValueError('Kaynak inceleme hedefi tekrarlı veya bulunamadı')
        seen.add(key)
        if row['reviewer_kind'] != 'agent' or row['result'] != 'reviewed':
            raise ValueError('Kaynak incelemesi ajan okuması olmalı')
        aware_time(row['reviewed_at'])
        if any(not isinstance(row[k], str) or len(row[k].strip()) < 10 for k in ('supported_claim', 'limitations', 'reason')):
            raise ValueError('Kaynak inceleme açıklaması eksik')
        try:
            arrays = [json.loads(row[k]) for k in ('source_version_ids', 'passage_ids', 'inspected_sections')]
        except (TypeError, ValueError):
            raise ValueError('Kaynak inceleme dizisi geçersiz')
        for items in arrays:
            if not isinstance(items, list) or not items or any(not isinstance(x, str) or not x.strip() for x in items) or len(set(items)) != len(items):
                raise ValueError('Kaynak inceleme dizisi boş veya geçersiz')
        version_ids, passage_ids, sections = arrays
        vague = {'all', 'tümü', 'tamamı', 'source', 'kaynak', 'article', 'haber', 'full article'}
        if any(section.strip().casefold() in vague or len(section.strip()) < 5 for section in sections):
            raise ValueError('İncelenen bölümler somut olarak belirtilmeli')
        description = tuple(row[k].strip() for k in ('inspected_sections', 'supported_claim', 'limitations', 'reason'))
        if description in descriptions:
            raise ValueError('Aynı genel açıklama birden çok hedefe kopyalanamaz')
        descriptions.add(description)
        required, parties = targets[key]
        if (not set(passage_ids) <= required or (latest and (require_coverage or not versioned) and set(passage_ids) != required) or any(p not in passages for p in passage_ids)):
            raise ValueError('Kaynak inceleme pasajı hedefle uyuşmuyor')
        if set(version_ids) != {passages[p]['version_id'] for p in passage_ids} or any(v not in versions for v in version_ids):
            raise ValueError('Kaynak inceleme sürümü pasajla uyuşmuyor')
        for p in passage_ids:
            v = passages[p]['version_id']
            document = documents.get(versions[v]['document_id'])
            if not document or any(document['party_id'] != party and (v, party, p) not in shared for party in parties):
                raise ValueError('Kaynak inceleme parti sahibi uyuşmuyor')
    if require_coverage and seen != set(targets):
        raise ValueError('Kaynak inceleme hedef kapsamı eksik')
    return True


def practice_source_review_pending(data, reviews, revisions, selection=None, *, party_id=None, target_keys=None):
    """Return uncovered current targets after validating all historical readings."""
    validate_practice_source_review(data, reviews, selection, require_coverage=False,
                                    party_id=party_id, revisions=revisions, target_keys=target_keys)
    targets = practice_review_targets(data, selection if target_keys is None else None)
    if target_keys is not None:
        targets = {key: targets[key] for key in target_keys}
    if party_id is not None:
        targets = {key: value for key, value in targets.items() if not value[1] or party_id in value[1]}
    latest = {(row['subject_kind'], row['subject_id']): (1, row) for row in reviews}
    for row in revisions:
        key = (row['subject_kind'], row['subject_id'])
        if row['revision'] > latest[key][0]:
            latest[key] = (row['revision'], row)
    return [dict(subject_kind=kind, subject_id=identity, state='pending')
            for (kind, identity), (required, _) in sorted(targets.items())
            if (kind, identity) not in latest or set(json.loads(latest[(kind, identity)][1]['passage_ids'])) != required]


def prepare_practice_merge_pending_reviews(payload, base_records):
    """Preserve accepted base readings and activate the v2 adapter for a partial merge."""
    import copy
    result = copy.deepcopy(payload)
    records = result['practice_records']
    if result.get('stage') != 'partial' or not set(PRACTICE_MERGE_TABLES) <= set(records):
        raise ValueError('Bekleyen inceleme yalnız kısmi birleşmede kullanılabilir')
    if not base_records.get('practice_source_review_contract'):
        raise ValueError('Önceki kaynak incelemesi bulunamadı')
    old_revision_tables = set(base_records).intersection(PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
    if old_revision_tables and old_revision_tables != set(PRACTICE_SOURCE_REVIEW_REVISION_TABLES):
        raise ValueError('Önceki inceleme revizyonu eksik')
    preserved = {name: copy.deepcopy(base_records[name]) for name in PRACTICE_SOURCE_REVIEW_TABLES}
    preserved.update({name: copy.deepcopy(base_records[name]) for name in PRACTICE_SOURCE_REVIEW_REVISION_TABLES if name in base_records})
    preserved.setdefault('practice_source_review_revision_contract', [dict(version=2)])
    preserved.setdefault('practice_source_review_revision', [])
    for name, rows in preserved.items():
        if name in records and records[name] != rows:
            raise ValueError('Önceki kaynak incelemesi değiştirilemez')
        records[name] = rows
    refs = [dict(subject_kind=kind, subject_id=identity)
        for kind, identity in sorted({(row['subject_kind'], row['subject_id']) for row in preserved['practice_source_review'] + preserved['practice_source_review_revision']})]
    existing_refs = result.get('source_review_refs')
    if existing_refs not in (None, [], refs):
        raise ValueError('Birleşme kaynak inceleme başvuruları değiştirilemez')
    result['source_review_refs'] = refs
    return result


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def build_practice_inventory(data, extensions=()):
    """Derive the research queue from the authoritative completed selection."""
    selection = json.loads(max(data['comparison_completion_revision'], key=lambda x: x['epoch'])['selection'])
    topics = list(selection['topics'])
    selected_ids = {t['topic_id'] for t in topics}
    passages = {p['id'] for p in data['passage']}
    extension_ids = set()
    for extension in extensions:
        if (not isinstance(extension, dict) or set(extension) != {'id', 'parent_topic_id', 'definition', 'basis_passage_ids', 'reason'} or
                any(not isinstance(extension[k], str) or not extension[k] for k in ('id', 'parent_topic_id', 'definition', 'reason')) or
                extension['id'] in selected_ids or extension['id'] in extension_ids or
                extension['parent_topic_id'] not in selected_ids or not extension['definition'] or not extension['reason'] or
                not isinstance(extension['basis_passage_ids'], list) or not extension['basis_passage_ids'] or
                any(not isinstance(p, str) for p in extension['basis_passage_ids']) or
                not set(extension['basis_passage_ids']) <= passages):
            raise ValueError('Konu uzantısı kaynak veya kapsamı geçersiz')
        extension_ids.add(extension['id'])
        topics.append(dict(topic_id=extension['id'], taxonomy_version=4, parent_topic_id=extension['parent_topic_id'], definition=extension['definition'], basis_passage_ids=extension['basis_passage_ids'], reason=extension['reason']))
    parties = sorted(data['scope_party'], key=lambda x: x['approved_order'])
    method = max(data['method'], key=lambda x: x['version'])
    cells = []
    for party in parties:
        pid = party['party_id']
        starts = [x['valid_from'] for x in data['identity_observation'] if x['entity_kind'] == 'party' and x['entity_id'] == pid and x['valid_from']]
        if len(starts) != 1:
            raise ValueError('Parti için tek kuruluş tarihi gerekli')
        for topic in topics:
            for kind in ('statement', 'event'):
                key = [pid, topic['topic_id'], topic['taxonomy_version'], starts[0], method['cutoff_at'], kind]
                cells.append(dict(cell_id='practice-' + _digest(key), party_id=pid, topic_id=topic['topic_id'], taxonomy_version=topic['taxonomy_version'], period_start=starts[0], cutoff_at=method['cutoff_at'], research_kind=kind, state='not_researched'))
    return dict(base_release=data['release_id'], method_version=method['version'], cutoff_at=method['cutoff_at'], taxonomy_version=4, parties=parties, topics=topics, cells=cells, source_collections=selection['inventory'])


def validate_practice_coverage(data, inventory, extensions=()):
    expected = build_practice_inventory(data, extensions)
    if inventory != expected:
        raise ValueError('Envanter kanonik seçili evrenle uyuşmuyor')
    return True


def validate_preview_inventory(data, accepted_base, base_release, inventory, extensions=()):
    """Validate the universe against the base or its recorded inventory history."""
    if not isinstance(inventory, dict):
        raise ValueError('Envanter geçersiz')
    inventory_base = base_release
    if inventory.get('base_release') != base_release:
        try:
            rows = accepted_base.get('practice_coverage_contract', []) + accepted_base.get('practice_inventory_revision', [])
            recorded = [json.loads(row['inventory_json']) for row in rows]
        except (KeyError, TypeError, ValueError):
            raise ValueError('Kabul edilmiş kapsam geçmişi geçersiz')
        if inventory not in recorded:
            raise ValueError('Envanter kabul edilmiş kapsam geçmişinde bulunamadı')
        inventory_base = inventory['base_release']
    return validate_practice_coverage(dict(data, release_id=inventory_base), inventory, extensions)


def validate_practice_closure(data, inventory, extensions=()):
    """Validate append-only coverage records against the canonical universe.

    A closure records a bounded research process, never proof that no event
    exists. A later relevant lead must reopen that closure before it can be
    counted as closed again.
    """
    from arsiv import aware_time, safe_url, normalize_url, validate_dates

    snapshot = dict(data, release_id=inventory['base_release'])
    validate_practice_coverage(snapshot, inventory, extensions)
    cells = {cell['cell_id']: cell for cell in inventory['cells']}
    scopes = {scope['id']: scope for scope in data['practice_scope_v2']}
    relation_scopes = {scope['id']: scope for scope in data.get('practice_scope', [])}
    relation_scopes.update(scopes)
    attempts = {attempt['id']: attempt for attempt in data['practice_attempt_v2']}
    legacy_attempts = {attempt['id']: attempt for attempt in data['attempt']}
    legacy_leads = {lead['id']: lead for lead in data['lead']}
    legacy_closures = {item['id']: item for item in data['closure']}
    bridged_topics = {}
    for bridge in data.get('practice_legacy_scope', []):
        old = legacy_closures.get(bridge['closure_id'])
        if old:
            bridged_topics.setdefault(bridge['scope_id'], set()).add(old['topic_id'])
    leads = {lead['id']: dict(lead) for lead in data['practice_lead']}
    closures = {closure['id']: closure for closure in data['practice_closure']}
    versions = {version['id']: version for version in data['document_version']}
    documents = {doc['id']: doc for doc in data['document']}
    passages = {passage['id']: passage for passage in data['passage']}
    shared = {(x['version_id'], x['party_id'], x['passage_id']) for x in data['practice_source_party'] if x['scope_reason']}

    def source_allowed(version_id, party, passage_id=None):
        version = versions.get(version_id)
        document = documents.get(version['document_id']) if version else None
        return bool(document and (document['party_id'] == party or any(v == version_id and p == party and (passage_id is None or ref == passage_id) for v, p, ref in shared)))

    for relation in data['practice_relation']:
        if relation['scope_id']:
            scope = relation_scopes.get(relation['scope_id'])
            if not scope or (scope['party_id'], scope['topic_id']) != (relation['party_id'], relation['topic_id']):
                raise ValueError('İlişki araştırma kapsamıyla uyuşmuyor')

    revisions = sorted(data.get('practice_lead_revision', []), key=lambda r: aware_time(r['recorded_at']))
    if len({(r['lead_id'], aware_time(r['recorded_at'])) for r in revisions}) != len(revisions):
        raise ValueError('Uç revizyonları aynı zamanda çakışamaz')
    for revision in revisions:
        lead = leads.get(revision['lead_id'])
        if not lead or not revision['reason'] or revision['state'] not in ('pending', 'examined', 'blocked', 'excluded'):
            raise ValueError('Uç revizyonu geçersiz')
        lead.update(state=revision['state'], attempt_ids=revision['attempt_ids'])

    for scope in scopes.values():
        cell = cells.get(scope['id'])
        if not cell or not scope['boundary_reason'] or any(scope[k] != cell[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')):
            raise ValueError('Kanonik parti kapsamı uyuşmuyor')
    for item in attempts.values():
        scope = scopes.get(item['scope_id'])
        original = legacy_attempts.get(item['id'])
        allowed_topics = {scope['topic_id']} | bridged_topics.get(scope['id'], set()) if scope else set()
        if (not scope or not item['query'] or not item['reason'] or item['result'] not in ('no_result', 'results', 'failure', 'examined', 'inconclusive', 'confirmed', 'excluded') or
                (original and (original['party_id'] != scope['party_id'] or original['topic_id'] not in allowed_topics or
                 any(original[k] != item[k] for k in ('attempted_at', 'query', 'result', 'reason', 'source_version_id'))))):
            raise ValueError('Gerçek parti ve konu girişimi gerekli')
        aware_time(item['attempted_at'])
        old_lead = legacy_leads.get(original['lead_id']) if original else None
        if original and original['result'] == 'examined' and (not old_lead or (old_lead['party_id'], old_lead['topic_id']) != (original['party_id'], original['topic_id'])):
            raise ValueError('Kaynak incelemesi aynı kapsamda kayıtlı uç gerektirir')
        if item['url']:
            safe_url(item['url'])
            if original and ((old_lead and old_lead['url'] != item['url']) or (not old_lead and original['query'] != item['url'])):
                raise ValueError('Girişim URL kaynağıyla uyuşmuyor')
        if item['source_version_id'] and not source_allowed(item['source_version_id'], scope['party_id']):
            raise ValueError('Girişim kaynağı parti kapsamı dışında')
        if item['result'] == 'examined':
            version = versions.get(item['source_version_id'])
            if not version or not item['url'] or item['url'] not in (version['original_url'], version['final_url']):
                raise ValueError('Kaynak incelemesi arşivlenmiş kaynak adresini gerektirir')
        if item['result'] == 'no_result':
            if not original or original['type'] != 'search' or not any(m['attempt_id'] == item['id'] and m['party_id'] == scope['party_id'] and m['topic_id'] == original['topic_id'] and m['heading'] == original['heading'] and m['status'] == 'Bulunamadı' and m['reason'] for m in data['missing']):
                raise ValueError('Sonuçsuz arama gerçek eksik zinciri gerektirir')
    for bridge in data.get('practice_legacy_scope', []):
        scope = scopes.get(bridge['scope_id'])
        old = legacy_closures.get(bridge['closure_id'])
        attempt = legacy_attempts.get(bridge['attempt_id'])
        if (not scope or not old or not attempt or not bridge['mapping_reason'] or
                attempt['party_id'] != scope['party_id'] or attempt['topic_id'] != old['topic_id'] or
                not attempt['source_version_id'] or not source_allowed(attempt['source_version_id'], scope['party_id'])):
            raise ValueError('Eski tarama köprüsü parti veya kaynakla uyuşmuyor')
        relations = [r for r in data['practice_relation'] if (r['party_id'], r['topic_id']) == (scope['party_id'], scope['topic_id'])]
        event_ids = {r['event_id'] for r in relations}
        event_passages = {e['passage_id'] for e in data['practice_event_evidence'] if e['event_id'] in event_ids}
        statement_ids = {r['statement_id'] for r in relations}
        statement_versions = {s['version_id'] for s in data['practice_statement'] if s['id'] in statement_ids}
        supported = (any(passages.get(p, {}).get('version_id') == attempt['source_version_id'] for p in event_passages)
                     if scope['research_kind'] == 'event' else attempt['source_version_id'] in statement_versions)
        if not supported:
            raise ValueError('Eski tarama köprüsü seçili konu kanıtına bağlanmalı')
    for lead in leads.values():
        scope = scopes.get(lead['scope_id'])
        try:
            linked = json.loads(lead['attempt_ids'])
            safe_url(lead['url'])
        except (ValueError, TypeError):
            raise ValueError('Uç girişimleri veya URL geçersiz')
        if not scope or not lead['relevance_reason'] or lead['state'] not in ('pending', 'examined', 'blocked', 'excluded') or not isinstance(linked, list) or any(not isinstance(a, str) for a in linked):
            raise ValueError('Araştırma ucu geçersiz')
        old_lead = legacy_leads.get(lead['id'])
        allowed_topics = {scope['topic_id']} | bridged_topics.get(scope['id'], set())
        if old_lead and (old_lead['party_id'] != scope['party_id'] or old_lead['topic_id'] not in allowed_topics or old_lead['url'] != lead['url']):
            raise ValueError('Önceki uç parti, konu veya URL ile uyuşmuyor')
        if any(a not in attempts or attempts[a]['scope_id'] != scope['id'] for a in linked) or (lead['state'] != 'pending' and not linked):
            raise ValueError('Uç aynı kapsamdaki gerçek girişimi gerektirir')
        resolved = [attempts[a] for a in linked if attempts[a]['url'] and normalize_url(attempts[a]['url']) == normalize_url(lead['url'])]
        if lead['state'] == 'examined' and not any(a['result'] == 'examined' and a['source_version_id'] for a in resolved):
            raise ValueError('İncelenen uç kaynaklı inceleme gerektirir')
        if lead['state'] == 'blocked' and not any(a['result'] in ('failure', 'inconclusive') for a in resolved):
            raise ValueError('Engelli uç gerçek başarısız girişim gerektirir')
        if lead['state'] == 'excluded' and not any(a['result'] == 'excluded' for a in resolved):
            raise ValueError('Dışlanan uç gerekçeli inceleme gerektirir')
    for source in data['practice_scope_source']:
        scope = scopes.get(source['scope_id'])
        if not scope or not source['inspected_sections'] or not source_allowed(source['version_id'], scope['party_id']):
            raise ValueError('İncelenen kaynak veya parti kapsamı geçersiz')
        aware_time(source['inspected_at'])
        if not any(a['scope_id'] == scope['id'] and a['source_version_id'] == source['version_id'] and a['result'] == 'examined' and aware_time(a['attempted_at']) <= aware_time(source['inspected_at']) for a in attempts.values()):
            raise ValueError('İncelenen kaynak gerçek girişim gerektirir')
    events = {event['id']: event for event in data['practice_event']}
    relations = {r['id']: r for r in data['practice_relation']}
    candidates = {c['id']: dict(c) for c in data['practice_candidate']}
    candidate_revisions = sorted(data.get('practice_candidate_revision', []), key=lambda row: aware_time(row['recorded_at']))
    if len({(r['candidate_id'], aware_time(r['recorded_at'])) for r in candidate_revisions}) != len(candidate_revisions):
        raise ValueError('Aday revizyonları aynı zamanda çakışamaz')
    for revision in candidate_revisions:
        candidate = candidates.get(revision['candidate_id'])
        if not candidate or not revision['reason']:
            raise ValueError('Aday revizyonu geçersiz')
        candidate.update({k: revision[k] for k in ('event_id', 'relation_id', 'state', 'reason', 'passage_ids')})
    for candidate in candidates.values():
        scope = scopes.get(candidate['scope_id'])
        try:
            refs = json.loads(candidate['passage_ids'])
        except (ValueError, TypeError):
            raise ValueError('Aday pasajları geçersiz')
        if (not scope or not candidate['reason'] or candidate['state'] not in ('eligible', 'excluded', 'unverified', 'unmatched') or
                not isinstance(refs, list) or not refs or any(not isinstance(p, str) or p not in passages or not source_allowed(passages[p]['version_id'], scope['party_id'], p) for p in refs)):
            raise ValueError('Aday kaynak veya kapsamı geçersiz')
        if any(not any(s['scope_id'] == scope['id'] and s['version_id'] == passages[p]['version_id'] for s in data['practice_scope_source']) for p in refs):
            raise ValueError('Aday pasajı incelenen kapsam kaynağı gerektirir')
        if candidate['event_id'] and candidate['event_id'] not in events:
            raise ValueError('Aday olayı bulunamadı')
        if candidate['state'] == 'eligible' and (not candidate['event_id'] or not any(e['event_id'] == candidate['event_id'] and e['passage_id'] in refs for e in data['practice_event_evidence'])):
            raise ValueError('Uygun aday olayla bağlı kanıt gerektirir')
        if candidate['state'] == 'eligible' and not (any(r['event_id'] == candidate['event_id'] and (r['party_id'], r['topic_id']) == (scope['party_id'], scope['topic_id']) for r in data['practice_relation']) or
                any(u['event_id'] == candidate['event_id'] and (u['party_id'], u['topic_id']) == (scope['party_id'], scope['topic_id']) for u in data.get('practice_unmatched', []))):
            raise ValueError('Uygun olay için parti ve konu bağı gerekli')
        if candidate['state'] == 'unmatched':
            event = events.get(candidate['event_id'])
            linked = {e['passage_id'] for e in data['practice_event_evidence'] if e['event_id'] == candidate['event_id']}
            if (scope['research_kind'] != 'event' or candidate['relation_id'] or not event or not set(refs) <= linked or
                    validate_dates(event['event_at'], event['date_precision'], scope['period_start'], scope['cutoff_at'],
                                   event['date_unknown_reason']) == 'outside'):
                raise ValueError('Eşleşmemiş olay için aynı kapsamdaki bağlı olay kanıtı gerekli')
        if candidate['relation_id']:
            relation = relations.get(candidate['relation_id'])
            if not relation or (relation['party_id'], relation['topic_id'], relation['event_id']) != (scope['party_id'], scope['topic_id'], candidate['event_id']):
                raise ValueError('Aday ilişkisi kapsam dışında')
    old_candidates = {candidate['id']: candidate for candidate in data['match_candidate']}
    candidate_links = set()
    for link in data.get('practice_candidate_legacy', []):
        candidate, old = candidates.get(link['candidate_id']), old_candidates.get(link['legacy_id'])
        scope = scopes.get(candidate['scope_id']) if candidate else None
        if (not scope or not old or not link['reason'] or old['party_id'] != scope['party_id'] or
                old['topic_id'] not in ({scope['topic_id']} | bridged_topics.get(scope['id'], set())) or
                (old.get('passage_id') and old['passage_id'] not in json.loads(candidate['passage_ids']))):
            raise ValueError('Eski aday köprüsü kapsam dışında')
        candidate_links.add((scope['id'], old['id']))
    for closure in closures.values():
        scope = scopes.get(closure['scope_id'])
        try:
            residual = json.loads(closure['residual_lead_ids'])
        except (ValueError, TypeError):
            raise ValueError('Kapanış uçları geçersiz')
        closed_at = aware_time(closure['closed_at'])
        prior = [a for a in attempts.values() if scope and a['scope_id'] == scope['id'] and aware_time(a['attempted_at']) <= closed_at]
        if (not scope or not closure['reason'] or not isinstance(residual, list) or any(not isinstance(x, str) for x in residual) or
                any(x not in leads or leads[x]['scope_id'] != scope['id'] or leads[x]['state'] not in ('blocked', 'excluded') for x in residual) or
                not any(a['result'] in ('results', 'no_result') for a in prior)):
            raise ValueError('Kapanış için gerçek kapsamlı girişim gerekli')
        for attempt in prior:
            if attempt['result'] == 'results' and not any(lead['scope_id'] == scope['id'] and attempt['id'] in json.loads(lead['attempt_ids']) for lead in leads.values()):
                raise ValueError('Sonuç veren aramanın ilgili uçları gerekli')
            if attempt['result'] == 'examined' and not any(s['scope_id'] == scope['id'] and s['version_id'] == attempt['source_version_id'] for s in data['practice_scope_source']):
                raise ValueError('Kapanış incelenen kaynak bölümlerini gerektirir')
    for reopen in data['practice_reopen']:
        closure, lead = closures.get(reopen['closure_id']), leads.get(reopen['lead_id'])
        if not closure or not lead or lead['scope_id'] != closure['scope_id'] or not reopen['reason'] or aware_time(reopen['opened_at']) <= aware_time(closure['closed_at']):
            raise ValueError('Yeniden açılma kapsam veya dönemi geçersiz')
    for scope in scopes.values():
        history = sorted((c for c in closures.values() if c['scope_id'] == scope['id']), key=lambda c: aware_time(c['closed_at']))
        if not history:
            continue
        if len({aware_time(c['closed_at']) for c in history}) != len(history):
            raise ValueError('Kapsam kapanışları aynı zamanda çakışamaz')
        for previous, following in zip(history, history[1:]):
            if not any(r['closure_id'] == previous['id'] and aware_time(previous['closed_at']) < aware_time(r['opened_at']) < aware_time(following['closed_at']) for r in data['practice_reopen']):
                raise ValueError('Yeni kapanış önceki yeniden açılmayı gerektirir')
        latest = history[-1]
        reopened = any(r['closure_id'] == latest['id'] for r in data['practice_reopen'])
        if not reopened and any(l['scope_id'] == scope['id'] and l['state'] == 'pending' for l in leads.values()):
            raise ValueError('Bekleyen uçla kapanış yapılamaz')
        residual_ids = set(json.loads(latest['residual_lead_ids']))
        if not reopened and any(l['scope_id'] == scope['id'] and l['state'] == 'blocked' and l['id'] not in residual_ids for l in leads.values()):
            raise ValueError('Erişilemeyen uç kapanış sınırında korunmalı')
        allowed_topics = {scope['topic_id']} | bridged_topics.get(scope['id'], set())
        if not reopened and any(l['party_id'] == scope['party_id'] and l['topic_id'] in allowed_topics and not any(n['scope_id'] == scope['id'] and normalize_url(n['url']) == l['normalized_url'] for n in leads.values()) for l in legacy_leads.values()):
            raise ValueError('Kapsamdaki kayıtlı uçlar kapanıştan atlanamaz')
        candidate_ids = {c['id'] for c in candidates.values() if c['scope_id'] == scope['id']}
        if not reopened and any(c['party_id'] == scope['party_id'] and c['topic_id'] in allowed_topics and c['id'] not in candidate_ids and (scope['id'], c['id']) not in candidate_links for c in data['match_candidate']):
            raise ValueError('Kapsamdaki kayıtlı adaylar kapanıştan atlanamaz')
        if not reopened and any(s['scope_id'] == scope['id'] and aware_time(s['inspected_at']) > aware_time(latest['closed_at']) for s in data['practice_scope_source']):
            raise ValueError('Yeni kaynak kapsamı yeniden açmalı')
        if not reopened and any(a['scope_id'] == scope['id'] and aware_time(a['attempted_at']) > aware_time(latest['closed_at']) for a in attempts.values()):
            raise ValueError('Yeni girişim kapsamı yeniden açmalı')
        if not reopened and any(leads[r['lead_id']]['scope_id'] == scope['id'] and aware_time(r['recorded_at']) > aware_time(latest['closed_at']) for r in revisions):
            raise ValueError('Yeni uç bilgisi kapsamı yeniden açmalı')
        if not reopened and any(candidates[r['candidate_id']]['scope_id'] == scope['id'] and aware_time(r['recorded_at']) > aware_time(latest['closed_at']) for r in candidate_revisions):
            raise ValueError('Yeni aday bilgisi kapsamı yeniden açmalı')
    return True


def practice_coverage_states(data, inventory):
    """Compute current states without mutating immutable scope history."""
    from arsiv import aware_time
    scopes = {s['id'] for s in data.get('practice_scope_v2', [])}
    researched = {a['scope_id'] for a in data.get('practice_attempt_v2', [])}
    researched.update(b['scope_id'] for b in data.get('practice_legacy_scope', []))
    researched.update(l['scope_id'] for l in data.get('practice_lead', []))
    researched.update(c['scope_id'] for c in data.get('practice_candidate', []))
    latest = {}
    for closure in data.get('practice_closure', []):
        current = latest.get(closure['scope_id'])
        if current is None or aware_time(closure['closed_at']) > aware_time(current['closed_at']):
            latest[closure['scope_id']] = closure
    reopened = {r['closure_id'] for r in data.get('practice_reopen', [])}
    result = []
    for cell in inventory['cells']:
        sid = cell['cell_id']
        state = 'not_researched'
        if sid in scopes and sid in researched:
            state = 'open'
        if sid in latest and latest[sid]['id'] not in reopened:
            state = 'closed'
        result.append(dict(cell_id=sid, party_id=cell['party_id'], topic_id=cell['topic_id'], research_kind=cell['research_kind'], state=state))
    return result


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
    unmatched_parties = {}
    for _, row, scope in _unmatched_candidates(data, data):
        unmatched_parties.setdefault(row['event_id'], set()).add(scope['party_id'])
    for dispute in disputes.values():
        if dispute['event_id'] not in events or not all(dispute[k] for k in ('supported_points', 'disputed_points', 'unresolved_points')):
            raise ValueError('İhtilaf noktaları veya olayı eksik')
        parties = {r['party_id'] for r in data['practice_relation'] if r['event_id'] == dispute['event_id']}
        parties |= {u['party_id'] for u in data.get('practice_unmatched', []) if u['event_id'] == dispute['event_id']}
        parties.update(unmatched_parties.get(dispute['event_id'], ()))
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
        parties.update(unmatched_parties.get(dispute['event_id'], ()))
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
    coverage = set(data).intersection(PRACTICE_COVERAGE_TABLES)
    if coverage:
        if coverage != set(PRACTICE_COVERAGE_TABLES) or len(data['practice_coverage_contract']) != 1 or data['practice_coverage_contract'][0]['version'] != 2:
            raise ValueError('Uygulama kapsam sözleşmesi eksik')
        try:
            initial_inventory = json.loads(data['practice_coverage_contract'][0]['inventory_json'])
            extensions = [dict(x, basis_passage_ids=json.loads(x['basis_passage_ids'])) for x in data['practice_topic_extension']]
            revisions = sorted(data['practice_inventory_revision'], key=lambda row: row['epoch'])
            inventory = json.loads(revisions[-1]['inventory_json']) if revisions else initial_inventory
        except (ValueError, TypeError):
            raise ValueError('Uygulama kapsam envanteri geçersiz')
        canonical_base = dict(data, release_id=initial_inventory['base_release'])
        validate_practice_coverage(canonical_base, initial_inventory)
        previous_ids = set()
        for revision in revisions:
            if revision['epoch'] < 1 or not revision['reason']:
                raise ValueError('Envanter revizyonu geçersiz')
            revised = json.loads(revision['inventory_json'])
            ids = {t['topic_id'] for t in revised['topics']} - {t['topic_id'] for t in initial_inventory['topics']}
            if not previous_ids < ids or not ids <= {e['id'] for e in extensions}:
                raise ValueError('Envanter uzantıları yalnız eklenebilir')
            validate_practice_coverage(canonical_base, revised, [e for e in extensions if e['id'] in ids])
            previous_ids = ids
        if {e['id'] for e in extensions} != previous_ids:
            raise ValueError('Konu uzantısı envanter revizyonu gerektirir')
        validate_practice_closure(data, inventory, extensions)
        if c[0]['stage'] == 'complete' and any(item['state'] != 'closed' for item in practice_coverage_states(data, inventory)):
            raise ValueError('Tam uygulama için bütün kanonik kapsamlar kapanmalı')
    linked = {value for name in ('practice_statement', 'practice_relation', 'practice_contribution', 'practice_dispute', 'practice_position_change') for row in data.get(name, []) for key, value in row.items() if key.endswith('finding_id') and value}
    pairs = {findings[fid]['pair_id'] for fid in linked if fid in findings}
    for finding in findings.values():
        if finding['pair_id'] in pairs:
            check_finding(finding['id'], finding['party_id'])
    review_extension = set(data).intersection(PRACTICE_SOURCE_REVIEW_TABLES)
    revision_extension = set(data).intersection(PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
    if revision_extension and (revision_extension != set(PRACTICE_SOURCE_REVIEW_REVISION_TABLES) or not review_extension or data['practice_source_review_revision_contract'] != [{'version': 2}]):
        raise ValueError('Kaynak inceleme revizyon sözleşmesi eksik')
    if review_extension:
        if review_extension != set(PRACTICE_SOURCE_REVIEW_TABLES) or data['practice_source_review_contract'] != [{'version': 1}]:
            raise ValueError('Kaynak inceleme sözleşmesi eksik')
        validate_practice_source_review(data, data['practice_source_review'], require_coverage=c[0]['stage'] == 'complete', revisions=data['practice_source_review_revision'] if revision_extension else None)
    elif c[0]['stage'] == 'complete':
        raise ValueError('Tam uygulama kaynak incelemesi gerektirir')
    validate_practice_merge(data)
    return True


def practice_manifest_fields(data):
    c = data['practice_contract'][0]
    result = dict(practice_validation_version=c['version'], practice_stage=c['stage'], practice_inventory_sha256=c['inventory_digest'], practice_selection_sha256=_digest({k: data[k] for k in PRACTICE_TABLES}))
    if 'practice_variant_contract' in data:
        result['practice_variant_sha256'] = _digest({k: data[k] for k in PRACTICE_VARIANT_TABLES})
    if 'practice_evidence_contract' in data:
        result['practice_evidence_sha256'] = _digest({k: data[k] for k in PRACTICE_EVIDENCE_TABLES})
    if 'practice_coverage_contract' in data:
        result['practice_coverage_sha256'] = _digest({k: data[k] for k in PRACTICE_COVERAGE_TABLES})
    if 'practice_source_review_contract' in data:
        result['practice_source_review_sha256'] = _digest({k: data[k] for k in PRACTICE_SOURCE_REVIEW_TABLES})
    if 'practice_source_review_revision_contract' in data:
        result['practice_source_review_revision_sha256'] = _digest({k: data[k] for k in PRACTICE_SOURCE_REVIEW_REVISION_TABLES})
    if 'practice_merge_contract' in data:
        result['practice_merge_provenance_sha256'] = _digest({k: data[k] for k in PRACTICE_MERGE_TABLES})
    return result


def validate_practice_descent(base, candidate):
    if 'practice_merge_contract' in base:
        for name in PRACTICE_MERGE_TABLES:
            if name not in candidate or any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki birleşme kökeni değiştirilemez')
    previous = {row['id'] for row in base.get('practice_merge_provenance', [])}
    for row in candidate.get('practice_merge_provenance', []):
        if row['id'] not in previous:
            claimed = json.loads(row['base_records_json'])
            schemas = (PRACTICE_TABLES | PRACTICE_VARIANT_TABLES | PRACTICE_EVIDENCE_TABLES |
                       PRACTICE_COVERAGE_TABLES | PRACTICE_SOURCE_REVIEW_TABLES | PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
            if set(claimed) != set(base).intersection(schemas) or any(records != base[table] for table, records in claimed.items()):
                raise ValueError('Birleşme kabul edilmiş tabanla uyuşmuyor')
    if 'practice_source_review_revision_contract' in base:
        for name in PRACTICE_SOURCE_REVIEW_REVISION_TABLES:
            if name not in candidate or any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki kaynak inceleme revizyonu değiştirilemez')
    if 'practice_source_review_contract' in base:
        for name in PRACTICE_SOURCE_REVIEW_TABLES:
            if name not in candidate or any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki kaynak incelemesi değiştirilemez')
    if 'practice_coverage_contract' in base:
        for name in PRACTICE_COVERAGE_TABLES:
            if name not in candidate or any(row not in candidate[name] for row in base[name]):
                raise ValueError('Önceki uygulama kapsam kaydı değiştirilemez')
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


def _load_practice_copy(work, payload, base, *, storage_root=None, allow_inherited_review_pending=False):
    from arsiv import (DATA, aware_time, check_attempt, check_missing, connect, pdf_page_text, safe_path,
                       safe_url, validate_phase_one_workspace, validate_view)
    if payload.get('base_release') != base or payload.get('contract_version') != 1 or payload.get('stage') not in ('tracer', 'partial', 'complete') or payload.get('taxonomy_version') != 4:
        raise ValueError('Uygulama paketi veya tabanı geçersiz')
    if len(payload.get('practice_records', {}).get('practice_contract', [])) != 1 or payload['practice_records']['practice_contract'][0].get('stage') != payload['stage']:
        raise ValueError('Paket ve uygulama aşaması uyuşmuyor')
    if payload['stage'] == 'complete' and 'practice_coverage_contract' not in payload['practice_records']:
        raise ValueError('Tam uygulama kanonik kapsam sözleşmesi gerektirir')
    if not isinstance(payload.get('scope_inventory'), list) or payload['practice_records']['practice_contract'][0].get('inventory_digest') != _digest(payload['scope_inventory']):
        raise ValueError('Envanter kapsamı özeti uyuşmuyor')
    if allow_inherited_review_pending:
        from arsiv import export_db
        records = payload['practice_records']
        if (payload['stage'] != 'partial' or not set(PRACTICE_MERGE_TABLES) <= set(records) or
                not set(PRACTICE_SOURCE_REVIEW_REVISION_TABLES) <= set(records)):
            raise ValueError('Bekleyen kaynak incelemesi yalnız kısmi birleşmede kullanılabilir')
        accepted = export_db(Path(work) / 'records.sqlite3', base, storage_root=storage_root)
        if not accepted.get('practice_source_review_contract') or not accepted.get('practice_source_review'):
            raise ValueError('Kabul edilmiş önceki kaynak incelemesi gerekli')
    db = connect(work / 'records.sqlite3')
    try:
        migrate_practice_workspace(db, work / 'pre-practice-migration.sqlite3')
        db.execute('BEGIN IMMEDIATE')
        new_review_passages = set()
        new_review_subjects = set()
        input_findings = {entry['values']['id'] for entry in payload['entries'] if entry.get('kind') == 'finding' and isinstance(entry.get('values'), dict) and entry['values'].get('id')}
        actor_person_ids = {entry['values'].get('person_id') for entry in payload['entries']
                            if entry.get('kind') == 'actor' and isinstance(entry.get('values'), dict)}
        added_passages = set()
        for entry in payload['entries']:
            kind, values = entry['kind'], entry['values']
            if kind not in ENTRY_KINDS or not values:
                raise ValueError('Uygulama girdi türü geçersiz')
            if payload.get('party_id') is not None and values.get('party_id') is not None and values['party_id'] != payload['party_id']:
                raise ValueError('Parti paketi başka partinin kaydını ekleyemez')
            if kind in ('document_version', 'archive_view', 'passage', 'source_attribution') and payload.get('party_id') is not None:
                if kind == 'document_version':
                    owner = db.execute('SELECT party_id FROM document WHERE id=?', (values.get('document_id'),)).fetchone()
                else:
                    owner = db.execute('SELECT d.party_id FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id=?', (values.get('version_id'),)).fetchone()
                if not owner or owner['party_id'] != payload['party_id']:
                    raise ValueError('Kaynak kaydı parti sahibine ait değil')
            if kind == 'document_version':
                safe_url(values['original_url']); safe_url(values['final_url'])
                if values.get('document_date') is None and (values.get('date_precision') != 'unknown' or not values.get('date_unknown_reason')):
                    raise ValueError('Bilinmeyen belge tarihi için gerekçe gerekli')
            if kind == 'archive_view':
                validate_view(DATA if storage_root is None else storage_root, values)
                version = db.execute('SELECT sha256 FROM document_version WHERE id=?', (values.get('version_id'),)).fetchone()
                if not version or version['sha256'] != values['source_sha256']:
                    raise ValueError('Arşiv görünümü özgün belgeyle uyuşmuyor')
            if kind == 'attempt':
                if (values.get('type'), values.get('result'), values.get('lead_id')) != ('search', 'no_result', None):
                    raise ValueError('Paket girişimi yalnız uçsuz sonuçsuz arama olabilir')
                check_attempt(db, values)
            if kind == 'missing':
                check_missing(db, values)
            if kind == 'review' and (values.get('kind'), values.get('reviewer_kind'), values.get('result')) != ('finding', 'agent', 'reviewed'):
                raise ValueError('Yalnız ajan bulgu incelemesi eklenebilir')
            if kind == 'review':
                if values.get('subject_id') not in input_findings or not values.get('reason'):
                    raise ValueError('İnceleme yeni bir bulguya ve gerekçeye bağlı olmalı')
                aware_time(values.get('reviewed_at'))
            if kind == 'person' and (values.get('id') not in actor_person_ids or
                                     not isinstance(values.get('name'), str) or not values['name'].strip()):
                raise ValueError('Kişi kaydı paket aktörüne ve ada bağlı olmalı')
            if kind == 'actor':
                role, person, authority = (values.get(key) for key in ('kind', 'person_id', 'authorization_passage_id'))
                if (role not in ('institution', 'authorized_representative', 'individual_mp') or
                        (role == 'institution' and (person or authority)) or
                        (role != 'institution' and not person) or
                        (role == 'authorized_representative' and not authority)):
                    raise ValueError('Aktör türü, kişi veya yetki kaydı geçersiz')
            if kind == 'manual_passage':
                passage_id = values.get('passage_id')
                if passage_id not in added_passages:
                    raise ValueError('Elle doğrulama yeni paket pasajına bağlı olmalı')
                if any(not isinstance(values.get(key), str) or not values[key].strip() for key in ('method', 'reason')):
                    raise ValueError('Elle doğrulama yöntemi veya gerekçesi eksik')
                aware_time(values.get('checked_at'))
                passage = db.execute(
                    'SELECT p.pdf_page_index, p.exact, v.mime, v.original_path FROM passage p '
                    'JOIN document_version v ON v.id=p.version_id WHERE p.id=?', (passage_id,)).fetchone()
                page = passage['pdf_page_index']
                if passage['mime'] != 'application/pdf' or page is None or page < 0:
                    raise ValueError('Elle doğrulama için PDF sayfası gerekli')
                original = safe_path(DATA if storage_root is None else storage_root, passage['original_path'])
                try:
                    text = pdf_page_text(original, page)
                except ValueError as exc:
                    if str(exc) != 'PDF sayfasında metin bulunamadı':
                        raise
                    text = ''
                if text.strip() and passage['exact'] not in text:
                    raise ValueError('Elle doğrulanan pasaj PDF metniyle uyuşmuyor')
            cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
            if not set(values) <= cols:
                raise ValueError('Bilinmeyen alan')
            pk = [x['name'] for x in sorted(db.execute(f'PRAGMA table_info({kind})'), key=lambda x: x['pk']) if x['pk']]
            if pk and all(key in values for key in pk):
                existing = db.execute(f"SELECT * FROM {kind} WHERE " + ' AND '.join(key + '=?' for key in pk), [values[key] for key in pk]).fetchone()
                if existing:
                    if not practice_entry_matches(kind, dict(existing), values):
                        raise ValueError('Önceki kayıt değiştirilemez')
                    continue
            db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
            if kind == 'passage':
                added_passages.add(values['id'])
            if kind == 'finding_evidence':
                new_review_passages.add(values['passage_id'])
            if kind == 'document_version':
                db.execute('INSERT OR IGNORE INTO url_alias VALUES (?,?,?)', (values['original_url'], values['final_url'], values['id']))
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
        coverage = set(records).intersection(PRACTICE_COVERAGE_TABLES)
        if not coverage and db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='practice_coverage_contract'").fetchone():
            raise ValueError('Önceki uygulama kapsam sözleşmesi kaldırılamaz')
        if coverage:
            if coverage != set(PRACTICE_COVERAGE_TABLES):
                raise ValueError('Uygulama kapsam tabloları eksik')
            existing_marker = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='practice_coverage_contract'").fetchone()
            marker_rows = records['practice_coverage_contract']
            if (len(marker_rows) != 1 or (not existing_marker and json.loads(marker_rows[0]['inventory_json']).get('base_release') != base)):
                raise ValueError('Kapsam envanteri taban sürümle uyuşmuyor')
            tables.update(PRACTICE_COVERAGE_TABLES)
            for name, definition in PRACTICE_COVERAGE_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        reviews = set(records).intersection(PRACTICE_SOURCE_REVIEW_TABLES)
        prior_reviews = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='practice_source_review_contract'").fetchone()
        if prior_reviews and not reviews:
            raise ValueError('Kaynak inceleme sözleşmesi kaldırılamaz')
        if reviews:
            if reviews != set(PRACTICE_SOURCE_REVIEW_TABLES):
                raise ValueError('Kaynak inceleme tabloları eksik')
            tables.update(PRACTICE_SOURCE_REVIEW_TABLES)
            for name, definition in PRACTICE_SOURCE_REVIEW_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        review_revisions = set(records).intersection(PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
        prior_revisions = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='practice_source_review_revision_contract'").fetchone()
        if prior_revisions and not review_revisions:
            raise ValueError('Kaynak inceleme revizyon sözleşmesi kaldırılamaz')
        if review_revisions:
            if review_revisions != set(PRACTICE_SOURCE_REVIEW_REVISION_TABLES) or not reviews:
                raise ValueError('Kaynak inceleme revizyon tabloları eksik')
            tables.update(PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
            for name, definition in PRACTICE_SOURCE_REVIEW_REVISION_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        merge = set(records).intersection(PRACTICE_MERGE_TABLES)
        prior_merge = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='practice_merge_contract'").fetchone()
        if prior_merge and not merge:
            raise ValueError('Birleşme sözleşmesi kaldırılamaz')
        if merge:
            if merge != set(PRACTICE_MERGE_TABLES):
                raise ValueError('Birleşme tabloları eksik')
            tables.update(PRACTICE_MERGE_TABLES)
            for name, definition in PRACTICE_MERGE_TABLES.items():
                db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        if set(records) != set(tables):
            raise ValueError('Uygulama tabloları eksik')
        for kind in tables:
            for values in records[kind]:
                cols = {x['name'] for x in db.execute(f'PRAGMA table_info({kind})')}
                if set(values) != cols:
                    raise ValueError('Uygulama alanları uyuşmuyor')
                if kind == 'practice_contract':
                    existing = db.execute('SELECT * FROM practice_contract').fetchone()
                    if existing:
                        old = dict(existing)
                        levels = {'tracer': 0, 'partial': 1, 'complete': 2}
                        if (any(old[k] != values[k] for k in ('version', 'taxonomy_version', 'method_version', 'inventory_digest')) or
                                values['stage'] not in levels or levels[values['stage']] < levels[old['stage']]):
                            raise ValueError('Uygulama sözleşmesi geriletilemez veya değiştirilemez')
                        if old['stage'] != values['stage']:
                            db.execute('UPDATE practice_contract SET stage=? WHERE version=?', (values['stage'], values['version']))
                        continue
                where = ' AND '.join(f'{key} IS ?' for key in values)
                if not db.execute(f'SELECT 1 FROM {kind} WHERE {where}', list(values.values())).fetchone():
                    if kind == 'practice_source_party' and payload.get('party_id') is not None and values.get('party_id') != payload['party_id']:
                        raise ValueError('Parti paketi başka partiye kaynak yetkisi veremez')
                    party = payload.get('party_id') if kind in PRACTICE_COVERAGE_TABLES else None
                    scope_id = values.get('scope_id') if kind in PRACTICE_COVERAGE_TABLES else None
                    if kind == 'practice_scope_v2':
                        scope_party = values['party_id']
                    else:
                        if kind == 'practice_reopen':
                            parent = db.execute('SELECT scope_id FROM practice_closure WHERE id=?', (values['closure_id'],)).fetchone()
                            scope_id = parent['scope_id'] if parent else None
                        elif kind == 'practice_lead_revision':
                            parent = db.execute('SELECT scope_id FROM practice_lead WHERE id=?', (values['lead_id'],)).fetchone()
                            scope_id = parent['scope_id'] if parent else None
                        elif kind in ('practice_candidate_revision', 'practice_candidate_legacy'):
                            parent = db.execute('SELECT scope_id FROM practice_candidate WHERE id=?', (values['candidate_id'],)).fetchone()
                            scope_id = parent['scope_id'] if parent else None
                        parent = db.execute('SELECT party_id FROM practice_scope_v2 WHERE id=?', (scope_id,)).fetchone() if scope_id else None
                        scope_party = parent['party_id'] if parent else None
                    if party is not None and scope_party is not None and party != scope_party:
                        raise ValueError('Parti paketi başka partinin kapsamını değiştiremez')
                    db.execute(f"INSERT INTO {kind} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})", list(values.values()))
                    if kind == 'practice_event_evidence':
                        new_review_passages.add(values['passage_id'])
                    if kind in ('practice_source_review', 'practice_source_review_revision'):
                        new_review_subjects.add((values['subject_kind'], values['subject_id']))
        # Validate a transaction-consistent snapshot before the commit.
        context_tables = ('comparison_contract', 'comparison_row', 'comparison_completion_revision',
                          'identity_observation', 'method', 'party', 'scope_party', 'action',
                          'match', 'match_candidate', 'lead', 'closure', 'reopen')
        data = {name: [dict(row) for row in db.execute(f'SELECT * FROM {name}')]
                for name in (*tables, *PRACTICE_ENTRY_ORDER, *context_tables)}
        data['release_id'] = base
        validate_practices(data)
        if allow_inherited_review_pending:
            validate_practice_descent(accepted, data)
        if reviews:
            refs = payload.get('source_review_refs')
            submitted_reviews = records['practice_source_review'] + (records['practice_source_review_revision'] if review_revisions else [])
            expected = [dict(subject_kind=kind, subject_id=identity) for kind, identity in sorted({(row['subject_kind'], row['subject_id']) for row in submitted_reviews})]
            if not isinstance(refs, list) or sorted(refs, key=lambda x: (x['subject_kind'], x['subject_id'])) != sorted(expected, key=lambda x: (x['subject_kind'], x['subject_id'])):
                raise ValueError('Kaynak inceleme başvuruları uyuşmuyor')
            party = payload.get('party_id')
            target_keys = set(practice_review_package_targets(data, records, new_review_passages, party))
            if not new_review_subjects <= target_keys:
                raise ValueError('Yeni kaynak incelemesi paket kapsamı dışında')
            initial = [row for row in data['practice_source_review'] if (row['subject_kind'], row['subject_id']) in target_keys]
            if review_revisions:
                later = [row for row in data['practice_source_review_revision'] if (row['subject_kind'], row['subject_id']) in target_keys]
                if allow_inherited_review_pending:
                    practice_source_review_pending(data, initial, later, party_id=party, target_keys=target_keys)
                    fresh_initial = [row for row in initial if (row['subject_kind'], row['subject_id']) in new_review_subjects]
                    fresh_later = [row for row in later if (row['subject_kind'], row['subject_id']) in new_review_subjects]
                    validate_practice_source_review(data, fresh_initial, party_id=party, revisions=fresh_later, target_keys=new_review_subjects)
                else:
                    validate_practice_source_review(data, initial, party_id=party, revisions=later, target_keys=target_keys)
            else:
                validate_practice_source_review(data, initial, party_id=party, target_keys=target_keys)
        if db.execute('PRAGMA foreign_key_check').fetchall() or db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Uygulama bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    validate_phase_one_workspace(work, storage_root=storage_root)


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
        if not submitted or not all(any(practice_entry_matches(item['kind'], existing, item['values'])
                                       for existing in current_data.get(item['kind'], [])) for item in submitted):
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


def _validate_new_source_path(values, key):
    import re
    path = values[key]
    digest = values.get('sha256')
    names = ('readable.html',) if key == 'readable_path' else ('original.pdf', 'original.html.bin')
    if not isinstance(path, str) or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest) or path not in {'objects/' + digest + '/' + name for name in names}:
        raise ValueError('Kaynak nesne yolu veya özeti geçersiz')


def merge_practice_packages(inventory, inputs, decisions_raw, *, source_roots=None):
    """Validate each party package before combining its immutable raw bytes."""
    import re
    import tempfile
    import arsiv
    from uygulama_birlestirme import merge_packages, _parse

    if not isinstance(inputs, list) or not inputs:
        raise ValueError('Birleşme girdisi gerekli')
    packages = [_parse(item['raw']) for item in inputs]
    base = packages[0].get('base_release')
    if not isinstance(base, str) or not re.fullmatch(r'[0-9a-f]{32}', base):
        raise ValueError('Geçersiz taban sürüm')
    folder = arsiv.safe_path(arsiv.DATA / 'releases', base)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest.get('release_id') != base or set(manifest.get('files', {})) != {'records.sqlite3', 'records.json', 'index.html'} or
            any(arsiv.sha(arsiv.safe_path(folder, name)) != digest for name, digest in manifest['files'].items())):
        raise ValueError('Taban sürüm manifesti uyuşmuyor')
    data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
    if arsiv.export_db(folder / 'records.sqlite3', base) != data:
        raise ValueError('Taban sürüm DB ve JSON uyuşmuyor')
    arsiv.audit_release(base)
    schemas = (PRACTICE_TABLES | PRACTICE_VARIANT_TABLES | PRACTICE_EVIDENCE_TABLES |
               PRACTICE_COVERAGE_TABLES | PRACTICE_SOURCE_REVIEW_TABLES | PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
    base_records = {name: data[name] for name in schemas if name in data}
    roots = source_roots or {}
    with tempfile.TemporaryDirectory(prefix='gsd-merge-inputs-') as tmp:
        for index, (item, package) in enumerate(zip(inputs, packages)):
            party = package.get('party_id')
            if not isinstance(party, str) or not re.fullmatch(r'[a-z0-9-]+', party):
                raise ValueError('Her birleşme girdisi için parti sahibi gerekli')
            if package.get('base_release') != base:
                raise ValueError('Birleşme tabanları uyuşmuyor')
            root = roots.get(item['identity'], arsiv.safe_path(arsiv.DATA / 'practices' / 'sources', party))
            render_practice_preview(package, Path(tmp) / str(index), inventory, base, source_root=root)
    outcome = merge_packages(inventory, inputs, decisions_raw,
        decisions_sha256=hashlib.sha256(decisions_raw).hexdigest(), base_records=base_records)
    payload = outcome['payload']
    payload['practice_records'].update(materialize_practice_merge(inventory, inputs, decisions_raw, base_records, outcome))
    if base_records.get('practice_source_review_contract'):
        payload = prepare_practice_merge_pending_reviews(payload, base_records)
    # The union can violate constraints even when each input is valid.
    # Validate the materialized union before returning it to the CLI writer.
    roots_by_entry = {}
    for item, package in zip(inputs, packages):
        root = roots.get(item['identity'], arsiv.safe_path(arsiv.DATA / 'practices' / 'sources', package['party_id']))
        for entry in package['entries']:
            roots_by_entry.setdefault(_digest(entry), root)
    with tempfile.TemporaryDirectory(prefix='gsd-merge-union-') as tmp:
        _render_practice_preview(payload, Path(tmp) / 'preview', inventory, base,
            allow_inherited_review_pending=bool(base_records.get('practice_source_review_contract')),
            _validated_merge_roots=roots_by_entry)
    return payload


def render_practice_preview(payload, out, inventory=None, base_release='current', *, storage_root=None, source_root=None, allow_inherited_review_pending=False, merge_source_roots=None):
    return _render_practice_preview(payload, out, inventory, base_release, storage_root=storage_root,
        source_root=source_root, allow_inherited_review_pending=allow_inherited_review_pending,
        merge_source_roots=merge_source_roots)


def _render_practice_preview(payload, out, inventory=None, base_release='current', *, storage_root=None, source_root=None, allow_inherited_review_pending=False, merge_source_roots=None, _validated_merge_roots=None):
    """Build a private, validated snapshot without touching the writer lock."""
    import os
    import re
    import shutil
    import tempfile
    import arsiv

    out = Path(out).resolve()
    if out == arsiv.ROOT or arsiv.ROOT in out.parents or out.exists():
        raise ValueError('Önizleme hedefi mevcut veya proje kökü içinde')
    if not out.parent.is_dir():
        raise ValueError('Önizleme hedefinin üst dizini bulunamadı')
    arsiv.require_local_sqlite_root(out.parent)
    storage_root = arsiv.DATA if storage_root is None else Path(storage_root)
    base = arsiv.current() if base_release == 'current' else base_release
    if not isinstance(base, str) or not re.fullmatch(r'[0-9a-f]{32}', base):
        raise ValueError('Geçersiz taban sürüm')
    folder = arsiv.safe_path(arsiv.DATA / 'releases', base)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if (manifest.get('release_id') != base or set(manifest.get('files', {})) != {'records.sqlite3', 'records.json', 'index.html'} or
            any(arsiv.sha(arsiv.safe_path(folder, name)) != digest for name, digest in manifest['files'].items())):
        raise ValueError('Taban sürüm manifesti uyuşmuyor')
    base_data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
    if arsiv.export_db(folder / 'records.sqlite3', base, storage_root=storage_root) != base_data:
        raise ValueError('Taban sürüm DB ve JSON uyuşmuyor')
    merge_roots_by_entry = {} if _validated_merge_roots is None else _validated_merge_roots
    if _validated_merge_roots is None and set(PRACTICE_MERGE_TABLES) <= set(payload.get('practice_records', {})):
        records = payload['practice_records']
        provenance = records['practice_merge_provenance']
        if len(provenance) != 1:
            raise ValueError('Tek birleşme kökeni gerekli')
        prov = provenance[0]
        raw_inputs = [dict(identity=row['input_identity'], raw=bytes.fromhex(row['raw_hex'])) for row in records['practice_merge_input'] if row['provenance_id'] == prov['id']]
        saved_inventory = json.loads(prov['inventory_json'])
        if inventory is not None and inventory != saved_inventory:
            raise ValueError('Birleşme envanteri uyuşmuyor')
        regenerated = merge_practice_packages(saved_inventory, raw_inputs, bytes.fromhex(prov['decisions_hex']), source_roots=merge_source_roots)
        if regenerated != payload:
            raise ValueError('Birleşme paketi doğrulanmış özgün girdilerle uyuşmuyor')
        for item in raw_inputs:
            original = json.loads(item['raw'])
            party = original['party_id']
            root = (merge_source_roots or {}).get(item['identity'], arsiv.safe_path(arsiv.DATA / 'practices' / 'sources', party))
            for entry in original['entries']:
                merge_roots_by_entry.setdefault(_digest(entry), root)
        allow_inherited_review_pending = bool(base_data.get('practice_source_review_contract'))
    adapted_from = None
    if payload.get('base_release') != base:
        # The original pilot is a historical input, not a mutable template.
        # Only the exact historical package can use its reviewed coverage
        # successor, after checking that every original row exists in base.
        original = json.loads((arsiv.DATA / 'practices' / '04-tracer.json').read_text(encoding='utf-8'))
        successor = json.loads((arsiv.DATA / 'practices' / '04-coverage-tracer.json').read_text(encoding='utf-8'))
        ancestor = payload.get('base_release')
        cursor, seen = base, set()
        while cursor != ancestor:
            if not isinstance(cursor, str) or not re.fullmatch(r'[0-9a-f]{32}', cursor) or cursor in seen:
                raise ValueError('Tarihsel sürüm taban zincirinde bulunamadı')
            seen.add(cursor)
            history = arsiv.safe_path(arsiv.DATA / 'releases', cursor)
            historical_manifest = json.loads((history / 'manifest.json').read_text(encoding='utf-8'))
            if (historical_manifest.get('release_id') != cursor or
                    set(historical_manifest.get('files', {})) != {'records.sqlite3', 'records.json', 'index.html'}):
                raise ValueError('Tarihsel sürüm manifesti uyuşmuyor')
            cursor = historical_manifest.get('base_release')
        submitted = list(payload.get('entries', [])) + [dict(kind=k, values=row) for k, rows in payload.get('practice_records', {}).items() for row in rows]
        if (payload != original or successor.get('base_release') != base or not submitted or
                not all(any(practice_entry_matches(item['kind'], row, item['values'])
                            for row in base_data.get(item['kind'], [])) for item in submitted)):
            raise ValueError('Taban sürüm veya tarihsel paket ardıllığı uyuşmuyor')
        adapted_from = _digest(payload)
        payload = successor
    records = payload.get('practice_records', {})
    markers = records.get('practice_coverage_contract', [])
    if inventory is not None:
        revisions = records.get('practice_inventory_revision', [])
        if len(markers) != 1:
            raise ValueError('Kapsam envanteri işaretçisi eksik')
        active = max(revisions, key=lambda x: x['epoch'])['inventory_json'] if revisions else markers[0]['inventory_json']
        if json.loads(active) != inventory:
            raise ValueError('Paket ve kanonik envanter uyuşmuyor')
    with tempfile.TemporaryDirectory(prefix='.practice-preview-', dir=out.parent) as tmp:
        preview_root = Path(tmp)
        release = arsiv.uuid.uuid4().hex
        work = preview_root / 'releases' / release
        work.mkdir(parents=True)
        shutil.copyfile(folder / 'records.sqlite3', work / 'records.sqlite3')
        def copy_asset(root, relative, *, reject_links=False):
            if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
                raise ValueError('Geçersiz kaynak yolu')
            if reject_links:
                current = Path(root)
                for part in Path(relative).parts:
                    current = current / part
                    if current.is_symlink():
                        raise ValueError('Kaynak sembolik bağlantı içeremez')
            source = arsiv.safe_path(root, relative)
            target = arsiv.safe_path(preview_root, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.read_bytes() != source.read_bytes():
                raise ValueError('Kaynak varlığı değiştirilemez')
            if not target.exists(): shutil.copyfile(source, target)

        def copy_view(root, view, *, reject_links=False):
            arsiv.validate_view(root, view)
            path = view['manifest_path']
            copy_asset(root, path, reject_links=reject_links)
            view_manifest = json.loads(arsiv.safe_path(root, path).read_text(encoding='utf-8'))
            for name in view_manifest['files']:
                copy_asset(root, str(Path(path).parent / name), reject_links=reject_links)
            return view_manifest

        for version in base_data['document_version']:
            for key in ('original_path', 'readable_path'): copy_asset(storage_root, version[key])
        for view in base_data.get('archive_view', []): copy_view(storage_root, view)
        source_root = storage_root if source_root is None else Path(source_root).resolve()
        party = payload.get('party_id')
        entries = payload.get('entries', [])
        for entry in entries:
            kind, values = entry['kind'], entry['values']
            entry_root = merge_roots_by_entry.get(_digest(entry), source_root)
            if kind in ('document_version', 'archive_view') and any(
                    all(row.get(key) == value for key, value in values.items())
                    for row in base_data.get(kind, [])):
                continue
            if kind == 'document_version':
                if not merge_roots_by_entry and (not isinstance(party, str) or not re.fullmatch(r'[a-z0-9-]+', party)):
                    raise ValueError('Yeni kaynak için parti sahibi gerekli')
                for key in ('original_path', 'readable_path'):
                    _validate_new_source_path(values, key)
                    copy_asset(entry_root, values[key], reject_links=True)
                original = arsiv.safe_path(preview_root, values['original_path'])
                if original.stat().st_size > arsiv.MAX_SOURCE:
                    raise ValueError('Kaynak boyut sınırını aşıyor')
                raw = original.read_bytes()
                if not raw or len(raw) > arsiv.MAX_SOURCE or arsiv.sha(original) != values['sha256']:
                    raise ValueError('Kaynak baytları veya özeti geçersiz')
                if original.name == 'original.pdf':
                    if not raw.startswith(b'%PDF-'): raise ValueError('PDF kaynak biçimi geçersiz')
                else:
                    from arsiv_gorunum import decode_html
                    try:
                        decode_html(raw)
                    except ValueError:
                        view_entry = next((item for item in entries if item['kind'] == 'archive_view'
                                           and item['values'].get('version_id') == values['id']
                                           and item['values'].get('source_sha256') == values['sha256']), None)
                        if view_entry is None:
                            raise
                        view_root = merge_roots_by_entry.get(_digest(view_entry), source_root)
                        view_manifest = copy_view(view_root, view_entry['values'], reject_links=True)
                        charset = view_manifest.get('http_charset')
                        if view_manifest.get('source_url') != values['final_url'] or not isinstance(charset, str) or not charset:
                            raise
                        decode_html(raw, charset)
            elif kind == 'archive_view':
                copy_view(entry_root, values, reject_links=True)
        if merge_roots_by_entry:
            import copy
            payload = copy.deepcopy(payload)
            order = {kind: index for index, kind in enumerate(PRACTICE_ENTRY_ORDER)}
            payload['entries'].sort(key=lambda item: order[item['kind']])
        _load_practice_copy(work, payload, base, storage_root=preview_root, allow_inherited_review_pending=allow_inherited_review_pending)
        data = arsiv.export_db(work / 'records.sqlite3', release, strict_identity=True, storage_root=preview_root)
        if inventory is not None:
            extensions = [dict(row, basis_passage_ids=json.loads(row['basis_passage_ids']))
                          for row in data.get('practice_topic_extension', [])]
            # A later accepted base retains its already bound inventory history.
            validate_preview_inventory(data, base_data, base, inventory, extensions)
        arsiv.validate_policy_descent(base_data, data)
        arsiv.validate_comparison_descent(base_data, data)
        validate_practice_descent(base_data, data)
        (work / 'records.json').write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        # Use the ordinary release layout and preserve exact renderer bytes.
        asset_root = preview_root
        paths = {v[k] for v in data['document_version'] for k in ('original_path', 'readable_path')}
        for view in data.get('archive_view', []):
            arsiv.validate_view(preview_root, view)
            view_manifest = json.loads(arsiv.safe_path(preview_root, view['manifest_path']).read_text(encoding='utf-8'))
            parent = Path(view['manifest_path']).parent
            paths.add(view['manifest_path'])
            paths.update(str(parent / name) for name in view_manifest['files'])
        asset_hashes = {}
        for relative in sorted(paths):
            target = arsiv.safe_path(asset_root, relative)
            asset_hashes[relative] = arsiv.sha(target)
        report = arsiv.render_comparison_snapshot(data, arsiv.render_report)
        (work / 'index.html').write_text(report, encoding='utf-8')
        arsiv.validate_phase_one_html(data, report)
        arsiv.validate_phase_three_workspace(work, data['comparison_contract'][0]['stage'])
        if data != json.loads((work / 'records.json').read_text(encoding='utf-8')):
            raise ValueError('Önizleme DB ve JSON uyuşmuyor')
        preview_manifest = arsiv.build_release_manifest(
            work, data, release, arsiv.RENDERER_VERSION, base,
            manifest.get('phase2_delivery'), refresh=bool(manifest.get('phase2_delivery')))
        preview_manifest.update(preview=True, asset_files=asset_hashes)
        if adapted_from:
            preview_manifest['legacy_input_canonical_sha256'] = adapted_from
        (work / 'manifest.json').write_text(json.dumps(preview_manifest, sort_keys=True) + '\n', encoding='utf-8')
        arsiv.audit_release(release, storage_root=preview_root)
        (work / 'pre-practice-migration.sqlite3').unlink(missing_ok=True)
        os.rename(preview_root, out)
    return out
