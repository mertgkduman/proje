import copy, datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_text, readable_bytes

D = Path(__file__).parent
ROOT = Path('data/practices/sources/tip')
read = lambda p: json.loads(Path(p).read_text())
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
live = Path('data/practices/04-tip.json')
review_path = Path('data/practices/04-tip-review.json')
assert digest(live) == '8a5b7e203cce506e47ad140302e86c285270247aad0e41b42213ec2e1f2fa18e'
assert digest(review_path) == '849a75655d9c9d921d5fc9397a961e899136ab8ed4b3f95fcb2292c78ef72f02'
package, previous = read(live), read(review_path)
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def add(table, **values): entries.append(dict(kind=table, values=values))
captures = read(D/'69660-capture.json')
news = read(D/'fatura-bas-capture.json')
specs = [(news, 'speech', 'Baş’ın faturalar hakkında açıklaması', '2022-04-13', 'journalism'),
         (captures[0], 'question', '7/69660 yazılı soru', '2022-08-04', 'official'),
         (captures[1], 'answer', '7/69660 Bakanlık yanıtı', '2023-04-04', 'official'),
         (captures[2], 'detail', '7/69660 TBMM kayıt ekranı', None, 'official')]
for cap, key, title, date, kind in specs:
    doc = '0405-tip-fatura-'+key; vid=doc+'-v1'; sha=cap['sha256']; url=cap['url']
    ispdf=key in ('question','answer'); filename='original.pdf' if ispdf else 'original.html.bin'; raw=(ROOT/'objects'/sha/filename).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==sha
    readable=ROOT/'objects'/sha/'readable.html'
    if not readable.exists(): readable.write_bytes(readable_bytes(raw, 'pdf' if ispdf else 'html', legacy=False))
    add('document',id=doc,party_id='tip',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,version_label=title,accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf' if ispdf else 'text/html',sha256=sha,original_path=f'objects/{sha}/{filename}',readable_path=f'objects/{sha}/readable.html',date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ekranının yayın tarihi belirtilmemiştir.')
    add('source_attribution',version_id=vid,kind=kind,publisher='Bodrum Gündem' if key=='speech' else ('Enerji ve Tabii Kaynaklar Bakanlığı' if key=='answer' else 'Türkiye Büyük Millet Meclisi'),author=None,social_handle=None,published_at=date if key=='speech' else None,date_precision='day' if key=='speech' else 'unknown',public_url=url,basis='Haberin Baş’a atfettiği açıklama okundu.' if key=='speech' else 'TBMM özgün soru, Bakanlık yanıtı veya kayıt ekranı incelendi.')
    if not ispdf:
        view=copy.deepcopy(cap['view']); view['version_id']=vid
        add('archive_view',**view)
    if key=='speech':
        text=html_source_text(raw); exact='Devlet bir &#8220;genel&#8221; ödeme yapacaksa fahiş fatura zamlarının altında kalan yurttaşlara ödeyecek bunu'; section='13 Nisan 2022 açıklaması'; page=None
    elif key=='question':
        text=pdf_page_text(ROOT/'objects'/sha/filename,0); exact='Son üç ayda kaç hanenin ve işyerinin elektriği, borç nedeniyle kesilmiştir?'; section='İmzalı sorunun birinci sorusu'; page=0
    elif key=='answer':
        text=pdf_page_text(ROOT/'objects'/sha/filename,1); exact='81 ilimizde 2022 yılının Aralık ayı sonu itibarıyla borcu ödenmediği için elektriği kesik olan abone\nsayısına ilişkin veriler aşağıdaki tabloda yer almaktadır.'; section='Yanıtın il tablosu açıklaması'; page=1
    else:
        text=html_source_text(raw); exact='04.08.2022'; section='Başkanlığa geliş tarihi'; page=None
    assert exact in text,(key,exact)
    add('passage',id=doc+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)

topic='tuketici-haklari'; prefix='0405-tip-fatura-69660'; st=prefix+'-statement'; ev=prefix+'-event'; rel=prefix+'-relation'
sp='0405-tip-fatura-speech-p'; qp='0405-tip-fatura-question-p'; ap='0405-tip-fatura-answer-p'; dp='0405-tip-fatura-detail-p'
findings=[(prefix+'-summary','Baş, fatura zamlarından etkilenen yurttaşlara destek verilmesini savundu.','summary',[sp]),(prefix+'-quote','Devlet bir &#8220;genel&#8221; ödeme yapacaksa fahiş fatura zamlarının altında kalan yurttaşlara ödeyecek bunu','quote',[sp]),(prefix+'-question','Kadıgil, borç nedeniyle son üç ayda elektriği kesilen hane ve iş yerlerinin sayısını sordu.','summary',[qp,dp]),(prefix+'-answer','Bakanlık yanıtı, 2022 Aralık sonu itibarıyla borcundan dolayı elektriği kesik abonelere ilişkin il tablosu verdi.','summary',[ap]),(prefix+'-explanation','Baş’ın fatura desteği açıklamasından sonra Kadıgil elektrik kesintileri hakkında yazılı soru yöneltti. Yanıtın ay sonu stoku, sorulan üç aylık kesinti akışı değildir.','summary',[sp,qp,dp,ap])]
for fid,text,prov,pids in findings:
    add('finding',id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=st if fid in (prefix+'-summary',prefix+'-quote') else fid,text=text,provenance=prov,epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Açıklama, soru ve yanıtın ayrı tarihleri ve ölçüleri okundu.')
    for pid in pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='quotation' if prov=='quote' else 'support')
        add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün pasaj bağlamıyla okundu; PDF sayfaları görsel kontrol edildi.')
