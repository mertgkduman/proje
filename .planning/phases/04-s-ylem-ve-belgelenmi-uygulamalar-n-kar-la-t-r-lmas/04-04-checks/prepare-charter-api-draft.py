import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti');digest='4a1481d97a845c31a4b8c97384ccc94de1dee1014fc8e89ab39337f11e3af6d2';raw=(root/'objects'/digest/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
u='https://api.yeni-parti.org.tr/api/haberler/295';identity='0404-charter-announcement-api';at='2026-11-21T21:35:30.869818+00:00'
exact='bir sonraki olağan kurultay takvimine kadar geçerli olmak üzere, seksenden yüz elliye çıkartılmasına, otuz da yedek üyenin görev yapmasına'
assert exact in html_source_text(raw)
view=build_view(raw,u,root,fetch_assets=False,http_charset='utf-8');view['version_id']=identity+'-v1';validate_view(root,view)
assert exact in (root/view['index_path']).read_text()
entries=[
 dict(kind='document',values=dict(id=identity,party_id='yeni-parti',title='Zeynel Emre tüzük değişikliği ve kurultay açıklaması',source_kind='party')),
 dict(kind='document_version',values=dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date='2026-11-09',version_label='Site API özgün JSON yanıtı; sözcü açıklaması',accessed_at=at,verified_at=at,mime='application/json',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),
 dict(kind='archive_view',values=view),
 dict(kind='passage',values=dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Parti Meclisinin 150 üyeye çıkarılması ve bir defalık geçici süre',pdf_page_index=None,printed_page=None)),
 dict(kind='source_attribution',values=dict(version_id=identity+'-v1',kind='party',publisher='Yeni Parti (yeni-parti.org.tr yayını)',author=None,social_handle=None,published_at='2026-11-09',date_precision='day',public_url=u,basis='Haber sayfası JavaScriptinin çağırdığı kamuya açık JSON yanıtında başlık, Zeynel Emreye atfedilen açıklama ve created_at incelendi; bu alan adı kullanıcının seçtiği başka resmî alan adıyla özdeşlenmedi.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/charter-api-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n');print('API_RECORDS_DRAFT',len(entries),view['view_id'])
