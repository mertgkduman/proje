"""7 Ekim fon bilgilendirmesindeki iki DEM konuşması ve karşıt görüş."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');d=Path('data/practices');sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(d/'04-dem.json').read_bytes();rr=(d/'04-dem-review.json').read_bytes()
assert sha(raw)=='3b29f030c76cda43adafe2e33db8fb7008b1a233c83bc14f6f82dcb259d9c17c' and sha(rr)=='62534d40d4865a3fead5940678864ae3995bee7aee98f156055f3200b8d4a72e'
pkg,review=json.loads(raw),json.loads(rr);now=datetime.datetime.now(datetime.timezone.utc).isoformat();entries=json.loads((p/'2026-10-07-fon-source-records.json').read_text())['entries']
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'};passages={e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
for v in passages.values():
 ver=versions[v['version_id']];path=d/'sources/dem'/ver['original_path'];assert sha(path.read_bytes())==ver['sha256'] and v['exact'] in html_source_text(path.read_bytes())
q=lambda n:'0406-2026-10-07-'+n+'-p'; qs=list(passages);ver='0406-2026-10-07-full-v1'
event='0406-2026-fund-1007';finding='0406-2026-fund-1007-f';dispute='0406-2026-fund-1007-dispute';df='0406-2026-fund-1007-dispute-f';contribution='0406-2026-fund-1007-contribution';candidate='0406-2026-fund-1007-unmatched';scope='practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'
def add(k,**v):entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Gülüstan Kılıç Koçyiğit ve Sezai Temelli, DEM Grubu adına fon piyasası bilgilendirmesinde Meclis araştırma komisyonu ve denetim talep etti. Koçyiğit ödeme takvimini sordu; Yılmaz ve Koçyiğit sistemik risk konusunda farklı değerlendirme yaptı.',provenance='summary',epistemic_type='claim')
add('finding',id=df,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=df,text='Cumhurbaşkanı Yardımcısı Cevdet Yılmaz finans piyasalarında sistemik risk olmadığını söyledi; DEM Grubu adına Koçyiğit sorunu sistemsel olarak değerlendirdi.',provenance='summary',epistemic_type='claim')
for f,ps in [(finding,qs),(df,[q('yilmaz-role'),q('yilmaz-system'),q('kocyigit-role'),q('kocyigit-system')])]:
 for z in ps:add('finding_evidence',finding_id=f,passage_id=z,role='support');add('verification',finding_id=f,passage_id=z,checked_at=now,result='confirmed',reason='Özgün TBMM tutanağında konuşmacı ve pasaj karşılaştırıldı.')
 add('review',id='review-'+f,kind='finding',subject_id=f,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Görüşler aktörlerine atfedildi; plan ve sonuç ayrı tutuldu.')
points=[(z,'action',v['section'],'TBMM birleşimindeki konuşmacı veya açıklama.') for z,v in passages.items()]
rec={
'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='seffaflik-yolsuzluk',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 7 Ekim 2026 fon piyasası bilgilendirmesindeki grup görüşü; diğer kapsam araştırılıyor.')],
'practice_event':[dict(id=event,common_event_key='tbmm-28-5-003-fon-piyasasi-bilgilendirme',event_at='2026-10-07',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 5. yasama yılı 3. birleşimde fon piyasaları gündem dışı bilgilendirmesi',title='Fon piyasaları hakkında Genel Kurul bilgilendirmesi',occurrence_basis='7 Ekim 2026 TBMM birleşimi tam tutanağı ve özeti.')],
'practice_event_evidence':[dict(event_id=event,passage_id=z,supported_point=point,stage=stage,concrete_basis=basis,limitation='Konuşma ve geleceğe dönük plan, isimli oy, yasa veya fiilen ödeme sonucu değildir.',epistemic_type='claim') for z,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=z,stage=stage,basis_kind='document') for z,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Grup adına iki konuşma; araştırma komisyonunun kurulması, oy veya fiilî ödeme sonucu değil.')],
'practice_attempt_v2':[dict(id='0406-fund-1007-reading',scope_id=scope,attempted_at=now,query='7 Ekim 2026 TBMM fon piyasaları Yılmaz Koçyiğit Temelli görüşmeleri',url=versions[ver]['original_url'],result='examined',reason='İlgili gündem dışı bilgilendirme ve iki DEM konuşması okundu; diğer birleşim konuları açık.',source_version_id=ver)],
'practice_scope_source':[dict(scope_id=scope,version_id=ver,inspected_sections=json.dumps([v['section'] for v in passages.values()],ensure_ascii=False),inspected_at=now)],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Bağımsız güncel program ve tarihli önceki söylem araştırması açık; ortak tarihsel belge sürümleri arasındaki fark çözümlenmedi. Görüşme komisyon kurulması veya ödeme sonucu değildir.',passage_ids=json.dumps(qs,ensure_ascii=False))],
'practice_dispute':[dict(id=dispute,event_id=event,supported_points='Yılmaz ve DEM grubu fon piyasalarındaki gelişmeler üzerine Genel Kurulda konuştu.',disputed_points='Yılmaz sistemik risk olmadığını, Koçyiğit sorunun sistemsel olduğunu söyledi.',unresolved_points='Riskin ekonomik niteliği ve olayın sonuçları bağımsız olarak doğrulanmadı.',summary_finding_id=df)],
'practice_dispute_evidence':[dict(dispute_id=dispute,passage_id=q('kocyigit-system'),point='DEM sistemsel sorun değerlendirmesi',source_position='Koçyiğit sistemsel sorun olduğunu söyler.',role='conflict'),dict(dispute_id=dispute,passage_id=q('yilmaz-system'),point='Yılmaz sistemik risk değerlendirmesi',source_position='Yılmaz sistemik risk bulunmadığını söyler.',role='reply')]
}
pkg['entries']+=entries
for k,v in rec.items():pkg['practice_records'].setdefault(k,[]).extend(v)
items=[('practice_event_evidence',event+'|'+z+'|'+stage,[z],point) for z,stage,point,_ in points]
items += [('practice_event',event,qs,'Gündem dışı bilgilendirme ve grup görüşmeleri.'),('practice_contribution',contribution,qs,'İki DEM konuşması ve çağrısı.'),('practice_contribution.finding_id',contribution,qs,'Grup açıklamaları ve Yılmaz karşıt görüşü.'),('practice_candidate',candidate,qs,'Tarihsel söylem eşlemesi ve sonuçlar açık.'),('practice_dispute',dispute,qs,'Risk niteliği konusunda görüş ayrılığı.'),('practice_dispute.summary_finding_id',dispute,[q('yilmaz-role'),q('yilmaz-system'),q('kocyigit-role'),q('kocyigit-system')],'Görüşler aktörlerine atfedilir.'),('practice_dispute_evidence',dispute+'|'+q('kocyigit-system')+'|DEM sistemsel sorun değerlendirmesi|conflict',[q('kocyigit-system')],'Koçyiğit sistemsel sorun dedi.'),('practice_dispute_evidence',dispute+'|'+q('yilmaz-system')+'|Yılmaz sistemik risk değerlendirmesi|reply',[q('yilmaz-system')],'Yılmaz sistemik risk yok dedi.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(passages[z]['version_id'] for z in ps)),ensure_ascii=False),passage_ids=json.dumps(ps,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(passages[z]['section'] for z in ps)),ensure_ascii=False),supported_claim=claim,limitations='Görüşme isimli oy, komisyonun kuruluşu veya fiilî ödeme sonucu değildir.',result='reviewed',reason='TBMM özgün birleşim kaynağı okundu: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('fund-1007-draft.json',pkg),('fund-1007-review-draft.json',review)]:
 path=p/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path.read_bytes()))
