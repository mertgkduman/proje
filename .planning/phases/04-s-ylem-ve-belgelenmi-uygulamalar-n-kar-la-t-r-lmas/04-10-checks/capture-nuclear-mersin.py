import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-nuclear-2026-party.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);url='https://www.emep.org/cernobilin-40-yilinda-mersinde-nukleer-karsiti-aciklama-akkuyuya-hayir';ident='0410-emep-mersin-nuclear-2026-party';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);text=html_source_text(raw)
passages=[('event','Çernobil Nükleer patlamasının 40 yılı nedeniyle Emek Partisi Mersin İl Örgütü Koton önünde basın açıklaması gerçekleştirdi.','Mersin il örgütünün basın açıklaması'),('actor','Mersin Emek ve Demokrasi Platformu bileşenlerinin de katılarak destek verdiği açıklamada EMEP İl Başkanı Sedat Başkavak','Katılım ve parti sözcüsü'),('headline','Çernobil’in 40. yılında Mersin’de nükleer karşıtı açıklama: &#039;Akkuyu’ya hayır&#039;','Parti yayınının nükleer karşıtı açıklama başlığı')]
rows=[dict(kind='document',values=dict(id=ident,party_id='emep',title='Çernobil’in 40. yılında Mersin’de nükleer karşıtı açıklama',source_kind='party')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2026-04-27',date_precision='day',date_unknown_reason=None,version_label='27 Nisan 2026 parti haberi; açıklamanın tam günü ayrıca belirtilmiyor',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')),dict(kind='archive_view',values=view),dict(kind='source_attribution',values=dict(version_id=version,kind='party_publication',publisher='Emek Partisi',author=None,social_handle=None,published_at='2026-04-27',date_precision='day',public_url=url,basis='Partinin tarihli Mersin açıklaması yayını; parti ve platformun rolleri ayrı.'))]
for suffix,exact,section in passages:
 assert exact in text;rows.append(dict(kind='passage',values=dict(id=ident+'-'+suffix+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'nuclear-mersin-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='27 Nisan tarihli parti haberi Mersin il örgütü açıklamasını bildirir; olay günü açıkça belirtilmedi. Platform destekçisi ile EMEP örgütü ayrı. Kazalar, enerji maliyetleri ve ölüm sayıları kaynağın iddiasıdır; bu olayla doğrulanmış sonuç sayılmaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
print(sha,view['view_id'])
