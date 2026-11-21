import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti');raw=Path('/tmp/gsd-0404-tbmm-3960.html').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='5a5b39805347c8e8903d2cd1e7435ceb76782517a6fba846877aabbcd11e4d89'
u='https://tbmm.gov.tr/Yasama/KanunTeklifi/86a79e3f-10fa-4d58-8941-01a143f5093a';identity='0404-tbmm-emekli-3960';exact='Teklif ile en d&#xFC;&#x15F;&#xFC;k emekli ayl&#x131;&#x11F;&#x131; miktar&#x131;n&#x131;n, net asgari &#xFC;cret d&#xFC;zeyine &#xE7;&#x131;kar&#x131;lmas&#x131; ama&#xE7;lanmaktad&#x131;r.';assert exact in html_source_text(raw)
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dst=folder/name
 if dst.exists():assert dst.read_bytes()==content
 else:dst.write_bytes(content)
view=build_view(raw,u,root,fetch_assets=False,http_charset='utf-8');view['version_id']=identity+'-v1';validate_view(root,view)
at='2026-11-21T21:47:56+00:00';entries=[('document',dict(id=identity,party_id='yeni-parti',title='2/3960 en düşük emekli aylığı kanun teklifi',source_kind='official')),('document_version',dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date=None,version_label='TBMM 2/3960 dinamik kayıt; yakalanan HTML',accessed_at=at,verified_at=at,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Kayıt sayfasının yayın tarihi belirtilmiyor; 16 Ekim 2026 teklif geliş tarihidir.')),('archive_view',view),('passage',dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Teklifin özeti; HTML karakter varlıkları özgün biçimde',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='TBMM yasama kayıt sayfası, teklif künyesi ve ilk imza incelendi.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/pension-proposal-records-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n');print('PENSION_PROPOSAL_DRAFT',view['view_id'])
