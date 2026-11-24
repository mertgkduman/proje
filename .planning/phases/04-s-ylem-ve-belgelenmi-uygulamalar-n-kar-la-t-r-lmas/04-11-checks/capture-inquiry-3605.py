from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here = Path(__file__).resolve().parent
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
sources = [
 ('speech','/tmp/saadet-575-tv5.html','https://www.tv5.com.tr/mahmut-arikan-iktidarin-son-kullanma-tarihi-gecmistir','TV5','journalism','journalism','2026-01-14', [('intent','Arıkan bağımlılık konusunda araştırma önergesi duyurusu','Bugün, yine bir kez daha bir araştırma önergesi vereceğiz.'),('prior','Arıkan önceki araştırma önergeleri sayısı','6 adet araştırma önergesi vermişiz')]),
 ('detail','/tmp/saadet-3605-detail.html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/8e03e9de-eb94-4700-a0c8-019be0b6ef35','TBMM','official','official',None,[('id','10/3605 dosya numarası','10 / 3605'),('date','Başkanlığa geliş günü','14/01/2026'),('status','Dosya durumu','G&#xFC;ndemde')]),
 ('session','/tmp/saadet-3605-session.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/47/Tam/f6645ad5-103b-4c44-ad54-757a7950460a.html','TBMM','official','official','2026-01-14',[('scope','Yeni Yol grup önerisinin araştırma konusu','Grup Başkanı İstanbul Milletvekili Bülent Kaya ve 19 milletvekili tarafından, uyuşturucu, sanal kumar ve bahis başta olmak üzere, tüm bağımlılık türlerine yönelik'),('speaker','Yeni Yol Grubu adına Mustafa Kaya konuşması','YENİ YOL GRUBU ADINA MUSTAFA KAYA (İstanbul)')]),
 ('summary','/tmp/saadet-3605-summary.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/47/Ozet/8219d1e0-ba36-4294-98b0-477803e9a45f.html','TBMM','official','official','2026-01-14',[('result','Görüşmenin öne alınması önerilerinin sonucu','Görüşmelerinin Genel Kurulun 14 Ocak 2026 Çarşamba günkü birleşiminde yapılmasına ilişkin önerileri yapılan görüşmelerden sonra kabul edilmedi.')]),
]
entries=[]; paths=set()
def add(table, **values): entries.append(dict(kind=table,values=values))
def save(path, body):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists(): assert path.read_bytes()==body
 else: path.write_bytes(body)
 paths.add(str(path))
for key, file, url, publisher, source_kind, kind, day, anchors in sources:
 path=Path(file); raw=path.read_bytes(); digest=sha256(raw).hexdigest(); doc='0411-inquiry-3605-'+key; vid=doc+'-v1'
 original=f'objects/{digest}/original.html.bin'; readable=f'objects/{digest}/readable.html'
 save(root/original,raw); save(root/readable,readable_bytes(raw,'html',legacy=False))
 add('document',id=doc,party_id='saadet',title='10/3605 bağımlılık araştırması: '+key,source_kind=source_kind)
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM sicil sayfasının ilk yayın günü açık.',version_label='Erişilen özgün kaynak.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='text/html',sha256=digest,original_path=original,readable_path=readable)
 add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=kind,published_at=day,date_precision='day' if day else 'unknown',social_handle=None,public_url=url,basis='Kaynak künye ve işlem tarihi ayrı incelendi.')
 view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view)
 manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
 body=html_source_text(raw)
 if key=='session':
  start=body.index('YENİ YOL GRUBU ADINA MUSTAFA KAYA (İstanbul)'); i=body.index('Öneri kabul edilmemiştir.',start); end=body.index('Halkların Eşitlik ve Demokrasi Partisi Grubunun',i)+len('Halkların Eşitlik ve Demokrasi Partisi Grubunun'); anchors.append(('result','Yeni Yol gündem önerisi sonucu ve sonraki öneri',body[i:end]))
 for suffix,section,exact in anchors:
  assert exact in body,(key,suffix); add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
(here/'inquiry-3605-source-records.json').write_text(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-3605-paths').write_text('\n'.join(sorted(paths))+'\n')
print(len(entries),len(paths))
