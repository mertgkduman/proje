from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here=Path(__file__).resolve().parent; root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat(); entries=[]; paths=set()
def add(table,**row): entries.append({'kind':table,'values':row})
def put(rel,raw):
 p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==raw
 else: p.write_bytes(raw)
 paths.add(str(p))
base='https://cdn.tbmm.gov.tr/'
sources=[
 ('speech','village-2691-session23-original.html',base+'TbmmWeb/Tutanak/28/3/23/Tam/260b480d-495f-4ea1-a594-92560c1ed386.html','2024-11-26'),
 ('session','village-2691-session27-original.html',base+'TbmmWeb/Tutanak/28/3/27/Tam/12a47eea-ab74-449b-ba00-5205b03fdb2b.html','2024-12-05'),
 ('vote','village-2691-printed-original.pdf',base+'TbmmWeb/Tutanak/28/3/27/Basilmis/3d3cb6ec-87c9-45c9-ac04-10a5dbcb5df4.pdf','2024-12-05'),
 ('law','village-7534-law-original.html',base+'KKBSPublicFile/D28/Y2/KanunMetni/4aba0cb1-eea3-4aaf-8423-8ce36da1a35f.htm','2024-12-05')]
for key,name,url,day in sources:
 raw=(here/name).read_bytes(); h=sha256(raw).hexdigest(); doc='0411-village-2691-'+key; vid=doc+'-v1'; fmt='pdf' if key=='vote' else 'html'; original=f'objects/{h}/original.'+('pdf' if fmt=='pdf' else 'html.bin'); readable=f'objects/{h}/readable.html'; put(original,raw); put(readable,readable_bytes(raw,fmt,legacy=False))
 add('document',id=doc,party_id='saadet',title='2/2691 köy kanunu teklifi: '+key,source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label='27. birleşim 4 Aralık açıldı; oy ve kabul 5 Aralık.' if key in ('session','vote','law') else 'TBMM 23. birleşimi.',accessed_at=datetime.fromtimestamp((here/name).stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=h,original_path=original,readable_path=readable)
 add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='Birleşim ve işlem günü çevrimiçi nüshanın bilinmeyen yayım tarihinden ayrıdır.')
 if fmt=='html':
  view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view); m=root/view['manifest_path']; paths.add(str(m)); paths.update(str(m.parent/n) for n in json.loads(m.read_bytes())['files']); body=html_source_text(raw)
 if key=='speech':
  anchors=[('identity','Görüşülen 2/2691 teklifinin adı ve esas numarası','Köy Kanunu ile Bazı Kanunlarda Değişiklik Yapılmasına Dair Kanun Teklifi (2/2691)',None),('authority','Atmacanın dönemsel grup sıfatı','SAADET PARTİSİ GRUBU ADINA MEHMET ATMACA (Bursa)',None),('stance','Teklifin bütünü için ret konuşması','bu kanun değişikliğine ret oyu vereceğimizi ifade ediyorum',None)]
 elif key=='session':
  start=body.rindex("174 sıra sayılı Kanun Teklifi'nin açık oylama sonucu:"); end=body.index('Teklif kabul edilmiş ve kanunlaşmıştır.',start)+len('Teklif kabul edilmiş ve kanunlaşmıştır.'); text=body[start:end]; assert ': 320' in text and ': 247' in text and ': 73' in text
  anchors=[('totals','Başkanın 174 sıra sayılı nihai oy sonucu ve kabul açıklaması',text,None)]
 elif key=='vote':
  text=pdf_page_text(root/original,149); start=text.index('Kabul Edenler'); end=text.index('İli Soyadı',start); totals=text[start:end]; assert all(x in totals for x in ('242','74','321','Mükerrer'))
  anchors=[('atmaca','Atmaca bireysel oy satırı','Bursa Atmaca Mehmet YENİ YOL Ret',152),('totals','Basılı cetvelde farklı toplam ve mükerrer oylar',totals,149)]
 else: anchors=[('number','Kanun numarası','Kanun No. 7534',None),('adopt','Kanun kabul günü','Kabul Tarihi: 5/12/2024',None)]
 for suffix,section,exact,page in anchors:
  content=body if page is None else pdf_page_text(root/original,page)
  assert exact in content,(key,suffix); add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
(here/'village-2691-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-village2691-paths').write_text('\n'.join(sorted(paths))+'\n')
print('source entries',len(entries),'paths',len(paths))
