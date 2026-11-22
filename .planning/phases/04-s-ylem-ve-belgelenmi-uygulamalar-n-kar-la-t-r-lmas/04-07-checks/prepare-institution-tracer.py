import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, 'src')
import arsiv
import uygulamalar

D = Path(__file__).parent
base = json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
inventory = json.loads(Path('data/practices/04-inventory.json').read_text())
old = json.loads(subprocess.check_output(['git', 'show', 'da1e2b8:data/practices/04-yeni-parti.json']))
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
records = {k: [] for k in old['practice_records']}
records['practice_contract'] = old['practice_records']['practice_contract']
records['practice_coverage_contract'] = old['practice_records']['practice_coverage_contract']
event_scope = next(x for x in inventory['cells'] if x['party_id']=='iyi' and x['topic_id']=='merkez-kurul-olusumu' and x['research_kind']=='event')
statement_scope = next(x for x in inventory['cells'] if x['party_id']=='iyi' and x['topic_id']=='merkez-kurul-olusumu' and x['research_kind']=='statement')
for cell in [event_scope, statement_scope]:
    row = {k: cell[k] for k in ['party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind']}
    row.update(id=cell['cell_id'], boundary_reason='2020 tüzük ve 2023 kurultayının dar ilk incelemesi; diğer dönemler, seçim tutanağı ve tüm ilgili kaynaklar açıktır.')
    records['practice_scope_v2'].append(row)

entries = []
for filename in ['bianet-2023-source-draft.json', 'kurultay-cagri-2023-source-draft.json']:
    entries.extend(json.loads((D/filename).read_text())['entries'])
