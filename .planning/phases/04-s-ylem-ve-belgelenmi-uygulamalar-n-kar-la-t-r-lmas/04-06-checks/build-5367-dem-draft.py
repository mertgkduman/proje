"""5367 DEM grubu açıklaması: olayı ve ihtilaflı sayımı kaynaklarla ekle."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import pdf_page_text, html_source_text

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
d = Path('data/practices'); sha = lambda b: hashlib.sha256(b).hexdigest()
raw = (d/'04-dem.json').read_bytes(); rr = (d/'04-dem-review.json').read_bytes()
assert sha(raw) == 'abc848b7f06d0de100a1ca28d95f228d9a4dc89c5d67f810583c49143151966d'
assert sha(rr) == '1ec892c2ff51afb9f0114d45b5bbcdd36b120e1961c67293fa743600b4b580ab'
pkg, review = json.loads(raw), json.loads(rr); now = datetime.datetime.now(datetime.timezone.utc).isoformat()
entries = json.loads((p/'2026-5367-dem-source-records.json').read_text())['entries'] + json.loads((p/'2026-5367-news-source-records.json').read_text())['entries']
versions = {e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
passages = {e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
for v in passages.values():
    ver = versions[v['version_id']]; path = d/'sources/dem'/ver['original_path']
    assert sha(path.read_bytes()) == ver['sha256']
    text = pdf_page_text(path, v['pdf_page_index']) if ver['mime']=='application/pdf' else html_source_text(path.read_bytes())
    assert v['exact'] in text
event='0406-2026-mdkd-report'; finding='0406-2026-mdkd-dem-f'; dispute='0406-2026-mdkd-tally-dispute'; df='0406-2026-mdkd-tally-f'; contribution='0406-2026-mdkd-dem-contribution'; candidate='0406-2026-mdkd-dem-unmatched'
scope='practice-1ad7f794262942a259b8312e1d7a94fd4bbcd4226334b2a97325d089c8c24ad5'
pdf=lambda n:f'0406-2026-mdkd-5367-p{n}'
news='0406-dem-mdkd-siirt-tally-p'; qs=[pdf(19),pdf(20),pdf(21),pdf(22),pdf(23),pdf(60),news]
def add(k,**v): entries.append(dict(kind=k,values=v))
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Gülüstan Kılıç Koçyiğit DEM adına komisyon çalışmalarına katkıyı olumlu değerlendirdi; Cengiz Çiçek taslak diline itirazları ve ana dili haklarına ilişkin görüşü açıkladı. Komisyon raporu kabul etti; kaynaklar kabul oyu sayısında ayrılıyor.',provenance='summary',epistemic_type='claim')
add('finding',id=df,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=df,text='TBMM Başkanı komisyon sonucunu 47 kabul, 2 ret ve 1 çekimser olarak duyurdu; Artı Siirt haberi 42 kabul, 2 ret ve 1 çekimser bildirdi. Farkın nedeni doğrulanmadı.',provenance='summary',epistemic_type='claim')
for f,ps in [(finding,qs),(df,[pdf(60),news])]:
 for q in ps:
  add('finding_evidence',finding_id=f,passage_id=q,role='support'); add('verification',finding_id=f,passage_id=q,checked_at=now,result='confirmed',reason='İlgili toplantı ve haber pasajı kendi kaynağına atfedilerek okundu.')
 add('review',id='review-'+f,kind='finding',subject_id=f,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Grup açıklaması, toplu sonuç ve atıflı kaynak farkı ayrıldı.')
points=[(pdf(19),'action','DEM grubu adına konuşma','Başkan Koçyiğit’i DEM adına çağırdı.'),(pdf(20),'action','DEM taslak değerlendirmesi','Koçyiğit sözü parti görüşü ve itirazı için Çiçek’e bıraktı.'),(pdf(21),'action','Taslak diline itiraz','Çiçek taslağın kullanılan kavramlarına itiraz etti.'),(pdf(22),'action','Taslak hakkındaki itirazın gerekçesi','Çiçek farklı görüşü gerekçelendirdi.'),(pdf(23),'action','Ana dili hakları','Çiçek ana dili hakkına ilişkin görüşü açıkladı.'),(pdf(60),'result','TBMM başkanının sonuç duyurusu','Başkan kabulü ve 47/2/1 toplamını duyurdu.'),(news,'result','Haberin alternatif sayımı','Artı Siirt 42/2/1 yazdı.')]
rec={
'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='anadil-hakki',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='18 Şubat 2026 komisyon görüşmesindeki ana dili açıklaması; diğer konu kapsamı araştırılıyor.')],
'practice_event':[dict(id=event,common_event_key='tbmm-mdkd-komisyon-rapor-2026-02-18',event_at='2026-02-18',date_precision='day',date_unknown_reason=None,scope_context='TBMM Millî Dayanışma, Kardeşlik ve Demokrasi Komisyonu 21. toplantısı',title='Komisyon raporu görüşmesinde DEM açıklaması',occurrence_basis='18 Şubat 2026 özgün komisyon tutanağı; sonuç sayısında haberle fark vardır.')],
'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Grup konuşması bireysel oy değildir; raporun kabulü yasalaşma veya fiilî sonuç değildir.',epistemic_type='claim') for q,stage,point,basis in points],
'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,_,_ in points],
'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM adına sözlü açıklama ve çekince; bireysel oy veya yürürlüğe giren düzenleme değildir.')],
'practice_attempt_v2':[dict(id='0406-5367-reading',scope_id=scope,attempted_at=now,query='TBMM 18 Şubat 2026 DEM komisyon raporu Çiçek ana dili',url=versions['0406-2026-mdkd-5367-v1']['original_url'],result='examined',reason='Tutanağın 62 sayfası okundu; görüş ve oylama ayrıldı.',source_version_id='0406-2026-mdkd-5367-v1'),dict(id='0406-5367-news-reading',scope_id=scope,attempted_at=now,query='18 Şubat komisyon raporu sonuç sayısının alternatif haberi',url=versions['0406-dem-mdkd-siirt-v1']['original_url'],result='examined',reason='Haberin 42/2/1 sayımı tutanakla farklı; fark açık.',source_version_id='0406-dem-mdkd-siirt-v1')],
'practice_scope_source':[dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([passages[q]['section'] for q in qs if passages[q]['version_id']==v],ensure_ascii=False),inspected_at=now) for v in versions],
'practice_candidate':[dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki bağımsız güncel parti programı ve tarihli söylem araştırması açık; komisyon açıklaması ve rapor kabulü ana dili hakkının fiilî gerçekleşmesi değildir.',passage_ids=json.dumps(qs,ensure_ascii=False))],
'practice_dispute':[dict(id=dispute,event_id=event,supported_points='Komisyon raporunun kabul edildiği hem tutanakta hem haberde bildirilir.',disputed_points='Başkan 47 kabul, haber 42 kabul bildirir; her ikisinde 2 ret ve 1 çekimser vardır.',unresolved_points='Farkın nedeni ve isimli oy çizelgesi doğrulanmadı.',summary_finding_id=df)],
'practice_dispute_evidence':[dict(dispute_id=dispute,passage_id=pdf(60),point='Başkanın duyurduğu sayım',source_position='TBMM Başkanı 47 kabul, 2 ret, 1 çekimser duyurdu.',role='conflict'),dict(dispute_id=dispute,passage_id=news,point='Haberin bildirdiği sayım',source_position='Artı Siirt 42 kabul, 2 ret, 1 çekimser bildirdi.',role='reply')]
}
pkg['entries'] += entries
for k,v in rec.items(): pkg['practice_records'].setdefault(k,[]).extend(v)
items=[('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,[q for q,_,_,_ in points],'Görüşme ve kabul, farklı sayımlarla.'),('practice_contribution',contribution,qs,'DEM adına katkı ve çekinceler.'),('practice_contribution.finding_id',contribution,qs,'Grup konuşması ve sayım ayrımı.'),('practice_candidate',candidate,qs,'Önceki söylem eşlemesi açık.'),('practice_dispute',dispute,[q for q,_,_,_ in points],'Kabul sayıları kaynaklarda farklı.'),('practice_dispute.summary_finding_id',dispute,[pdf(60),news],'İki sayı atıfla ayrı.'),('practice_dispute_evidence',dispute+'|'+pdf(60)+'|Başkanın duyurduğu sayım|conflict',[pdf(60)],'Başkan 47/2/1 dedi.'),('practice_dispute_evidence',dispute+'|'+news+'|Haberin bildirdiği sayım|reply',[news],'Haber 42/2/1 dedi.')]
for kind,ident,ps,claim in items:
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(passages[q]['version_id'] for q in ps)),ensure_ascii=False),passage_ids=json.dumps(ps,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(passages[q]['section'] for q in ps)),ensure_ascii=False),supported_claim=claim,limitations='DEM tekil oyu ve sonraki uygulama doğrulanmadı; kabul sayısı kaynaklarda farklı.',result='reviewed',reason='Özgün kaynaklar okundu: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('5367-dem-draft.json',pkg),('5367-dem-review-draft.json',review)]:
 path=p/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,sha(path.read_bytes()))
