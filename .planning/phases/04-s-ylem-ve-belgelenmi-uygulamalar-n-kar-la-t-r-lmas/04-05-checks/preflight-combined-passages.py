import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); package=json.loads((p/'combined-append-draft.json').read_text()); root=Path('data/practices/sources/tip'); entries=package['entries']; versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}; count=0
for e in entries:
 if e['kind']!='passage':continue
 row=e['values'];v=versions[row['version_id']]; path=root/v['original_path']; raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==v['sha256'],v['id']
 content=pdf_page_text(path,row['pdf_page_index']) if v['mime']=='application/pdf' else html_source_text(raw)
 assert row['exact'] in content,row['id'];count+=1
print('PASSAGE_BYTES_OK',count,'new passages; semantic readings in referenced source-review drafts')
