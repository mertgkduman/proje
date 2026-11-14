import datetime
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

root = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2/original.pdf')
version = '0210-demokrat-program-archive-v1'
pages = [pdf_page_text(pdf,i) for i in range(83)]
taxonomy = {r['values']['topic_id']:r['values'] for r in json.loads(Path('data/comparisons/03-taxonomy.json').read_text())['records'] if r['kind']=='comparison_topic' and r['values']['domain']=='program'}
specs = defaultdict(list)
for n,line in enumerate((root/'03-13-specs.tsv').read_text().splitlines(),1):
    page,topic,kind,anchor,summary = line.split('|')
    page=int(page); text=pages[page-1]
    m=re.search(re.escape(anchor).replace(r'\ ',r'\s+'),text,re.IGNORECASE)
    assert m,(n,page,topic,anchor)
    starts=[x.end() for x in re.finditer(r'(?<!\d)[.!?](?=\s)',text[:m.start()])]
    start=starts[-1] if starts else 0
    end=m.end()
    if not anchor.endswith(('.', '?', '!')):
        tail=re.search(r'(?<!\d)[.!?](?=\s|$)',text[end:])
        end=end+tail.end() if tail else len(text)
    quote=text[start:end].strip()
    quote=re.sub(r'^\d+\s*\n','',quote)
    if page==18 and topic in ('aile-politikalari','demokrasi-katilim'):
        start=text.rfind('•',0,m.start()); end=text.find('\n•',m.end())
        quote=text[start+1:end if end>=0 else len(text)].strip().rstrip(',')
    if page==58 and topic=='okul-oncesi-egitim':
        start=text.index('Bu cümleden olarak,'); quote=text[start:end].strip()
    if page==71 and topic=='bakim-ebeveyn-izni' and 'DİYSE Modeli' in quote:
        quote=quote[:quote.index('Ebeveyn)')+len('Ebeveyn)')]
    if page==66 and topic=='cocuk-haklari' and 'aile içi şiddetin' in quote:
        start=text.index('Belediyeler ve okullar'); quote=text[start:end].strip()
    specs[topic].append(dict(n=n,page=page,kind=kind,summary=summary,quote=quote))
absence={}
for line in (root/'03-13-absence.tsv').read_text().splitlines():
    owner,topic,question=line.split('|'); absence[topic]=(int(owner),question)
assert set(specs)|set(absence)==set(taxonomy) and not set(specs)&set(absence)
part1=set('demokrasi-katilim anayasa-yapimi anayasal-denetim senato yaribaskanlik-sistemi secim-siyasi-partiler siyasal-ittifaklar genel-secim-oy diaspora yerel-demokrasi kamu-hesap-verebilirlik seffaflik-yolsuzluk kamu-istisare ifade-basin-ozgurlugu medya ayrimcilik-cogulculuk cinsel-yonelim inanc-mezhep-esitligi laiklik islam-inanc-orgutlenmesi anadil-hakki anadilde-egitim sivil-toplum yargi-bagimsizligi avrupa-birligi ic-guvenlik terorle-mucadele dis-guvenlik guvenlik kurt-sorunu dis-politika bm-guvenlik-konseyi nato-iliskileri abd-iliskileri rusya-iliskileri turk-cumhuriyetleri karadeniz-isbirligi eko-isbirligi kibris iran-iliskileri komsularla-iliskiler dijital-katilim savunma-sanayi uluslararasi-ekonomik-kurumlar program-dusunsel-temel turkiye-cumhuriyet-tarih'.split())
records={1:[],2:[]}; decisions={1:[],2:[]}; cross=[]; equivalent={}; supplement_pages=defaultdict(set); supplements=defaultdict(list)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()

def add(part,kind,values): records[part].append(dict(kind=kind,values=values))
def semantic(part,kind,subject,reason,pids):
    x=dict(subject_kind=kind,subject_id=subject,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason=reason)
    add(part,'comparison_semantic_review',x); decisions[part].append({**x,'passage_ids':pids})
def add_passage(part,pid,page,quote,section='Parti programı'):
    add(part,'passage',dict(id=pid,version_id=version,exact=quote,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page-1,printed_page=str(page+6)))
