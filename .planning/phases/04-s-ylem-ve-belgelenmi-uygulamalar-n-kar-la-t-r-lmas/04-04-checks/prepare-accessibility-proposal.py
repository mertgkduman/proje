import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti');raw=Path('/tmp/gsd-0404-tbmm-3853.html').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='1a10eabde6169a8a46946875edb9a6ce381ddc557e4b5ad14691472275c489c1'
u='https://tbmm.gov.tr/Yasama/KanunTeklifi/d847873f-4e57-405e-b96d-01a0af3a7e22';identity='0404-tbmm-engelli-3853';exact='Teklif ile, engelli &#xF6;&#x11F;rencilerin ihtiya&#xE7; duyduklar&#x131; eri&#x15F;ilebilir ders ve e&#x11F;itim materyalleri ile yard&#x131;mc&#x131; yaz&#x131;l&#x131;m, donan&#x131;m ve destek teknolojilerinin &#xFC;cretsiz sa&#x11F;lanmas&#x131; ama&#xE7;lanmaktad&#x131;r.';assert exact in html_source_text(raw)
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dst=folder/name
 if dst.exists():assert dst.read_bytes()==content
 else:dst.write_bytes(content)
view=build_view(raw,u,root,fetch_assets=False,http_charset='utf-8');view['version_id']=identity+'-v1';validate_view(root,view)
at='2026-11-21T21:54:51+00:00';entries=[('document',dict(id=identity,party_id='yeni-parti',title='2/3853 erişilebilir eğitim materyalleri kanun teklifi',source_kind='official')),('document_version',dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date=None,version_label='TBMM 2/3853 dinamik kayıt; yakalanan HTML',accessed_at=at,verified_at=at,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Kayıt sayfasının yayın tarihi belirtilmiyor; 17 Eylül 2026 teklif geliş tarihidir.')),('archive_view',view),('passage',dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Teklifin özeti; HTML karakter varlıkları özgün biçimde',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='TBMM yasama kayıt sayfası, teklif künyesi ve ilk imza incelendi.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/accessibility-proposal-records-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n');print('ACCESSIBILITY_PROPOSAL_DRAFT',view['view_id'])
