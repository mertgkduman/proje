import hashlib,json,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from uygulamalar import practice_review_targets

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); live=Path('data/practices/04-tip.json'); rev=Path('data/practices/04-tip-review.json')
assert hashlib.sha256(live.read_bytes()).hexdigest()=='abc5a952f12b4cb46227ce33ee73a05055f519d1bc08196647682e84f2157bc5'
assert hashlib.sha256(rev.read_bytes()).hexdigest()=='082a0812f4195ec2fd5eb1f3c84403b26cb295b467795b2f701e6fda9ea8c74a'
package=json.loads(live.read_text()); review=json.loads(rev.read_text()); now=datetime.now(timezone.utc).isoformat(); inv=json.loads(Path('data/practices/04-inventory.json').read_text())
entries=[]; records={}
for name in ['yurt-manual-source-draft.json','yurt-news-source-draft.json','yurt-outcome-source-draft.json','kadin-sources-draft.json','kadigil-identity-draft.json']:
 entries.extend(json.loads((p/name).read_text())['entries'])
def add(k,v):entries.append(dict(kind=k,values=v))
def rec(k,v):records.setdefault(k,[]).append(v)
Y='0405-tip-yurt'; W='0405-tip-kadin'; yp='0405-tip-yurt-273833-free-dorm-p'; ya='0405-tip-yurt-273833-authority-p'; yi='0405-tip-yurt-gercek-intent-p'; yf='0405-tip-yurt-gercek-free-p'; yz='0405-tip-yurt-hukumsuz-p'; wa='0405-tip-kadigil-bio-authority-p'; w1='0405-tip-kadin-274653-duty-p'; w2='0405-tip-kadin-281566-duty-p'; wn='0405-tip-kadin-hukumsuz-number-p'; wt='0405-tip-kadin-hukumsuz-title-p'
ws='0405-tip-kadin-program-statement'; ys=Y+'-statement'; ev1=Y+'-273833-event'; ev2=W+'-274653-event'; ev3=W+'-281566-event'; r1=Y+'-relation'; r2=W+'-old-relation'; r3=W+'-renewed-relation'; c1=Y+'-contribution';c2=W+'-old-contribution';c3=W+'-renewed-contribution'
add('person',dict(id='0405-tip-sera-kadigil',name='Saliha Sera Kadıgil'))
add('actor',dict(id=Y+'-bas',kind='authorized_representative',party_id='tip',person_id='0405-tip-erkan-bas',authorization_passage_id=ya))
add('actor',dict(id=W+'-kadigil',kind='authorized_representative',party_id='tip',person_id='0405-tip-sera-kadigil',authorization_passage_id=wa))
findings=[
 (Y+'-statement-summary','Gerçek Haberci, Baş’ın öğrenci nöbetinde TİP olarak TBMM’ye yurt sorunu için teklif vereceklerini söylediğini aktardı.','summary',[yi]),
 (Y+'-statement-quote','TİP olarak TBMM’ye kanun teklifi vereceklerini söyledi.','quote',[yi]),
 (Y+'-initiative','Baş’ın imzaladığı öğrenci barınması teklifi kamu yurtlarında ücretsiz barınma öngördü.','summary',[ya,yp]),
 (Y+'-result','TBMM 2 Haziran 2023 tutanağı 27. dönem 2/3833 teklifini hükümsüz sayılanlar arasında listeledi.','summary',[yz]),
 (Y+'-explanation','Haberde aktarılan yurt sorunu için teklif verme sözü ile ertesi gün sunulan ücretsiz kamu yurdu düzenlemesi konu ve zaman bakımından ilişkilidir; teklif 2023’te hükümsüz sayılmıştır.','summary',[yi,yf,yp,yz]),
 (W+'-old-initiative','TİP milletvekili Sera Kadıgil bütün belediyelerin kadın danışma merkezi açmasını öngören 2/4653 teklifini sundu.','summary',[wa,w1]),
 (W+'-old-result','TBMM 2 Haziran 2023 tutanağı 27. dönem 2/4653 teklifini hükümsüz sayılanlar arasında listeledi.','summary',[wn,wt]),
 (W+'-old-explanation','Program kadınların mücadelesini destekler; 2022 teklifi şiddetle mücadelede kadın danışma merkezleri için somut düzenleme önerir ve 2023’te hükümsüz sayılmıştır. Program sürümünün 2022’de yürürlüğü belirlenmemiştir.','summary',['0304-tip-program-kadin-p1','0304-tip-program-kadin-p2',w1,wn,wt]),
 (W+'-new-initiative','Kadıgil 28. dönemde 7 Eylül 2023’te bütün belediyelere kadın danışma merkezi yükümlülüğünü öngören ayrı 2/1566 teklifini sundu.','summary',[wa,w2]),
 (W+'-new-explanation','2023’te aynı konuya ilişkin yeni dönemde ayrı bir teklif sunulmuştur; bu, 2022 teklifinin hükümsüz sayılmasından sonraki girişimdir ve kanunlaşma göstermez.','summary',['0304-tip-program-kadin-p1','0304-tip-program-kadin-p2',w1,wn,wt,w2])]
