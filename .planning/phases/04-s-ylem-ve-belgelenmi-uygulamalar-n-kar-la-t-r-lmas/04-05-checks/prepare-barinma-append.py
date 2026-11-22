import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
live=Path('data/practices/04-tip.json'); reviewfile=Path('data/practices/04-tip-review.json')
assert hashlib.sha256(live.read_bytes()).hexdigest()=='34a7dc27a19ea525b4086e333e2d0634681c7b8dec1b2b49b81154ffd17e518a'
assert hashlib.sha256(reviewfile.read_bytes()).hexdigest()=='b293ce15db84bda91c78fa33f3e12aaa9af2bb28f1ff1dc95c611c8823f3570c'
package=json.loads(live.read_text()); review=json.loads(reviewfile.read_text()); now=datetime.now(timezone.utc).isoformat()
new=json.loads((p/'barinma-sources-draft.json').read_text())['entries']; records=package['practice_records']; inv=json.loads(Path('data/practices/04-inventory.json').read_text())
st='0405-tip-barinma-statement'; ev='0405-tip-barinma-274462-event'; rel='0405-tip-barinma-iliski'; contribution='0405-tip-barinma-katki'; actor='0405-tip-barinma-bas'
fund='0405-tip-barinma-10mayis-fund-p'; rent='0405-tip-barinma-10mayis-rental-p'; intro='0405-tip-barinma-274462-pdf-intro-p'; provision='0405-tip-barinma-274462-pdf-rental-p'; ident='0405-tip-barinma-duyuru-identity-p'; number='0405-tip-barinma-hukumsuz-number-p'; title='0405-tip-barinma-hukumsuz-title-p'
def add(kind,values):new.append(dict(kind=kind,values=values))
def record(kind,values):records.setdefault(kind,[]).append(values)
add('actor',dict(id=actor,kind='authorized_representative',party_id='tip',person_id='0405-tip-erkan-bas',authorization_passage_id=ident))
findings=[('0405-tip-barinma-hedef','Independent Türkçe, Baş’ın 10 Mayıs 2022 açıklamasında konut destek fonu ve öğrenciler için kira yardımını önerdiğini aktardı.','summary',[fund,rent]),('0405-tip-barinma-alinti',"3'ten fazla konutu olanlardan her ev için artan oranda vergi alınarak bir konut destek fonu oluşturulsun.",'quote',[fund]),('0405-tip-barinma-girisim','Erkan Baş ve üç TİP milletvekili öğrenci kira desteği dahil bir barınma kanun teklifi sundu.','summary',[ident,intro,provision]),('0405-tip-barinma-sonuc','TBMM 2 Haziran 2023 tutanağında 2/4462 teklifini hükümsüz sayılanlar arasında listeledi.','summary',[number,title]),('0405-tip-barinma-aciklama','10 Mayıs haberinde aktarılan fon ve öğrencilere kira yardımı önerisiyle 18 Mayıs teklifindeki fon kaynaklı öğrenci kira desteği konu bakımından ilişkilidir. Haber üçten fazla konut derken teklif farklı vergi koşulları kullanır; teklif 2023’te hükümsüz sayılmıştır.','summary',[fund,rent,provision,number,title])]
for fid,text,prov,refs in findings:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=st if fid in ('0405-tip-barinma-hedef','0405-tip-barinma-alinti') else fid,text=text,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'))
  add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Tarihli haber ve TBMM belgesinin ilgili bağlamı okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Haber aktarımı, öneri ve hükümsüzlük ayrıldı; vergi eşikleri birleştirilmedi.'))
for kind in ('statement','event'):
 cell=next(c for c in inv['cells'] if c['party_id']=='tip' and c['topic_id']=='barinma-konut' and c['research_kind']==kind)
 record('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='barinma-konut',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili kaynaklar incelendi; diğer dönem ve ilgili uçlar açık, kapanış yapılmadı.'))
 if kind=='event': event_scope=cell['cell_id']
