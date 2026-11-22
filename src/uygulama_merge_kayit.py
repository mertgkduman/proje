"""Internal, replayable merge extension. Inputs still require external validation.

Origins retain exact original JSON and are not current-scope source reviews.
Each batch includes raw inputs, decisions, inventory and accepted base evidence;
replay checks every decision, alias, origin and resulting record on every export.
"""
import hashlib
import json


PRACTICE_MERGE_TABLES = {
    'practice_merge_contract': 'version INTEGER PRIMARY KEY',
    'practice_merge_provenance': 'id TEXT PRIMARY KEY, version INTEGER NOT NULL, inventory_digest TEXT NOT NULL, input_digests TEXT NOT NULL, decisions_sha256 TEXT NOT NULL, inventory_json TEXT NOT NULL, decisions_hex TEXT NOT NULL, base_records_json TEXT NOT NULL',
    'practice_merge_input': 'provenance_id TEXT NOT NULL REFERENCES practice_merge_provenance(id), input_identity TEXT NOT NULL, input_package_sha256 TEXT NOT NULL, raw_hex TEXT NOT NULL, PRIMARY KEY(provenance_id,input_identity), UNIQUE(provenance_id,input_package_sha256)',
    'practice_event_decision': 'provenance_id TEXT NOT NULL REFERENCES practice_merge_provenance(id), id TEXT NOT NULL, candidate_keys TEXT NOT NULL, event_refs TEXT NOT NULL, decision TEXT NOT NULL, canonical_event_id TEXT, overlap_reason TEXT NOT NULL, source_passage_ids TEXT NOT NULL, reviewed_at TEXT NOT NULL, reviewer_kind TEXT NOT NULL, PRIMARY KEY(provenance_id,id)',
    'practice_event_alias': 'provenance_id TEXT NOT NULL REFERENCES practice_merge_provenance(id), input_package_sha256 TEXT NOT NULL, input_event_id TEXT NOT NULL, canonical_event_id TEXT NOT NULL REFERENCES practice_event(id), decision_id TEXT, PRIMARY KEY(provenance_id,input_package_sha256,input_event_id), FOREIGN KEY(provenance_id,decision_id) REFERENCES practice_event_decision(provenance_id,id)',
    'practice_merge_origin': 'provenance_id TEXT NOT NULL REFERENCES practice_merge_provenance(id), origin_kind TEXT NOT NULL, ordinal INTEGER NOT NULL, input_package_sha256 TEXT NOT NULL, input_identity TEXT NOT NULL, party_id TEXT, original_json TEXT NOT NULL, canonical_subject_id TEXT, PRIMARY KEY(provenance_id,origin_kind,ordinal), FOREIGN KEY(provenance_id,input_identity) REFERENCES practice_merge_input(provenance_id,input_identity)',
}

ORIGIN_KINDS = ('review_origins', 'review_contract_origins', 'review_ref_origins', 'entry_origins')
ENTRY_KINDS = frozenset(('document', 'document_version', 'archive_view', 'passage', 'finding',
                         'finding_evidence', 'verification', 'source_attribution', 'review', 'attempt', 'missing'))
REVIEW_FIELDS = {
    'practice_statement': ('summary_finding_id', 'quote_finding_id'),
    'practice_relation': ('target_finding_id', 'result_finding_id', 'explanation_finding_id'),
    'practice_contribution': ('finding_id',),
    'practice_dispute': ('summary_finding_id',),
    'practice_position_change': ('explanation_finding_id',),
}


def _review_target_exists(data, kind, identity):
    if kind == 'practice_event_evidence':
        return any('|'.join((r['event_id'], r['passage_id'], r['stage'])) == identity for r in data.get(kind, []))
    if kind == 'practice_dispute_evidence':
        return any('|'.join((r['dispute_id'], r['passage_id'], r['point'], r['role'])) == identity for r in data.get(kind, []))
    table, dot, field = kind.partition('.')
    if table not in set(REVIEW_FIELDS) | {'practice_event', 'practice_unmatched', 'practice_candidate', 'practice_candidate_revision'}:
        return False
    if dot and field not in REVIEW_FIELDS.get(table, ()):
        return False
    return any(r['id'] == identity and (not dot or r.get(field)) for r in data.get(table, []))


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _contract_descends(previous, current):
    """Only the operational stage may advance; every other field is immutable."""
    levels = {'tracer': 0, 'partial': 1, 'complete': 2}
    return (isinstance(previous, dict) and isinstance(current, dict) and
            set(previous) == set(current) and 'stage' in previous and
            previous['stage'] in levels and current['stage'] in levels and
            levels[current['stage']] >= levels[previous['stage']] and
            all(value == current[key] for key, value in previous.items() if key != 'stage'))


