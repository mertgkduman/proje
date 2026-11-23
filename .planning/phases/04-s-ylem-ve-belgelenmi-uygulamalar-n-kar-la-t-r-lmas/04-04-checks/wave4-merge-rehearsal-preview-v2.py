"""Exercise the structurally verified rehearsal in an isolated reader preview."""

from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import shutil
import sqlite3
import tempfile

from uygulamalar import (
    PRACTICE_TABLES, PRACTICE_VARIANT_TABLES, PRACTICE_EVIDENCE_TABLES,
    PRACTICE_COVERAGE_TABLES, PRACTICE_SOURCE_REVIEW_TABLES,
    PRACTICE_SOURCE_REVIEW_REVISION_TABLES, _digest, _render_practice_preview,
)
from uygulama_merge_kayit import materialize_practice_merge

here = Path(__file__).resolve().parent
exercise = runpy.run_path(str(here/'wave4-merge-rehearsal-01.py'))
input_rows = exercise['inputs']
decisions = exercise['decision_bytes']
inventory = exercise['inventory']
base = exercise['base']
outcome = exercise['first']
data = exercise['data']
payload = outcome['payload']
records = payload['practice_records']
schemas = (PRACTICE_TABLES | PRACTICE_VARIANT_TABLES | PRACTICE_EVIDENCE_TABLES |
           PRACTICE_COVERAGE_TABLES | PRACTICE_SOURCE_REVIEW_TABLES | PRACTICE_SOURCE_REVIEW_REVISION_TABLES)
base_records = {name:base[name] for name in schemas if name in base}
records.update(materialize_practice_merge(inventory,input_rows,decisions,base_records,outcome))
docs = {name:{r['id']:r for r in base[name]} for name in ('document','document_version','passage')}
for entry in payload['entries']:
    if entry['kind'] in docs:
        docs[entry['kind']][entry['values']['id']] = entry['values']
attributions = {e['values']['version_id']:e['values'] for e in payload['entries'] if e['kind']=='source_attribution'}
party_by_digest = {sha256(r['raw']).hexdigest():r['identity'] for r in input_rows}
existing = {(r['version_id'],r['party_id'],r['passage_id'])
    for r in base.get('practice_source_party',[])+records['practice_source_party']}
grants = []
joined = {}
for decision in outcome['decisions']:
    if decision['decision'] != 'same':
        continue
    key = decision['id']
    eid = decision['canonical_event_id']
    parties = {party_by_digest[r['input_package_sha256']] for r in decision['event_refs']}
    joined[key] = (eid,parties)
    passages = {r['passage_id'] for r in records['practice_event_evidence'] if r['event_id']==eid}
    disputes = {r['id'] for r in records['practice_dispute'] if r['event_id']==eid}
    passages.update(r['passage_id'] for r in records['practice_dispute_evidence'] if r['dispute_id'] in disputes)
    assert set(decision['source_passage_ids']) <= passages
    for pid in sorted(passages):
        version = docs['document_version'][docs['passage'][pid]['version_id']]
        document = docs['document'][version['document_id']]
        assert document['party_id'] in parties
        if key.startswith('tbmm-28-5-'):
            assert document['source_kind']=='official'
        else:
            assert key=='tbmm-sik-makas-karaca-isci-basin-toplantisi-2026'
            assert parties=={'emep','tip'}
            source = attributions[version['id']]
            if document['source_kind'] == 'party':
                assert document['party_id']=='emep' and source['kind']=='party_publication'
                assert source['publisher']=='Emek Partisi'
            else:
                assert document['source_kind']=='journalism' and source['kind']=='journalism'
                assert source['publisher']=='ANKA Haber'
        for party in sorted(parties-{document['party_id']}):
            identity = (version['id'],party,pid)
            if identity not in existing:
                existing.add(identity)
                grants.append(dict(version_id=version['id'],party_id=party,passage_id=pid,
                    scope_reason=f'{key} için aynı olaya bağlı pasaj. Özgün yayıncı ve parti katkısının atfı korunur.'))
records['practice_source_party'].extend(grants)
print('MATERIALIZED_REHEARSAL',len(grants),flush=True)
roots = {_digest(entry):data/'practices/sources'/row['identity']
         for row in input_rows for entry in json.loads(row['raw'])['entries']}
job = os.environ['SLURM_JOB_ID']
pointer = data/'current.json'
before = sha256(pointer.read_bytes()).hexdigest()
base_id = inventory['base_release']
assert json.loads(pointer.read_bytes())['release_id']==base_id
assert before=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
destination = data/'.staging'/f'gsd-wave4-rehearsal-preview-{job}'
with tempfile.TemporaryDirectory(prefix='gsd-wave4-rehearsal-') as directory:
    preview = Path(directory)/'preview'
    _render_practice_preview(payload,preview,inventory,base_id,_validated_merge_roots=roots)
    shutil.copytree(preview,destination)
release, = (destination/'releases').iterdir()
saved = json.loads((release/'records.json').read_bytes())
manifest = json.loads((release/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
assert all(sha256((release/k).read_bytes()).hexdigest()==v for k,v in manifest['files'].items())
assert all(row in saved['practice_source_party'] for row in grants)
with sqlite3.connect((release/'records.sqlite3').resolve().as_uri()+'?mode=ro',uri=True) as db:
    assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    for key,(eid,parties) in joined.items():
        rows = db.execute('SELECT id FROM practice_event WHERE common_event_key=?',(key,)).fetchall()
        assert rows==[(eid,)]
        assert {r[0] for r in db.execute('SELECT party_id FROM practice_relation WHERE event_id=?',(eid,))} <= parties
        assert len(db.execute('SELECT 1 FROM practice_event_alias WHERE decision_id=?',(key,)).fetchall())==len(parties)
page = (release/'index.html').read_text()
for r in records['practice_relation']:
    for view in ('party','comparison'):
        target=f'{view}-practice-{r["id"]}'
        assert page.count(f'id="{target}"')==1 and f'href="#{target}"' in page,target
assert sha256(pointer.read_bytes()).hexdigest()==before
result = dict(job=job,preview=str(release.resolve()),manifest_sha256=sha256((release/'manifest.json').read_bytes()).hexdigest(),
              events=len(records['practice_event']),relations=len(records['practice_relation']),
              source_permissions=len(grants),shared_keys=sorted(joined),canonical_pointer_sha256=before,
              closures=len(records['practice_closure']))
print('UNION_REHEARSAL_PREVIEW_OK',json.dumps(result,ensure_ascii=False),flush=True)