def add_field(part,row,topic,spec):
    n=spec['n']; tag=f'0313-demokrat-{n:03d}-{topic}'; pid=tag+'-p'; fid=tag+'-f'; sf=tag+'-s'; qf=tag+'-q'; pair=tag+'-pair'
    add_passage(part,pid,spec['page'],spec['quote'])
    pids=[pid]
    if topic=='yargi-bagimsizligi' and spec['page']==21 and 'Teftiş' in spec['quote']:
        p2=pid+'-devam'; add_passage(part,p2,22,'Savcılar Yüksek Kurulu’na bağlı olacaktır.'); pids.append(p2)
    if topic=='tarim-hayvancilik' and spec['page']==40 and 'tarım dışı' in spec['quote']:
        p2=pid+'-once'; text=pages[38]; start=text.index('1. ve 2. Sınıf tarım toprakları'); add_passage(part,p2,39,text[start:].strip()); pids.append(p2)
    if topic=='cocuk-haklari' and spec['page']==65 and 'hiçbir çocuğun' in spec['quote']:
        p2=pid+'-devam'; text=pages[65]; end=text.index('.')+1; add_passage(part,p2,66,text[:end].strip()); pids.append(p2)
    if topic=='rusya-iliskileri' and spec['page']==80 and spec['quote'].startswith('hassa'):
        p2=pid+'-once'; text=pages[78]; start=text.rindex('Türkiye, Rusya Federasyonu’yla'); add_passage(part,p2,79,text[start:].strip()); pids.append(p2)
    if topic=='doga-ekoloji' and spec['page']==76 and 'karbon vergisi' in spec['quote']:
        p2=pid+'-once'; text=pages[74]; start=text.index('Demokrat Parti iktidarında yerli sanayimizin'); add_passage(part,p2,75,text[start:].strip()); pids.append(p2)
    reason=(f"PDF {spec['page']}, basılı {spec['page']+6}: {spec['summary']} "
            'Bu, erişilen program nüshasında kaynaklı öneri veya yaklaşımdır; uygulama ve kabul tarihi varsayılmamıştır.')
    if len(pids)>1 and part==2: reason+=' Cümlenin sayfalar arasındaki devamı iki kaynak pasajıyla birlikte incelendi.'
    key=(part,row,spec['kind'],spec['summary'])
    if key in equivalent:
        old_sf,old_decision=equivalent[key]
        for link in pids: add(part,'finding_evidence',dict(finding_id=old_sf,passage_id=link,role='support'))
        old_decision['passage_ids'].extend(pids)
        source_owner=1 if spec['page']<=30 or 55<=spec['page']<=56 or spec['page']>=77 else 2
        if source_owner!=part: cross.append(dict(topic=topic,pdf_page=spec['page'],source_owner=source_owner,topic_owner=part,status='reviewed-equivalent',passage_id=pid))
        return
    for finding,body,provenance,role in ((sf,spec['summary'],'summary','support'),(qf,spec['quote'],'quote','quotation')):
        add(part,'finding',dict(id=finding,party_id='demokrat',heading='Program',pair_id=pair,text=body,provenance=provenance,epistemic_type='claim'))
        for link in (pids if provenance=='summary' else [pid]): add(part,'finding_evidence',dict(finding_id=finding,passage_id=link,role=role))
        add(part,'review',dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason=reason))
    condition = ('Birleşmenin olmaması' if topic=='kibris' and 'olmazsa' in spec['summary'] else
                 'Düşük ücretli ve niteliği az işte veya düşük gelirli tarımsal işte çalışma' if topic=='sosyal-guvenlik' and 'sosyal sigorta' in spec['summary'] else
                 'Düşük gelirli tarımsal işte çalışma' if topic=='tarim-iscisi' and 'sosyal sigorta' in spec['summary'] else
                 'Belgelendirme' if topic=='maliye-vergi' and 'belgelendirme koşuluyla' in spec['summary'] else
                 'Nüfusu 50 bini aşan yerler' if topic=='toplumsal-cinsiyet' and '50 bini' in spec['summary'] else
                 'Emisyonlarını kısıtlamayan ülkelerden ithalat' if topic=='doga-ekoloji' and 'karbon vergisi' in spec['summary'] else
                 'Birden fazla üniversite öğrencisi ve ihtiyaç durumu' if topic=='aile-politikalari' and 'birden fazla üniversite' in spec['summary'] else
                 '15 yaşından küçük' if topic=='cocuk-haklari' and '15 yaşından küçük' in spec['summary'] else None)
    add(part,'comparison_field',dict(id=fid,row_id=row,field=spec['kind'],summary_finding_id=sf,quote_finding_id=qf,condition_key=condition))
    semantic(part,'comparison_field',fid,reason,pids)
    equivalent[key]=(sf,decisions[part][-1])
    source_owner=1 if spec['page']<=30 or 55<=spec['page']<=56 or spec['page']>=77 else 2
    if source_owner!=part: cross.append(dict(topic=topic,pdf_page=spec['page'],source_owner=source_owner,topic_owner=part,status='reviewed',passage_id=pid))