for fid,text,provenance,refs in findings:
 pair=ys if fid in (Y+'-statement-summary',Y+'-statement-quote') else fid
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if provenance=='quote' else 'support'))
  add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Kaynak ve olay aşaması bağlamında görsel veya metin üzerinden okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Tarihler, ilgili belge ve yetki sınırları ayrı karşılaştırıldı.'))
for fid,refs in [('0304-tip-program-kadin-summary',['0304-tip-program-kadin-p1','0304-tip-program-kadin-p2','0304-tip-program-kadin-q']),('0304-tip-program-kadin-quote',['0304-tip-program-kadin-q'])]:
 for ref in refs:add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Arşivli program pasajı ve bağlamı okundu.'))
for kind in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='toplumsal-cinsiyet' and x['research_kind']==kind)
 rec('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='toplumsal-cinsiyet',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili kaynaklar incelendi, diğer dönem ve uçlar açık; kapanış yapılmadı.'))
 if kind=='event': women_scope=cell['cell_id']
housing_scope=next(x['id'] for x in package['practice_records']['practice_scope_v2'] if x['topic_id']=='barinma-konut' and x['research_kind']=='event')
for ident,date,key,title in [(ev1,'2021-09-23','tbmm-27-2-3833','Öğrenci yurtlarında ücretsiz barınma teklifi'),(ev2,'2022-10-11','tbmm-27-2-4653','Kadın danışma merkezleri teklifi'),(ev3,'2023-09-07','tbmm-28-2-1566','Kadın danışma merkezleri yeni dönem teklifi')]:
 rec('practice_event',dict(id=ident,common_event_key=key,event_at=date,date_precision='day',date_unknown_reason=None,scope_context=key,title=title,occurrence_basis='TBMM özgün imzalı teklif metni.'))
