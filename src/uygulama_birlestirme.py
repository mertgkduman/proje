"""Internal deterministic merger. Inputs must already pass source/schema validation.

This is not an ingestion, SQL, audit, review, or source-ownership validator.
It does not write files and its output is not yet a loadable public package:
review origins must be integrated without claiming current review coverage.
"""
import copy
import hashlib
import json
import sqlite3
from datetime import datetime


class MergeError(ValueError):
    pass


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise MergeError('Duplicate JSON key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique)
    except (ValueError, TypeError, UnicodeDecodeError) as exc:
        raise MergeError('Invalid JSON envelope') from exc


def _string(value):
    return isinstance(value, str) and bool(value.strip())


EVENT_FK_TABLES = frozenset(('practice_event_evidence', 'practice_contribution', 'practice_relation',
    'practice_legacy_link', 'practice_unmatched', 'practice_evidence_assessment', 'practice_dispute',
    'practice_candidate', 'practice_candidate_revision'))
REVIEW_TABLES = frozenset(('practice_source_review', 'practice_source_review_revision'))


def merge_packages(inventory, inputs, decisions_raw, *, decisions_sha256, base_records):
    """Merge validated envelopes; inputs are {identity, raw: bytes}, identity is opaque.

    decisions_sha256 is the expected SHA-256 of exact decision-file bytes.
    base_records is the accepted snapshot's practice table mapping. Neither input
    records nor accepted base rows are modified. Raises MergeError before output.
    """
    from uygulamalar import (PRACTICE_TABLES, PRACTICE_VARIANT_TABLES, PRACTICE_EVIDENCE_TABLES,
        PRACTICE_COVERAGE_TABLES, PRACTICE_SOURCE_REVIEW_TABLES, PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
    schemas = {**PRACTICE_TABLES, **PRACTICE_VARIANT_TABLES, **PRACTICE_EVIDENCE_TABLES, **PRACTICE_COVERAGE_TABLES, **PRACTICE_SOURCE_REVIEW_TABLES, **PRACTICE_SOURCE_REVIEW_REVISION_TABLES}
    known = set(schemas)
    if not isinstance(decisions_raw, bytes) or _hash(decisions_raw) != decisions_sha256:
        raise MergeError('Decision digest mismatch')
    if not isinstance(inputs, list) or not inputs or not isinstance(inventory, dict) or not isinstance(base_records, dict):
        raise MergeError('Invalid input envelope')
    envelopes, identities, hashes = [], {}, set()
    for envelope in inputs:
        if not isinstance(envelope, dict) or set(envelope) != {'identity', 'raw'} or not _string(envelope['identity']) or not isinstance(envelope['raw'], bytes):
            raise MergeError('Invalid input envelope')
        identity, sha = envelope['identity'], _hash(envelope['raw'])
        if identity in identities or sha in hashes:
            raise MergeError('Duplicate input identity or digest')
        identities[identity] = sha
        hashes.add(sha)
        package = _parse(envelope['raw'])
        if not isinstance(package, dict) or not isinstance(package.get('practice_records'), dict) or not isinstance(package.get('entries'), list):
            raise MergeError('Invalid input package')
        if set(package['practice_records']) - known:
            raise MergeError('Unknown practice table')
        envelopes.append((sha, identity, package))
    envelopes.sort()
    decision_doc = _parse(decisions_raw)
    inventory_sha = _hash(_json(inventory).encode())
    if not isinstance(decision_doc, dict) or set(decision_doc) != {'version', 'inventory_digest', 'input_digests', 'decisions'} or decision_doc['version'] != 1 or decision_doc['inventory_digest'] != inventory_sha or decision_doc['input_digests'] != identities or not isinstance(decision_doc['decisions'], list):
        raise MergeError('Decision envelope or digest mismatch')
    head = envelopes[0][2]
    for _, _, p in envelopes:
        if any(p.get(k) != head.get(k) for k in ('contract_version', 'base_release', 'taxonomy_version', 'stage', 'scope_inventory')):
            raise MergeError('Incompatible input package headers')
        variable = {'entries', 'practice_records', 'party_id', 'source_review_refs', 'tranches'}
        if {k: v for k, v in p.items() if k not in variable} != {k: v for k, v in head.items() if k not in variable}:
            raise MergeError('Incompatible input package metadata')
    events, candidates, evidence = {}, {}, {}
    for sha, _, p in envelopes:
        records = p['practice_records']
        for table, rows in records.items():
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise MergeError('Invalid practice rows')
        for event in records.get('practice_event', []):
            eid, key = event.get('id'), event.get('common_event_key')
            ref = (sha, eid)
            if not _string(eid) or ref in events or (key is not None and not _string(key)):
                raise MergeError('Invalid event identity')
            events[ref] = event
            if key: candidates.setdefault(key, set()).add(ref)
        for row in records.get('practice_event_evidence', []):
            evidence.setdefault((sha, row.get('event_id')), set()).add(row.get('passage_id'))
    candidates = {key: refs for key, refs in candidates.items() if len(refs) > 1}
    parent = {ref: ref for ref in events}
    def root(ref):
        while parent[ref] != ref: ref = parent[ref]
        return ref
    parsed, claimed, ids = [], set(), set()
    fields = {'id', 'candidate_keys', 'event_refs', 'decision', 'canonical_event_id', 'overlap_reason', 'source_passage_ids', 'reviewed_at', 'reviewer_kind'}
    for decision in decision_doc['decisions']:
        if not isinstance(decision, dict) or set(decision) != fields or not _string(decision['id']) or decision['id'] in ids:
            raise MergeError('Invalid or duplicate decision')
        ids.add(decision['id'])
        keys, refs = decision['candidate_keys'], decision['event_refs']
        if not isinstance(keys, list) or not keys or len(keys) != len(set(keys)) or not isinstance(refs, list) or len(refs) < 2:
            raise MergeError('Invalid candidate decision')
        try:
            refs = [(r['input_package_sha256'], r['event_id']) for r in refs if set(r) == {'input_package_sha256', 'event_id'}]
            refset = set(refs)
        except (KeyError, TypeError):
            raise MergeError('Invalid event refs')
        if len(refs) != len(decision['event_refs']) or len(refs) != len(refset) or not refset <= set(events):
            raise MergeError('Dangling or duplicate event refs')
        if any(k not in candidates or k in claimed or candidates[k] != refset for k in keys):
            raise MergeError('Mismatched or conflicting candidate decision')
        claimed.update(keys)
        sources = decision['source_passage_ids']
        if not isinstance(sources, list) or not sources or any(not _string(s) for s in sources) or len(sources) != len(set(sources)) or any(not (evidence.get(ref, set()) & set(sources)) for ref in refs) or not set(sources) <= set().union(*(evidence.get(ref, set()) for ref in refs)):
            raise MergeError('Decision sources do not cover event evidence')
        if decision['reviewer_kind'] != 'agent' or not _string(decision['overlap_reason']):
            raise MergeError('Invalid decision attribution')
        try:
            if datetime.fromisoformat(decision['reviewed_at'].replace('Z', '+00:00')).utcoffset() is None: raise ValueError()
        except (ValueError, TypeError, AttributeError):
            raise MergeError('Invalid decision time')
        kind, canonical = decision['decision'], decision['canonical_event_id']
        if kind not in ('same', 'distinct', 'unresolved') or (kind == 'same' and canonical not in {ref[1] for ref in refs}) or (kind != 'same' and canonical is not None):
            raise MergeError('Invalid identity decision')
        if kind == 'same':
            representative = root(refs[0])
            for ref in refs[1:]: parent[root(ref)] = representative
        parsed.append((decision, refset))
    if claimed != set(candidates):
        raise MergeError('Missing candidate decision: ' + _json(sorted(set(candidates) - claimed)))
    for decision, refs in parsed:
        if decision['decision'] != 'same' and len({root(r) for r in refs}) != len(refs):
            raise MergeError('Distinct or unresolved events joined by same decision')
    groups = {}
    for ref in events: groups.setdefault(root(ref), []).append(ref)
    base_events = {row['id']: row for row in base_records.get('practice_event', [])}
    mapping, used, aliases = {}, set(), []
    for refs in sorted((sorted(v) for v in groups.values())):
        applicable = [(d, group) for d, group in parsed if group & set(refs)]
        same = [d for d, group in applicable if d['decision'] == 'same']
        requested = {d['canonical_event_id'] for d in same}
        if len(requested) > 1: raise MergeError('Conflicting canonical event IDs')
        base_ids = {r[1] for r in refs if r[1] in base_events and events[r] == base_events[r[1]]}
        if len(base_ids) > 1 or (base_ids and requested and requested != base_ids):
            raise MergeError('Accepted base event cannot be rewritten')
        if len(refs) > 1:
            values = [{k: v for k, v in events[r].items() if k != 'id'} for r in refs]
            if any(v != values[0] for v in values[1:]): raise MergeError('Conflicting single-valued event fields')
        canonical = next(iter(base_ids or requested), refs[0][1])
        if canonical in used or (canonical in base_events and canonical not in base_ids):
            canonical = canonical + '--' + refs[0][0][:16]
        if canonical in used or (canonical in base_events and canonical not in base_ids): raise MergeError('Canonical event collision')
        used.add(canonical)
        for ref in refs:
            mapping[ref] = canonical
            relevant = sorted(d['id'] for d, g in applicable if ref in g)
            aliases.append(dict(input_package_sha256=ref[0], input_event_id=ref[1], canonical_event_id=canonical, decision_id=relevant[0] if relevant else None))
    output, origins, entry_origins, refs_origins, review_contract_origins = {}, [], [], [], []
    def resolve_event(sha, event_id):
        ref = (sha, event_id)
        if ref in mapping:
            return mapping[ref]
        # A reference to an unchanged accepted base event does not assert a
        # new identity relationship or constitute a candidate decision.
        if event_id in base_events:
            mapping[ref] = event_id
            aliases.append(dict(input_package_sha256=sha, input_event_id=event_id,
                                canonical_event_id=event_id, decision_id=None))
            return event_id
        raise MergeError('Dangling event reference')
    def append(table, row):
        rows = output.setdefault(table, [])
        if row not in rows: rows.append(row)
    entries = []
    for sha, identity, p in envelopes:
        for entry in p['entries']:
            if not isinstance(entry, dict) or set(entry) != {'kind', 'values'} or not isinstance(entry['values'], dict) or any('event' in k for k in entry['values']):
                raise MergeError('Unknown entry or event reference')
            if entry not in entries: entries.append(copy.deepcopy(entry))
            entry_origins.append(dict(input_package_sha256=sha, input_identity=identity, party_id=p.get('party_id'), entry=copy.deepcopy(entry)))
        for table, rows in p['practice_records'].items():
            if table in ('practice_source_review_contract', 'practice_source_review_revision_contract'):
                review_contract_origins.append(dict(input_package_sha256=sha, input_identity=identity, party_id=p.get('party_id'), table=table, original=copy.deepcopy(rows)))
                continue
            if table not in REVIEW_TABLES:
                output.setdefault(table, [])
            for original in rows:
                row = copy.deepcopy(original)
                if table in REVIEW_TABLES:
                    kind, subject = row.get('subject_kind'), row.get('subject_id')
                    canonical = subject
                    if kind == 'practice_event': canonical = resolve_event(sha, subject)
                    elif kind == 'practice_event_evidence':
                        parts = subject.split('|') if isinstance(subject, str) else []
                        if len(parts) != 3: raise MergeError('Invalid review event evidence subject')
                        canonical = '|'.join([resolve_event(sha, parts[0]), *parts[1:]])
                    if not _string(canonical): raise MergeError('Dangling review subject')
                    origins.append(dict(input_package_sha256=sha, input_identity=identity, party_id=p.get('party_id'), table=table, original=row, canonical_subject_id=canonical))
                    continue
                for key in row:
                    if 'event' in key and key not in (('id', 'common_event_key', 'event_at') if table == 'practice_event' else ('event_id',) if table in EVENT_FK_TABLES else ()):
                        raise MergeError('Unknown event-bearing field')
                if table == 'practice_event': row['id'] = mapping[(sha, row['id'])]
                elif table in EVENT_FK_TABLES:
                    if 'event_id' not in row: raise MergeError('Missing event reference')
                    if row['event_id'] is not None:
                        row['event_id'] = resolve_event(sha, row['event_id'])
                if original in base_records.get(table, []) and row != original:
                    raise MergeError('Accepted base row cannot be rewritten')
                append(table, row)
        for ref in p.get('source_review_refs', []):
            if not isinstance(ref, dict) or set(ref) != {'subject_kind', 'subject_id'}:
                raise MergeError('Invalid review ref')
            matches = [origin for origin in origins if origin['input_package_sha256'] == sha and origin['original'].get('subject_kind') == ref['subject_kind'] and origin['original'].get('subject_id') == ref['subject_id']]
            if not matches: raise MergeError('Dangling review ref')
            refs_origins.append(dict(input_package_sha256=sha, input_identity=identity, party_id=p.get('party_id'), original=copy.deepcopy(ref), canonical_subject_id=matches[0]['canonical_subject_id']))
    schema_db = sqlite3.connect(':memory:')
    try:
        keys = {}
        for table in output:
            schema_db.execute('CREATE TABLE ' + table + ' (' + schemas[table] + ')')
            info = schema_db.execute('PRAGMA table_info(' + table + ')').fetchall()
            keys[table] = [r[1] for r in sorted(info, key=lambda r: r[5]) if r[5]]
    finally:
        schema_db.close()
    for table, rows in output.items():
        by_id = {}
        for row in rows:
            pk = keys[table]
            if pk and all(k in row for k in pk):
                identity = tuple(row[k] for k in pk)
                if identity in by_id and by_id[identity] != row: raise MergeError('Conflicting row identity: ' + table)
                by_id[identity] = row
        rows.sort(key=_json)
    entry_ids = {}
    for entry in entries:
        if 'id' in entry['values']:
            key = (entry['kind'], entry['values']['id'])
            if key in entry_ids and entry_ids[key] != entry:
                raise MergeError('Conflicting entry identity')
            entry_ids[key] = entry
    entries.sort(key=_json)
    payload = {k: copy.deepcopy(v) for k, v in head.items() if k not in ('entries', 'practice_records', 'party_id', 'source_review_refs', 'tranches')}
    payload.update(party_id=None, entries=entries, practice_records=output, source_review_refs=[], tranches=sorted({ _json(t) for _, _, p in envelopes for t in p.get('tranches', []) }))
    payload['tranches'] = [json.loads(t) for t in payload['tranches']]
    return dict(payload=payload, aliases=sorted(aliases, key=_json), decisions=sorted(copy.deepcopy(decision_doc['decisions']), key=_json),
        provenance=dict(version=1, inventory_digest=inventory_sha, input_digests=dict(sorted(identities.items())), decisions_sha256=decisions_sha256),
        review_origins=sorted(origins, key=_json), review_contract_origins=sorted(review_contract_origins, key=_json), review_ref_origins=sorted(refs_origins, key=_json), entry_origins=sorted(entry_origins, key=_json))
