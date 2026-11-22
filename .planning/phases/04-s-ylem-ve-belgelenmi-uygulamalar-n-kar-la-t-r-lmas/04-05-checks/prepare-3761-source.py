import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');root=Path('data/practices/sources/tip');entries=[]
def add(k,v):entries.append(dict(kind=k,values=v))
def source(doc,title):
 cap=json.loads((p/(doc+'-v1-capture.json')).read_text());h=cap['sha256'];url=cap['url'];raw=(root/'objects'/h/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==h
 if doc.endswith('tutanak'):assert hashlib.sha256((root/'objects'/h/'readable.html').read_bytes()).hexdigest()=='2374b87000c871c696d85f044150e93507cb443176a0d0b1f10a5e4e84202219'
 add('document',dict(id=doc,party_id='tip',title=title,source_kind='official'))
 add('document_version',dict(id=doc+'-v1',document_id=doc,original_url=url,final_url=url,document_date='2023-10-17',version_label='TBMM tutanağı',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None));add('archive_view',cap['view'])
 add('source_attribution',dict(version_id=doc+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='17 Ekim 2023 birleşim belgesi; UTF-8 olmayan özgün bayt ve Windows-1254 pasif görünümü korundu.'))
 return raw
def passage(doc,suffix,exact,section):
 text=html_source_text((root/'objects'/caps[doc]/'original.html.bin').read_bytes());assert exact in text and '\ufffd' not in exact
 add('passage',dict(id=doc+'-'+suffix+'-p',version_id=doc+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
t='0405-tip-20231017-tezkere-tutanak';v='0405-tip-20231017-tezkere-oy';caps={x:json.loads((p/(x+'-v1-capture.json')).read_text())['sha256'] for x in (t,v)}
traw=source(t,'TBMM 17 Ekim 2023 8. birleşim tam tutanağı');oraw=source(v,'TBMM 3/761 kesin açık oylama cetveli')
passage(t,'authority','Türkiye İşçi Partisi adına Sayın Sera Kadıgil','Kadıgil’e parti adına söz verilmesi')
full_tutanak=html_source_text(traw);start=full_tutanak.index('Türkiye İşçi Partisi adına Sayın Sera Kadıgil');end=full_tutanak.index('Saliha Sera Kadıgil',start)+len('Saliha Sera Kadıgil')
passage(t,'authority-full',full_tutanak[start:end],'Parti adına söz ile tam adın aynı oturum bağlamı')
passage(t,'statement','Başka ülkelerin topraklarında askerî operasyon yürütülmesine “hayır” diyoruz.','Oylama öncesi Kadıgil açıklaması')
passage(t,'ballot','Oylama işlemini başlatıyorum.','Konuşmadan sonraki oylama sırası')
full=oraw.decode('windows-1254');row=next(r for r in re.findall(r'<tr\b.*?</tr>',full,re.I|re.S) if 'Saliha Sera' in r and 'KADIGİL' in r)
assert all(x in row for x in ('RET','17.10.2023','19:33:57'))
rawtext=html_source_text(oraw);position=rawtext.index('Saliha Sera');end=rawtext.index('</tr>',position);fragment=rawtext[position:end];vote=fragment[fragment.index('<td><span style="color:Ret">RET'):];assert '\ufffd' not in vote and '19:33:57' in vote
passage(v,'name','Saliha Sera','Kadıgil’in oy cetvelindeki ad hücresi');passage(v,'vote',vote,'Aynı satırda ret, gün ve saat')
(p/'tezkere-3761-source-records.json').write_text(json.dumps(dict(party_id='tip',entries=entries,limitations=['Oy cetvelinin Windows-1254 özgün satırı görselde doğru çözümlenir; dar ASCII pasaj aynı satırdaki RET ve saati gösterir.','Oturum duyurusu ve kesin cetvel sayıları ayrı aşamalardır.']),ensure_ascii=False,indent=2)+'\n')
print('SOURCE_DRAFT_ONLY',len(entries))