for topic,entries in specs.items():
    part=1 if topic in part1 else 2
    row=f'0313-demokrat-{topic}'; organ='Program'; level=taxonomy[topic]['applicable_levels']
    if topic in ('kamu-istisare','seffaflik-yolsuzluk','kamu-hesap-verebilirlik','dijital-katilim','sosyal-hizmet'): level='yerel'
    if topic=='uluslararasi-ekonomik-kurumlar': level='uluslararası'
    if topic=='demokrasi-katilim': row='03-v2-demokrat-demokrasi'; organ='Siyasal katılım'; level='ulusal ve yerel'
    if topic=='temel-yurttaslik-geliri': row='03-v2-demokrat-temel-yurttaslik-geliri'; organ='Gelir desteği'; level='ulusal'
    add(part,'comparison_row',dict(id=row,topic_id=topic,taxonomy_version=2,party_id='demokrat',level=level,organ=organ,version_id=version,alternative_group=None,source_role='program',state='evidence',scope_id=None,missing_id=None,selection_reason='29.12.2021 arşiv yakalamalı Demokrat Parti program nüshası; kabul ve güncellik tarihi bilinmiyor.'))
    for spec in entries: add_field(part,row,topic,spec)
for n,line in enumerate((root/'03-13-supplement.tsv').read_text().splitlines(),1001):
    page,topic,kind,anchor,summary=line.split('|'); page=int(page); text=pages[page-1]
    assert topic in part1 and topic in specs
    match=re.search(re.escape(anchor).replace(r'\ ',r'\s+'),text,re.IGNORECASE)
    assert match,(page,topic,anchor)
    starts=[x.end() for x in re.finditer(r'(?<!\d)[.!?](?=\s)',text[:match.start()])]
    start=starts[-1] if starts else 0; end=match.end()
    if not anchor.endswith(('.', '?', '!')):
        tail=re.search(r'(?<!\d)[.!?](?=\s|$)',text[end:]); end=end+tail.end() if tail else len(text)
    quote=re.sub(r'^\d+\s*\n','',text[start:end].strip())
    row='03-v2-demokrat-demokrasi' if topic=='demokrasi-katilim' else f'0313-demokrat-{topic}'
    item=dict(n=n,page=page,kind=kind,summary=summary,quote=quote)
    add_field(2,row,topic,item); supplements[topic].append(item)
    supplement_pages[topic].add(page)
for topic,(part,question) in absence.items():
    scope=f'0313-demokrat-scope-{topic}'
    reason=f'Erişilen program nüshasının 1–83. PDF sayfaları {question} açısından incelendi; bu dar soruda açık ifade saptanmadı. Sonuç yalnız incelenen nüsha ve soruyla sınırlıdır.'
    add(part,'comparison_review_scope',dict(id=scope,party_id='demokrat',version_id=version,sections='Arşiv programının PDF 1–83 sayfaları, önsöz/sunuş ve 1–7. bölümler',query_terms=question,reviewed_at=now,result='no_explicit_statement',reason=reason))
    add(part,'comparison_row',dict(id=scope+'-row',topic_id=topic,taxonomy_version=2,party_id='demokrat',level=taxonomy[topic]['applicable_levels'],organ='Program',version_id=version,alternative_group=None,source_role='program',state='no_explicit_statement',scope_id=scope,missing_id=None,selection_reason=reason))
    semantic(part,'comparison_review_scope',scope,reason,[])

absence_context=defaultdict(list)
for n,line in enumerate((root/'03-13-absence-context.tsv').read_text().splitlines(),1):
    topic,page,anchor=line.split('|'); page=int(page); assert topic in absence
    text=pages[page-1]; match=re.search(re.escape(anchor).replace(r'\ ',r'\s+'),text,re.IGNORECASE)
    assert match,(topic,page,anchor)
    starts=[x.end() for x in re.finditer(r'(?<!\d)[.!?](?=\s)',text[:match.start()])]
    start=starts[-1] if starts else 0; end=match.end()
    if not anchor.endswith(('.', '?', '!')):
        tail=re.search(r'(?<!\d)[.!?](?=\s|$)',text[end:]); end=end+tail.end() if tail else len(text)
    quote=re.sub(r'^\d+\s*\n','',text[start:end].strip())
    pid=f'0313-demokrat-absence-context-{n:02d}-p'
    add_passage(2,pid,page,quote,'İncelenen bağlam; dar soruya olumlu yanıt değildir')
    absence_context[topic].append(pid)
