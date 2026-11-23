"""Record seven local employment, social, education and sports decisions."""

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
aux=read(here/'baglar-february-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
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
        aid=f'baglar-february-reading-{lane}-{topic}-{vid}'
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
assert party == 'dbp'
electoral_context = ['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limits = ('YSK kaydı yönetimin 2014 seçim bağlamını veriyor. '
                  'İşlem belediye meclisine ait. Parti adına bağımsız bir karar veya kişisel oy açık.')
events = (
    ('32','2015-02-03','sosyal-hizmet','Bağlar’da glutensiz gıda desteği kararı',
     'Bağlar Belediye Meclisi 40 çölyak hastası için altı ay glutensiz gıda desteğini kabul etti.',
     'Yardımın satın alma ve teslim belgeleri ile desteğin gerçekleşen süresi açık.',
     (('action','action','Kararda 40 kişi için altı aylık glutensiz gıda desteği öngörülüyor.'),
      ('approved','result','Meclis 3 Şubat’ta yardım kararını oybirliğiyle kabul etti.'))),
    ('35','2015-02-04','yerel-demokrasi','5 Nisan Mahallesi sakinlerinin hizmet talepleri',
     'Halkla İlişkiler Komisyonu 5 Nisan Mahallesi’nin konteyner, kaldırım ve yol bakım taleplerini meclise aktardı.',
     '9 Ocak 2015/27 sevki bu mahalledeki taleplerin dinlenmesiyle ilgili. İş emri, harcama ve tamamlanma kaydı açık.',
     (('action','action','Komisyon, 5 Nisan sakinlerinin çöp konteyneri ve bakım taleplerini kaydetti.'),
      ('approved','result','Meclis komisyon raporunu 4 Şubat’ta kabul etti.'))),
    ('36','2015-02-04','egitime-erisim','Bağlar ve Halk Eğitim ortak kurs raporu',
     'Bağlar Belediye Meclisi, Halk Eğitim Merkezi ile üç belediye merkezindeki kursları inceleyen raporu kabul etti.',
     'Rapor Eğitim Destek Evi için 16 bilgisayar, 16 halk oyunları ve 15 resim katılımcısı bildiriyor. Protokol aslı, ödemeler ve kurs bitirme sayıları açık.',
     (('action','action','Rapor Eğitim Destek Evi, Kardelen Kadın Evi ve 5 Nisan Mahalle Evi için protokol uygulamasını aktardı.'),
      ('centers','action','Eğitim Destek Evi için 16 bilgisayar, 16 halk oyunları ve 15 resim katılımcısı raporlandı.'),
      ('approved','result','Meclis ortak kurs raporunu 4 Şubat’ta kabul etti.'))),
    ('37','2015-02-04','yerel-demokrasi','5 Nisan pazarları hakkında çevre ve sağlık raporu',
     'Bağlar Belediye Meclisi, üç semt pazarı hakkındaki Çevre ve Sağlık Komisyonu raporunu kabul etti.',
     'Komisyon cuma pazarının kaldırılmaması talebini ve gıda hijyeni kaygılarını aktardı. Pazarın statüsü ve zabıta sonucu açık.',
     (('action','action','Komisyon sakinlerin cuma pazarının kaldırılmasını istemediklerini bildirdi.'),
      ('hygiene','action','Gıda hijyeni kaygıları pazar kullanıcılarının aktardığı görüşler arasında.'),
      ('approved','result','Meclis Çevre ve Sağlık Komisyonu raporunu 4 Şubat’ta kabul etti.'))),
    ('39','2015-02-05','yerel-demokrasi','5 Nisan pazarları hakkında ikinci komisyon raporu',
     'Bağlar Belediye Meclisi, aynı pazar başvurusu hakkında İnceleme ve Araştırma Komisyonunun raporunu kabul etti.',
     '2015/37 kararı ayrı komisyona ait. Taşıt sınırlaması, araç çekicisi ve pazar statüsüne yönelik uygulama açık.',
     (('action','action','Rapor büyük kamyonlar yerine küçük kamyonetlerle ürün getirilmesini önerdi.'),
      ('towing','action','Raporda araç çekicisi istendiği belirtiliyor.'),
      ('approved','result','Meclis bu ayrı raporu 5 Şubat’ta kabul etti.'))),
    ('40','2015-02-05','yerel-demokrasi','Suruç Belediyesine çöp aracı hibe kararı',
     'Bağlar Belediye Meclisi, Suruç Belediyesinin hizmet talebi üzerine bir çöp toplama aracının hibesini kabul etti.',
     'Aracın teslim tutanağı ve Suruç Belediyesinin kullanım kaydı araştırılıyor.',
     (('action','action','Suruç Belediyesinin çevre temizliği aracı talebi ve hibe önerisi mecliste görüşüldü.'),
      ('approved','result','Meclis 5 Şubat’ta bir aracın hibesini oybirliğiyle kabul etti.'))),
    ('41','2015-02-05','gocmen-multeci','Yenişehir mülteci çadırlarının elektriği için yetki',
     'Bağlar Belediye Meclisi, Yenişehir Karayolları Fidanlığındaki mülteci çadırlarının elektrik giderleri ve yardımlar için belediye başkanına yetki verdi.',
     'Karar iki elektrik aboneliğini kapsıyor. Ödeme makbuzu, yardımların teslimi ve gerçekleşen tutar açık.',
     (('action','action','Görüşme Yenişehir’deki mülteci çadırlarının elektrik aboneliği giderlerine ilişkin.'),
      ('authority','action','Meclis belediye başkanı Birsen Kaya Akat’a yetki verilmesini görüştü.'),
      ('approved','result','Meclis 5 Şubat’ta yetkiyi oybirliğiyle kabul etti.'))),
)
for number,day,topic,title,context,detail,anchors in events:
    stem='0409-baglar-february-'+number
    limit=detail+' '+context_limits
    evidence=[(stem+'-file','initiative','document',f'Bağlar Belediye Meclisi 2015/{number} dosyası.'),
              (stem+'-date','initiative','document',f'Meclis kararının tutanaktaki günü {day}.')]
    evidence.extend((stem+'-'+label,stage,'document',claim) for label,stage,claim in anchors)
    eid=event(stem,day,title,context,evidence,limit)
    records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2015-'+number
    pids=[r[0] for r in evidence]
    scope=readings(topic,'event',pids+electoral_context)
    reason=detail+' Daha önceki aynı kapsamlı tarihli parti hedefi araştırılıyor.'
    candidate=stem+'-unmatched'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
        relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
    task('practice_candidate',candidate,reason,limit)

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
for name,content in [('baglar-february-draft.json',package),('baglar-february-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
