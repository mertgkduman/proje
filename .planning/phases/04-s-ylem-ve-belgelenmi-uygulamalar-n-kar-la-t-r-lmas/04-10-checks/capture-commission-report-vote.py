import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.now(timezone.utc).isoformat(timespec='seconds');rows=[]
sources=[('tbmm','pdf','/tmp/gsd0410-commission-2026-tbmm.html','https://tbmm.gov.tr/Tutanaklar/TutanakGoster/5367','official','Türkiye Büyük Millet Meclisi'),('press','html','/tmp/gsd0410-commission-artisiirt.html','https://www.artisiirt.com/meclis-komisyonu-nun-ortak-nihai-raporu-oy-cokluguyla-kabul-edildi/45333/','journalism','Artı Siirt')]
def add(k,**v):rows.append(dict(kind=k,values=v))
for role,typ,path,url,kind,publisher in sources:
 raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);original='original.pdf' if typ=='pdf' else 'original.html.bin';ident='0410-emep-mdkd-report-2026-'+role;version=ident+'-v1'
 for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
  p=obj/name
  if p.exists():assert p.read_bytes()==content
  else:p.write_bytes(content)
 add('document',id=ident,party_id='emep',title='18 Şubat 2026 komisyon raporu '+('tutanağı' if role=='tbmm' else 'oylama haberi'),source_kind=kind)
 add('document_version',id=version,document_id=ident,original_url=url,final_url=url,document_date='2026-02-18',date_precision='day',date_unknown_reason=None,version_label='Tutanak toplantı günü; yayımlanma günü bilinmiyor' if role=='tbmm' else '18 Şubat 2026 haber',accessed_at=now,verified_at=now,mime='application/pdf' if typ=='pdf' else 'text/html',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html')
 if typ=='html':
  view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);add('archive_view',**view);text=html_source_text(raw)
  exact='Oylamada Türkiye İşçi Partisi (TİP) üyesi Ahmet Şık ile Emek Partisi (EMEP) üyesi İskender Bayhan rapora “hayır” oyu verdi.';assert exact in text
  add('passage',id=ident+'-individual-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Haberde kişisel ret oyları',pdf_page_index=None,printed_page=None)
  exact2='Gerçekleştirilen oylama sonucunda rapor, 42 kabul, 2 ret ve 1 çekimser oyla kabul edildi.';assert exact2 in text
  add('passage',id=ident+'-aggregate-p',version_id=version,exact=exact2,prefix=None,suffix=None,article=None,section='Haberde bildirilen oy toplamı',pdf_page_index=None,printed_page=None)
 else:
  for suffix,index,term,section in [('speaker',50,'EMEP ad ı na İ skender Bayhan, buyurun.','Komisyon başkanının EMEP adına söz vermesi'),('intent',53,'İ SKENDER BAYHAN ( İ stanbul) - Onun için, "hay ı r" oyu kullanaca ğı z, bunun','Bayhan’ın rapora hayır yönündeki beyanı'),('aggregate',60,'47 kabul\noyu, 2 ret oyu var, 1 arkada şı m ı z da çekimser kald ı .','Komisyon başkanının açıkladığı oy toplamı')]:
   content=pdf_page_text(Path(path),index);assert term in content,(suffix,repr(content[-700:]))
   add('passage',id=ident+'-'+suffix+'-p',version_id=version,exact=term,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=str(index+1))
 add('source_attribution',version_id=version,kind=kind,publisher=publisher,author=None,social_handle=None,published_at=None if role=='tbmm' else '2026-02-18',date_precision='unknown' if role=='tbmm' else 'day',public_url=url,basis='TBMM komisyon toplantısı tutanağı; işlem günü yayımlanma tarihi sayılmaz.' if role=='tbmm' else 'Artı Siirt tarihli haber; kişisel oyu bildirir. Haberin 42 kabul sayısı ile TBMM tutanağının 47 kabul sayısı ayrı korunur.')
 print(role,sha)
out=Path(__file__).parent/'commission-report-vote-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='TBMM PDF sayfa indisleri 50,53,60: EMEP adına söz, Bayhan’ın hayır kullanacağını açıklaması, başkanın rapor kabulü ve 47/2/1 duyurusu. Tutanak bireysel oy cetveli değildir; Artı Siirt Şık ve Bayhan hayır bildirir, fakat 42/2/1 yazar. 42/47 uyuşmazlığı uzlaştırılmadı. Komisyon raporu Genel Kurul kararı değildir.'),f,ensure_ascii=False,indent=2);f.write('\n')