assert set(absence_context)==set(absence),(set(absence)-set(absence_context))
for decision in decisions[2]:
    if decision['subject_kind']=='comparison_review_scope':
        topic=decision['subject_id'].removeprefix('0313-demokrat-scope-')
        decision['passage_ids'].extend(absence_context[topic])
        decision['reason']+=' Bağlam pasajı dar soruya olumlu yanıt değildir.'
(root/'03-13-absence-context-draft.json').write_text(json.dumps(absence_context,ensure_ascii=False,indent=2)+'\n')

visual_evidence=[]
visuals=[
 ('anayasal-denetim',26,'Senato, yasama',8,'yasama faaliyetlerinin anayasaya uygunluk denetimini yapacak ikinci bir meclisin, yani “Senato”nun kurulmasını kaçınılmaz görmekteyiz.'),
 ('secim-siyasi-partiler',27,'Seçimlerde ülke barajını',8,'seçimlerde ülke barajının temsilde adaleti sağlayacak bir orana indirilmesini'),
 ('dis-guvenlik',56,'ülke savunmasının',83,'Ülke savunması, siyaset ve partiler üstü bir konu olarak ele alınmalı...'),
 ('kamucu-planli-ekonomi',32,'ne kapalı ve devletçi',83,'Kapalı, devletçi bir ekonomiye de vahşi kapitalizme de karşıyız...'),
 ('egitime-erisim',58,'herkesin okul öncesinden',1,'Herkes, hiçbir ayrımcılığa tâbi tutulmadan eğitim alabilmelidir...'),
 ('dis-politika',82,'stratejik özel-',83,'Ülkenin stratejik özelliğini, barış ve istikrar için kullanacağız...'),
 ('genclik',11,'ceğini en güzel şekilde',83,'Umutsuzluğu yenmek ve gençliğimizin,geleceğini en güzel şekilde bu topraklar üzerinde kurmasını sağlamaktır.'),
 ('secim-siyasi-partiler',27,'“Yönetimde İstikrar, Tem-',1,'Demokrat Parti, “temsilde adalet, yönetimde istikrarı” sağlayacak...'),
 ('demokrasi-katilim',17,'barış içinde bir arada yaşama',1,'“Demokrat Parti” barış içinde birarada yaşama projesinin adıdır...')]
for n,(topic,source_page,anchor,page,quote) in enumerate(visuals,1):
    entry=next(x for x in specs[topic]+supplements[topic] if x['page']==source_page and anchor in x['quote'])
    pid=f'0313-demokrat-image-{n:02d}-p'; summary_id=f"0313-demokrat-{entry['n']:03d}-{topic}-s"
    add(2,'passage',dict(id=pid,version_id=version,exact=quote,prefix=None,suffix=None,article=None,section='Kapak veya önsöz görseli',pdf_page_index=page-1,printed_page='14' if page==8 else None))
    add(2,'manual_passage',dict(passage_id=pid,checked_at=now,method='Özgün PDF sayfası Poppler-glib ve Cairo ile görüntülenerek görsel okundu.',reason='Bu sayfanın metin katmanı boştur; görünen ifade kaynak görselinden aktarıldı.'))
    add(2,'finding_evidence',dict(finding_id=summary_id,passage_id=pid,role='support'))
    visual_evidence.append(dict(topic_id=topic,summary_finding_id=summary_id,passage_id=pid,pdf_page=page,review='Görsel tekrar aynı kaynaklı öneriye ek kanıt olarak bağlandı.'))
    cross.append(dict(topic=topic,pdf_page=page,source_owner=1,topic_owner=1 if topic in part1 else 2,completion_task=2,status='reviewed-visual-equivalent',passage_id=pid))
(root/'03-13-visual-evidence-draft.json').write_text(json.dumps(visual_evidence,ensure_ascii=False,indent=2)+'\n')

