"""Record dated council decisions and preserve municipal budget provenance."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'baglar-may-chains-source-records.json')
party=aux['party_id']
package=read(here/'baglar-april-chains-draft.json')
review=read(here/'baglar-april-chains-review-draft.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
records=package['practice_records']
when=datetime.now(timezone.utc).isoformat()
passages={r['id']:r for r in snapshot['passage']}
passages.update({e['values']['id']:e['values'] for e in entries if e['kind']=='passage'})
versions={r['id']:r for r in snapshot['document_version']}
versions.update({e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'})
tasks={}
def new(table,**row):
    entries.append(dict(kind=table,values=row))
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Bağlar Belediye Meclisi kararının ilgili bölümü özgün derlemede okundu.'))
    return sid
def readings(topic,lane,refs):
    sid=scope_for(topic,lane)
    grouped={}
    for pid in refs:
        p=passages[pid]
        grouped.setdefault(p['version_id'],set()).add(p['section'])
    for vid,sections in grouped.items():
        existing=[r for r in records['practice_scope_source'] if (r['scope_id'],r['version_id'])==(sid,vid)]
        if existing and set(json.loads(existing[-1]['inspected_sections']))>=sections:
            continue
        if existing:
            sections.update(json.loads(existing[-1]['inspected_sections']))
            if existing[-1]['inspected_at']==when:
                existing[-1]['inspected_sections']=encoded(sorted(sections))
                continue
        url=versions[vid]['final_url']
        aid=f'baglar-may-chains-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Bağlar Belediye Meclisi kararı veya yerel seçim dönem kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Bağlar Belediyesi 2015 Meclis karar derlemesindeki tarihli karar.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid

assert party=='dbp'
assert sha256((here/'baglar-april-chains-draft.json').read_bytes()).hexdigest()=='b2f446c0f16c5063836bf1ec8a00d78a90a6cdd0d7cac00acd6a7e3c23c257ec'
assert sha256((here/'baglar-april-chains-review-draft.json').read_bytes()).hexdigest()=='9d89e7b7ae94de4b65831ad3f884b462da01f4351ae1a259f4ac4e5b6354f2ab'
from decimal import Decimal
assert Decimal('26772318.56')-Decimal('23025318.56')==Decimal('3747000.00')
prefix='0409-baglar-may-chains-';electoral=['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party'];base_limit='İşlem belediye meclisine ait; YSK kaydı 2014 seçim bağlamını verir. Parti organı kararı ve kişisel oylar açık.'
cases=[('44','2015-02-06','yerel-demokrasi','Şeyhşamil Fen İşleri incelemesinin sevki','Bağlar Belediye Meclisi Şeyhşamil Mahallesindeki Fen İşleri çalışmalarının araştırılmasını komisyona sevk etti.','2015/103 sonraki komisyon raporu; sevk hizmet tamamlanması veya ödeme kanıtı değildir.',[('file','initiative','2015/44 kararı.'),('topic','action','Şeyhşamil Fen İşleri araştırmasının sevki.')]),('63','2015-03-06','kadin-istihdami','Jiyan pazarındaki eşitlik incelemesinin sevki','Bağlar Belediye Meclisi Jiyan Sabit Semt Pazarı çalışmalarının cinsiyet eşitliği açısından incelenmesini komisyona sevk etti.','2015/102 sonraki rapor; sevk pazarın taşındığını veya sorunların çözüldüğünü göstermez.',[('file','initiative','2015/63 kararı.'),('topic','action','Jiyan pazarına ilişkin inceleme.')]),('64','2015-03-06','yerel-demokrasi','Kaynartepe mahalle sorunlarının sevki','Bağlar Belediye Meclisi Kaynartepe Mahallesi sakinlerinin sorunlarının incelenmesini komisyona sevk etti.','2015/100 sonraki rapor; sevk hizmet teslimi değildir.',[('file','initiative','2015/64 kararı.'),('topic','action','Kaynartepe sakinleri başvurusunun sevki.')]),('103','2015-05-06','yerel-demokrasi','Şeyhşamil Fen İşleri raporunun kabulü','Bağlar Belediye Meclisi Şeyhşamil Fen İşleri çalışmalarına ilişkin İnceleme ve Araştırma Komisyonu raporunu kabul etti.','2015/44 önceki sevk. Komisyon altı sokakta parke döşendiğini bildirdi; ihale, teslim, ödeme ve diğer sokakların tamamlanması açık.',[('file','initiative','2015/103 kararı.'),('result','action','Komisyon altı sokak hakkında döşeme bildirdi.'),('approved','result','Komisyon raporu mecliste kabul edildi.')]),('102','2015-05-06','kadin-istihdami','Jiyan pazarı komisyon raporunun kabulü','Bağlar Belediye Meclisi Jiyan Sabit Semt Pazarı hakkında Kadın-Erkek Eşitlik Komisyonu raporunu kabul etti.','2015/63 önceki sevk. Raporda esnafın yer değişikliği talebi bulunur; fiyat iddiaları ve taşınma sonucu açık.',[('file','initiative','2015/102 kararı.'),('result','action','Raporda pazar yerinin değiştirilmesi talebi.'),('approved','result','Komisyon raporu mecliste kabul edildi.')]),('100','2015-05-06','yerel-demokrasi','Kaynartepe mahalle raporunun kabulü','Bağlar Belediye Meclisi Kaynartepe mahalle sakinlerinin sorunlarına ilişkin Halkla İlişkiler Komisyonu raporunu kabul etti.','2015/64 önceki sevk. Talepler ilgili birimlere yönlendirildi; hizmet emri, ödeme ve teslim açık.',[('file','initiative','2015/100 kararı.'),('result','action','Komisyon mahalle sakinlerinin aydınlatma beyanını aktardı.'),('approved','result','Komisyon raporu mecliste kabul edildi.')]),('105','2015-05-07','kamu-hesap-verebilirlik','Bağlar 2014 kesin hesabının kabulü','Bağlar Belediye Meclisi 2014 yılı bütçe kesin hesabını kabul etti; hesapta Temizlik İşleri için 26.772.318,56 TL yazıyor.','2015/99 komisyon raporu aynı müdürlük ve yıl için 23.025.318,56 TL bildiriyor; aritmetik fark 3.747.000 TL. Kapsam, muhasebe belgeleri ve ödemeler açık.',[('file','initiative','2015/105 kesin hesap kararı.'),('sum','action','Kesin hesapta Temizlik İşleri 26.772.318,56 TL.'),('approved','result','2014 kesin hesabı mecliste kabul edildi.')])]
for number,day,topic,title,context,detail,anchors in cases:
 stem=prefix+number;limit=detail+' '+base_limit;ev=[(stem+'-'+label,stage,'document',point) for label,stage,point in anchors];prior={'103':'44','102':'63','100':'64'}.get(number)
 if prior:ev.append((prefix+prior+'-file','initiative','document','Önceki 2015/'+prior+' komisyon sevki.'))
 if number=='105':ev.append((prefix+'99-sum','initiative','document','2015/99 komisyon raporunda aynı müdürlüğün toplamı 23.025.318,56 TL.'))
 eid=event(stem,day,title,context,ev,limit);records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2015-'+number;pids=[x[0] for x in ev];scope=readings(topic,'event',pids+electoral);reason=detail+' Önceleyen aynı kapsamlı tarihli parti hedefi araştırılıyor.';cid=stem+'-unmatched';records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)));task('practice_candidate',cid,reason,limit)
 if number=='105':
  did=stem+'-amount-dispute';fid=did+'-finding';text='2015/99 Temizlik İşleri komisyon raporunda 23.025.318,56 TL, 2015/105 kesin hesabında 26.772.318,56 TL yazıyor. Aritmetik fark 3.747.000 TL; hesap kapsamı ve nedeni açık.'
  new('finding',id=fid,party_id=party,heading='Belgelenmiş uygulamalar',text=text,pair_id=fid,provenance='summary',epistemic_type='claim');new('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='İki özgün sayfa görüntüsü ve aritmetik fark incelendi.')
  for pid in (prefix+'99-sum',stem+'-sum'):
   new('finding_evidence',finding_id=fid,passage_id=pid,role='support');new('verification',finding_id=fid,passage_id=pid,checked_at=when,result='confirmed',reason='İki kararın ilgili satırları görsel olarak okundu.')
  records['practice_dispute'].append(dict(id=did,event_id=eid,summary_finding_id=fid,supported_points='İki belge de 2014 Temizlik İşleri için ayrı toplam bildiriyor.',disputed_points='2015/99 raporu 23.025.318,56 TL, 2015/105 kesin hesap 26.772.318,56 TL yazıyor.',unresolved_points='3.747.000 TL aritmetik farkın nedeni, hesap kapsamları, muhasebe fişleri ve ödemeler açık.'))
  for pid,position,point in [(prefix+'99-sum','2015/99 komisyon raporu','Rapor 23.025.318,56 TL bildiriyor.'),(stem+'-sum','2015/105 kesin hesap','Kesin hesap 26.772.318,56 TL bildiriyor.')]:records['practice_dispute_evidence'].append(dict(dispute_id=did,passage_id=pid,point=point,source_position=position,role='conflict'))
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination:destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]);destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot);targets=practice_review_package_targets(snapshot,records,[e['values']['id'] for e in entries if e['kind']=='passage'],party);reviews=review['practice_source_review'];existing={(r['subject_kind'],r['subject_id']) for r in reviews}
for (kind,identity),(pids,owners) in sorted(targets.items()):
 if (kind,identity) in existing:continue
 assert party in owners;rows=[passages[p] for p in sorted(pids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({x['version_id'] for x in rows})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({x['section'] for x in rows})),supported_claim='Bağlar belediye kararının ilgili sayfaları okundu.',limitations='Komisyon beyanı, kurum ve parti ayrımı, tutar farkı, ödeme ve uygulama sınırları korundu.',result='reviewed',reason=kind+' / '+identity+' özgün kaynak ve işlem sınırları incelendi.'))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party);refs=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in reviews];package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('baglar-may-chains-draft.json',package),('baglar-may-chains-review-draft.json',review)]:
 path=here/name
 with path.open('x') as out:out.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print('MAY_CHAINS_SEMANTIC_PASS',len(records['practice_event']),len(records['practice_relation']),len(records['practice_dispute']))