def materialize_practice_merge(inventory, inputs, decisions_raw, base_records, outcome):
    """Encode an already validated engine result; this does not validate sources."""
    from uygulama_birlestirme import merge_packages
    replay = merge_packages(inventory, inputs, decisions_raw, decisions_sha256=_sha(decisions_raw), base_records=base_records)
    if outcome != replay:
        raise ValueError('Birleşme sonucu yeniden üretilemiyor')
    prov = replay['provenance']
    envelope = dict(inventory=inventory, inputs=[dict(identity=x['identity'], raw_hex=x['raw'].hex()) for x in sorted(inputs, key=lambda x: x['identity'])], decisions_hex=decisions_raw.hex(), base_records=base_records)
    batch = _sha(_json(envelope).encode())
    result = {name: [] for name in PRACTICE_MERGE_TABLES}
    result['practice_merge_contract'] = [dict(version=1)]
    result['practice_merge_provenance'] = [dict(id=batch, version=prov['version'], inventory_digest=prov['inventory_digest'], input_digests=_json(prov['input_digests']), decisions_sha256=prov['decisions_sha256'], inventory_json=_json(inventory), decisions_hex=decisions_raw.hex(), base_records_json=_json(base_records))]
    result['practice_merge_input'] = [dict(provenance_id=batch, input_identity=x['identity'], input_package_sha256=_sha(x['raw']), raw_hex=x['raw'].hex()) for x in sorted(inputs, key=lambda x: x['identity'])]
    for decision in replay['decisions']:
        row = dict(decision, provenance_id=batch)
        for key in ('candidate_keys', 'event_refs', 'source_passage_ids'): row[key] = _json(row[key])
        result['practice_event_decision'].append(row)
    result['practice_event_alias'] = [dict(x, provenance_id=batch) for x in replay['aliases']]
    for kind in ORIGIN_KINDS:
        for ordinal, origin in enumerate(replay[kind]):
            result['practice_merge_origin'].append(dict(provenance_id=batch, origin_kind=kind, ordinal=ordinal, input_package_sha256=origin['input_package_sha256'], input_identity=origin['input_identity'], party_id=origin['party_id'], original_json=_json(origin), canonical_subject_id=origin.get('canonical_subject_id')))
    return result


