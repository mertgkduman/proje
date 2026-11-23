import hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view, validate_view

url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/AcikOylamaSonuc/1abc0fa2-28a9-46b0-b91f-6b6cc340b619.html'
raw=Path('/tmp/gsd0410-climate/vote.html').read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha=='f7df0eac646ee87b066a347118dca3c2e74e4e0f08db7084dcb4f95b0256aae4'
root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=True))]:
    p=obj/name
    if p.exists(): assert p.read_bytes()==content
    else: p.write_bytes(content)
ident='0410-emep-climate-2025-ballot';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
view=build_view(raw,url,root,fetch_assets=False,http_charset='windows-1254');view['version_id']=version;validate_view(root,view)
entries=[]
def add(record_kind,**values):entries.append(dict(kind=record_kind,values=values))
add('document',id=ident,party_id='emep',title='TBMM 2 Temmuz 2025 İklim Kanunu kesin açık oy cetveli',source_kind='official')
add('document_version',id=version,document_id=ident,original_url=url,final_url=url,document_date='2025-07-02',date_precision='day',date_unknown_reason=None,version_label='2 Temmuz 2025 kesin cetvel; yayın zamanı bilinmiyor',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html')
add('archive_view',**view)
add('source_attribution',version_id=version,kind='official',publisher='TBMM Tutanak Hizmetleri Başkanlığı',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Oylama günü ile belgenin yayın günü ayrı tutulur.')
text=raw.decode('windows-1254')
for name,needle,result in [('bayhan','<td>BAYHAN</td>','KATILMADI'),('karaca','<td>KARACA DEM&#x130;R</td>','RET')]:
    found=[row for row in re.findall(r'<tr[^>]*>.*?</tr>',text,re.S|re.I) if needle in row];assert len(found)==1 and 'Emek Partisi' in found[0] and result in found[0]
    exact=found[0][4:-5].strip();assert exact.isascii()
    add('passage',id=ident+'-'+name+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=name+' kesin açık oy satırı',pdf_page_index=None,printed_page=None)
out=Path(__file__).parent/'climate-vote-source-draft.json'
with out.open('x') as f:
    json.dump(dict(status='source_read_package_pending',entries=entries,note='Kesin cetvel: Karaca Demir RET 22:27:51; Bayhan KATILMADI, pusula yok. 242 kabul, 140 ret, 1 mükerrer. Nisan açıklaması bireysel oy değildir.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('CLIMATE_BALLOT_CAPTURE_OK',sha,view['view_id'])
