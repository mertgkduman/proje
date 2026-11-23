"""Exercise real shared-event records in temporary inputs without changing the package pairs."""

from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

from uygulama_birlestirme import _json, merge_packages, MergeError
from uygulama_merge_kayit import ENTRY_KINDS

root = Path('data')
report = json.loads(Path(__file__).with_name('wave4-common-event-audit-01.json').read_bytes())
inventory = json.loads((root/'practices/04-inventory.json').read_bytes())
base = json.loads((root/'releases'/report['base_release']/'records.json').read_bytes())
selected = ('iyi','yeni-yol')
keys = ('tbmm-28-4-050-2-3464-7573','tbmm-28-4-079-10-3998-gundem')
shared = {row['candidate_key']:row for row in report['common_event_candidates'] if row['candidate_key'] in keys}
common = {
    keys[0]: ('2/3464 teklifinin 50. Birleşimde kabulü',
              'TBMM 2/3464 teklifinin tümünü kabul etti. Teklif 7573 sayılı Kanuna dönüştü.',
              '50. Birleşim tam tutanağı, kesin açık oy cetveli ve TBMM kanun kaydı.'),
    keys[1]: ('10/3998 araştırma önergesinin gündeme alınması',
              'Yeni Yol Grubu TÜİK araştırma önergesinin ön görüşmesini aynı güne almak istedi. Genel Kurul bu öneriyi kabul etmedi.',
              'TBMM 10/3998 dosyası, 79. Birleşim tam tutanağı ve işlem özeti.'),
}


def digest(raw):
    return sha256(raw).hexdigest()


def load(join_review=False, normalize=False):
    result = []
    for party in selected:
        path = root/'practices'/f'04-{party}.json'
        raw = subprocess.check_output(['git','show','78c1a0f3:'+str(path)])
        assert digest(raw)==report['packages'][party]['package_sha256']
        if join_review or normalize:
            package = json.loads(raw)
            records = package['practice_records']
            if join_review:
                review_path = path.with_name(f'04-{party}-review.json')
                review_raw = subprocess.check_output(['git','show','78c1a0f3:'+str(review_path)])
                assert digest(review_raw)==report['packages'][party]['companion_review_sha256']
                review = json.loads(review_raw)
                records['practice_source_review'] = review['practice_source_review']
                records['practice_source_review_contract'] = [{'version':1}]
            if normalize:
                for event in records['practice_event']:
                    if event['common_event_key'] in common:
                        title,context,basis = common[event['common_event_key']]
                        event.update(title=title,scope_context=context,occurrence_basis=basis)
            raw = _json(package).encode()
        result.append(dict(identity=party,raw=raw))
    return result


def decision_bytes(inputs):
    digests = {row['identity']:digest(row['raw']) for row in inputs}
    result = []
    for key in keys:
        members = [row for row in shared[key]['party_records'] if row['party'] in selected]
        common_evidence = set(shared[key]['common_evidence_sha256'])
        evidence = sorted({row['passage_id'] for item in members for row in item['evidence']
                           if row['source_sha256'] in common_evidence})
        refs = [dict(input_package_sha256=digests[row['party']],event_id=row['event']['id']) for row in members]
        reason = 'Aynı teklif ve aynı TBMM işlem aşaması, ortak resmî kayıt nüshaları ile belgelendi.'
        result.append(dict(id=key,candidate_keys=[key],event_refs=refs,decision='same',canonical_event_id=refs[0]['event_id'],
            overlap_reason=reason,source_passage_ids=evidence,reviewed_at='2026-11-23T01:24:00+00:00',reviewer_kind='agent'))
    return _json(dict(version=1,inventory_digest=digest(_json(inventory).encode()),input_digests=digests,decisions=result)).encode()


for label,joined,normalized in [('original',False,False),('prototype_metadata',False,True),('prototype_metadata_and_reviews',True,True)]:
    inputs = load(joined,normalized)
    decisions = decision_bytes(inputs)
    try:
        outcome = merge_packages(inventory,inputs,decisions,decisions_sha256=digest(decisions),base_records=base)
    except MergeError as err:
        print(label,str(err))
    else:
        payload=outcome['payload']
        print(label,'structural merge passes',
              len(payload['practice_records']['practice_event']),len(payload['practice_records']['practice_relation']),
              len(outcome['aliases']),len(outcome['review_origins']))
        print('origin audit entry kinds outside whitelist',
              sorted({row['kind'] for row in payload['entries']}-ENTRY_KINDS))
        assert outcome==merge_packages(inventory,list(reversed(inputs)),decisions,decisions_sha256=digest(decisions),base_records=base)