for event,pid,stage,point,basis in [(ev1,yp,'initiative','Ücretsiz kamu yurdu hizmeti önerildi','Taranmış teklif, görsel okunan 1. madde.'),(ev1,yz,'result','2/3833 hükümsüz sayılan tekliflerde listelendi','2 Haziran 2023 tutanağı, basılı 174 sıra 3586.'),(ev2,w1,'initiative','Bütün belediyelere danışma merkezi önerildi','27. dönem teklif 1. madde.'),(ev2,wn,'result','2/4653 hükümsüz listesinde yer aldı','2 Haziran 2023 tutanağı sıra 4366.'),(ev2,wt,'result','Liste başlığı Kadıgil teklifini tanımlar','Aynı tutanak, basılı 210 başlık sütunu.'),(ev3,w2,'initiative','Yeni dönemde aynı konu için ayrı teklif sunuldu','28. dönem 2/1566 teklif 1. madde.')]:
 rec('practice_event_evidence',dict(event_id=event,passage_id=pid,supported_point=point,stage=stage,concrete_basis=basis,limitation='Teklif sunulması veya hükümsüzlüğü, uygulama ve ülke genelinde sonuç değildir.',epistemic_type='claim'))
 rec('practice_evidence_assessment',dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
for con,event,actor,fid,authority,date in [(c1,ev1,Y+'-bas',Y+'-initiative',ya,'2021-09-23'),(c2,ev2,W+'-kadigil',W+'-old-initiative',wa,'2022-10-11'),(c3,ev3,W+'-kadigil',W+'-new-initiative',wa,'2023-09-07')]:
 rec('practice_contribution',dict(id=con,event_id=event,party_id='tip',actor_id=actor,contribution_kind='task',finding_id=fid,authority_passage_id=authority,membership_passage_id=None,responsibility_limit='Milletvekili teklifi sunar; kanun kabulü TBMM yetkisindedir.'))
 rec('practice_actor_period',dict(contribution_id=con,valid_from=date,valid_to=date,identity_passage_id=authority))
rec('practice_statement',dict(id=ys,party_id='tip',topic_id='barinma-konut',taxonomy_version=4,summary_finding_id=Y+'-statement-summary',quote_finding_id=Y+'-statement-quote',statement_at='2021-09-22',date_precision='day',version_id='0405-tip-yurt-gercek-v1',period_basis='23 Eylül tarihli haber toplantıyı önceki gece olarak aktarır.',uncertainty_reason='Önceki gece tarihi haberin ifadesinden çıkarılır; doğrudan tam konuşma kaydı yoktur.',comparison_row_id='04-03-v3-0304-tip-program-barinma-row'))
rec('practice_statement',dict(id=ws,party_id='tip',topic_id='toplumsal-cinsiyet',taxonomy_version=4,summary_finding_id='0304-tip-program-kadin-summary',quote_finding_id='0304-tip-program-kadin-quote',statement_at=None,date_precision='unknown',version_id='0203-tip-program-v1',period_basis='Faz 3 seçili arşivli program.',uncertainty_reason='Programın 2022–2023 tarihli sürümü belirlenemedi.',comparison_row_id='04-03-v3-0304-tip-program-kadin-row'))
for ident,statement,event,topic,scope,target,result,explain,temporal,uncert in [(r1,ys,ev1,'barinma-konut',housing_scope,Y+'-statement-summary',Y+'-result',Y+'-explanation','Haber önceki geceyi, teklif 23 Eylül 2021 ve hükümsüz liste Haziran 2023’ü gösterir.','Haber aktarımıdır; tam konuşma kaydı yoktur.'),(r2,ws,ev2,'toplumsal-cinsiyet',women_scope,'0304-tip-program-kadin-summary',W+'-old-result',W+'-old-explanation','Teklif Ekim 2022, hükümsüz liste Haziran 2023; programın tarihsel sürümü bilinmiyor.','Teklifin sonucu ülke genelindeki hizmetler değildir.'),(r3,ws,ev3,'toplumsal-cinsiyet',women_scope,'0304-tip-program-kadin-summary',None,W+'-new-explanation','2023 yeni dönem teklifi, önceki hükümsüz tekliften ayrıdır; program tarihi bilinmiyor.','Yeni teklifin kesim anındaki aşaması ve hizmetlerin sonucu ayrıca araştırılmalıdır.')]:
 rec('practice_relation',dict(id=ident,statement_id=statement,event_id=event,party_id='tip',topic_id=topic,scope_id=scope,comparability_reason='Kaynaklarda belirtilen alan aynı olmakla birlikte genel ilke ve somut teklifin kapsamı ayrıdır.',target_finding_id=target,result_finding_id=result,explanation_finding_id=explain,temporal_context=temporal,authority_context='Milletvekili teklif sunar; yasalaşma TBMM yetkisindedir.',uncertainty_reason=uncert))
package['entries'].extend(entries)
for k,rows in records.items():package['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in package['practice_records'].items()}
for entry in package['entries']:data.setdefault(entry['kind'],[]).append(entry['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for name in ('finding_evidence','passage'):
 data.setdefault(name,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+name))
targets=practice_review_targets(data,records); passage_versions={x['id']:x['version_id'] for x in data['passage']}; seen={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,identity),(refs,parties) in targets.items():
 assert (kind,identity) not in seen; versions=sorted({passage_versions[x] for x in refs})
 if identity.startswith(Y):
  claim='Haberin Baş’a atfettiği teklif niyeti, imzalı ücretsiz kamu yurdu önerisi ve TBMM hükümsüzlük listesi ilgili kayıt için karşılaştırıldı.'
  limitations='Haber doğrudan konuşma dökümü değildir; teklif ve hükümsüzlük barınma sonucunu göstermez.'
 elif identity.startswith(W) or identity==ws:
  claim='Programın genel kadın mücadelesi ilkesi, Kadıgil’in iki ayrı dönem danışma merkezi teklifi ve ilgili 2022 teklifinin hükümsüzlük kaydı karşılaştırıldı.'
  limitations='Programın ilgili tarihlerdeki sürümü ve 2023 teklifinin kesim anındaki aşaması bilinmiyor; kanunlaşma çıkarılmadı.'
 else:
  claim='Belirtilen kaynak pasajının bu kayda özgü olay, aktör veya söylem desteği incelendi.'
  limitations='Belgenin kapsamadığı sonuçlar çıkarılmadı.'
 row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(versions),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['2021 haber ve imzalı tarama; 2022 ve 2023 TBMM teklifleri; 2023 hükümsüz liste; program kadın bölümü'],ensure_ascii=False),supported_claim=claim,limitations=limitations,result='reviewed',reason='Kayıt türü, tarih ve yetki bağlamı karşılaştırıldı: '+kind+' '+identity)
 review['practice_source_review'].append(row);review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for filename,obj in [('next-policy-append-draft.json',package),('next-policy-review-draft.json',review)]: (p/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY entries',len(entries),'review_targets',len(targets),'events',len(records['practice_event']))