def validate_practice_merge(data):
    present = set(data).intersection(PRACTICE_MERGE_TABLES)
    if not present: return True
    if present != set(PRACTICE_MERGE_TABLES) or data['practice_merge_contract'] != [dict(version=1)] or not data['practice_merge_provenance']:
        raise ValueError('Birleşme sözleşmesi eksik')
    batches = {x['id'] for x in data['practice_merge_provenance']}
    if len(batches) != len(data['practice_merge_provenance']): raise ValueError('Tekrarlı birleşme')
    for table in PRACTICE_MERGE_TABLES:
        if table not in ('practice_merge_contract', 'practice_merge_provenance') and any(x['provenance_id'] not in batches for x in data[table]): raise ValueError('Köksüz birleşme kaydı')
    try:
        for prov in data['practice_merge_provenance']:
            batch = prov['id']
            inputs = [dict(identity=x['input_identity'], raw=bytes.fromhex(x['raw_hex'])) for x in data['practice_merge_input'] if x['provenance_id'] == batch]
            inventory, base = json.loads(prov['inventory_json']), json.loads(prov['base_records_json'])
            inventories = [json.loads(row['inventory_json']) for row in data.get('practice_coverage_contract', [])]
            inventories += [json.loads(row['inventory_json']) for row in data.get('practice_inventory_revision', [])]
            if inventory not in inventories:
                raise ValueError('Birleşme envanteri kanonik kapsam geçmişinde bulunamadı')
            raw_decisions = bytes.fromhex(prov['decisions_hex'])
            from uygulama_birlestirme import merge_packages
            replay = merge_packages(inventory, inputs, raw_decisions, decisions_sha256=prov['decisions_sha256'], base_records=base)
            expected = materialize_practice_merge(inventory, inputs, raw_decisions, base, replay)
            for table, rows in expected.items():
                actual = data[table] if table == 'practice_merge_contract' else [x for x in data[table] if (x['id'] if table == 'practice_merge_provenance' else x['provenance_id']) == batch]
                if sorted(map(_json, actual)) != sorted(map(_json, rows)): raise ValueError('Birleşme kökeni veya kararı uyuşmuyor: ' + table)
            for table, rows in replay['payload']['practice_records'].items():
                if table == 'practice_contract':
                    current = data.get(table, [])
                    if len(rows) != 1 or len(current) != 1 or not _contract_descends(rows[0], current[0]):
                        raise ValueError('Birleşme sözleşmesi geriletilemez veya değiştirilemez')
                    continue
                if any(row not in data.get(table, []) for row in rows): raise ValueError('Birleşme kaydı kayıp: ' + table)
            for entry in replay['payload']['entries']:
                if entry['kind'] not in ENTRY_KINDS or not any(all(existing.get(k) == v for k, v in entry['values'].items())
                           for existing in data.get(entry['kind'], [])):
                    raise ValueError('Birleşme girdisi kayıp')
            if any(row not in data.get(table, []) for table, rows in base.items() if table != 'practice_contract' for row in rows):
                raise ValueError('Birleşme tabanı kayıp')
            if base.get('practice_contract'):
                current = data.get('practice_contract', [])
                if len(base['practice_contract']) != 1 or len(current) != 1 or not _contract_descends(base['practice_contract'][0], current[0]):
                    raise ValueError('Birleşme taban sözleşmesi geriletilemez')
            events = {x['id'] for x in data.get('practice_event', [])}
            if any(x['canonical_event_id'] not in events for x in expected['practice_event_alias']): raise ValueError('Birleşme olayı bulunamadı')
            for kind in ('review_origins', 'review_ref_origins'):
                for origin in replay[kind]:
                    original = origin['original']
                    if not _review_target_exists(data, original['subject_kind'], origin['canonical_subject_id']):
                        raise ValueError('Birleşme inceleme hedefi bulunamadı')
                    if kind == 'review_origins':
                        passages = {p['id']: p for p in data.get('passage', [])}
                        versions = {v['id']: v for v in data.get('document_version', [])}
                        passage_ids = json.loads(original['passage_ids'])
                        version_ids = json.loads(original['source_version_ids'])
                        if (not isinstance(passage_ids, list) or not passage_ids or len(set(passage_ids)) != len(passage_ids) or
                                not isinstance(version_ids, list) or not version_ids or len(set(version_ids)) != len(version_ids) or
                                any(p not in passages for p in passage_ids) or any(v not in versions for v in version_ids) or
                                set(version_ids) != {passages[p]['version_id'] for p in passage_ids}):
                            raise ValueError('Birleşme inceleme kaynakları bulunamadı')
                        if original['subject_kind'] in ('practice_event', 'practice_event_evidence'):
                            event_id = origin['canonical_subject_id'].split('|')[0]
                            allowed = {e['passage_id'] for e in data.get('practice_event_evidence', []) if e['event_id'] == event_id}
                            if original['subject_kind'] == 'practice_event_evidence':
                                allowed = {origin['canonical_subject_id'].split('|')[1]}
                            if not set(passage_ids) <= allowed:
                                raise ValueError('Birleşme inceleme pasajı hedefe bağlı değil')
                        party = origin['party_id']
                        if party is not None:
                            documents = {d['id']: d for d in data.get('document', [])}
                            grants = {(r['version_id'], r['party_id'], r['passage_id']) for r in data.get('practice_source_party', []) if r.get('scope_reason')}
                            for passage_id in passage_ids:
                                version_id = passages[passage_id]['version_id']
                                document = documents.get(versions[version_id]['document_id'])
                                if not document or (document['party_id'] != party and (version_id, party, passage_id) not in grants):
                                    raise ValueError('Birleşme inceleme kaynak sahibi uyuşmuyor')
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError('Birleşme kaydı geçersiz') from exc
    return True
