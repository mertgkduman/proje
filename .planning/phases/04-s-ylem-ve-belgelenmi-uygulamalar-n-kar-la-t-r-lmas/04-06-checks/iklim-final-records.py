"""2 Temmuz 2025 kesin oy, kişi ve önceki grup kaynağı pasajları."""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import re
from arsiv import html_source_text,pdf_page_text
import json
c=Path(__file__).resolve().parent;root=c.parents[3];base=root/'data/practices/sources/dem';now=datetime.now(timezone.utc).isoformat();rows=[]
def add(table,**values):rows.append(dict(kind=table,values=values))
specs=[('floor','84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/Tam/1252814c-e8f1-40c6-ae66-f1d33b9950b8.html','2025-07-02','f4d94dbe95b800ee75ff6faba96ae2b0'),('ballot','f7df0eac646ee87b066a347118dca3c2e74e4e0f08db7084dcb4f95b0256aae4','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/AcikOylamaSonuc/1abc0fa2-28a9-46b0-b91f-6b6cc340b619.html','2025-07-02','ea7a787f2dc66a7d8040ecee800dc546'),('register','59627fe3ddacd51bb94b908a5f538314d3266652b9b17f7b7bc204da8a367503','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/a0d0d465-837b-41f0-bd57-0195237fad31',None,'8425671d8f689efe89f7ed1fe867ba0f'),('law','7cc55ef8965e0cf06950b200fcc50cec931c839981b9beda7e79974538c15b37','html','https://tbmm.gov.tr/Yasama/Kanun/a0d0d465-837b-41f0-bd57-0195237fad31',None,'c3898fbaccb6f4e6359a6132b1fb9b20'),('printed','a9d9131d2f90156f59bb714179479ed7e952e8e140c6e029170156e1fd673fdb','pdf','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/Basilmis/8bdcb98b-ad59-4bbc-87bc-a99266ceec25.pdf','2025-07-02',None),('roster','f2f0d2dee129ac073d02e81c076427ac8514f621b3e6c778ac20882c75165e01','pdf','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/32/Tam/db4525a4-d1c2-4fc7-91cc-78a3a20b340a.pdf','2024-12-12',None),('koca','af22c1395ef2734831309f604d762d8b9edb258365ab7ef5d67bf931777e9ac0','html','https://www.tbmm.gov.tr/Haber/Detay?Id=2d7ed35f-612d-4c9b-82a5-0197a8e5e4eb','2025-06-25','d05728b62556cea677eda91f7d390008')]
for label,digest,fmt,url,date,viewid in specs:
 obj=Path('objects')/digest;orig=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin');raw=(base/orig).read_bytes();assert sha256(raw).hexdigest()==digest
 doc='0406-iklim-final-'+label;vid=doc+'-v1'
 add('document',id=doc,party_id='dem',title={'floor':'2 Temmuz 2025 TBMM 104. birleşim tam tutanağı','ballot':'İklim Kanunu kesin açık oy cetveli','register':'2/2927 TBMM teklif sicili','law':'7552 TBMM kanun kaydı','printed':'2 Temmuz 2025 TBMM basılı tutanağı','roster':'12 Aralık 2024 TBMM 32. birleşim tam tutanağı','koca':'25 Haziran 2025 TBMM Koca haber kaydı'}[label],source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Kayıt ekranının yayın tarihi bilinmiyor.',version_label='Belirtilen TBMM belgesi; arşiv yakalaması 23 Kasım 2026.',accessed_at=now,verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(orig),readable_path=str(obj/'readable.html'))
 add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='TBMM resmî tutanağı, kesin cetvel, kanun sicili veya haberi.')
 if viewid:
  manifest=base/'views'/viewid/'manifest.json';v=dict(view_id=viewid,format_version=2,source_sha256=digest,index_path=f'views/{viewid}/index.html',manifest_path=f'views/{viewid}/manifest.json',manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),version_id=vid);add('archive_view',**v)
 def passage(key,section,exact,page=None):
  text=pdf_page_text(base/orig,page) if fmt=='pdf' else html_source_text(raw);assert exact in text,(label,key,repr(exact))
  add('passage',id='0406-iklim-final-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
 if label=='floor':
  passage('koca-identity','Koca TBMM kimlik anonsu','Mersin Milletvekili Sayın Perihan Koca.')
  passage('koca-membership','Koca DEM grubu anonsu','Halkların Eşitlik ve Demokrasi Partisi Grubu adına Mersin Milletvekili Sayın Perihan Koca.')
  passage('first-count','Başkanın ilk oy duyurusu','Kullanılan oy sayısı')
 if label=='ballot':
  text=html_source_text(raw)
  for key,city,last in [('akin-online','&#x130;ZM&#x130;R','AKIN'),('koca-online','MERS&#x130;N','KOCA DO&#x11E;AN'),('kordu-online','TUNCEL&#x130;','KORDU')]:
   pattern=r'<td>'+city+r'</td>\s*<td>'+last+r'</td>\s*<td>.*?</td>\s*<td style="text-align:left">.*?</td>\s*<td><span>RET</span>'
   m=re.search(pattern,text,re.S);assert m,key;passage(key,'Kesin çevrimiçi kişisel ret satırı',m.group())
 if label=='register':passage('law-number','Teklif esas numarası','2 / 2927')
 if label=='printed':
  passage('akin-vote','İbrahim Akın kesin oy satırı','İzmir Akın İbrahim DEM PARTİ Ret',146)
  passage('koca-vote','Perihan Koca Doğan kesin oy satırı','Mersin Koca Doğan Perihan DEM PARTİ Ret',148)
  passage('kordu-vote','Ayten Kordu kesin oy satırı','Tunceli Kordu Ayten DEM PARTİ Ret',151)
  passage('final-count','Kesin cetvel toplamları','Kabul Edenler\nReddedenler\nÇekimserler\nBoş\nGeçersiz Oylar\nMükerrer Oylar\nToplam\nAçık Üyelikler\nKanunlaşmıştır : 22:27\n: 600\n: 242\n: 140',138)
 if label=='roster':
  text=pdf_page_text(base/orig,5);a=text.index('Halkların Eşitlik ve Demokrasi Partisi Grubu adına: Ayten Kordu');b=text.index('İbrahim Akın, İzmir',a)+len('İbrahim Akın, İzmir');q=text[a:b]
  passage('kordu-membership','2024 DEM grup konuşmacı listesi: Kordu',q,5);passage('akin-membership','2024 DEM grup konuşmacı listesi: Akın',q,5)
  passage('kordu-identity','2024 grup listesinde Ayten Kordu','Ayten Kordu, Tunceli',5)
  passage('akin-identity','2024 grup listesinde İbrahim Akın','İbrahim Akın, İzmir',5)
 if label=='koca':passage('koca-name-variant','TBMM haberinde Koca Doğan ad varyantı',"DEM Parti'li Perihan Koca Doğan")
(c/'iklim-final-records.json').write_text(json.dumps(dict(party_id='dem',entries=rows),ensure_ascii=False,indent=2)+'\n');print('IKLIM_FINAL_PASS',len(rows))
