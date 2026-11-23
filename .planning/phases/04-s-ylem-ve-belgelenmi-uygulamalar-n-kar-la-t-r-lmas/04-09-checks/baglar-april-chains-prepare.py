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
aux=read(here/'baglar-april-chains-source-records.json')
party=aux['party_id']
package=read(here/'baglar-march-reports-v2-draft.json')
review=read(here/'baglar-march-reports-v2-review-draft.json')
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
        aid=f'baglar-april-chains-reading-{lane}-{topic}-{vid}'
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
assert sha256((here/'baglar-march-reports-v2-draft.json').read_bytes()).hexdigest()=='ed8ce1205c3ec0baac700d2be712402441814c4688972ba21d77f727a41aae8f'
assert sha256((here/'baglar-march-reports-v2-review-draft.json').read_bytes()).hexdigest()=='6af83d6895837fd2a34d45b78887e545163ed47c1a2b401065fea40f081988a4'
prefix='0409-baglar-april-chains-';election=['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limit='İşlem belediye meclisine aittir; YSK kaydı yalnız 2014 seçim bağlamını gösterir. Parti organı kararı ve kişisel oylar açık.'
cases=[
 ('46','2015-02-06','barinma-konut','Yapı kontrol çalışmalarının komisyona sevki','Bağlar Belediye Meclisi, Yapı Kontrol Müdürlüğünün kaçak yapılaşma çalışmalarının incelenmesi önergesini İmar ve Şehircilik Komisyonuna sevk etti.','2015/83 daha sonra kabul edilen komisyon raporu. Sevk, yıkımın veya ceza tahsilatının kanıtı değildir.',[('file','initiative','2015/46 sevk kararı.'),('topic','action','Yapı kontrol çalışmalarının incelenmesi.')]),
 ('61','2015-03-06','yerel-demokrasi','Sakarya Caddesindeki kadınların sorunları için sevk','Bağlar Belediye Meclisi, Sakarya Caddesindeki kadınların sorunları önergesini Kadın Sorunlarını Araştırma Komisyonuna sevk etti.','2015/84 sonraki rapor; sevk, hizmetlerin gerçekleştiğini göstermez.',[('file','initiative','2015/61 sevk kararı.'),('topic','action','Sakarya Caddesinde kadınların sorunlarının araştırılması.')]),
 ('66','2015-03-06','barinma-konut','4209 ada 4 parsel imar dosyasının komisyona sevki','Bağlar Belediye Meclisi, 4209 ada 4 parselin 1/1000 imar planı değişikliği dosyasını komisyona sevk etti.','Üst tarih 06/03/2015, sonuç satırı 06/03/2014; aynı belgede çelişki var. 2015/82 sonraki rapor; plan eki, yürürlük ve uygulama açık.',[('file','initiative','2015/66 sevk kararı.'),('date-head','initiative','Belgenin üst tarihi 6 Mart 2015.'),('date-end','initiative','Son satırda 6 Mart 2014 yazılı.'),('parcel','action','4209 ada 4 parsel plan dosyası.')]),
 ('82','2015-04-08','barinma-konut','4209 ada 4 parsel imar komisyon raporunun kabulü','Bağlar Belediye Meclisi, 4209 ada 4 parsel plan notları hakkında İmar ve Şehircilik Komisyonu raporunu kabul etti.','2015/66 önceki sevk; komisyon raporu iki plan notu değişikliği talebini aktarıyor. Plan eki, askı, yürürlük ve yapı uygulaması açık.',[('file','initiative','2015/82 rapor kararı.'),('request','action','Aynı 4209 ada 4 parsel talebi.'),('plan','action','Komisyonun plan notlarına ilişkin değerlendirmesi.'),('approved','result','Raporun mecliste kabulü.')]),
 ('83','2015-04-09','barinma-konut','Yapı kontrol çalışmalarına ilişkin komisyon raporu','Bağlar Belediye Meclisi, Yapı Kontrol Müdürlüğünün 2014 çalışmaları hakkındaki İmar ve Şehircilik Komisyonu raporunu kabul etti.','2015/46 önceki sevk. Komisyon 42 mühürleme, 3 uygunlaştırma, 10 yıkım kararı, 2 gerçekleşmiş yıkım ve 1.353.551,71 TL kesilen ceza bildiriyor. İlk tutanaklar ve tahsilat açık.',[('file','initiative','2015/83 rapor kararı.'),('period','action','Komisyon 30 Mart–31 Aralık 2014 dönemini aktardı.'),('demolition','action','Komisyon iki yıkım gerçekleştiğini bildirdi.'),('fine','action','Komisyon ceza kesildiğini bildirdi; tahsilat değil.'),('approved','result','Raporun mecliste kabulü.')]),
 ('84','2015-04-09','yerel-demokrasi','Sakarya Caddesi kadın görüşmeleri raporunun kabulü','Bağlar Belediye Meclisi, Sakarya Caddesinde kadınlarla görüşmelere ilişkin Kadın Sorunlarını Araştırma Komisyonu raporunu kabul etti.','2015/61 önceki sevk. Rapor tuvalet ve sokak işgali hakkında kadınların beyanlarını aktarıyor; görüşme sayısı ve hizmet sonucu açık.',[('file','initiative','2015/84 rapor kararı.'),('request','action','Görüşülen kadınların hijyenik tuvalet talebi.'),('approved','result','Raporun mecliste kabulü.')]),
 ('81','2015-04-08','kamu-hesap-verebilirlik','Halfeti parkı için yardım kararı ve oylama kaydı','Bağlar Belediye Meclisi kararında Halfeti Belediyesi Amara Parkı için 10.000 TL yardımın kabulü yazıyor; aynı cümlede ret ve oybirliği ifadeleri birlikte geçiyor.','Karar metni oy ifadesinde kendi içinde çelişkili. Tek yönlü oy dağılımı, ödeme, transfer ve parkın yapımı açık.',[('file','initiative','2015/81 yardım kararı.'),('amount','action','Kararda 10.000 TL yardım konusu.'),('conflict','result','Aynı cümlede ret ve oybirliği ile kabul ifadeleri.')])]
for number,day,topic,title,context,detail,anchors in cases:
 stem=prefix+number;limit=detail+' '+context_limit;ev=[(stem+'-'+label,stage,'document',point) for label,stage,point in anchors]
 prior={'82':'66','83':'46','84':'61'}.get(number)
 if prior:ev.append((prefix+prior+'-file','initiative','document','Önceki 2015/'+prior+' komisyon sevki.'))
 eid=event(stem,day,title,context,ev,limit);records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2015-'+number
 pids=[x[0] for x in ev];scope=readings(topic,'event',pids+election);reason=detail+' Önceleyen aynı kapsamlı tarihli parti hedefi araştırılıyor.';cid=stem+'-unmatched'
 records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)));task('practice_candidate',cid,reason,limit)
 if number=='81':
  did=stem+'-vote-dispute';fid=did+'-finding';text='2015/81 yardım kararında Sedat Gültekin’in reddi ile mevcudun oybirliği ifadesi aynı cümlede yer alır; oylama tutanağı ve ödeme kaydı açıktır.'
  new('finding',id=fid,party_id=party,heading='Belgelenmiş uygulamalar',text=text,pair_id=fid,provenance='summary',epistemic_type='claim');new('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Kararın özgün sayfası görsel ve metin katmanıyla incelendi.')
  for pid in (stem+'-reject',stem+'-unanimous'):
   new('finding_evidence',finding_id=fid,passage_id=pid,role='support');new('verification',finding_id=fid,passage_id=pid,checked_at=when,result='confirmed',reason='Aynı karar cümlesi görsel okundu.')
  records['practice_dispute'].append(dict(id=did,event_id=eid,summary_finding_id=fid,supported_points='Karar metni yardımın kabul edildiğini ifade ediyor.',disputed_points='Ret beyanı ile mevcudun oybirliği ifadesi aynı cümlede yer alıyor.',unresolved_points='Oylama tutanağı, kesin oy dağılımı ve ödeme kaydı açık.'))
  for label,role,point in [('reject','conflict','Metin bir üyenin reddini yazıyor.'),('unanimous','support','Aynı cümle mevcudun oybirliğiyle kabul ifadesini içeriyor.')]:
   pid=stem+'-'+label;records['practice_dispute_evidence'].append(dict(dispute_id=did,passage_id=pid,point=point,source_position='2015/81 kararının aynı cümlesi.',role=role))
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination:destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]);destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[e['values']['id'] for e in entries if e['kind']=='passage'],party);reviews=review['practice_source_review'];existing={(r['subject_kind'],r['subject_id']) for r in reviews}
for (kind,identity),(pids,owners) in sorted(targets.items()):
 if (kind,identity) in existing:continue
 assert party in owners;rows=[passages[p] for p in sorted(pids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({x['version_id'] for x in rows})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({x['section'] for x in rows})),supported_claim='Bağlar belediye kararı özgün sayfası okundu.',limitations='Komisyonun aktardığı olgular, oy çelişkisi, hizmet, ödeme ve parti-kurum sınırları ayrı tutuldu.',result='reviewed',reason=kind+' / '+identity+' özgün karar ve işlem sınırları incelendi.'))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party);refs=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in reviews];package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('baglar-april-chains-draft.json',package),('baglar-april-chains-review-draft.json',review)]:
 path=here/name
 with path.open('x') as out:out.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print('APRIL_CHAINS_SEMANTIC_PASS',len(records['practice_event']),len(records['practice_relation']))