history=[
 ('secim-siyasi-partiler','0210-demokrat-democracy-program1-v1',10,'Seçim Kanunu','Çoğunluğun tercihini yansıtması için, gerek genel, gerekse mahallî seçimler iki turlu yapılacaktır.', 'DYP II. Demokrasi Programı genel ve yerel seçimlerde iki turlu sistemi önerir.'),
 ('yargi-bagimsizligi','0210-demokrat-democracy-program2-v1',5,'Hâkimler ve Savcılar Yüksek Kurulu','Hakimler ve Savcılar Yüksek Kurulu, Hakimler ve Savcılar Yüksek Kurulları olarak ayrılacak ve bağımsızlaştırılarak, siyasî etkilerden uzaklaştırılacaktır.','DYP II. Demokrasi Programı ayrı hâkim ve savcı kurulları önerir.'),
 ('cezaevleri','0210-demokrat-democracy-program2-v1',15,'Cezaevlerinin Islahı','Cezaevlerinde hücre ve büyük koğuş yerine, daha yaşanabilir şartlara sahip bir kaç kişilik küçük odalardan oluşan sisteme geçilecektir.','DYP II. Demokrasi Programı hücre ve büyük koğuş yerine birkaç kişilik küçük odalar önerir.'),
 ('yerel-demokrasi','0210-demokrat-old1985-v1',87,'Program madde 20 — Mahallî İdareler','Belirli zaruri kamu hizmetlerinin sağlanamamasında gerektiğinde genel bütçeden yardım yapılmalıdır.','1985 DYP programı belirli zorunlu yerel hizmetler sağlanamadığında gerektiğinde genel bütçe yardımı önerir.'),
 ('sagliga-erisim','0210-demokrat-old1985-v1',102,'Program madde 45 — Sağlık Hizmetlerinin Yaygınlaştırılması','Bütün vatandaşların genel ve mecburi sağlık sigortası kapsamına alınmasını, yoksulların sigorta primlerinin Devlet tarafından karşılanmasını','1985 DYP programı bütün vatandaşlara zorunlu sağlık sigortası ve yoksulların primlerinin devletçe karşılanmasını önerir.'),
 ('yerel-demokrasi','0210-demokrat-old1983-v1',89,'Program madde 19 — Mahallî İdareler','Belirli zaruri kamu hizmetlerinin sağlanamamasında gerektiğinde genel bütçeden yardım yapılmalıdır.','1983 DYP programı belirli zorunlu yerel hizmetler sağlanamadığında gerektiğinde genel bütçe yardımı önerir.'),
 ('yerel-demokrasi','0210-demokrat-old1988-v1',102,'Program madde 20 — Mahallî İdareler','Belirli zaruri kamu hizmetlerinin sağlanamamasında gerektiğinde genel bütçeden yardım yapılmalıdır.','1988 kataloglu DYP programı belirli zorunlu yerel hizmetler sağlanamadığında gerektiğinde genel bütçe yardımı önerir.'),
 ('yerel-demokrasi','0210-demokrat-old1990-v1',102,'Program madde 20 — Mahallî İdareler','Belirli zaruri kamu hizmetlerinin sağlanamamasında gerektiğinde genel bütçeden yardım yapılmalıdır.','1990 kataloglu DYP programı belirli zorunlu yerel hizmetler sağlanamadığında gerektiğinde genel bütçe yardımı önerir.')]
