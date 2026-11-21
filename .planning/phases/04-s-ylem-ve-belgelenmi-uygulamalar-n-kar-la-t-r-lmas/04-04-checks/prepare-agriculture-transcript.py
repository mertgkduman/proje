import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/yeni-parti');raw=Path('/tmp/gsd-0404-tbmm-123.html').read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='b2036b0b5a5d7bddf23cd6357c23365e2b13669f3d7a5f3e752dda32155990d5'
u='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/123/Ham/1b3f5332-d3ef-4874-a338-4ed690455794.html';identity='0404-tbmm-tarim-tutanak';exact='tarım sektöründe yaşanan sorunların araştırılması amacıyla 8/8/2026 tarihinde Türkiye Büyük Millet Meclisi Başkanlığına verilmiş olan genel görüşme önergesinin ön görüşmelerinin, Genel Kurulun 8 Ağustos 2026 Cumartesi günkü birleşiminde yapılmasına ilişkin önerisi';vote='Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Öneri kabul edilmemiştir.'
text=html_source_text(raw);start=text.index(exact);end=text.index(vote,start);assert 48000<end-start<48500
folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 dst=folder/name
 if dst.exists():assert dst.read_bytes()==content
 else:dst.write_bytes(content)
view=build_view(raw,u,root,fetch_assets=False);view['version_id']=identity+'-v1';validate_view(root,view)
at='2026-11-21T21:43:06+00:00';entries=[('document',dict(id=identity,party_id='yeni-parti',title='TBMM 123. birleşim tarım genel görüşme grup önerisi',source_kind='official')),('document_version',dict(id=identity+'-v1',document_id=identity,original_url=u,final_url=u,document_date=None,version_label='8 Ağustos TBMM 123. birleşim ham tutanağı; yakalanan HTML',accessed_at=at,verified_at=at,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Birleşme tarihi 8 Ağustos 2026; tutanak sayfasının yayım tarihi belirtilmemiştir.')),('archive_view',view)]
for suffix,content,section in [('oneri',exact,'Tarım genel görüşme önergesinin öne alınması grup önerisi'),('oylama',vote,'Yeter sayı yoklaması sonrasında grup önerisinin reddi')]:entries.append(('passage',dict(id=identity+'-'+suffix+'-p',version_id=identity+'-v1',exact=content,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
entries.append(('source_attribution',dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=u,basis='TBMM Tutanak Hizmetleri Başkanlığı 28. dönem 4. yasama yılı 123. birleşim metni incelendi.')))
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/agriculture-transcript-records-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n');print('AGRICULTURE_TRANSCRIPT_DRAFT',view['view_id'])
