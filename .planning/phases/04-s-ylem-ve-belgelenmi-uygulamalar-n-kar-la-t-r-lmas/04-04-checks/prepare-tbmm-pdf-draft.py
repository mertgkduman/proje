"""Bind the captured 2/3790 PDF and its actual first-page passage."""
import hashlib
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text

root=Path('data/practices/sources/yeni-parti'); digest='e828a2a5ad9ff52e2bc9f3e5831bd18edc1eecbd49992baa2204836e9e6ca68b'; source=root/digest; raw=(source/'original.pdf').read_bytes(); assert hashlib.sha256(raw).hexdigest()==digest
assert 'Yeni Parti Genel Başkanı' in pdf_page_text(source/'original.pdf',0)
target=root/'objects'/digest; target.mkdir(parents=True,exist_ok=True)
for name in ('original.pdf','readable.html'):
 a,b=source/name,target/name
 if b.exists(): assert a.read_bytes()==b.read_bytes()
 else: shutil.copyfile(a,b)
u='https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/36f0a6f0-ed91-4d84-8a6f-fd928174e540.pdf'; at='2026-11-21T19:53:01.482680+00:00'; identity='0404-tbmm-3790-pdf'
entries=[
 dict(kind='document',values=dict(id=identity,party_id='yeni-parti',title='2/3790 asgari ücret kanun teklifi metni',source_kind='official')),
 dict(kind='document_version',values=dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date='2026-08-03',version_label='TBMM Başkanlığına sunulan teklif metni',accessed_at=at,verified_at=at,mime='application/pdf',sha256=digest,original_path='objects/'+digest+'/original.pdf',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),
 dict(kind='passage',values=dict(id=identity+'-p',version_id=identity+'-v1',exact='Özgür ÖZEL\n[anisa Milletvekili\nYeni Parti Genel Başkanı',prefix=None,suffix=None,article=None,section='Birinci sayfa, Özgür Özel imza unvanı',pdf_page_index=0,printed_page=None)),
 dict(kind='source_attribution',values=dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='TBMM özgün teklif metninin başlık ve evrak kayıt tarihi incelendi.'))]
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/tbmm-pdf-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n');print('PDF_RECORDS_DRAFT',len(entries))
