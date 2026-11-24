import json, sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
checks = Path(__file__).resolve().parent
source = checks/'agriculture-2020-sources'
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
entries = []
specs = [
 ('emep-3570.html.bin','party','2020-04-22','EMEP tarımsal destek açıklaması','party','party_publication','Emek Partisi','EMEP Genel Merkezi','https://www.emep.org/gida-kitligina-yol-acacak-tarim-politikalarindan-vazgecilsin',[(None,'request','2019 desteklerinin Nisan ayında ödenmesi talebi','Borçla\nüretim yapan köylüye 2019 yılından kalma tarım destekleme ödemeleri tamamen ve\nnisan ayında ödenmelidir.')]),
 ('aa-24.html.bin','schedule','2020-04-24','Bakanın buzağı ödeme takvimi açıklaması','journalism','journalism','Anadolu Ajansı','Enes Duran','https://www.aa.com.tr/tr/ekonomi/ureticilere-1-milyar-626-milyon-liralik-destek-odemeleri-basliyor/1817134',[(None,'schedule','Bakanın Nisan ve Mayıs tarihleri','son rakamı 2 olanlara 30 Nisan, 4 olanlara 8 Mayıs, 6 ve 8 olanlara ise 15 Mayıs')]),
 ('haykoop.html.bin','prior',None,'Haykoop önceden duyurulan buzağı takvimi','independent_report','other','Balıkesir Haykoop',None,'https://www.balikesirhaykoop.com.tr/Gundem/Duyurular?sayfa=6',[(None,'day','Duyurunun tarih ve saati','21.04.2020 16:41:00'),(None,'schedule','2019 ilk dönem buzağı takvimi','2019 yılı 1. dönem buzağı desteklemeleri T.C. Kimlik Numarası son hanesi 0 ile biten 24 Nisan 2020,\xa0\xa02 ile biten 30 Nisan 2020,4 ile biten 08 Mayıs 2020, 6-8 ile biten 15 Mayıs 2020')]),
 ('hmb-agustos.pdf','budget',None,'Hazine 2020 Ağustos bütçe bülteni','official','official','Hazine ve Maliye Bakanlığı',None,'https://ms.hmb.gov.tr/uploads/2020/09/A%C4%9Fustos.pdf',[(35,'row','2020 aylık buzağı desteği gerçekleşmeleri','Buzağı Desteği Ödemeleri 1.350 0 0 710 690 0 0 0 2.750'),(35,'header','Birim ve dönem','(MİLYON TL)')])
]
def add(table, **values): entries.append(dict(kind=table,values=values))
for filename, role, day, title, skind, akind, publisher, author, url, anchors in specs:
 raw=(source/filename).read_bytes(); digest=sha256(raw).hexdigest(); fmt='pdf' if filename.endswith('.pdf') else 'html'; obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True); original=obj/('original.pdf' if fmt=='pdf' else 'original.html.bin'); readable=obj/'readable.html'
 for path,blob in ((original,raw),(readable,readable_bytes(raw,fmt,legacy=False))):
  if path.exists(): assert path.read_bytes()==blob
  else: path.write_bytes(blob)
 doc='0410-agriculture-2020-'+role; ver=doc+'-v1'
 add('document',id=doc,party_id='emep',title=title,source_kind=skind)
 add('document_version',id=ver,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else ('Çoklu duyuru sayfasının ilk yayım günü bilinmiyor; ilgili duyuru kendi içinde 21 Nisan 2020 tarihlidir.' if role=='prior' else 'Ağustos 2020 bülteninin kesin yayım günü belirlenmedi.'),version_label=title,accessed_at=now,verified_at=now,mime='application/pdf' if fmt=='pdf' else 'text/html',sha256=digest,original_path=str(original.relative_to(root)),readable_path=str(readable.relative_to(root)))
 add('source_attribution',version_id=ver,kind=akind,publisher=publisher,author=author,social_handle=None,published_at=day,date_precision='day' if day else 'unknown',public_url=url,basis='Özgün metin doğrudan okundu; kapsam, kurum ve tarih farklılıkları ayrıldı.')
 if fmt=='html':
  view=build_view(raw,url,root,fetch_assets=False); view['version_id']=ver; validate_view(root,view); add('archive_view',**view)
 for page,suffix,section,exact in anchors:
  text=html_source_text(raw) if page is None else pdf_page_text(source/filename,page); assert exact in text,(role,suffix)
  add('passage',id=doc+'-'+suffix+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
 print(role,digest)
out=checks/'agriculture-2020-source-draft.json'
with out.open('x') as f: json.dump({'entries':entries,'limits':'Bütçe satırı ülke çapında aylık toplamdır; belirli dönem, hesap veya bireysel tahsilatı kanıtlamaz. Bakanın takvimi AA haberinde aktarılır; uygulamanın tümü veya parti nedenselliği gösterilmez.'},f,ensure_ascii=False,indent=2); f.write('\n')
print('AGRICULTURE_CAPTURE_OK',len(entries))
