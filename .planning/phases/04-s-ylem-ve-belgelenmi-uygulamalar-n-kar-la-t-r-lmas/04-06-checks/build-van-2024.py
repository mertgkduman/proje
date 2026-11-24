import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:"0406-van-2024-"+x
base=root/"data/practices/04-dem.json";rp=root/"data/practices/04-dem-review.json"
assert sha(base)=="0f861578ff8e556d09e693cda410663d2a932a6b83d2dc1a98d01c30b3fccefc" and sha(rp)=="564da8c8b14818a1b4be591dd513564e926eaf0229366207f7fdfce91161de33"
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/"van-2024-capture.json").read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();scope="practice-e65794f6bf91077b14af9defd5619d256b99c44fc728f28f5fa36402c2e5d2ff"
entries=[]; records={k:[] for k in ('practice_scope_v2','practice_statement','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_relation','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v): entries.append(dict(kind=category,values=v))
records['practice_scope_v2'].append(dict(id=scope,party_id='dem',topic_id='yerel-demokrasi',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='2024 Van mazbata itirazı ve YSK sonucu incelendi. Kapsam araştırması sürüyor.'))
anchors={
 'dem-call':('dem','This erroneous ruling must be promptly overturned.','DEM MYK kararın kaldırılması çağrısı'),
 'dem-date':('dem','DEM Party Central Executive Board<br />2 April 2024','DEM MYK ve tarih'),
 'appeal-decision':('appeal','Van İl Seçim Kurulunun 02.04.2024 tarih ve 2024/25 sayılı','İtiraz metnindeki il kurulu kararı'),
 'appeal-request':('appeal','İtiraz Eden (Asil) Abdullah ZEYDAN<br />\nİtiraz Eden Vekili Av. Mahsuni KARAMAN<br />\nDEM Parti ikaz Yetkilisi Ay. Cihat DURMAZ','Basında yayımlanan başvuru ve aktörler'),
 'result':('result',"DEM Parti YSK Temsilcisi Mehmet Rüştü Tiryaki, YSK'nın, Van İl Seçim Kurulu'nun kararını kaldırarak mazbatanın Zeydan'a verilmesine karar verdiğini açıkladı.",'YSK kararının açıklanması')}
for key in ('dem','appeal','result'):
 x=cap[key];path=root/'data/practices/sources/dem'/x['original_path']; assert sha(path)==x['sha256'];raw=html_source_text(path.read_bytes());doc=q(key);vid=doc+'-v1';date='2024-04-02' if key=='dem' else '2024-04-03'
 add('document',id=doc,party_id='dem',title={'dem':'DEM MYK Van açıklaması','appeal':'Van itirazı basın metni','result':'YSK Van kararı haberi'}[key],source_kind='party' if key=='dem' else 'news')
 add('document_version',id=vid,document_id=doc,original_url=x['url'],final_url=x['url'],document_date=date,date_precision='day',date_unknown_reason=None,version_label='Özgün yayın gövdesi',accessed_at=x['accessed_at'],verified_at=when,mime='text/html',sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'])
 add('archive_view',**x['view']);add('source_attribution',version_id=vid,publisher={'dem':'HALKLARIN EŞİTLİK VE DEMOKRASİ PARTİSİ','appeal':'Sol Medya','result':'Bianet'}[key],author=None,kind='party_publication' if key=='dem' else 'journalism',published_at=date,date_precision='day',social_handle=None,public_url=x['url'],basis='Özgün yayın ve tarihli gövde incelendi.')
 keys=[k for k,v in anchors.items() if v[0]==key]
 for k in keys:
  _,exact,section=anchors[k];assert exact in raw,k;add('passage',id=q(k),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([anchors[k][2] for k in keys]),inspected_at=when))
 records['practice_attempt_v2'].append(dict(id=q(key+'-reading'),scope_id=scope,attempted_at=when,query='2 Nisan Van 2024/25 kararı ve 3 Nisan DEM itirazı ile YSK sonucu',url=x['url'],result='examined',reason='Açıklama, basın aktarımındaki başvuru ve haber sonucu ayrı okundu. İmzalı karar ve başvuru nüshası açık.',source_version_id=vid))
def finding(ident,text,refs,provenance='summary',pair=None):
 add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=pair or ident,text=text,provenance=provenance,epistemic_type='claim')
 for pid in refs:
  add('finding_evidence',finding_id=ident,passage_id=pid,role='support');add('verification',finding_id=ident,passage_id=pid,checked_at=when,result='confirmed',reason='Kaynakların tarih ve aktörleri ayrı okundu.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Parti açıklaması, başvuru ve karar sonucu ayrıldı.')
statement=q('statement');target=q('target');quote=q('quote');event=q('event');contribution=q('contribution');result=q('result-finding');explain=q('explanation');relation=q('relation')
finding(target,'DEM Parti Merkez Yürütme Kurulu, 2 Nisan 2024 tarihinde Van’da Abdullah Zeydan’a mazbata verilmemesine karşı ilgili kararın kaldırılmasını istedi.',[q('dem-call'),q('dem-date')])
finding(quote,'This erroneous ruling must be promptly overturned.',[q('dem-call')],provenance='quote',pair=target)
records['practice_statement'].append(dict(id=statement,party_id='dem',topic_id='yerel-demokrasi',taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2024-04-02',date_precision='day',version_id=q('dem-v1'),period_basis='DEM MYK açıklamasının özgün gövdesindeki 2 Nisan 2024 tarihi.',uncertainty_reason=None,comparison_row_id='04-03-v3-0305-dem-program-yerel-row'))
finding(result,'Bianet’in haberine göre YSK, 3 Nisan 2024’te Van İl Seçim Kurulu kararını kaldırdı ve mazbatanın Abdullah Zeydan’a verilmesine karar verdi.',[q('result')])
finding(explain,'DEM Parti MYK 2 Nisan’da kararın kaldırılmasını istedi. Basında aktarılan 3 Nisan itirazı Van İl Seçim Kurulunun 2024/25 sayılı kararını hedefledi. Aynı gün YSK bu kararı kaldırarak mazbatanın Abdullah Zeydan’a verilmesine karar verdi. Parti açıklaması, başvuru ve YSK kararı ayrı işlemlerdir. YSK kararının numarası ve imzalı metni burada doğrulanmadı.',[q('dem-call'),q('dem-date'),q('appeal-decision'),q('appeal-request'),q('result')])
records['practice_event'].append(dict(id=event,common_event_key='van-2024-04-03-ysk-mazbata-itirazi',event_at='2024-04-03',date_precision='day',date_unknown_reason=None,title='Van mazbata itirazı ve YSK kararı',scope_context='Van İl Seçim Kurulunun 2 Nisan 2024 tarihli 2024/25 kararı üzerine DEM Parti ve aday adına yapılan itirazın 3 Nisan’da YSK tarafından değerlendirilmesi.',occurrence_basis='3 Nisan tarihli Bianet haberi ve itiraz metnini aktaran Sol Medya yayını.'))
for key,stage in [('appeal-decision','initiative'),('appeal-request','action'),('result','result')]:
 pid=q(key);records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=anchors[key][2],stage=stage,concrete_basis='Basın aktarımı',limitation='İmzalı başvuru ve YSK kararının özgün metni ile YSK karar numarası doğrulanmadı.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=explain,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM itirazı ve temsilcisi basın aktarımına dayanır. YSK kararı bağımsız kurul işlemidir.'))
reason='İki kayıt aynı Van mazbata kararının kaldırılmasıyla ilgilidir. Önce MYK çağrısı, sonra ayrı başvuru ve kurul kararı vardır.'
records['practice_relation'].append(dict(id=relation,statement_id=statement,event_id=event,party_id='dem',topic_id='yerel-demokrasi',scope_id=scope,comparability_reason=reason,target_finding_id=target,result_finding_id=result,explanation_finding_id=explain,temporal_context='2 Nisan MYK açıklaması ve il kurulu kararı, 3 Nisan itirazı ve YSK kararı.',authority_context='Açıklama DEM MYK’ya, başvuru DEM ve adaya, sonuç YSK’ya aittir.',uncertainty_reason='YSK karar numarası ve imzalı gerekçe ile imzalı başvuru nüshası açık.'))
pids=[q(x) for x in anchors];records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=relation,state='eligible',reason=reason,passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-halic-2022-62621426/releases/659669de6cf0468e8b14fe3bf929f933/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('SEMANTIC_PASS',flush=True)
targets=practice_review_package_targets(data,records,pids,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='Van mazbata açıklaması ve itirazı '+kind+' '+ident,limitations='İmzalı başvuru ve YSK kararı ile karar numarası açık.',result='reviewed',reason='DEM yayını ve iki ayrı basın aktarımı okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];pkg['source_review_refs']=review['source_review_refs'];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('van-2024-dem-draft.json',pkg),('van-2024-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