if '--preview' in sys.argv:
    from uygulamalar import merge_practice_packages
    inputs = load(join_review=True, normalize=True)
    decisions = decision_bytes(inputs)
    source_roots = {party: root/'practices'/'sources'/party for party in selected}
    output = merge_practice_packages(inventory, inputs, decisions, source_roots=source_roots)
    records = output['practice_records']
    aliases = records['practice_event_alias']
    assert len(aliases) == 17
    assert len(records['practice_event']) == 13
    assert len(records['practice_relation']) == 11
    assert len(records['practice_event_decision']) == 2
    assert all(row['decision'] == 'same' for row in records['practice_event_decision'])
    assert len([row for row in records['practice_merge_origin'] if row['origin_kind']=='review_origins']) == 223
    assert json.loads((root/'current.json').read_bytes())['release_id'] == report['base_release']
    print('TWO_PARTY_SOURCE_AND_SQLITE_PREVIEW_OK', flush=True)


def scoped_union_preview():
    """Test explicit passage grants for the two audited TBMM procedures."""
    from uygulamalar import _digest, _render_practice_preview
    from uygulama_merge_kayit import materialize_practice_merge

    inputs = load(join_review=True, normalize=True)
    decisions = decision_bytes(inputs)
    result = merge_packages(inventory, inputs, decisions,
        decisions_sha256=digest(decisions), base_records=base)
    payload = result['payload']
    records = payload['practice_records']
    records.update(materialize_practice_merge(inventory,inputs,decisions,base,result))
    documents = {r['id']:r for r in base['document']}
    versions = {r['id']:r for r in base['document_version']}
    passages = {r['id']:r for r in base['passage']}
    for entry in payload['entries']:
        row = entry['values']
        catalogs = {'document':documents, 'document_version':versions, 'passage':passages}
        if entry['kind'] in catalogs:
            catalogs[entry['kind']][row['id']] = row
    existing = {(r['version_id'],r['party_id'],r['passage_id'])
                for r in records['practice_source_party']+base.get('practice_source_party',[])}
    grants = []
    for decision in result['decisions']:
        assert decision['decision']=='same' and decision['id'] in common
        eid = decision['canonical_event_id']
        ids = {r['passage_id'] for r in records['practice_event_evidence'] if r['event_id']==eid}
        disputes = {r['id'] for r in records['practice_dispute'] if r['event_id']==eid}
        ids.update(r['passage_id'] for r in records['practice_dispute_evidence'] if r['dispute_id'] in disputes)
        assert set(decision['source_passage_ids']) <= ids
        for pid in sorted(ids):
            version = versions[passages[pid]['version_id']]
            document = documents[version['document_id']]
            assert document['source_kind']=='official' and document['party_id'] in selected
            for party in selected:
                if document['party_id']==party or (version['id'],party,pid) in existing:
                    continue
                reason = ('Geçici ortak olay denetimi. '+decision['id']+
                          ' kararının aynı TBMM işlemine bağlı özgün resmî pasajı. '
                          'Alıntılanan parti veya kişiye ait rol, oy ve önerge başvuruları ayrı korunuyor.')
                grants.append(dict(version_id=version['id'],party_id=party,passage_id=pid,scope_reason=reason))
    grants.sort(key=_json)
    assert len(grants)==43,len(grants)
    records['practice_source_party'].extend(grants)
    roots = {_digest(entry):root/'practices/sources'/item['identity']
             for item in inputs for entry in json.loads(item['raw'])['entries']}
    output = root/'.staging'/('gsd-wave4-shared-scoped-'+os.environ['SLURM_JOB_ID'])
    with tempfile.TemporaryDirectory(prefix='gsd-wave4-scoped-') as directory:
        preview = Path(directory)/'preview'
        _render_practice_preview(payload,preview,inventory,report['base_release'],
                                 _validated_merge_roots=roots)
        shutil.copytree(preview,output)
    release, = (output/'releases').iterdir()
    saved = json.loads((release/'records.json').read_bytes())
    assert all(row in saved['practice_source_party'] for row in grants)
    assert len(records['practice_event_alias'])==17
    assert len(records['practice_event'])==13
    assert len(records['practice_relation'])==11
    page = (release/'index.html').read_text()
    for row in records['practice_relation']:
        for view in ('party','comparison'):
            tag = f'id="{view}-practice-{row["id"]}"'
            assert page.count(tag)==1,tag
    assert json.loads((root/'current.json').read_bytes())['release_id']==report['base_release']
    print('TWO_PARTY_SCOPED_SOURCE_AND_SQLITE_PREVIEW_OK',len(grants),release,flush=True)


if '--scoped-preview' in sys.argv:
    scoped_union_preview()
