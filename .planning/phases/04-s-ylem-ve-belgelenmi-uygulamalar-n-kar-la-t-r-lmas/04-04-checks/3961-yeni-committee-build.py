import json, hashlib, sys, shutil
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

c=Path(__file__).parent
root=Path('/work/mg551/gsd-phase04-recovery.L0IReu/yeni-3961-source')
base=Path('data/practices/04-yeni-parti.json'); rev=Path('data/practices/04-yeni-parti-review.json')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
assert sha(base.read_bytes())=='e0e68011435a15b591d9481fe71a84bb7cfd34b4c779d71d0d5378c05797a165'
if not root.exists(): shutil.copytree('data/practices/sources/yeni-parti',root)
p=json.loads(base.read_bytes()); r=json.loads(rev.read_bytes()); now=datetime.now(timezone.utc).isoformat()
q=lambda s:'0404-3961-yeni-committee-'+s
add=lambda k,v:p['entries'].append({'kind':k,'values':v})
new={k:[] for k in p['practice_records']}
sources={
 'anka':(c/'3961-yeni-committee-anka-original.html','https://ankahaber.net/haber/yeni-parti-il-baskanlari-toplantisi-ozgur-ozel-yeni-parti-turk-askerini-yemen-collerine-gondermeye-asla-destek-olmaz-baad0a52','2026-10-27','journalism','ANKA Haber Ajansı','2026-11-26T05:10:37.675600+00:00'),
 'sozcu':(c/'3961-yeni-committee-members-original.html','https://www.sozcu.com.tr/husiler-somali-de-mehmetcik-e-tehdit-p375390','2026-11-03','journalism','Sözcü','2026-11-26T05:07:08.619126+00:00'),
 'report':(Path('data/practices/sources/dem/objects/0d813e029374bdeb9274911cbb8f04ffd33facbd68b8edb887ce650b017d9e98/original.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/DosyaKomisyonRaporunuVerdi/cd70ebe9-711b-42fe-8baf-896ee6b8eb29.pdf','2026-10-30','official','TBMM','2026-11-22T04:43:26.806427+00:00')}
for k,(f,url,day,kind,publisher,accessed) in sources.items():
 raw=f.read_bytes();digest=sha(raw); media='pdf' if k=='report' else 'html'; folder=Path('objects')/digest; original=folder/('original.pdf' if media=='pdf' else 'original.html.bin'); readable=folder/'readable.html'
 for path,data in [(original,raw),(readable,readable_bytes(raw,media,legacy=False))]:
  z=root/path;z.parent.mkdir(parents=True,exist_ok=True)
  if z.exists():assert z.read_bytes()==data
  else:z.write_bytes(data)
 doc=q(k);version=doc+'-v1';add('document',dict(id=doc,party_id='yeni-parti',title={'anka':'27 Ekim Yeni Parti il başkanları toplantısı','sozcu':'3 Kasım şerh haberi','report':'2/3961 sıra 295 Dışişleri Komisyonu raporu'}[k],source_kind=kind))
 add('document_version',dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='Özgün kaynak',accessed_at=accessed,verified_at=now,mime='application/pdf' if media=='pdf' else 'text/html',sha256=digest,original_path=str(original),readable_path=str(readable)))
 add('source_attribution',dict(version_id=version,kind=kind,publisher=publisher,author=None,social_handle=None,published_at=day,date_precision='day',public_url=url,basis='Tarih, yayıncı ve metin kaynak üzerinde incelendi.'))
 if media=='html':
  view=build_view(raw,url,root,fetch_assets=False);validate_view(root,view);add('archive_view',dict(view,version_id=version))

passages={
 'statement':('anka',None,None,'Türk askerini Yemen çöllerine göndermeye YENİ Parti asla sessiz kalmaz, asla destek olmaz.','Genel başkanın açıklaması'),
 'authority':('anka',None,None,"YENİ Parti Genel Başkanı Özgür Özel, TBMM Dışişleri Komisyonu'nda görüşülen Mekke Ortak Savunma Anlaşması",'Genel başkan sıfatı ve aynı teklif'),
 'news':('sozcu',None,None,'YENİ Parti Eskişehir Milletvekili Utku Çakırözer ve Düzce Milletvekili Talih Özcan, kanun teklifine yazdıkları muhalefet şerhinde','Şerhin iki milletvekili'),
 'signed':('report',25,'26','28.10.2026','Şerhin kendi tarihi ve basılı adların bulunduğu sayfa'),
 'identity':('report',23,'24','Bizler TBMM Dışişleri Komisyonu’nun Yeni Parti’ye mensup temsilcileri olarak','İki üyenin parti sıfatı ve görevini bildiren şerh'),
}
for k,(source,page,printed,exact,label) in passages.items():
 raw=sources[source][0].read_bytes();text=html_source_text(raw) if page is None else pdf_page_text(sources[source][0],page)
 if k!='identity':assert exact in text,(k,exact)
 add('passage',dict(id=q(k),version_id=q(source)+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=label,pdf_page_index=page,printed_page=printed))
 if k=='identity':add('manual_passage',dict(passage_id=q(k),checked_at=now,method='Özgün PDF 23. indeks sayfası Poppler/Cairo görüntüsünde okundu.',reason='Şerh gövdesi tarama görüntüsüdür, metin katmanı yalnız altbilgi içerir.'))

