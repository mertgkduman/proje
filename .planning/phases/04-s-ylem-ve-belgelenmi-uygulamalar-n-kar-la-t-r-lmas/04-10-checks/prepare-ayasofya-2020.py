import copy, datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes, pdf_page_text
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules

D=Path(__file__).parent
root=Path('data/practices/sources/emep')
read=lambda p: json.loads(Path(p).read_text())
package=read('data/practices/04-emep.json')
previous=read('data/practices/04-emep-review.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory=read('data/practices/04-inventory.json')
entries=package['entries']; records=package['practice_records']
assert len(records['practice_event'])==69 and len(records['practice_relation'])==71
assert not any('ayasofya' in str(v).lower() for v in records['practice_event'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
items=[
 ('court','pdf','https://danistay.gov.tr/assets/pdf/guncelKararlar/10_07_2020_060019.pdf','https://danistay.gov.tr/assets/pdf/guncelKararlar/10_07_2020_060019.pdf','/tmp/gsd-emep-ayasofya-court.pdf','2020-07-02','Danıştay Onuncu Dairesi','Danıştay kararı','Dava konusu Bakanlar Kurulu Kararının İPTALİNE,',17),
 ('gazette','pdf','https://www.resmigazete.gov.tr/eskiler/2020/07/20200710M1-1.pdf','https://upload.wikimedia.org/wikipedia/commons/7/7d/Resm%C3%AE_Gazete_Say%C4%B1_31181_M%C3%BCkerrer.pdf','/tmp/gsd-emep-ayasofya-rg-mirror.pdf','2020-07-10','T.C. Resmî Gazete','2729 sayılı karar','Karar Sayısı: 2729',0),
 ('diyanet','html','https://aksaray.diyanet.gov.tr/sayfalar/contentdetail.aspx?ContentId=1787&MenuCategory=Kurumsal','https://aksaray.diyanet.gov.tr/sayfalar/contentdetail.aspx?ContentId=1787&MenuCategory=Kurumsal','/tmp/gsd-emep-ayasofya-ak.html','2020-08-11','Aksaray İl Müftülüğü','Fiilî açılış hakkında Diyanet yayını','24 Temmuz 2020 tarihinde kılınan ilk cuma namazı ile birlikte fiilen ibadete açılmıştır.',None),
 ('party','html','https://www.emep.org/ayasofya-siyasi-malzeme-yapilamaz','https://www.emep.org/ayasofya-siyasi-malzeme-yapilamaz','/tmp/gsd-emep-ayasofya-party.html','2020-07-12','Emek Partisi','Ayasofya siyasi malzeme yapılamaz','gerilim politikalarını onaylamamakta',None),
]
def add(table,**v): entries.append(dict(kind=table,values=v))
sources={}
for role,typ,url,final,local,day,publisher,title,exact,page in items:
 raw=Path(local).read_bytes(); sha=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/sha; obj.mkdir(parents=True,exist_ok=True)
 name='original.pdf' if typ=='pdf' else 'original.html.bin'
 for n,b in ((name,raw),('readable.html',readable_bytes(raw,typ,legacy=False))):
  p=obj/n
  if p.exists(): assert p.read_bytes()==b
  else: p.write_bytes(b)
 doc='0410-ayasofya-'+role; ver=doc+'-v1'; pid=doc+'-p'; sources[role]=(ver,pid,url)
 add('document',id=doc,party_id='emep',title=title,source_kind='party' if role=='party' else 'official')
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=final,document_date=day,date_precision='day',date_unknown_reason=None,version_label=('11 Ağustos tarihli müftülük yayını; olay 24 Temmuz' if role=='diyanet' else day+' tarihli kaynak'),accessed_at=now,verified_at=now,mime='application/pdf' if typ=='pdf' else 'text/html',sha256=sha,original_path='objects/'+sha+'/'+name,readable_path='objects/'+sha+'/readable.html')
 if typ=='html':
  assert exact in html_source_text(raw),role
  view=build_view(raw,final,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=ver; validate_view(root,view); add('archive_view',**view)
 add('passage',id=pid,version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=page,printed_page=None)
 if typ=='pdf' and exact not in pdf_page_text(Path(local),page):
  assert role=='gazette'
  add('manual_passage',passage_id=pid,checked_at=now,method='Wikimedia kopyası PDF sayfa 1 Poppler/Cairo ile görselleştirilerek okundu; TBMM tutanağıyla karşılaştırıldı.',reason='Kararın gövdesi PDF metin katmanında değil; resmî ilk kaynağa doğrudan erişim zaman aşımına uğradı.')
 add('source_attribution',version_id=ver,kind='party_publication' if role=='party' else 'official',publisher=publisher,author='Selma Gürkan' if role=='party' else None,social_handle=None,published_at=day,date_precision='day',public_url=final,basis=('11 Ağustos sayfa tarihi olay tarihi değildir.' if role=='diyanet' else 'Özgün kaynak tarih ve içeriği incelendi; 2729 için Wikimedia kopyası ve TBMM tutanağı kullanıldı.' if role=='gazette' else 'Yayın veya karar tarihi ve özgün gövde incelendi.'))
 print(role,sha)

decision_exact='10/7/2020 tarihli ve 2729 sayılı Cumhurbaşkanlığı kararı ile caminin yönetiminin 22/6/1965 tarihli ve 633 sayılı Diyanet İşleri Başkanlığı Kuruluş ve Görevleri Hakkında Kanunun 35 inci maddesi gereği Diyanet İşleriBaşkanlığına devredilerek ibadete açılması uygun görülmüştür.'
assert decision_exact in html_source_text(Path('/tmp/gsd-emep-ayasofya-ak.html').read_bytes())
add('passage',id='0410-ayasofya-diyanet-decision-p',version_id=sources['diyanet'][0],exact=decision_exact,prefix=None,suffix=None,article=None,section='2729 kararını aktaran Diyanet yayını',pdf_page_index=None,printed_page=None)

cell=next(c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']=='laiklik' and c['research_kind']=='event')
scope=cell['cell_id']
if not any(s['id']==scope for s in records['practice_scope_v2']):
 records['practice_scope_v2'].append(dict(id=scope,party_id='emep',topic_id='laiklik',taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind='event',boundary_reason='Ayasofya karar ve fiilî açılış kaynakları ile parti açıklaması incelendi; kapsam açıktır.'))
for role,(ver,pid,url) in sources.items():
 aid='0410-ayasofya-'+role+'-reading'
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=ver,inspected_sections=json.dumps([next(i[7] for i in items if i[0]==role)],ensure_ascii=False),inspected_at=now))
 records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Karar, tutanak veya açıklama özgün kaynak gövdesinden incelendi; Resmî Gazete için kopya görseli kullanıldı.',source_version_id=ver))
 records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='Ayasofya idarî, yargısal ve fiilî süreç ile parti açıklaması.',state='examined',attempt_ids=json.dumps([aid])))