for n,(topic,v,page,section,quote,summary) in enumerate(history,1):
    part=2; tag=f'0313-demokrat-history-{n:02d}'; row=tag+'-row'; pid=tag+'-p'; sf=tag+'-s'; qf=tag+'-q'; fid=tag+'-f'; pair=tag+'-pair'
    label = ('14 Mayıs 1985 kongresinde kabul edilmiş DYP programı.' if 'old1985' in v else
             'Kataloglanan ayrı DYP program nüshası; katalog ve kabul tarihi aynı varsayılmaz.' if '-old' in v else
             'DYP II. Demokrasi Programı, kataloglu ayrı tarihsel kitapçık; kesin tarih ve ara sıralama bilinmiyor.')
    add(part,'comparison_row',dict(id=row,topic_id=topic,taxonomy_version=2,party_id='demokrat',level=taxonomy[topic]['applicable_levels'],organ='Program',version_id=v,alternative_group=None,source_role='historical',state='evidence',scope_id=None,missing_id=None,selection_reason=label))
    printed = page-5 if 'old1983' in v or 'old1985' in v else page-1 if 'old1988' in v or 'democracy-program' in v else page-2
    add(part,'passage',dict(id=pid,version_id=v,exact=quote,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page-1,printed_page=str(printed)))
    add(part,'manual_passage',dict(passage_id=pid,checked_at=now,method='Özgün PDF sayfası Poppler-glib ve Cairo ile görüntülenerek görsel okundu.',reason='Taranmış kitapçığın metin katmanı boştur.'))
    for f,text,prov,role in ((sf,summary,'summary','support'),(qf,quote,'quote','quotation')):
        add(part,'finding',dict(id=f,party_id='demokrat',heading='Program',pair_id=pair,text=text,provenance=prov,epistemic_type='claim'))
        add(part,'finding_evidence',dict(finding_id=f,passage_id=pid,role=role))
        add(part,'review',dict(id='review-'+f,kind='finding',subject_id=f,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason=summary))
    add(part,'comparison_field',dict(id=fid,row_id=row,field='instrument',summary_finding_id=sf,quote_finding_id=qf,condition_key=None))
    semantic(part,'comparison_field',fid,summary,[pid])

def spec_pid(topic,page,contains):
    entry=next(x for x in specs[topic] if x['page']==page and contains in x['quote'])
    return f"0313-demokrat-{entry['n']:03d}-{topic}-p"
backfill={1:[],2:[
    dict(topic='Asgari nakit gelir desteğinin kapsamı',source_version=version,passage_ids=[spec_pid('temel-yurttaslik-geliri',45,'asgari nakit')],backfill_plan='03-14',scope='Her vatandaş için iş, aş ve asgari nakit gelir desteği; eşit ödeme, gelir eşiği ve diğer uygulama koşulları belirtilmez. Gelirsiz yurttaş tanımıyla kapsam farkı kontrol edilmeli.'),
    dict(topic='Düşük gelirli çalışanlara sosyal sigorta',source_version=version,passage_ids=[spec_pid('sosyal-guvenlik',69,'tarımsal')],backfill_plan='03-14',scope='Düşük ücretli ve niteliği az işlerde çalışanlar ile düşük gelirli tarımsal işlerde çalışanlara asgari gelir sağlayan sosyal sigorta, genel nakit destekten ayrı kapsamdadır.'),
    dict(topic='Yenilenebilir, nükleer ve kömür kaynakları',source_version=version,passage_ids=[spec_pid('doga-ekoloji',41,'jeotermal'),spec_pid('nukleer-enerji',41,'nükleer'),spec_pid('madencilik',42,'kömür')],backfill_plan='03-14',scope='Yenilenebilir yatırımı, nükleer destek ve kömür kullanım teşviki ayrı araçlardır; fosilden çıkış veya net sıfır sonucu çıkarılmaz.'),
    dict(topic='2020 emisyon hedefinin karşılaştırma tabanı',source_version=version,passage_ids=[spec_pid('doga-ekoloji',75,'2020')],backfill_plan='03-14',scope='2020 için değişiklik yapılmaması halinde öngörülen seviyenin yüzde 20 altında emisyon hedefidir; mutlak azaltım veya net sıfır değildir.'),
    dict(topic='İthalatta karbon vergisi',source_version=version,passage_ids=[spec_pid('doga-ekoloji',76,'karbon vergisi')+'-once',spec_pid('doga-ekoloji',76,'karbon vergisi')],backfill_plan='03-14',scope='Emisyonlarını kısıtlamayan ülkelerden ithalat koşulu ve önceki sayfadaki cümle devamı korunmalıdır.') ]}
for n,(page,anchor,name,scope) in enumerate([
    (61,'fedakâr öğretmenlerimizin eğitimleri','Öğretmenlerin mesleki gelişimi','Hizmet içi eğitim ve yaşam standartlarının yükseltilmesi; ücretsiz öğrenci erişimiyle eşitlenmez.'),
    (60,'müfredat içeriklerinde yapılması zorunlu','Müfredat ve ders ağırlıkları','Fen, sosyal bilimler, yabancı dil ve bilişim derslerinin ortaöğretimdeki ağırlığı; ücretli veya ücretsiz erişim sonucu değildir.')],1):
    text=pages[page-1]; m=re.search(re.escape(anchor).replace(r'\ ',r'\s+'),text,re.IGNORECASE); assert m,(page,anchor)
    starts=[x.end() for x in re.finditer(r'(?<!\d)[.!?](?=\s)',text[:m.start()])]; start=starts[-1] if starts else 0
    end=re.search(r'(?<!\d)[.!?](?=\s|$)',text[m.end():]); end=m.end()+end.end() if end else len(text)
    pid=f'0313-demokrat-backfill-{n:02d}-p'; add_passage(2,pid,page,text[start:end].strip())
    backfill[2].append(dict(topic=name,source_version=version,passage_ids=[pid],backfill_plan='03-14',scope=scope))
