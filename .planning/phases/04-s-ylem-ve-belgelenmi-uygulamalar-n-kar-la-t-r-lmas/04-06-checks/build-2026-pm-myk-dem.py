"""Kongre adayı geçerse ona iki ayrı 7 Eylül kurumsal işlemini ekler."""
import datetime,hashlib,json
from pathlib import Path
c=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p,r=c/'2026-congress-dem-draft.json',c/'2026-congress-dem-review-draft.json'
assert sha(p)=='41dcecda6759d881634fa06bb764ff73ebc76863a7176b9fe6823a95f986a6a2'
assert sha(r)=='4ff6002d431d89d1be21dd8af075a32780b1ed0603e04cfbeb7471da83f48613'
pkg,rev=json.loads(p.read_text()),json.loads(r.read_text())
entries=json.loads((c/'2026-pm-myk-records.json').read_text())['entries']
passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
versions={x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
now=datetime.datetime.now(datetime.timezone.utc).isoformat();q=lambda s:'0406-2026-pm-myk-'+s
def add(table,**values):pkg['practice_records'].setdefault(table,[]).append(values)
specs=[dict(key='myk',scope='practice-8cf3c5e8f9fd6b398460efa4830fa7af02b546cadc83f38f45f889d6a1178df5',topic='merkez-kurul-olusumu',common='dem-2026-09-07-pm-myk-belirlenmesi',title='Parti Meclisi toplantısı sonrası MYK üyelerinin belirlenmesi',text='Mezopotamya Ajansı, DEM Parti’nin 7 Eylül 2026 Parti Meclisi toplantısının ardından basın komisyonunun Merkez Yürütme Kurulu üyelerinin belirlendiğini açıkladığını bildirdi. Haberde toplantı tutanağı ve oylama yöntemi sunulmadı.',points=['meeting','announcement']),dict(key='kadin',scope='practice-18dd5f1dfb6192f19d34e66ba2cf772207ce39dfcad62f8bf8f4e2466f7f85bc',topic='kadin-meclisi',common='dem-2026-09-07-kadin-meclisi-koordinasyon',title='Kadın Meclisi sözcüsü ve koordinasyonunun belirlenmesi',text='Mezopotamya Ajansı, 7 Eylül 2026’da ayrıca toplanan DEM Parti Kadın Meclisinde Halide Türkoğlu’nun sözcü seçildiğini ve yeni Kadın Koordinasyonu üyelerinin belirlendiğini bildirdi. Haberde toplantı tutanağı ve oylama yöntemi sunulmadı.',points=['women'])]
for item in specs:
 key=item['key'];scope=item['scope'];event,finding,contribution,candidate=(q(key+'-'+x) for x in ('event','finding','contribution','candidate'));ids=[q(x) for x in item['points']]
 add('practice_scope_v2',id=scope,party_id='dem',topic_id=item['topic'],taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 7 Eylül 2026 toplantısı; ilgili organ kapsamı araştırması sürüyor.')
 entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=item['text'],provenance='summary',epistemic_type='claim')))
 for pid in ids:
  section=passages[pid]['section'];stage='action'
  entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='Haberin ilgili toplantı bölümü okundu.'))])
  add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=section,stage=stage,concrete_basis='7 Eylül 2026 Mezopotamya Ajansı haberi; haber parti açıklamasına atıf yapar.',limitation='Toplantı tutanağı ve oylama yöntemi henüz elde edilmedi.',epistemic_type='claim')
  add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
 entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ayrı toplantı ve kaynak atfı incelendi.')))
 add('practice_event',id=event,common_event_key=item['common'],event_at='2026-09-07',date_precision='day',date_unknown_reason=None,title=item['title'],scope_context='DEM Parti’nin 5. Olağan Büyük Kongresi sonrasındaki ayrı kurumsal toplantısı.',occurrence_basis='7 Eylül 2026 tarihli Mezopotamya Ajansı haberi; toplantı tutanağı elde edilmedi.')
 add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='İlgili parti organının işlemi; işlem yöntemi ve bireysel oylar kaynakta gösterilmiyor.')
 add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='İlgili tüzük nüshasının dönemsel yürürlüğü ve usul karşılaştırması ayrıca araştırılıyor.',passage_ids=json.dumps(ids,ensure_ascii=False))
 targets=[('practice_event_evidence',event+'|'+pid+'|action',[pid],passages[pid]['section']) for pid in ids]
 targets += [('practice_event',event,ids,'Ayrı toplantı ve açıklanan işlem.'),('practice_contribution',contribution,ids,'İlgili parti organı işlemi.'),('practice_contribution.finding_id',contribution,ids,'Haber atfı ve yöntem sınırı.'),('practice_candidate',candidate,ids,'Tüzük ve usul karşılaştırması açık.')]
 for typ,ident,refs,description in targets:
  rev['practice_source_review'].append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(passages[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(passages[x]['section'] for x in refs)),ensure_ascii=False),supported_claim=description,limitations='Haber parti açıklamasına dayanmaktadır; tutanak ve oylama yöntemi elde edilmedi.',result='reviewed',reason='İlgili haber bölümü okundu.'))
 vid=q('mezopotamya-v1');add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps([passages[x]['section'] for x in ids],ensure_ascii=False),inspected_at=now)
 add('practice_attempt_v2',id=q(key+'-reading'),scope_id=scope,attempted_at=now,query='DEM 7 Eylül 2026 Parti Meclisi MYK ve kadın koordinasyonu',url=versions[vid]['original_url'],result='examined',reason='İlgili toplantı haberi okundu; kurumsal işlemler ayrı tutuldu.',source_version_id=vid)
pkg['entries']+=entries
rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('2026-pm-myk-dem-draft.json',pkg),('2026-pm-myk-dem-review-draft.json',rev)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path))
