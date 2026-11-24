"""1 Temmuz 10/2879 başvurusunu ayrı, eşleşmemiş aday olarak hazırla."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text
from uygulamalar import practice_review_targets, validate_practice_source_review

c = Path(__file__).resolve().parent
root = c.parents[3]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base, review = root/'data/practices/04-dem.json', root/'data/practices/04-dem-review.json'
assert sha(base) == '04b06110aad4ff0dc7a4cf64155b0277114175e2255897c8c8ebc040da4ebd2e'
assert sha(review) == '5aa6e1feed4e99f638c2cb8503d976595e555c1e8c81f97f4f7b464519f9602e'
pkg, rev = json.loads(base.read_text()), json.loads(review.read_text())
captures = json.loads((c/'sivas-2879-source-capture.json').read_text())
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
q = lambda s: '0406-sivas-2879-'+s
scope = 'practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae'
existing_scope = next(x for x in pkg['practice_records']['practice_scope_v2'] if x['id'] == scope)
assert existing_scope['boundary_reason'].startswith('Yalnız 2 Temmuz 2025')
existing_scope['boundary_reason'] += ' Ayrıca 1 Temmuz 2025 10/2879 başvurusu incelendi; önceki söylem ve dosya sonucu araştırması açıktır.'
entries=[]
def entry(category, **v): entries.append(dict(kind=category, values=v))
def passage(name, version, exact, section, page=None):
    entry('passage', id=q(name), version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=page, printed_page=None)
for suffix, cap in zip(('register', 'signed'), captures):
    doc, version = q(suffix), q(suffix+'-v1')
    path=root/cap['original_path']; assert sha(path)==cap['sha256']
    reg = suffix=='register'
    entry('document', id=doc, party_id='dem', title='TBMM 10/2879 '+('esas kaydı' if reg else 'imzalı önerge'), source_kind='official')
    entry('document_version', id=version, document_id=doc, original_url=cap['source_url'], final_url=cap['source_url'], document_date=None if reg else '2025-07-01', date_precision='unknown' if reg else 'day', date_unknown_reason='Dinamik TBMM esas kaydının ilk yayın günü bilinmiyor.' if reg else None, version_label='TBMM özgün kaynak nüshası.', accessed_at=cap['accessed_at'], verified_at=now, mime='text/html' if reg else 'application/pdf', sha256=cap['sha256'], original_path='objects/'+cap['sha256']+'/'+('original.html.bin' if reg else 'original.pdf'), readable_path='objects/'+cap['sha256']+'/readable.html')
    entry('source_attribution',version_id=version,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=cap['source_url'],basis='TBMM esas kaydı ve imzalı evrak.')
    if reg:
        view=dict(cap['view']); view['version_id']=version; entry('archive_view', **view)
        raw=html_source_text(path.read_bytes())
        for name, exact, section in [('number','10 / 2879','Esas numarası'),('date','01/07/2025','Başkanlığa geliş tarihi'),('sponsor','Meral Dan&#x131;&#x15F; Be&#x15F;ta&#x15F; ve 20 Milletvekili','Önerge sahibi ve 20 milletvekili'),('status','G&#xFC;ndemde','Erişimde esas dosyasının durumu')]:
            assert exact in raw; passage(name,version,exact,section)
    else:
        assert '10/2879' in pdf_page_text(path,0); passage('signed-number',version,'10/2879','İmzalı önergenin esas numarası',0)
event, finding, contribution, candidate = (q(x) for x in ('event','finding','contribution','candidate'))
entry('finding', id=finding, party_id='dem', heading='Belgelenmiş uygulamalar', pair_id=finding, text='Meral Danış Beştaş ve 20 milletvekilinin Sivas Madımak olaylarının araştırılmasına ilişkin 10/2879 sayılı önergesi 1 Temmuz 2025’te TBMM Başkanlığına ulaştı. TBMM esas kaydı 24 Kasım 2026 erişiminde Gündemdeydi. Bu bireysel önerge 2 Temmuz tarihli 10/2880 grup önergesinden ayrıdır; araştırmanın açıldığı veya sonuçlandığı bu kayıtlardan çıkarılamaz.', provenance='summary', epistemic_type='claim')
ids=[q(x) for x in ('number','date','sponsor','status','signed-number')]
passages={e['values']['id']:e['values'] for e in entries if e['kind']=='passage'}
new={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(k,**v): new[k].append(v)
add('practice_event',id=event,common_event_key='tbmm-28-3-10-2879-filing',event_at='2025-07-01',date_precision='day',date_unknown_reason=None,title='10/2879 Sivas araştırma önergesinin sunulması',scope_context='Erzurum Milletvekili Meral Danış Beştaş ve 20 milletvekilinin Sivas Madımak olaylarının araştırılmasına ilişkin önergesi 1 Temmuz 2025’te TBMM Başkanlığına ulaştı.',occurrence_basis='TBMM 10/2879 esas kaydı ve imzalı önerge.')
for pid in ids:
    stage='result' if pid==q('status') else 'initiative';p=passages[pid]
    entry('finding_evidence',finding_id=finding,passage_id=pid,role='support')
    entry('verification',finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='TBMM esas kaydı ve altı sayfalık imzalı önerge görsel incelendi.')
    add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=p['section'],stage=stage,concrete_basis='TBMM esas kaydı ve imzalı önerge.',limitation='Gündemde durumu erişim anına aittir; araştırmanın açılması veya sonucu gösterilmez.',epistemic_type='claim')
    add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
entry('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Sicil ve imzalı dosya incelendi; ayrı 10/2880 grup gündemiyle karıştırılmadı.')
add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='unknown',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM milletvekillerinin bireysel önergesi; parti görevlendirmesi veya araştırmanın sonucu çıkarılmaz.')
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki bağımsız parti söylemi, dönemsel ilişki ve esas dosya süreci araştırması açıktır.',passage_ids=json.dumps(ids,ensure_ascii=False))
for cap,suffix in zip(captures,('register','signed')):
    vid=q(suffix+'-v1'); refs=[x for x in ids if passages[x]['version_id']==vid]
    add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps([passages[x]['section'] for x in refs],ensure_ascii=False),inspected_at=now)
    add('practice_attempt_v2',id=q(suffix+'-reading'),scope_id=scope,attempted_at=now,query='10/2879 Sivas araştırma önergesi',url=cap['source_url'],result='examined',reason='Sicil ve imzalı PDF’nin altı sayfası incelendi.',source_version_id=vid)
pkg['entries']+=entries
for k,rows in new.items(): pkg['practice_records'].setdefault(k,[]).extend(rows)
data=dict(pkg['practice_records'])
for e in pkg['entries']: data.setdefault(e['kind'],[]).append(e['values'])
selection={k:new[k] for k in ('practice_event','practice_event_evidence','practice_contribution','practice_candidate')}
targets=practice_review_targets(data,selection);allp={p['id']:p for p in data['passage']};reviews=[]
for (typ,ident),(refs,_) in targets.items():
    refs=sorted(refs); reviews.append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(allp[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(allp[x]['section'] for x in refs)),ensure_ascii=False),supported_claim='10/2879 başvuru ve sicil: '+typ+' / '+ident,limitations='Başvuru tarihi, erişimde durum ve araştırma sonucu ayrı; önceki söylem ilişkisi açık.',result='reviewed',reason='TBMM sicili ve imzalı önergenin altı sayfası incelendi.'))
validate_practice_source_review(data,reviews,selection=selection);rev['practice_source_review']+=reviews;rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('sivas-2879-dem-draft.json',pkg),('sivas-2879-dem-review-draft.json',rev)]:
    p=c/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(p))
print('SIVAS_2879_SOURCE_REVIEW_PASS',len(targets))
