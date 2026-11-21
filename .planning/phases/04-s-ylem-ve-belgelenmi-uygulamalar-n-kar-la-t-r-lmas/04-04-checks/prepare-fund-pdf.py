import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes

root=Path('data/practices/sources/yeni-parti'); raw=Path('/tmp/gsd-0404-tbmm-3895.pdf').read_bytes(); digest=hashlib.sha256(raw).hexdigest()
assert digest=='0df31b1c2ab049142d3453f1cc490ddf967ff63ac99f2dc23193fb2f74fb5eda'
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 dst=folder/name
 if dst.exists(): assert dst.read_bytes()==content
 else: dst.write_bytes(content)
exact='Tarih: 1-10-2026 Esas No:2/3895'
assert exact in pdf_page_text(folder/'original.pdf',0)
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/02b7bb10-296b-4bee-b929-14db999ee954.pdf'; at='2026-11-21T20:58:25+00:00'; identity='0404-tbmm-3895-pdf'
entries=[
 dict(kind='document',values=dict(id=identity,party_id='yeni-parti',title='2/3895 yatırım fonları adil tasfiye kanun teklifi metni',source_kind='official')),
 dict(kind='document_version',values=dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date='2026-09-28',version_label='TBMM Başkanlığına sunulan teklif metni',accessed_at=at,verified_at=at,mime='application/pdf',sha256=digest,original_path='objects/'+digest+'/original.pdf',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),
 dict(kind='passage',values=dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Birinci sayfa, TBMM havale ve esas numarası',pdf_page_index=0,printed_page=None)),
 dict(kind='source_attribution',values=dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='TBMM teklif sayfası ve özgün metnin ilk sayfası incelendi.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/fund-pdf-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n');print('PDF_RECORDS_DRAFT',len(entries))
