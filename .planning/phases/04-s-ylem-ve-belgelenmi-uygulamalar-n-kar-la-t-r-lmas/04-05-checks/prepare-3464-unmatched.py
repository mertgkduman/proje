import hashlib,json,re,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
from uygulamalar import practice_review_targets
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');root=Path('data/practices/sources/tip');live=Path('data/practices/04-tip.json');rev=Path('data/practices/04-tip-review.json');sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(live)=='0642fe49eff0995cf1a4943786be2e85ae6ec928f25659fb98b5d8548e9070b2' and sha(rev)=='c8c06a1438a97bdeb0be3630c8a972c81964228315fca245c2184fd70121e16f'
pkg=json.loads(live.read_text());review=json.loads(rev.read_text());now=datetime.now(timezone.utc).isoformat();entries=[];records={}
def add(k,v):entries.append(dict(kind=k,values=v))
def rec(k,v):records.setdefault(k,[]).append(v)
raw=json.loads(Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-11-checks/pension-floor-final-complete-source-records.json').read_text())['entries'];old='0411-floor-iyi-7573-50-v1';doc='0405-tip-3464-tutanak';vid=doc+'-v1'
oldversion=next(x['values'] for x in raw if x['kind']=='document_version' and x['values']['id']==old).copy();oldversion.update(id=vid,document_id=doc);add('document',dict(id=doc,party_id='tip',title='TBMM 50. birleşim 2/3464 tümü oylaması',source_kind='official'));add('document_version',oldversion)
view=next(x['values'] for x in raw if x['kind']=='archive_view' and x['values']['version_id']==old).copy();view['version_id']=vid;add('archive_view',view);add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=oldversion['original_url'],basis='2/3464 tümünün oylanması ve başkanın açıklaması incelendi; tutanak duyurusunun sayıları kesin cetvelden ayrıldı.'))
t=html_source_text((root/oldversion['original_path']).read_bytes());exact='BAŞKAN - Teklif kabul edilmiş ve kanunlaşmıştır.';assert exact in t;add('passage',dict(id=doc+'-accept-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Teklifin tümü ve kabul açıklaması',pdf_page_index=None,printed_page=None))
cap=json.loads((p/'3464-ballot-capture.json').read_text());h=cap['sha256'];url=cap['url'];raw=(root/'objects'/h/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==h;doc='0405-tip-3464-ballot';vid=doc+'-v1';cap['view']['version_id']=vid
add('document',dict(id=doc,party_id='tip',title='TBMM 2/3464 kesin açık oy cetveli',source_kind='official'));add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2026-01-23',version_label='TBMM kesin açık oy cetveli',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None));add('archive_view',cap['view']);add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Windows-1254 çözümünde üç TİP kişisel oy satırı ve kesin toplam okundu.'))
t=html_source_text(raw);rows=re.findall(r'<tr\b.*?</tr>',t,re.I|re.S)
for suffix,name,surname,vote in [('bas','Erkan','BA&#x15E;','RET'),('kadigil','Saliha Sera','KADIG&#x130;L','KATILMADI'),('sik','Ahmet','&#x15E;IK','KATILMADI')]:
 row=next(r for r in rows if '<td>'+name+'</td>' in r and '<td>'+surname+'</td>' in r and 'T&#xFC;rkiye' in r);assert '\ufffd' not in row and vote in row
 add('passage',dict(id=doc+'-'+suffix+'-p',version_id=vid,exact=row,prefix=None,suffix=None,article=None,section='TİP milletvekilinin kesin kişisel oy satırı',pdf_page_index=None,printed_page=None))
