import hashlib, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import pdf_page_text, html_source_text
from uygulamalar import practice_review_targets

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); root=Path('data/practices/sources/tip')
live=Path('data/practices/04-tip.json'); rev=Path('data/practices/04-tip-review.json')
assert hashlib.sha256(live.read_bytes()).hexdigest()=='7b495b9533f49680bb705d7338cb47dc16a6698e14e8009052c409403ba6278b'
assert hashlib.sha256(rev.read_bytes()).hexdigest()=='25286178318c14cbedc3213b526026bb74ab264b4106d2b7c1a1f4c655d4af16'
pkg=json.loads(live.read_text()); review=json.loads(rev.read_text()); now=datetime.now(timezone.utc).isoformat(); entries=[]; records={}
def add(k,v): entries.append(dict(kind=k,values=v))
def rec(k,v): records.setdefault(k,[]).append(v)
caps=json.loads((p/'okul-yemegi-capture.json').read_text())
for cap,date in zip(caps,['2022-09-12','2023-09-12']):
 n=cap['name']; h=cap['sha256']; doc='0405-tip-okul-'+n; vid=doc+'-v1'; f=root/'objects'/h/'original.pdf'; assert hashlib.sha256(f.read_bytes()).hexdigest()==h
 add('document',dict(id=doc,party_id='tip',title='TBMM okulda gıda ve su teklifi 2/'+n,source_kind='official'))
 add('document_version',dict(id=vid,document_id=doc,original_url=cap['url'],final_url=cap['url'],document_date=date,version_label='TBMM özgün teklif',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=h,original_path=f'objects/{h}/original.pdf',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
 add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=cap['url'],basis='Özgün teklifin altı sayfası ve madde metni okundu.'))
 t=pdf_page_text(f,5); start=t.index('öğrencilere ücretsiz gıda desteği sağlanır.'); end=t.index('Bu maddenin',start); exact=t[start:end].strip()
 add('passage',dict(id=doc+'-measure-p',version_id=vid,exact=exact,prefix=None,suffix=None,article='MADDE 1',section='Ücretsiz gıda ve temiz su önerisi',pdf_page_index=5,printed_page=None))
 if n=='4600':
  t=pdf_page_text(f,3); start=t.index('Bizler de Türkiye İşçi Partisi');end=t.index('savunuyoruz.',start)+len('savunuyoruz.');exact=t[start:end].strip()
  add('passage',dict(id=doc+'-statement-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='TİP adına eğitim ve gıda ilkesi',pdf_page_index=3,printed_page=None))
cap=json.loads((p/'okul-1573-detail-capture.json').read_text()); h=cap['sha256']; url=cap['url']; vid='0405-tip-1573-detail-v1'; raw=(root/'objects'/h/'original.html.bin').read_bytes(); t=html_source_text(raw)
add('document',dict(id='0405-tip-1573-detail',party_id='tip',title='TBMM 2/1573 teklif ayrıntısı',source_kind='official'))
add('document_version',dict(id=vid,document_id='0405-tip-1573-detail',original_url=url,final_url=url,document_date=None,version_label='TBMM teklif ayrıntısı',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='unknown',date_unknown_reason='Dinamik ayrıntı kaydı için yayın tarihi verilmemiştir.'))
add('archive_view',cap['view']);add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Teklif numarası, geliş tarihi ve ilk imzacı alanları okundu; güncel süreç kesim anına taşınmadı.'))
for suffix,exact in [('signature','Saliha Sera KADIG&#x130;L'),('number','2 / 1573'),('date','12/09/2023')]:
 assert exact in t
 add('passage',dict(id='0405-tip-1573-detail-'+suffix+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Teklif ayrıntısı ve ilk imzacı tablosu',pdf_page_index=None,printed_page=None))
f=root/'objects/ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed/original.pdf'; t=pdf_page_text(f,241)
for suffix,exact in [('number','4314 2/4600'),('title','İlköğretim ve Eğitim Kanununda Değişiklik Yapılmasına İlişkin Kanun Teklifi (İstanbul\nMilletvekili Saliha Sera Kadıgil Sütlü)')]:
 assert exact in t
 add('passage',dict(id='0405-tip-okul-hukumsuz-'+suffix+'-p',version_id='0405-tip-sendika-hukumsuz-v1',exact=exact,prefix=None,suffix=None,article=None,section='Hükümsüz teklifler sıra 4314, görsel satır eşlemesi',pdf_page_index=241,printed_page='208'))
prefix='0405-tip-okul'; s=prefix+'-statement'; ev=prefix+'-1573-event'; rel=prefix+'-relation'; con=prefix+'-contribution'; st=prefix+'-4600-statement-p'; old=prefix+'-4600-measure-p'; new=prefix+'-1573-measure-p'; hn=prefix+'-hukumsuz-number-p'; ht=prefix+'-hukumsuz-title-p'; authority='0405-tip-kadigil-bio-authority-p'
add('actor',dict(id=prefix+'-kadigil',kind='authorized_representative',party_id='tip',person_id='0405-tip-sera-kadigil',authorization_passage_id=authority))
quote='Bizler de Türkiye İşçi Partisi olarak her çocuğun, temel gıda yardımı alarak, 12 yıl kesintisiz,\nparasız, bilimsel ve laik eğitim hakkının sağlanması gerektiğini savunuyoruz.'
assert quote in pdf_page_text(root/'objects'/caps[0]['sha256']/'original.pdf',3)
findings=[(prefix+'-summary','TİP, çocukların temel gıda desteğiyle parasız eğitim hakkını savundu.','summary',[st]),(prefix+'-quote',quote,'quote',[st]),(prefix+'-initiative','Sera Kadıgil 2023’te tam gün devlet okullarında ücretsiz gıda ve tüm devlet okullarında ücretsiz temiz su öneren 2/1573 teklifini sundu.','summary',[authority,new,'0405-tip-1573-detail-signature-p','0405-tip-1573-detail-number-p','0405-tip-1573-detail-date-p']),(prefix+'-explanation','2022 tarihli TİP açıklaması ve teklifi çocukların gıda ve eğitim hakkını ilişkilendirdi. İlk teklif 2023’te hükümsüz sayıldı; sonraki 2/1573 yeni dönem teklifidir ve kabul edilmiş uygulama göstermez.','summary',[st,old,hn,ht,new])]
for fid,value,prov,refs in findings:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=s if fid in (prefix+'-summary',prefix+'-quote') else fid,text=value,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'))
  add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='İlgili teklif ve dönem sonu listesi kendi bağlamında okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ayrı dönemler, madde kapsamı ve karar sınırı incelendi.'))
inv=json.loads(Path('data/practices/04-inventory.json').read_text())
for kind in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='egitime-erisim' and x['research_kind']==kind)
 rec('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='egitime-erisim',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili teklifler incelendi; diğer dönem ve uçlar açıktır.'))
 if kind=='event': scope=cell['cell_id']
