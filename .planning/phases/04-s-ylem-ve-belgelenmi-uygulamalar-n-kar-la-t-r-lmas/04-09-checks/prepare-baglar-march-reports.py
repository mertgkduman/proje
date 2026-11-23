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
aux=read(here/'baglar-march-reports-source-records.json')
party=aux['party_id']
package=read(here/'baglar-february-draft.json')
review=read(here/'baglar-february-review-draft.json')
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
        aid=f'baglar-march-reports-reading-{lane}-{topic}-{vid}'
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
prefix='0409-baglar-march-reports-'
electoral_context=['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limits=('YSK kaydı yönetimin 2014 seçim bağlamını veriyor. '
                'Meclisin işlemi belediyeye ait. Parti organına ait aynı kapsamlı karar veya kişisel oy açık.')
events=(
    ('42','2015-02-05','yerel-demokrasi','Fatih Mahallesi başvurusunun komisyona sevki',
     'Bağlar Belediye Meclisi, Fatih Mahallesi sakinlerinin sorunlarına ilişkin önergeyi Halkla İlişkiler Komisyonuna sevk etti.',
     '2015/56 raporun kabul edildiği sonraki işlem. Sevk günü hizmet emri ve teslim açık.',
     (('step','action','Fatih Mahallesi hakkında Halime Bayram ve Selam Taş’ın önergesi komisyona sevk edildi.'),),None),
    ('43','2015-02-06','tuketici-haklari','Kaynartepe fırınları önergesinin komisyona sevki',
     'Bağlar Belediye Meclisi, Kaynartepe’de fırınların denetlenmesi önergesini Çevre ve Sağlık Komisyonuna sevk etti.',
     '2015/57 rapor kararı daha sonraki işlem. Sevkin kendi gününde işyeri denetimleri raporlanmadı.',
     (('step','action','Kaynartepe fırınlarının denetlenmesi için Nevriye Çur ve Nasır Yentar’ın önergesi görüşüldü.'),),None),
    ('51','2015-03-04','kamu-hesap-verebilirlik','Bağlar Fen İşleri 2014 harcama raporunun kabulü',
     'Bağlar Belediye Meclisi, Fen İşleri Müdürlüğünün 2014 yılı harcama raporunu 4 Mart’ta kabul etti.',
     'Bütçe 18.420.000 TL. 22 satır 14.060.244,50 TL. Rapor 4.359.755,50 TL iade bildiriyor. Muhasebe fişleri ve ödemeler araştırmaya açık.',
     (('budget','action','Plan ve Bütçe Komisyonu 2014 dönemi için 18.420.000 TL ödenek bildirdi.'),
      ('spending','action','Raporda 14.060.244,50 TL harcama ve 4.359.755,50 TL iade yazıyor.'),
      ('approved','result','4 Mart’ta Fen İşleri harcamaları raporu oybirliğiyle kabul edildi.')),('26-referral','2015/26 önceki Fen İşleri komisyon sevki.')),
    ('52','2015-03-04','kadin-istihdami','Kadın belediye çalışanları hakkında komisyon raporu',
     'Bağlar Belediye Meclisi, Kültür ve Sosyal İşler Müdürlüğündeki kadın çalışanların sorunları hakkında hazırlanan raporu kabul etti.',
     'Rapora kız öğrencilere sağlık ve psikoloji eğitimi önerisi geçti. Program, katılım ve belediye çalışanlarının çalışma koşullarında değişiklik açık.',
     (('proposal','action','Kadın eğitimciler kız öğrencilere sağlık ve psikoloji eğitimi verilmesini önerdi.'),
      ('approved','result','Kadın Sorunlarını Araştırma Komisyonu raporu 4 Mart’ta kabul edildi.')),('29-referral','2015/29 kadın belediye çalışanları başvurusunun sevki.')),
    ('54','2015-03-04','ayrimcilik-cogulculuk','Bağlar ana hizmet binasında cinsiyet eşitliği raporu',
     'Bağlar Belediye Meclisi, ana hizmet binasındaki çalışanlarla görüşmeleri aktaran cinsiyet eşitliği raporunu kabul etti.',
     'Görüşülen kadınların ev ve çocuk bakımı anlatımları ile sosyal etkinlik önerisi raporda. Görüşülen kişi sayısı ve sonraki uygulama açık.',
     (('reported','action','Görüşülen kadınlar ev ve çocuk bakımı nedeniyle sosyal etkinliğe katılamadıklarını aktardı.'),
      ('proposal','action','Görüşülen çalışanlar kurum içinde sosyal etkinlik önerdi.'),
      ('approved','result','Kadın-Erkek Eşitlik Komisyonu raporu 4 Mart’ta kabul edildi.')),('31-referral','2015/31 ana hizmet binası eşitlik çalışması için komisyon sevki.')),
    ('56','2015-03-05','yerel-demokrasi','Fatih Mahallesi hizmet talepleri raporunun kabulü',
     'Bağlar Belediye Meclisi, Fatih Mahallesi’ndeki konteyner ve kaldırımlara ilişkin talepleri içeren komisyon raporunu kabul etti.',
     'Konteyner temini ve kaldırımların işgalden arındırılması için iş emri, uygulama ve teslim açık.',
     (('service','action','Fatih Mahallesi sakinleri konteyner ve kaldırım işgalinin giderilmesini istedi.'),
      ('approved','result','Halkla İlişkiler Komisyonu raporu 5 Mart’ta kabul edildi.')),('42-step','2015/42 Fatih Mahallesi sorunları komisyona sevk edilmişti.')),
    ('57','2015-03-05','tuketici-haklari','Kaynartepe fırın denetimleri raporunun kabulü',
     'Bağlar Belediye Meclisi, Kaynartepe’de 17 fırın hakkında tespitler içeren Çevre ve Sağlık Komisyonu raporunu kabul etti.',
     'Raporda 17 fırın hakkında altı uyarı, iki idari yaptırım tutanağı, bir eksik gramaj işlemi ve sekiz normal temizlik tespiti var. Denetim formları, ceza tutarı ve tahsilat açık.',
     (('inspection','action','Komisyon Kaynartepe fırınlarındaki incelemeyi raporladı.'),
      ('fine','action','Komisyon raporunda eksik gramaj nedeniyle işlem yapıldığı yazıyor.'),
      ('warning','action','Komisyon raporunda temizlik yetersizliği nedeniyle uyarı örneği var.'),
      ('administrative','action','Komisyon idari yaptırım tutanağı düzenlendiğini aktardı.'),
      ('approved','result','Çevre ve Sağlık Komisyonu raporu 5 Mart’ta kabul edildi.')),('43-step','2015/43 Kaynartepe fırın denetiminin önceki komisyon sevki.')),
    ('58','2015-03-05','esnaf-kobi','Sakarya Caddesi esnafı hakkındaki raporun kabulü',
     'Bağlar Belediye Meclisi, Sakarya Caddesi esnafının trafik, onarım, aydınlatma ve işgal konularındaki taleplerini içeren komisyon raporunu kabul etti.',
     '2015/47’de iki komisyona sevk yapıldı. Bu rapor İnceleme ve Araştırma Komisyonuna ait. Diğer rapor ve hizmetlerin gerçekleşmesi açık.',
     (('transit','action','Sakarya Caddesi esnafı taşıt giriş çıkışının önlenmesini istedi.'),
      ('light','action','Sakarya Caddesi esnafı akşam aydınlatması istedi.'),
      ('approved','result','İnceleme ve Araştırma Komisyonu raporu 5 Mart’ta kabul edildi.')),('47-referral','2015/47 Sakarya Caddesi esnafı hakkında iki komisyona sevk.')),
)
for number,day,topic,title,context,detail,anchors,prior in events:
    stem=prefix+number
    limit=detail+' '+context_limits
    evidence=[(stem+'-file','initiative','document',f'Bağlar Belediye Meclisi 2015/{number} dosyası.'),
              (stem+'-date','initiative','document',f'Meclis kararının tutanaktaki günü {day}.')]
    if prior:
        evidence.append((prefix+prior[0],'initiative','document',prior[1]))
    evidence.extend((stem+'-'+label,stage,'document',claim) for label,stage,claim in anchors)
    eid=event(stem,day,title,context,evidence,limit)
    record=records['practice_event'][-1]
    record['common_event_key']='baglar-belediye-meclisi-2015-'+number
    pids=[r[0] for r in evidence]
    scope=readings(topic,'event',pids+electoral_context)
    reason=detail+' Daha önceki aynı kapsamlı tarihli parti hedefi araştırılıyor.'
    candidate=stem+'-unmatched'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
        relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
    task('practice_candidate',candidate,reason,limit)

