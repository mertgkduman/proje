"""İki ayrı 5472 komisyon önergesini canlı çiftin üstüne ekleyerek hazırlar."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import pdf_page_text

c = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
p = Path('data/practices/04-dem.json'); r = Path('data/practices/04-dem-review.json')
pkg, review = json.loads(p.read_bytes()), json.loads(r.read_bytes())
h = 'bb6077353f49dbf12c19679e9c883f302ef70165b2010c8bf9390be48e50789b'
assert hashlib.sha256(p.read_bytes()).hexdigest() == 'f83e519e11a5e94908a9e6de1e8c9a399394b7dbb6a0d90751e012a063ec0c9a'
assert hashlib.sha256(r.read_bytes()).hexdigest() == 'a9f5107c61565e9937e09b924767ee4cf5cdb1e60c95e2adc1398dbc1d6e650e'
f = Path('data/practices/sources/dem/objects') / h / 'original.pdf'
assert hashlib.sha256(f.read_bytes()).hexdigest() == h
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
ver = '0406-dem-5472-v1'; doc = '0406-dem-5472'; url = 'https://tbmm.gov.tr/Tutanaklar/TutanakGoster/5472'
base = json.loads((Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')/'fund-commission-source-records.json').read_text())['entries'][:3]
base[0]['values'].update(id=doc, party_id='dem'); base[1]['values'].update(id=ver, document_id=doc, accessed_at=now, verified_at=now); base[2]['values']['version_id']=ver
pages={i:pdf_page_text(f,i) for i in (0,81,99)}
def span(page, start, end):
    t=pages[page]; i=t.index(start); j=t.index(end,i)+len(end); return t[i:j]
specs=[
 ('cebir',81,'bb607735', 'tbmm-28-5-plan-butce-2026-10-14-2-3939-dem-cebren-tahsil','DEM’in 2/3939 için cebren tahsil önergesi','DEM milletvekilleri, 2/3939 teklifine bazı kazançların cebren tahsili ve geri kazanım hesabına aktarılmasına ilişkin fıkra eklenmesini önerdi; komisyon önergeyi kabul etmedi.', 'Tasfiyesine Karar Verilen Bazı Yatırım Fonları Hakkında Kanun Teklifi\'nin\n4\'üncü maddesine aşağıdaki fıkranın eklenmesini', 'Önerge kabul\nedilmemiştir.'),
 ('hisse',99,'bb607735','tbmm-28-5-plan-butce-2026-10-14-2-3939-dem-hisse-tazmin','DEM’in bağlantılı hisse yatırımcıları önergesi','DEM milletvekilleri fonlarla bağlantılı hisselerde zarar gören küçük yatırımcıların tazmin ve geri kazanım kapsamına alınmasını önerdi; komisyon önergeyi kabul etmedi.', "DEM PARTİ'nin bir önergesi vardır", 'Kabul edilmemiştir.')]
scope='practice-eef45ed112da730d31f83015964c900d73e2f2a0bd64ee6694e03dacdad1839e'
def add(kind, **v): pkg['practice_records'].setdefault(kind,[]).append(v)
for key,page,_,common,title,context,start,end in specs:
    text=span(page,start,end); pid='0406-dem-5472-'+key; event=pid+'-event'; finding=pid+'-finding'; contribution=pid+'-contribution'; candidate=pid+'-candidate'
    base.append(dict(kind='passage',values=dict(id=pid,version_id=ver,exact=text,prefix=None,suffix=None,article=None,section='Komisyon tutanağı: '+title,pdf_page_index=page,printed_page=str(page+1))))
    claim=context+' Önerge gerekçesinde yer alan fiil ve zarar iddiaları, bu ret kararıyla ayrıca doğrulanmış sayılmaz.'
    base.extend([dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=claim,provenance='summary',epistemic_type='claim')),dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='TBMM komisyon tutanağındaki ayrı önerge ve ret okundu.')),dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İki önerge, ret ve isnat ayrıldı.'))])
    add('practice_event',id=event,common_event_key=common,event_at='2026-10-14',date_precision='day',date_unknown_reason=None,scope_context=context,title=title,occurrence_basis='TBMM Plan ve Bütçe Komisyonu tutanağı.')
    add('practice_event_evidence',event_id=event,passage_id=pid,supported_point='DEM imzalı önerge ve komisyonun ret duyurusu',stage='result',concrete_basis='14 Ekim 2026 komisyon tutanağı.',limitation='Gerekçedeki isnatlar bağımsız olarak doğrulanmadı.',epistemic_type='claim')
    add('practice_evidence_assessment',event_id=event,passage_id=pid,stage='result',basis_kind='document')
    add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Üç milletvekilinin önergesi; komisyon reddetti, yasalaşma kanıtı değil.')
    add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki parti söylemiyle ayrı eşleştirme araştırması açık.',passage_ids=json.dumps([pid]))
    for kind,ident in [('practice_event_evidence',event+'|'+pid+'|result'),('practice_event',event),('practice_contribution',contribution),('practice_contribution.finding_id',contribution),('practice_candidate',candidate)]:
        review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([ver]),passage_ids=json.dumps([pid]),inspected_sections=json.dumps(['Komisyon tutanağı: '+title],ensure_ascii=False),supported_claim=context,limitations='Tekil önerge reddi; iddialar ve genel kurul nihai işlemi ayrıdır.',result='reviewed',reason='TBMM özgün tutanağı okundu: '+title))
add('practice_attempt_v2',id='0406-dem-5472-reading',scope_id=scope,attempted_at=now,query='14 Ekim 2026 komisyon 2/3939 DEM Adalet Kaya Kamuran Tanhan Hakkı Saruhan Oluç',url=url,result='examined',reason='Kapak ve iki ayrı önerge/ret sayfası okundu; bütün komisyon tutanağı incelenmedi.',source_version_id=ver)
add('practice_scope_source',scope_id=scope,version_id=ver,inspected_sections=json.dumps(['Kapak','PDF 81 ve 99: iki ayrı önerge'],ensure_ascii=False),inspected_at=now)
pkg['entries'] += base
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('5472-motions-draft.json',pkg),('5472-motions-review-draft.json',review)]:
    path=c/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,hashlib.sha256(path.read_bytes()).hexdigest())