rec('practice_event',dict(id=ev,common_event_key='tbmm-28-1-2-1573-okul-yemegi',event_at='2023-09-12',date_precision='day',date_unknown_reason=None,scope_context='28. dönem 2/1573',title='Okullarda ücretsiz öğün ve su teklifi',occurrence_basis='TBMM 2/1573 özgün teklif metni.'))
rec('practice_event_evidence',dict(event_id=ev,passage_id=new,supported_point='Ücretsiz gıda ve temiz su düzenlemesi önerisi',stage='initiative',concrete_basis='Teklif birinci madde.',limitation='Teklifin verilmesi kabul veya fiilî hizmet değildir.',epistemic_type='claim'))
rec('practice_evidence_assessment',dict(event_id=ev,passage_id=new,stage='initiative',basis_kind='document'))
for pid in ('0405-tip-1573-detail-signature-p','0405-tip-1573-detail-number-p','0405-tip-1573-detail-date-p'):
 rec('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point='Teklifin ilk imzacısı, sayısı veya geliş tarihi',stage='initiative',concrete_basis='TBMM teklif ayrıntısı.',limitation='Güncel aşama geçmiş kesim anına taşınmadı.',epistemic_type='claim'))
 rec('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage='initiative',basis_kind='document'))
rec('practice_contribution',dict(id=con,event_id=ev,party_id='tip',actor_id=prefix+'-kadigil',contribution_kind='task',finding_id=prefix+'-initiative',authority_passage_id=authority,membership_passage_id=None,responsibility_limit='Milletvekili teklif sunar; kanun kabulü TBMM yetkisindedir.'))
rec('practice_actor_period',dict(contribution_id=con,valid_from='2022-09-12',valid_to='2023-09-12',identity_passage_id='0405-tip-kadigil-bio-identity-p'))
rec('practice_statement',dict(id=s,party_id='tip',topic_id='egitime-erisim',taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2022-09-12',date_precision='day',version_id=prefix+'-4600-v1',period_basis='12 Eylül 2022 tarihli teklif gerekçesindeki TİP adına açıklama.',uncertainty_reason='Teklif metnindeki kendi adına siyasi beyandır.',comparison_row_id='04-03-v3-0304-tip-program-egitim-row'))
rec('practice_relation',dict(id=rel,statement_id=s,event_id=ev,party_id='tip',topic_id='egitime-erisim',scope_id=scope,comparability_reason='Her iki metin eğitim ve gıda desteği hakkındaki aynı öneriyle ilgilidir.',target_finding_id=prefix+'-summary',result_finding_id=None,explanation_finding_id=prefix+'-explanation',temporal_context='2022 teklifini hükümsüzlük listesi ve 2023 yeni dönem teklifi izler.',authority_context='Milletvekili teklif sunar; kabul yetkisi TBMM’dedir.',uncertainty_reason='2023 teklifinin kesim anındaki aşaması ve uygulama sonucu bilinmiyor.'))
pkg['entries'].extend(entries)
for k,rows in records.items(): pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for entry in pkg['entries']: data.setdefault(entry['kind'],[]).append(entry['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for name in ('finding_evidence','passage'): data.setdefault(name,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+name))
versions={x['id']:x['version_id'] for x in data['passage']}; targets=practice_review_targets(data,records)
for (kind,identity),(refs,parties) in targets.items():
 row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['2022 ve 2023 tekliflerinin gerekçe ve maddeleri','2023 hükümsüzlük listesi 4314. satır'],ensure_ascii=False),supported_claim='İlgili söylem ve teklif dönem ve yetki bağlamıyla incelendi: '+identity,limitations='Teklifin kabulü ve ülke çapında hizmet sonucu gösterilmedi.',result='reviewed',reason='Bu hedefin özgün pasajları incelendi: '+kind+' '+identity)
 review['practice_source_review'].append(row);review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('okul-yemegi-append-draft.json',pkg),('okul-yemegi-review-draft.json',review)]: (p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
