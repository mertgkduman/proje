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
rehearsal = exercise['receipt']
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
        if key.startswith('tbmm-28-5-') or key in {
            'tbmm-28-4-100-10-4251-gundem',
            'tbmm-28-4-106-10-4314-gundem',
            'tbmm-28-4-108-10-4343-gundem',
            'tbmm-28-3-104-2-2927-iklim-kanunu',
            'tbmm-28-3-104-10-2881-gundem',
        }:
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
    assert db.execute('SELECT count(*) FROM practice_event').fetchone()[0] == rehearsal['merged_events']
    assert db.execute('SELECT count(*) FROM practice_relation').fetchone()[0] == rehearsal['merged_relations']
    assert db.execute('SELECT count(*) FROM practice_merge_origin WHERE origin_kind=?', ('review_origins',)).fetchone()[0] == rehearsal['review_origins']
    for key,(eid,parties) in joined.items():
        rows = db.execute('SELECT id FROM practice_event WHERE common_event_key=?',(key,)).fetchall()
        assert rows==[(eid,)]
        assert {r[0] for r in db.execute('SELECT party_id FROM practice_relation WHERE event_id=?',(eid,))} <= parties
        assert len(db.execute('SELECT 1 FROM practice_event_alias WHERE decision_id=?',(key,)).fetchall())==len(parties)
    if exercise['number'] in {'02', '03', '04', '05'}:
        november = {
            'tbmm-28-5-012-yeni-yol-genel-gorusme-fon-gundem',
            'tbmm-28-5-012-10-4961-gundem',
            'tbmm-28-5-012-yeni-parti-fon-gundem-299',
        }
        records_by_key = dict(db.execute(
            'SELECT common_event_key,id FROM practice_event WHERE common_event_key LIKE ?',
            ('tbmm-28-5-012-%',)))
        assert november <= records_by_key.keys()
        assert len({records_by_key[key] for key in november}) == 3
        for key in november & joined.keys():
            eid, parties = joined[key]
            expected = {'yeni-parti', 'iyi', 'yeni-yol'}
            if exercise['number'] in {'03', '04', '05'}:
                expected.add('dem')
            assert parties == expected
            contributions = db.execute(
                'SELECT party_id,actor_id,authority_passage_id FROM practice_contribution WHERE event_id=?', (eid,)
            ).fetchall()
            assert {row[0] for row in contributions} == parties
            assert len(contributions) == len({row[1] for row in contributions}) == len(parties)
            assert len({row[2] for row in contributions if row[2] is not None}) == 3
            if exercise['number'] in {'03', '04', '05'}:
                assert {row[0] for row in contributions if row[2] is None} == {'dem'}
    if exercise['number'] in {'03', '04', '05'}:
        for key in ('tbmm-28-4-106-10-4314-gundem', 'tbmm-28-4-108-10-4343-gundem'):
            eid, parties = joined[key]
            assert parties == {'dem', 'iyi', 'yeni-yol'}
            rows = db.execute('SELECT party_id,actor_id,authority_passage_id FROM practice_contribution WHERE event_id=?', (eid,)).fetchall()
            assert {r[0] for r in rows} == parties
            assert len(rows) == len({r[1] for r in rows}) == 3
            assert {r[0] for r in rows if r[2] is None} == {'dem'}
            assert len({r[2] for r in rows if r[2] is not None}) == 2
        climate, parties = joined['tbmm-28-3-104-2-2927-iklim-kanunu']
        expected_parties = {'tip', 'emep'}
        expected_passages = {'0405-tip-climate-2025-ballot-bas-p', '0405-tip-climate-2025-ballot-kadigil-p',
                             '0405-tip-climate-2025-ballot-sik-p', '0410-emep-climate-2025-ballot-bayhan-p',
                             '0410-emep-climate-2025-ballot-karaca-p'}
        if exercise['number'] == '05':
            expected_parties.add('dem')
            expected_passages.update('0406-iklim-final-' + name + '-vote' for name in ('akin', 'kordu', 'koca'))
            contributions = db.execute(
                'SELECT actor_id,authority_passage_id,membership_passage_id FROM practice_contribution WHERE party_id=? AND event_id=?',
                ('dem',climate),
            ).fetchall()
            assert len(contributions) == len({r[0] for r in contributions}) == len({r[2] for r in contributions}) == 3
            assert all(r[1] is None and r[2] for r in contributions)
        assert parties == expected_parties
        rows = db.execute('SELECT passage_id FROM practice_event_evidence WHERE event_id=?', (climate,)).fetchall()
        assert expected_passages <= {r[0] for r in rows}
    if exercise['number'] in {'04', '05'}:
        hububat, parties = joined['tbmm-28-4-100-10-4251-gundem']
        assert parties == {'yeni-yol', 'saadet'}
        assert db.execute(
            'SELECT party_id,actor_id,authority_passage_id FROM practice_contribution WHERE event_id=?',
            (hububat,),
        ).fetchall() == [('yeni-yol', '0408-hububat-actor', '0408-hububat-floor-role')]
        assert db.execute(
            'SELECT id,party_id FROM practice_relation WHERE event_id=?', (hububat,),
        ).fetchall() == [('0411-hububat-2026-agenda-relation', 'saadet')]
        assert db.execute(
            'SELECT state FROM practice_candidate WHERE id=?', ('0408-hububat-candidate',),
        ).fetchone() == ('unmatched',)
        for key in ('tmo-2026-06-25-hububat-ilk-odeme','tmo-2026-07-27-hububat-alim-odeme-bildirim','tmo-2026-08-17-hububat-alim-odeme-bildirim'):
            assert db.execute(
                'SELECT count(*) FROM practice_event WHERE common_event_key=?', (key,),
            ).fetchone() == (1,), key
    if exercise['number'] == '05':
        textile, parties = joined['tbmm-28-3-104-10-2881-gundem']
        assert parties == {'iyi', 'yeni-yol'}
        rows = db.execute(
            'SELECT party_id,actor_id,authority_passage_id FROM practice_contribution WHERE event_id=?', (textile,),
        ).fetchall()
        assert set(rows) == {
            ('iyi', '0407-agenda-104-2881-actor', '0407-agenda-104-floor-authority-2881'),
            ('yeni-yol', '0408-textile-2881-actor', '0408-textile-2881-floor-role'),
        }
        assert db.execute('SELECT id,party_id FROM practice_relation WHERE event_id=?', (textile,)).fetchall() == [
            ('0407-agenda-104-2881-relation', 'iyi'),
        ]
        assert db.execute('SELECT event_id,state FROM practice_candidate WHERE id=?',
                          ('0408-textile-2881-candidate',)).fetchone() == (textile,'unmatched')
        assert db.execute('SELECT event_id FROM practice_event_evidence WHERE passage_id=? AND stage=?',
                          ('0408-textile-2881-reply-number','action')).fetchone() == ('0408-textile-2881-29149-event',)
        assert db.execute('SELECT count(*) FROM practice_dispute_evidence WHERE dispute_id=?',
                          ('0408-textile-2881-export-dispute',)).fetchone() == (5,)
