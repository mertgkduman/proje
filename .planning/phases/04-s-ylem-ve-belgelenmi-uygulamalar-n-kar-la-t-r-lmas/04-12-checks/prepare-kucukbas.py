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
aux=read(here/'kucukbas-v2-source-records.json')
party=aux['party_id']
package=read(here/'framework-7595-draft.json')
review=read(here/'framework-7595-review-draft.json')
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
def finding(id,body,refs,reason,pair=None):
    new('finding',id=id,party_id=party,heading='Belgelenmiş uygulamalar',text=body,pair_id=pair or id,
        provenance='quote' if pair else 'summary',epistemic_type='claim')
    for pid in refs:
        new('finding_evidence',finding_id=id,passage_id=pid,role='support')
        new('verification',finding_id=id,passage_id=pid,checked_at=when,result='confirmed',reason=reason)
    new('review',id='review-'+id,kind='finding',subject_id=id,reviewer_kind='agent',
        reviewed_at=when,result='reviewed',reason=reason)
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Küçükbaş destek projesi, parti eleştirisi, başvuru ve teslim kayıtları okundu.'))
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
        aid=f'kucukbas-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Küçükbaş projesi ve parti açıklaması.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((here/'framework-7595-draft.json').read_bytes()).hexdigest()=='be1d7bcba72ce25c35cc28ac7cbd412b39c2884fbecdfab4ce297d8266e4dbe3'
assert sha256((here/'framework-7595-review-draft.json').read_bytes()).hexdigest()=='e9cb5b948ca843250fba1b2194f8a7a7f62bd484c23bff6eaf66504685f0cde8'
topic='hayvancilik'
stem='0412-kucukbas-2026'
src='0412-kucukbas-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
goal='Gültekin Uysal 23 Şubat’ta küçükbaş dağıtımına ilişkin maliyet eleştirisi yaptı. Yem bitkisi üretiminin artmasını, girdi maliyetlerinin düşmesini ve ithalatın istisna olmasını istedi.'
statement_limit='Fiyat, maliyet payı ve ithalat hakkındaki açıklamalar Demokrat Parti’ye ait. Programın tamamı ve üretim üzerindeki etkisi açık.'
statement_pids=[src+'statement-day',src+'statement-target',src+'statement-critique']
finding(target,goal,statement_pids,'Parti yayınının tarihi, konuşmacısı ve programla ilgili talebi okundu.')
finding(quote,passages[src+'statement-quote']['exact'],[src+'statement-quote'],'Açıklamadaki kısa özgün ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-02-23',date_precision='day',
    version_id=passages[src+'statement-target']['version_id'],period_basis='23 Şubat 2026 Demokrat Parti Basın Merkezi açıklaması.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0313-demokrat-hayvancilik'))