for kind in ('statement','event'):
    c=next(x for x in inventory['cells'] if x['party_id']=='tip' and x['topic_id']==topic and x['research_kind']==kind)
    if not any(x['id']==c['cell_id'] for x in records['practice_scope_v2']): records['practice_scope_v2'].append(dict(id=c['cell_id'],party_id='tip',topic_id=topic,taxonomy_version=4,period_start=c['period_start'],cutoff_at=c['cutoff_at'],research_kind=kind,boundary_reason='Fatura açıklaması, yazılı soru ve yanıt incelendi; diğer kaynak ve dönemler açık.'))
    if kind=='event': scope=c['cell_id']
records['practice_statement'].append(dict(id=st,party_id='tip',topic_id=topic,taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2022-04-13',date_precision='day',version_id='0405-tip-fatura-speech-v1',period_basis='13 Nisan 2022 tarihli Baş açıklaması.',uncertainty_reason='Açıklama belirli bir yasal düzenlemenin uygulandığını göstermez.',comparison_row_id='04-03-v3-0304-tip-program-scope-gida-etiket-row'))
records['practice_event'].append(dict(id=ev,common_event_key='tbmm-27-5-7-69660-elektrik-kesintisi',event_at='2022-08-04',date_precision='day',date_unknown_reason=None,scope_context='TBMM 27. dönem 7/69660 yazılı soru ve yanıtı',title='Elektrik kesintileri yazılı sorusu',occurrence_basis='TBMM soru belgesi, kayıt ekranı ve Bakanlık yanıtı.'))
for pid,stage,point in [(qp,'initiative','Kadıgil son üç aylık kesintileri sordu.'),(dp,'initiative','Soru 4 Ağustos 2022 tarihinde Başkanlığa geldi.'),(ap,'result','Bakanlık Aralık sonu kesik abone stokunu verdi.')]:
    records['practice_event_evidence'].append(dict(event_id=ev,passage_id=pid,supported_point=point,stage=stage,concrete_basis='Özgün TBMM kaydı veya Bakanlık yanıtı.',limitation='Aralık sonu stok üç aylık kesinti akışı değildir; uygulama etkisi çıkarılamaz.',epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=pid,stage=stage,basis_kind='document'))
records['practice_relation'].append(dict(id=rel,statement_id=st,event_id=ev,party_id='tip',topic_id=topic,scope_id=scope,comparability_reason='Açıklama fatura desteğine, sonraki soru fatura borcundan elektrik kesintilerine ilişkindir; farklı araçlardır.',target_finding_id=prefix+'-summary',result_finding_id=prefix+'-answer',explanation_finding_id=prefix+'-explanation',temporal_context='Nisan 2022 açıklaması, Ağustos 2022 sorusu ve Nisan 2023 yanıtı.',authority_context='Baş açıklama yaptı, Kadıgil yazılı soru sundu; yanıt Bakanlığa aittir.',uncertainty_reason='Soru desteğin uygulandığını veya açıklamadaki sayıları doğrulamaz; yanıt farklı zaman ve ölçü kullanır.'))
records['practice_candidate'].append(dict(id=prefix+'-candidate',scope_id=scope,event_id=ev,relation_id=rel,state='eligible',reason='Fatura desteği açıklaması ve sonraki ayrı denetim sorusu kaynaklarıyla incelendi.',passage_ids=json.dumps([sp,qp,dp,ap])))
for cap,key,title,date,kind in specs:
    vid='0405-tip-fatura-'+key+'-v1'; aid=prefix+'-attempt-'+key
    section=next(e['values']['section'] for e in entries if e['kind']=='passage' and e['values']['version_id']==vid)
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=cap['url'],relevance_reason=title,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=cap['url'],url=cap['url'],result='examined',reason=section+' okundu; kapsam açık.',source_version_id=vid))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items():
    if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'): data[table]=copy.deepcopy(rows)
    else: data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='tip')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    rows=[passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in rows})),passage_ids=json.dumps([x['id'] for x in rows]),inspected_sections=json.dumps(sorted({x['section'] for x in rows}),ensure_ascii=False),supported_claim='Fatura açıklaması, soru ve yanıtın ilgili pasajları incelendi.',limitations='Üç aylık akış ile Aralık sonu stok farklıdır; uygulama veya etki çıkarılmaz.',result='reviewed',reason=kind+' / '+identity+' özgün kaynakları incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='tip',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('fatura-69660-append-draft.json',package),('fatura-69660-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('FATURA_SEMANTIC_PASS',len(reviews),ev,rel)