pdf = 'data/objects/45b1a30149247ae80e00105290343bed2e6d056dbd3cf2db8f5964a3c542441b/original.pdf'
assert hashlib.sha256(Path(pdf).read_bytes()).hexdigest() == '45b1a30149247ae80e00105290343bed2e6d056dbd3cf2db8f5964a3c542441b'
passage = '0407-2020-charter-kurultay-p'
exact = 'a. İYİ Parti Genel Başkan’ını, Genel İdare Kurulu ve Merkez Disiplin Kurulu’nun asıl ve yedek üyelerini gizli oylamayla\nseçmek,'
assert exact in arsiv.pdf_page_text(pdf, 23)
entries.append({'kind':'passage','values':dict(id=passage, version_id='0205-iyi-charter-istanbul-v1', exact=exact, prefix=None, suffix=None, article='Madde 36', section='Kurultayın görev ve yetkileri', pdf_page_index=23, printed_page='23')})
summary='0407-2020-kurultay-statement-finding'
relation_finding='0407-2023-kurultay-relation-finding'
source_passage='0407-iyi-2023-kurultay-bianet-p'
for fid, text, pids in [
    (summary, '2020 değişiklikleri işlenmiş tüzük, Kurultayın genel başkanı ve diğer merkez organlarını gizli oyla seçmesini düzenler.', [passage]),
    (relation_finding, '2020 değişiklikli tüzük, genel başkan seçimini Kurultayın görevleri arasında sayar. Bianet, 2023 olağan kurultayında Meral Akşener’in yeniden genel başkan seçildiğini bildirir.', [passage,source_passage]),
]:
    entries.append({'kind':'finding','values':dict(id=fid,party_id='iyi',heading='Söylem ve uygulama',pair_id=fid,text=text,provenance='summary',epistemic_type='claim')})
    entries.append({'kind':'review','values':dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='2020 tüzük ve 2023 bağımsız haberin ilgili pasajları ayrı okundu; ara tüzük sürümü belirsizdir.')})
    for pid in pids:
        entries += [{'kind':'finding_evidence','values':dict(finding_id=fid,passage_id=pid,role='support')}, {'kind':'verification','values':dict(finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Kaynak pasajı ve desteklediği sınırlı iddia birlikte okundu.')}]

sid='0407-2020-kurultay-statement'; eid='0407-2023-kurultay-event'; rid='0407-2023-kurultay-relation'
records['practice_statement'].append(dict(id=sid,party_id='iyi',topic_id='merkez-kurul-olusumu',taxonomy_version=4,summary_finding_id=summary,quote_finding_id=None,statement_at='2020-09-20',date_precision='day',version_id='0205-iyi-charter-istanbul-v1',period_basis='Tüzük PDF kapak kaydı 20 Eylül 2020 değişikliklerini gösterir; belge yayın tarihi değildir.',uncertainty_reason='2023 kurultayından önceki ara sürüm ve değişiklikler ayrıca araştırılmaktadır.',comparison_row_id='04-03-v3-0306-iyi-detail-kurultay-secim-row'))
records['practice_event'].append(dict(id=eid,common_event_key='iyi-parti-2023-06-24-3-olagan-kurultay-genel-baskan',event_at='2023-06-24',date_precision='day',date_unknown_reason=None,scope_context='İYİ Parti 3. Olağan Kurultayı genel başkan seçimi',title='Kurultayda genel başkan seçimi',occurrence_basis='Bianet 24 Haziran kurultayını ve oy sonucunu bildirir.'))
records['practice_event_evidence'].append(dict(event_id=eid,passage_id=source_passage,supported_point='Meral Akşener tek aday olarak 1127 geçerli oy aldı.',stage='action',concrete_basis='Bianet kurultay ve oylama sonucunu somut sayılarla bildirir.',limitation='Resmî seçim tutanağı görülmedi; oy hesabının diğer ayrıntıları bu pasajla kanıtlanmaz.',epistemic_type='claim'))
records.setdefault('practice_evidence_assessment',[]).append(dict(event_id=eid,passage_id=source_passage,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id=sid,event_id=eid,party_id='iyi',topic_id='merkez-kurul-olusumu',scope_id=event_scope['cell_id'],comparability_reason='Her ikisi Kurultayın parti merkezindeki konumu veya seçimiyle ilgilidir.',target_finding_id=summary,result_finding_id=None,explanation_finding_id=relation_finding,temporal_context='2020 değişiklikli tüzük ile 24 Haziran 2023 kurultayı ayrı tarihlerdir.',authority_context='Kurultay organı ve genel başkan seçimi; çağrı yazısında genel başkanın Madde 37 yetkisine ayrıca atıf var.',uncertainty_reason='2023 öncesi ara tüzük değişiklikleri ve seçim tutanağı araştırılmaktadır.'))
records['practice_candidate'].append(dict(id='0407-kurultay-candidate',scope_id=event_scope['cell_id'],event_id=eid,relation_id=rid,state='eligible',reason='Kurultaydaki genel başkan seçimi kurultay mekanizmasıyla bağlantılıdır.',passage_ids=json.dumps([source_passage],ensure_ascii=False)))
for cell, version, url, section, suffix in [(statement_scope,'0205-iyi-charter-istanbul-v1','https://iyiparti.istanbul/wp-content/uploads/2024/11/IYI-PARTI-TUZUGU.pdf','2020 Madde 36','charter'), (event_scope,'0407-iyi-2023-kurultay-bianet-v1','https://bianet.org/haber/iyi-parti-de-3-olagan-kurultay-aksener-yeniden-genel-baskan-280801','24 Haziran 2023 seçimi','bianet')]:
    attempt='0407-'+suffix+'-reading'
    records['practice_scope_source'].append(dict(scope_id=cell['cell_id'],version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+attempt,scope_id=cell['cell_id'],url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([attempt])))
    records['practice_attempt_v2'].append(dict(id=attempt,scope_id=cell['cell_id'],attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=version))
data = {k:list(v) if isinstance(v,list) else v for k,v in base.items()}
for entry in entries: data.setdefault(entry['kind'],[]).append(entry['values'])
for key, rows in records.items(): data.setdefault(key,[]).extend(rows)
targets=uygulamalar.practice_review_targets(data,records)
passages={p['id']:p for p in data['passage']}
reviews=[]
for (kind,identity),(pids,_) in targets.items():
    ids=sorted(pids)
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({passages[p]['version_id'] for p in ids}),ensure_ascii=False),passage_ids=json.dumps(ids,ensure_ascii=False),inspected_sections=json.dumps(['2020 tüzük Madde 36 ve 2023 kurultay haberi'],ensure_ascii=False),supported_claim=kind+' / '+identity+' hedefi için ilgili tüzük ve haber pasajları sınırlı kapsamla okundu.',limitations='Tüzüğün 2023 ara sürümü ve seçim tutanağı açık.',result='reviewed',reason=identity+' için ilgili pasajlar ayrı incelendi.'))
uygulamalar.validate_practice_source_review(data,reviews,party_id='iyi')
refs=[dict(subject_kind=r['subject_kind'],subject_id=r['subject_id']) for r in reviews]
package=dict(contract_version=1,base_release='f67ca0a35e634035bf3aa83a46571f50',party_id='iyi',taxonomy_version=4,stage='tracer',entries=entries,practice_records=records,scope_inventory=[dict(party_id='iyi',topic_id='merkez-kurul-olusumu',event_id=eid,stage='tracer',boundary='Sadece 2020 tüzük ve 2023 kurultayının ilk incelemesi; tüm kapsam açıktır.')],tranches=[],source_review_refs=[])
for name,obj in [('institution-tracer-draft.json',package),('institution-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews))