for part in (1,2):
    payload=dict(contract_version=1,taxonomy_version=2,stage='partial',status='in_progress',note='Demokrat Parti arşiv programı: 83 PDF sayfası; 29.12.2021 yakalama kabul veya güncellik tarihi değildir.',backfill_candidates=backfill[part],records=records[part])
    (root/f'03-13-program-{part}-draft.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    (root/f'03-13-semantic-{part}-draft.json').write_text(json.dumps(decisions[part],ensure_ascii=False,indent=2)+'\n')
(root/'03-13-cross-draft.json').write_text(json.dumps(cross,ensure_ascii=False,indent=2)+'\n')
topic_review=[]
for topic,definition in taxonomy.items():
    if topic in specs:
        values=specs[topic]
        topic_review.append(dict(topic_id=topic,definition=definition['definition'],result='evidence',
            owner=1 if topic in part1 else 2,pdf_pages=sorted({x['page'] for x in values}|supplement_pages[topic]|{x['pdf_page'] for x in visual_evidence if x['topic_id']==topic}),
            questions='Belirtilen kapsam ve kaynak koşulları; uygulama iddiası ayrı.',
            note='İlke, hedef ve araçlar kaynak pasajlarıyla değerlendirilmiştir.'))
    else:
        owner,question=absence[topic]
        topic_review.append(dict(topic_id=topic,definition=definition['definition'],result='no_explicit_statement',
            owner=owner,pdf_pages=list(range(1,84)),questions=question,
            context_passage_ids=absence_context[topic],note='Yalnız erişilen nüshada bu dar soru açısından açık ifade saptanmamıştır; bağlam olumlu yanıt değildir.'))
(root/'03-13-topic-review-draft.json').write_text(json.dumps(topic_review,ensure_ascii=False,indent=2)+'\n')
def current_passage(topic, page, contains):
    entry = next(x for x in specs[topic] if x['page']==page and contains in x['quote'])
    return f"0313-demokrat-{entry['n']:03d}-{topic}-p"
history_pairs=[
 dict(topic='yargi-bagimsizligi', historical_passage='0313-demokrat-history-02-p',
      archive_passage=current_passage('yargi-bagimsizligi',21,'vesayetinden'),
      explanation='II. Demokrasi Programı ayrı hâkim ve savcı kurulları önerirken arşiv programı mevcut kurulun Bakanlık vesayetinden çıkarılmasını önerir. Ara sürümler ve II. Demokrasi Programının kesin tarihi bilinmez.'),
 dict(topic='yerel-demokrasi', historical_passages=['0313-demokrat-history-04-p','0313-demokrat-history-06-p','0313-demokrat-history-07-p','0313-demokrat-history-08-p'],
      archive_passage=current_passage('yerel-demokrasi',29,'merkezi yönetim'),
      explanation='1985 programı zorunlu hizmet sağlanamadığında gerektiğinde genel bütçe yardımını; arşiv programı merkezi bütçe ve fon aktarımı yerine yerel kaynak oluşturmayı önerir. Arşiv yakalaması kabul tarihi değildir; aradaki tam zincir bilinmez.'),
 dict(topic='sagliga-erisim',historical_passage='0313-demokrat-history-05-p',
      archive_passage=current_passage('sagliga-erisim',49,'katkı'),
      explanation='1985 programı herkes için zorunlu sigorta ve yoksulların priminin devletçe karşılanmasını; arşiv programı vatandaşlardan katkı payı alınmamasını önerir. Prim ve katkı payı aynı mekanizma sayılmaz; tam sürüm zinciri bilinmez.')]
(root/'03-13-history-pairs-draft.json').write_text(json.dumps(history_pairs,ensure_ascii=False,indent=2)+'\n')
second=root/'03-13-program-2-draft.json'
payload=json.loads(second.read_text()); payload['historical_pairs']=history_pairs
second.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_OK',*[len(records[p]) for p in (1,2)],'cross',len(cross))
