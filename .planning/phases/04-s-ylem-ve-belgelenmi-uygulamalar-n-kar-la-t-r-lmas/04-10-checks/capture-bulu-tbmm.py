import copy, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D=Path(__file__).parent; root=Path('data/practices/sources/emep')
raw=Path('/tmp/gsd-emep-bulu-tbmm.html').read_bytes()
url='https://www.tbmm.gov.tr/milletvekili/UyeKomisyonKonusmaTutanakDetay?tutanakId=45997'
exact='Bir kayyum gönderdiniz, Melih Bulu, görevden alındı, başka bir kayyum gönderdiniz.'
assert exact in html_source_text(raw)
digest=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    path=obj/name
    if path.exists(): assert path.read_bytes()==content
    else: path.write_bytes(content)
now=datetime.now(timezone.utc).isoformat(timespec='seconds'); doc='0410-emep-bulu-2021-tbmm'; version=doc+'-v1'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=version; validate_view(root,view)
entries=copy.deepcopy(json.loads((D/'bulu-2021-source-draft.json').read_text())['entries'])
entries=[e for e in entries if not (e['kind']=='manual_passage' and e['values']['passage_id']=='0410-emep-bulu-2021-official-p')]
official=next(e['values'] for e in entries if e['kind']=='passage' and e['values']['id']=='0410-emep-bulu-2021-official-p')
official['exact']='Karar: 2021/360\n14 Temmuz 2021'
assert official['exact'] in pdf_page_text('/tmp/gsd-emep-bulu-20210715.pdf',6)
entries.extend([
 dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM Plan ve Bütçe Komisyonu 2 Kasım 2021 konuşması',source_kind='official')),
 dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date='2021-11-02',date_precision='day',date_unknown_reason=None,version_label='TBMM konuşma tutanağı',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html')),
 dict(kind='archive_view',values=view),
 dict(kind='passage',values=dict(id=doc+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Garo Paylan komisyon konuşması',pdf_page_index=None,printed_page=None)),
 dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author='Garo Paylan',social_handle=None,published_at='2021-11-02',date_precision='day',public_url=url,basis='TBMM komisyon konuşması konuşmacı ve tarih alanları. İfade milletvekiline atıflıdır.')),
])
with (D/'bulu-2021-source-v2-draft.json').open('x') as f: json.dump(dict(status='source_read_package_pending',entries=entries),f,ensure_ascii=False,indent=2); f.write('\n')
print('TBMM',digest,view['view_id'])