for ident,day,title,basis,roles in [
 ('court','2020-07-02','Danıştayın 1934 müze kararını iptali','Danıştay Onuncu Dairesi E:2016/16015 K:2020/2595.',('court',)),
 ('gazette','2020-07-10','2729 sayılı Cumhurbaşkanı kararı','Karar görüntüsü 10 Temmuz 2020 mükerrer sayıda; 10 Temmuz TBMM tutanağı ve Diyanet yayınıyla karşılaştırıldı.',('gazette','diyanet-decision')),
 ('opening','2020-07-24','Ayasofya’da ilk cuma namazı ve fiilî açılış','Aksaray İl Müftülüğünün 11 Ağustos yayını 24 Temmuz fiilî açılışını aktarıyor.',('diyanet',)),
]:
 eid='0410-ayasofya-2020-'+ident+'-event'
 records['practice_event'].append(dict(id=eid,common_event_key='ayasofya-2020-'+ident,event_at=day,date_precision='day',date_unknown_reason=None,scope_context='Ayasofya, İstanbul',title=title,occurrence_basis=basis))
 refs=[]
 for role in roles:
  pid='0410-ayasofya-diyanet-decision-p' if role=='diyanet-decision' else sources[role][1]; refs.append(pid)
  records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage='action',supported_point=basis,concrete_basis='Danıştay kararı' if role=='court' else 'Resmî Gazete kopyası' if role=='gazette' else 'TBMM tutanağı' if role=='tbmm' else 'Diyanet yayını',limitation='EMEP açıklaması olayı tartışır; bu işlemde parti yetkisi veya nedenselliği gösterilmemiştir. 2729 kopyasının kaynağı Wikimedia, resmî PDF erişimi zaman aşımıdır.',epistemic_type='claim'))
  records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
 records['practice_candidate'].append(dict(id='0410-ayasofya-2020-'+ident+'-candidate',scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason='Parti açıklamasında konu tartışılır; bu işlemle eşleşebilir ölçülebilir önceden parti talebi veya parti karar yetkisi gösterilmedi.',passage_ids=json.dumps(refs)))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{e['values']['id'] for e in entries if e['kind']=='passage'},party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(ids,owners) in sorted(targets.items()):
 if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
 inspected=[passages[x] for x in sorted(ids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Ayasofya karar veya fiilî açılışına ilişkin ilgili resmî kaynak pasajı okundu.',limitations='Partiye karar yetkisi veya nedensellik atfedilmez. 2729 için resmî adrese erişilemediğinden Wikimedia kopyası ve TBMM tutanağı kullanıldı.',result='reviewed',reason=kind+' / '+identity+' için ilgili özgün pasaj incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets))
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('ayasofya-2020-union-draft.json',package),('ayasofya-2020-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('AYASOFYA_SEMANTIC_OK',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
