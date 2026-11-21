import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path.cwd()/'src'))
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/yeni-parti')
url='https://tbmm.gov.tr/Yasama/KanunTeklifi/8bdc192b-ef6a-4ef2-befe-01a0e803dd24'
raw=Path('/tmp/gsd-0404-tbmm-3895.html').read_bytes(); digest=hashlib.sha256(raw).hexdigest()
assert digest=='724f6b88fea0443df4881deefed05dfa28970649831a81c5008678963cf4f744'
assert '2 / 3895' in html_source_text(raw) and '28/09/2026' in html_source_text(raw)
folder=root/'objects'/digest; folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dst=folder/name
 if dst.exists(): assert dst.read_bytes()==content
 else: dst.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']='0404-tbmm-fon-3895-v1'; validate_view(root,view)
version=dict(id='0404-tbmm-fon-3895-v1',document_id='0404-tbmm-fon-3895',original_url=url,final_url=url,document_date=None,version_label='TBMM 2/3895 dinamik kayıt; yakalanan HTML',accessed_at='2026-11-21T20:52:02+00:00',verified_at='2026-11-21T20:52:02+00:00',mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Dinamik kayıt sayfasının yayımlanma tarihi verilmemiştir; 28 Eylül 2026 teklif geliş tarihidir.')
entries=[('document',dict(id='0404-tbmm-fon-3895',party_id='yeni-parti',title='2/3895 yatırım fonlarının adil tasfiyesi kanun teklifi',source_kind='official')),('document_version',version),('archive_view',view),('passage',dict(id='0404-tbmm-fon-3895-p',version_id=version['id'],exact='2 / 3895',prefix=None,suffix=None,article=None,section='Esas numarası, geliş tarihi ve teklif sahibi',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=version['id'],kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM yasama kayıt sayfası ve teklif künyesi incelendi.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/fund-proposal-records-draft.json'); out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n')
print('PREPARED',digest,view['view_id'])
