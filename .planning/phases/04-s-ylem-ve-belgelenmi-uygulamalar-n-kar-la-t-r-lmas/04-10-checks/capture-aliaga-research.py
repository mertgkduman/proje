import datetime, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
root=Path('data/practices/sources/emep');now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');entries=[]
sources=[('register','html','/tmp/gsd0410-104172-detail.html','https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/a7890d28-a5af-4026-8923-019e39f63301'),('pdf','pdf','/tmp/gsd0410-104172-proposal.pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T10/WebOnergeMetni/fe0725e2-03bb-4b0d-bd12-1315cd8b8c2f.pdf')]
def add(k,**v):entries.append(dict(kind=k,values=v))
for role,typ,path,url in sources:
    raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);name='original.html.bin' if typ=='html' else 'original.pdf';ident='0410-emep-research-104172-'+role;version=ident+'-v1'
    for filename,content in [(name,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
        target=obj/filename
        if target.exists():assert target.read_bytes()==content
        else:target.write_bytes(content)
    add('document',id=ident,party_id='emep',title='TBMM 10/4172 Aliağa ağır sanayi araştırma önergesi '+role,source_kind='official')
    add('document_version',id=version,document_id=ident,original_url=url,final_url=url,document_date=None,version_label='Resmî kayıt' if role=='register' else 'İmzalı sekiz sayfa tarama, görsel okuma',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=sha,original_path='objects/'+sha+'/'+name,readable_path='objects/'+sha+'/readable.html',date_precision='unknown',date_unknown_reason='Belge yayın günü ayrı doğrulanmadı; TBMM geliş tarihi kayıt içindedir.')
    add('source_attribution',version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None if role=='register' else 'İskender Bayhan ve diğer imzacılar',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM kayıt ekranı veya çok imzalı araştırma önergesi; başvuru, tartışma ve sonuç ayrı aşamalardır.')
    if typ=='html':
        view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);add('archive_view',**view)
        for suffix,exact,section in [('number','10 / 4172','Esas numarası'),('date','07/05/2026','Başkanlığa geliş')]:
            assert exact in html_source_text(raw);add('passage',id=ident+'-'+suffix+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
    print(role,sha)
out=Path(__file__).parent/'aliaga-research-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='Sekiz tarama sayfası görsel okundu; metin katmanı olmayan PDF için sahte pasaj üretilmedi.'),f,ensure_ascii=False,indent=2);f.write('\n')