page = (release/'index.html').read_text()
for r in records['practice_relation']:
    for view in ('party','comparison'):
        target=f'{view}-practice-{r["id"]}'
        assert page.count(f'id="{target}"')==1 and f'href="#{target}"' in page,target
active_candidates = {row['id']: row['state'] for row in saved.get('practice_candidate', [])}
by_time = sorted(saved.get('practice_candidate_revision', []), key=lambda row: row['recorded_at'])
for row in by_time:
    active_candidates[row['candidate_id']] = row['state']
for identity, state in active_candidates.items():
    if state == 'unmatched':
        for view in ('party', 'comparison'):
            target = f'{view}-unmatched-{identity}'
            assert page.count(f'id="{target}"') == 1 and f'href="#{target}"' in page, target
assert sha256(pointer.read_bytes()).hexdigest()==before
result = dict(job=job,rehearsal=exercise['number'],active_unmatched=sum(state=='unmatched' for state in active_candidates.values()),preview=str(release.resolve()),manifest_sha256=sha256((release/'manifest.json').read_bytes()).hexdigest(),
              events=len(records['practice_event']),relations=len(records['practice_relation']),
              source_permissions=len(grants),shared_keys=sorted(joined),canonical_pointer_sha256=before,
              closures=len(records['practice_closure']))
print('UNION_REHEARSAL_PREVIEW_OK',json.dumps(result,ensure_ascii=False),flush=True)