for number,focus in (
    ('49','2015/49 belediye kredi yetkisi'),
    ('99','2015/99 Temizlik İşleri harcama raporu'),
    ('161','2015/161 belediye kredi yetkisi'),
):
    prior_id=f'0409-baglar-2015-{number}-unmatched'
    existing=next(row for row in records['practice_candidate'] if row['id']==prior_id)
    exclusion=f'{focus} belediye bütçesi ve meclisine ait. Partinin tüzükteki yerel örgüt hesabı ve kendi bütçe kapsamı dışlandı.'
    revision=prior_id+'-public-finance-scope'
    records['practice_candidate_revision'].append(dict(id=revision,candidate_id=prior_id,recorded_at=when,
        event_id=existing['event_id'],relation_id=None,state='excluded',reason=exclusion,passage_ids=existing['passage_ids']))
    pids=json.loads(existing['passage_ids'])
    scope=readings('kamu-hesap-verebilirlik','event',pids+electoral_context)
    updated=prefix+number+'-public-finance'
    reason=f'{focus} kamusal hesap verebilirlik kapsamında incelendi. '+existing['reason']
    records['practice_candidate'].append(dict(id=updated,scope_id=scope,event_id=existing['event_id'],
        relation_id=None,state='unmatched',reason=reason,passage_ids=existing['passage_ids']))
    task('practice_candidate',updated,reason,context_limits)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot, records, [entry['values']['id'] for entry in entries if entry['kind']=='passage'], party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak metni, tarihi ve iddia sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('baglar-march-reports-v2-draft.json',package),('baglar-march-reports-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