event='0405-tip-3464-event';candidate='0405-tip-3464-unmatched';con='0405-tip-3464-contribution';fid='0405-tip-3464-finding';base=doc+'-bas-p';kad=doc+'-kadigil-p';sik=doc+'-sik-p';accept='0405-tip-3464-tutanak-accept-p';refs=[base,kad,sik,accept];auth='0405-tip-20241106-bas-authority-p'
add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Erkan Baş 2/3464 teklifinin tümüne ret oyu verdi; Kadıgil ve Şık oylamaya katılmadı. Teklif kabul edildi.',provenance='summary',epistemic_type='claim'))
for ref in refs:add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='support'));add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Kesin kişisel oy ve başkanın teklifin tümüne ilişkin açıklaması ayrı incelendi.'))
add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ret ve katılmama kişisel oylar; kabul toplam sonucudur.'))
scope=next(x['id'] for x in pkg['practice_records']['practice_scope_v2'] if x['topic_id']=='sosyal-guvenlik' and x['research_kind']=='event')
rec('practice_event',dict(id=event,common_event_key='tbmm-28-4-050-2-3464-7573',event_at='2026-01-23',date_precision='day',date_unknown_reason=None,scope_context='28. dönem 50. birleşimde 2/3464 teklifinin tümü',title='2/3464 kanun teklifinin tümü oylaması',occurrence_basis='TBMM tam tutanak ve kesin açık oy cetveli.'))
for pid,stage,point in [(base,'action','Baş ret oyu'),(kad,'action','Kadıgil katılmadı'),(sik,'action','Şık katılmadı'),(accept,'result','Teklif kabul edildi')]:
 rec('practice_event_evidence',dict(event_id=event,passage_id=pid,supported_point=point,stage=stage,concrete_basis='TBMM kesin cetvel satırı veya başkan açıklaması.',limitation='Teklifin tümüne verilen oy tek bir maddenin gerekçesini kanıtlamaz; katılmama ret değildir.',epistemic_type='claim'));rec('practice_evidence_assessment',dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
rec('practice_contribution',dict(id=con,event_id=event,party_id='tip',actor_id='0405-tip-kayyum-bas',contribution_kind='objection',finding_id=fid,authority_passage_id=auth,membership_passage_id=None,responsibility_limit='Baş’ın kişisel ret oyudur; diğer iki vekil oylamaya katılmadı ve belirli maddeye gerekçe gösterilmedi.'))
rec('practice_actor_period',dict(contribution_id=con,valid_from='2024-11-06',valid_to='2026-01-23',identity_passage_id=auth))
rec('practice_attempt_v2',dict(id='0405-tip-3464-tutanak-okuma',scope_id=scope,attempted_at=now,query='TBMM 2/3464 tümü açık oy cetveli, TİP satırları ve sonuç',url=url,result='examined',reason='Üç kişisel oy ve kabul açıklaması okundu; önceki özel gerekçe bulunmadı.',source_version_id=vid))
rec('practice_scope_source',dict(scope_id=scope,version_id=vid,inspected_sections=json.dumps(['Baş, Kadıgil ve Şık kişisel oy satırları','Kesin açık oy toplamları'],ensure_ascii=False),inspected_at=now))
rec('practice_candidate',dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='2019 ve 2022 EYT yaş koşulu söylemi ile 2026 torba kanunun tümüne ret oyu farklı konulardır; ret oyuna belirli madde gerekçesi atfedilmez. Önceki uygun doğrudan söylem araştırması açık.',passage_ids=json.dumps(refs,ensure_ascii=False)))
pkg['entries'].extend(entries)
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for e in pkg['entries']:data.setdefault(e['kind'],[]).append(e['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for k in ('finding_evidence','passage'):data.setdefault(k,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+k))
versions={x['id']:x['version_id'] for x in data['passage']};targets=practice_review_targets(data,records)
for (kind,identity),(ps,parties) in targets.items():
 row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in ps})),passage_ids=json.dumps(sorted(ps)),inspected_sections=json.dumps(['TİP kişisel oy satırları','Başkanın teklifin tümüne ilişkin kabul açıklaması'],ensure_ascii=False),supported_claim='Bu hedefin oy, sonuç ve eşlenmeme sınırı ayrı incelendi: '+identity,limitations='2019–2022 EYT yaş koşulu ile 2026 tüm teklif oyu eşit değildir; belirli madde gerekçesi gösterilmedi.',result='reviewed',reason='Bu hedefe bağlı özgün pasajlar incelendi: '+kind+' '+identity);review['practice_source_review'].append(row);review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('3464-unmatched-draft.json',pkg),('3464-unmatched-review-draft.json',review)]:(p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