readings(topic,'statement',statement_pids+[src+'statement-quote'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'statement-quote']['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('apply','tob-kucukbas-2026-04-01-basvuru','2026-04-01','Küçükbaş destek projesi başvurularının açılması',
     'Tarım ve Orman Bakanlığı 1 Nisan’da küçükbaş projesi başvurularının açıldığını ve 30 Nisan’da kapanacağını duyurdu.',
     '21 Şubat ve 1 Nisan tarihli Bakanlık duyuruları ve altı sayfalık uygulama talimatı.',
     'Proje 21 Şubat’ta duyuruldu, Uysal 23 Şubat’ta açıkladı, başvuru 1 Nisan’da başladı.',
     'Başvuru aşamasını Tarım ve Orman Bakanlığı yürütüyor. DP’nin rolü kamuya açık tutum.',
     '150 bin hayvan üç yıllık hedef. Bakım desteği, kredi ve bedel ödeme usulü talimatta. Başvuru aşamasında kişisel ödeme veya teslim kaydı açık.',
     'Başvuruların 1–30 Nisan’da yapılacağı ilan edildi. 100 hayvana üç ayda 45 bin TL bakım desteği, hayvan bedeli ve kredi ayrı koşullara bağlı.',
     'Uysal’ın hayvan dağıtımı ve girdi maliyeti eleştirisi, programın başvuru koşulları ve açıklanan bakım desteğiyle karşılaştırıldı.',
     (
         ('launch-day','initiative','Bakanlık projeyi 21 Şubat 2026’da duyurdu.'),
         ('launch-target','initiative','Üç yıllık hedef 150 bin küçükbaş.'),
         ('apply-opened','action','Bakanlık başvuruların açıldığını duyurdu.'),
         ('apply-day','result','Başvuru 1–30 Nisan 2026 için açıldı.'),
         ('apply-planned','result','100 hayvanlık işletme için üç aylık 45 bin TL bakım desteği açıklandı.'),
         ('instructions-window','result','Uygulama talimatı başvuru günlerini 1–30 Nisan olarak belirtiyor.'),
         ('instructions-price','result','Talimata göre hayvan bedeli peşin veya krediyle ödenebiliyor.'),
         ('instructions-actual','result','Talimatta fiilî hayvan sayısına dayalı 150 TL aylık bakım hesabı var.'),
     )),
    ('first','tob-kucukbas-2026-06-11-ilk-sonuc','2026-06-11','Küçükbaş projesinin ilk etap hak sahipliği duyurusu',
     'Tarım ve Orman Bakanlığı 11 Haziran’da ilk etap sonuçlarını açıkladı ve il bazında listelerin oluşturulduğunu bildirdi.',
     '11 Haziran Bakanlık sonuç duyurusu ve uygulama talimatının değerlendirme bölümü.',
     'İlk aşama Nisan başvurularını ve itiraz düzeltmelerini izledi.',
     'Hak sahipliğini Bakanlık ve TİGEM belirliyor. DP süreci eleştiren taraf.',
     'SMS bildirimi ve hak sahipliği listesi doğrulandı. Alım, teslim ve ödenen bakım desteği ayrı işlemler.',
     'Bakanlık illerde asil ve yedek listelerin oluşturulduğunu ve geçerli başvuru sahiplerine SMS gönderildiğini bildirdi.',
     '23 Şubat eleştirisinin konusu olan programda ilk etap idari sonucu kayda geçti. Ulusal üretim ve girdi maliyetlerinin etkisi ayrı inceleme gerektiriyor.',
     (
         ('instructions-scores','initiative','Uygulama talimatı il bazında puan sıralamasını öngörüyor.'),
         ('first-day','action','Bakanlık ilk etap sonucunu 11 Haziran’da yayımladı.'),
         ('first-list','result','İl bazında asil ve yedek listeler oluşturuldu.'),
         ('first-sms','result','Geçerli başvuru sahiplerine SMS gönderildiği bildirildi.'),
     )),
    ('duzce','tob-kucukbas-2026-09-16-duzce-bildirim','2026-09-16','Düzce’de bildirilen küçükbaş hayvan teslimi',
     'Düzce İl Tarım ve Orman Müdürlüğü 16 Eylül tarihli yayınında Gümüşova Halilbey’de bir işletmeye 100 küçükbaş teslim edildiğini bildirdi.',
     'Düzce İl Müdürlüğünün tarihli açıklaması, hayvan sayısı ve yerinde inceleme kaydı.',
     '16 Eylül kaynak yayımı. Hayvanların fiilî teslim günü ayrıca yazılmamış.',
     'Teslim ve incelemeyi il müdürlüğü kendi kurumsal yayınında bildiriyor. DP’nin rolü programla ilgili kamuya açık tutum.',
     'Teslimin kesin günü, hayvan bedeline ilişkin işlemler, bakım ödemesi ve üretim etkisi açık.',
     'İl Müdürlüğü Halilbey’de bir işletmeye 95 dişi ve 5 erkek olmak üzere 100 küçükbaş teslimi bildirdi.',
     'Düzce’de bildirilen teslim, 23 Şubat açıklamasının konusu olan projenin yerel gerçekleşme kaydı. Girdi maliyetleri ve yem üretimi üzerindeki etki açık.',
     (
         ('duzce-day','action','İl Müdürlüğü bildirimi 16 Eylül 2026 tarihli.'),
         ('duzce-visit','action','İl Müdürünün işletmede teslim edilen hayvanları incelediği bildirildi.'),
         ('duzce-delivery','result','Gümüşova Halilbey’de bir işletmeye 100 hayvan teslim edildiği bildirildi.'),
     )),
    ('yozgat','tob-kucukbas-2026-09-24-yozgat-bildirim','2026-09-24','Yozgat’ta hak sahipliği ve küçükbaş teslimlerinin bildirimi',
     'Yozgat İl Tarım ve Orman Müdürlüğü 24 Eylül tarihli yayında başvuru, asil ve yedek durumunu ve beş yetiştiriciye teslimi bildirdi.',
     'Yozgat İl Müdürlüğünün tarihli yerel uygulama ve teslim açıklaması.',
     '24 Eylül yayın günü. Açıklama o güne kadar bildirilen teslimleri kapsıyor.',
     'İl Müdürlüğü sonuçları bildiriyor. Açıklamada TİGEM işletmeleri teslim sürecinin parçası.',
     'Teslim günleri, bakım desteğinin ödenmesi ve ulusal dağıtım açık. Asil ve yedek listeler kendi nitelikleriyle ayrı.',
     'İl Müdürlüğü 2.381 başvuru, 14 asil ve 42 yedek sonuç ile dört ilçedeki beş yetiştiriciye teslim bildirdi.',
     'Yozgat teslimleri aynı projenin yerel uygulamasına örnek. Uysal’ın yem üretimi ve girdi maliyeti talebinin etkisi için ek veri açık.',
     (
         ('yozgat-day','action','İl Müdürlüğü bildirim günü 24 Eylül 2026.'),
         ('yozgat-applications','result','Yozgat’ta 2.381 başvuru bildirildi.'),
         ('yozgat-roster','result','İlk etap listesinde 14 asil ve 42 yedek ayrı.'),
         ('yozgat-reported','result','Yozgat açıklaması Çandır’da iki, Boğazlıyan, Sorgun ve Merkez’de birer yetiştiriciye teslim bildiriyor.'),
     )),
)
for label,key,day,title,context,basis,time,specific_authority,detail,observed,compare,anchors in events:
    event_stem=stem+'-'+label
    limit=detail+' '+statement_limit
    evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[row[0] for row in evidence]
    scope=readings(topic,'event',pids)
    rid,result,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result,observed,pids,basis)
    finding(explanation,compare+' '+limit,statement_pids+pids,limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result,explanation_finding_id=explanation,temporal_context=time,
        authority_context=specific_authority,uncertainty_reason=limit))
    candidate=event_stem+'-candidate'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (
        ('practice_relation',compare),('practice_relation.target_finding_id',goal),
        ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
    ):
        task(kind,rid,claim,limit)

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
for name,content in [('kucukbas-v2-draft.json',package),('kucukbas-v2-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