def finding(k,text,refs,quote=False,pair=None):
 ident=q(k);add('finding',dict(id=ident,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=pair or ident,text=text,provenance='quote' if quote else 'summary',epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=ident,passage_id=q(ref),role='support'))
  add('verification',dict(finding_id=ident,passage_id=q(ref),checked_at=now,result='confirmed',reason='Belirtilen özgün sayfa veya tarihli haber okundu.'))
 add('review',dict(id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Söylem ve sonraki tarihli şerh ile aktör sıfatları ayrı okundu.'))
 return ident
summary=finding('statement-summary','Özgür Özel, Yeni Parti genel başkanı olarak Mekke Anlaşması kapsamında Türk askerinin Yemen’e gönderilmesine karşı çıktı.',['statement','authority'])
quote=finding('statement-quote',passages['statement'][3],['statement'],True,summary)
explain=finding('explanation','Yeni Parti genel başkanı 27 Ekimde Mekke Anlaşması kapsamında Yemen’e asker gönderilmesine itiraz etti. İki Yeni Parti komisyon üyesi 28 Ekim tarihli şerhte anlaşmaya muhalefet etti. Şerh kişisel oy veya fiilî asker sevki kanıtı değildir.',['statement','authority','news','signed','identity'])
scope='practice-d49dcefd73a16d98c559f5127cd6d70a202d9e1614805d83e7f90d4cd310bb07';topic='dis-guvenlik';event=q('event');sid=q('statement-record');relation=q('relation')
new['practice_statement'].append(dict(id=sid,party_id='yeni-parti',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2026-10-27',date_precision='day',version_id=q('anka')+'-v1',period_basis='27 Ekim ANKA haberindeki Yeni Parti genel başkanı açıklaması.',uncertainty_reason='Konuşmanın komisyon toplantısına göre saati doğrulanmadı.',comparison_row_id='04-03-v3-0303-epm-program-dis-guvenlik-row'))
new['practice_event'].append(dict(id=event,common_event_key='tbmm-2-3961-yeni-parti-2026-10-28-serh',event_at='2026-10-28',date_precision='day',date_unknown_reason=None,title='2/3961 komisyon raporundaki Yeni Parti muhalefet şerhi',scope_context='Talih Özcan ile Utku Çakırözerin 28 Ekim tarihli Mekke Anlaşması muhalefet şerhi.',occurrence_basis='TBMM sıra 295 raporunun basılı 24 ve 26. sayfaları ile 3 Kasım Sözcü haberi.'))
for k in ('news','signed','identity'):
 new['practice_event_evidence'].append(dict(event_id=event,passage_id=q(k),stage='action',supported_point=passages[k][4],concrete_basis='TBMM raporunun görüntüsü veya şerhi aktaran haber.',limitation='Şerh tarihi toplantı, kişisel oy, yayın ve fiilî sevk tarihlerinden ayrıdır.',epistemic_type='claim'))
 new['practice_evidence_assessment'].append(dict(event_id=event,passage_id=q(k),stage='action',basis_kind='document'))
new['practice_relation'].append(dict(id=relation,statement_id=sid,event_id=event,party_id='yeni-parti',topic_id=topic,scope_id=scope,comparability_reason='Aynı anlaşma ve savaş ortamına asker sevki riski yönünden karşılaştırılır.',target_finding_id=summary,result_finding_id=None,explanation_finding_id=explain,temporal_context='27 Ekim açıklaması ve 28 Ekim tarihli şerh, 30 Ekim rapor ve 5 Kasım Genel Kurulundan ayrıdır.',authority_context='Özel genel başkan olarak konuştu. Özcan ve Çakırözer kendilerini komisyonun Yeni Parti temsilcileri olarak tanımladı.',uncertainty_reason='Kişisel oylar, şerhin hazırlama saati, açıklamanın etkisi ve fiilî sevk gösterilmiyor.'))
new['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=relation,state='eligible',reason='İki tarihli kaynak aynı anlaşma ve asker sevki kaygısını ele alır.',passage_ids=json.dumps([q(x) for x in ('news','signed','identity')])))
for k,rows in new.items():p['practice_records'][k].extend(rows)
data=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
for x in p['entries']:
 if x['values'] not in data.setdefault(x['kind'],[]):data[x['kind']].append(x['values'])
for k,rows in p['practice_records'].items():
 for x in rows:
  if x not in data.setdefault(k,[]):data[k].append(x)
rules.validate_practices(data);print('SEMANTIC_PASS',flush=True)
targets=rules.practice_review_package_targets(data,new,[q(x) for x in passages],'yeni-parti');allp={x['id']:x for x in data['passage']}
for (kind,ident),(refs,owners) in targets.items():
 ids=sorted(refs);r['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({allp[x]['version_id'] for x in ids})),passage_ids=json.dumps(ids),inspected_sections=json.dumps(sorted({allp[x]['section'] for x in ids}),ensure_ascii=False),supported_claim='27 Ekim açıklaması ve 28 Ekim tarihli şerh '+kind+' '+ident,limitations='Görsel şerh, basılı adlar ve haber kaynakları kişisel oy veya sevk göstermez.',result='reviewed',reason='Kaynaklar tarih ve yetki ayrımıyla okundu.'))
 r['source_review_refs'].append(dict(subject_kind=kind,subject_id=ident))
p['source_review_refs']=r['source_review_refs'];rules.validate_practice_source_review(data,r['practice_source_review'],party_id='yeni-parti')
for name,obj in [('3961-yeni-committee-package-draft.json',p),('3961-yeni-committee-review-draft.json',r)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f.read_bytes()),flush=True)