record('practice_event',dict(id=ev,common_event_key='tbmm-27-2-4462',event_at='2022-05-18',date_precision='day',date_unknown_reason=None,scope_context='27. dönem 2/4462 barınma kanun teklifi',title='Barınma ve öğrenci kira desteği teklifi',occurrence_basis='TBMM teklif aslı ve hükümsüz teklifler listesi.'))
for pid,stage,point,basis in [(provision,'initiative','Öğrenciler için fon kaynaklı kira desteği önerildi','Teklif 6. maddesi, PDF indeks 9.'),(number,'result','2/4462 hükümsüz teklifler listesinde yer aldı','2 Haziran 2023 tutanağı sıra 4186, PDF indeks 235.')]:
 record('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point=point,stage=stage,concrete_basis=basis,limitation='Teklif ve sonucu, genel barınma durumu veya yürürlüğe giriş değildir.',epistemic_type='claim'))
 record('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage=stage,basis_kind='document'))
record('practice_contribution',dict(id=contribution,event_id=ev,party_id='tip',actor_id=actor,contribution_kind='task',finding_id='0405-tip-barinma-girisim',authority_passage_id=ident,membership_passage_id=None,responsibility_limit='Baş ve üç milletvekili teklif sahibidir; kabul yetkisi TBMM’dedir.'))
record('practice_actor_period',dict(contribution_id=contribution,valid_from='2022-05-18',valid_to='2022-05-19',identity_passage_id=ident))
record('practice_statement',dict(id=st,party_id='tip',topic_id='barinma-konut',taxonomy_version=4,summary_finding_id='0405-tip-barinma-hedef',quote_finding_id='0405-tip-barinma-alinti',statement_at='2022-05-10',date_precision='day',version_id='0405-tip-barinma-10mayis-v1',period_basis='Independent Türkçe 10 Mayıs tarihli basın toplantısı haberi.',uncertainty_reason='Konuşmanın tüm özgün kaydı doğrulanmadı.',comparison_row_id='04-03-v3-0304-tip-program-barinma-row'))
record('practice_relation',dict(id=rel,statement_id=st,event_id=ev,party_id='tip',topic_id='barinma-konut',scope_id=event_scope,comparability_reason='Konut destek fonu ve öğrenci kira desteği iki kaynakta da yer alır; vergi koşulları farklıdır.',target_finding_id='0405-tip-barinma-hedef',result_finding_id='0405-tip-barinma-sonuc',explanation_finding_id='0405-tip-barinma-aciklama',temporal_context='10 Mayıs haber, 18 Mayıs teklif, 2 Haziran 2023 hükümsüzlük.',authority_context='Haber Baş’ın beyanını aktarır; dört vekil teklif sunar, yasa TBMM yetkisindedir.',uncertainty_reason='Konuşmanın tam kaydı ve ülke genelindeki sonuçlar ayrıca incelenmelidir.'))
package['entries'].extend(new)
specs=[('practice_event',ev,[provision,number]),('practice_event_evidence',ev+'|'+provision+'|initiative',[provision]),('practice_event_evidence',ev+'|'+number+'|result',[number]),('practice_statement',st,[fund,rent]),('practice_statement.summary_finding_id',st,[fund,rent]),('practice_statement.quote_finding_id',st,[fund]),('practice_relation',rel,[fund,rent,provision,number,title]),('practice_relation.target_finding_id',rel,[fund,rent]),('practice_relation.result_finding_id',rel,[number,title]),('practice_relation.explanation_finding_id',rel,[fund,rent,provision,number,title]),('practice_contribution',contribution,[ident,intro,provision]),('practice_contribution.finding_id',contribution,[ident,intro,provision])]
versions={fund:'0405-tip-barinma-10mayis-v1',rent:'0405-tip-barinma-10mayis-v1',intro:'0405-tip-barinma-274462-pdf-v1',provision:'0405-tip-barinma-274462-pdf-v1',ident:'0405-tip-barinma-duyuru-v1',number:'0405-tip-sendika-hukumsuz-v1',title:'0405-tip-sendika-hukumsuz-v1'}
for kind,ident,refs in specs:
 row=dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(refs),inspected_sections=json.dumps(['10 Mayıs haber; 18 Mayıs teklif; 19 Mayıs parti duyurusu; 2023 tutanak'],ensure_ascii=False),supported_claim='Kaynakların ilgili alanı ve olay aşaması incelendi: '+kind,limitations='Vergi eşikleri farklı; öneri hükümsüz sayılmıştır ve genel sonuç değildir.',result='reviewed',reason='Kaynak, tarih ve yetki sınırları ayrı incelendi: '+ident)
 review['practice_source_review'].append(row); review['source_review_refs'].append(dict(subject_kind=kind,subject_id=ident))
keys=[(r['subject_kind'],r['subject_id']) for r in review['practice_source_review']]; assert len(keys)==len(set(keys))
for filename,obj in [('barinma-append-draft.json',package),('barinma-review-append-draft.json',review)]: (p/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(new),len(specs))
