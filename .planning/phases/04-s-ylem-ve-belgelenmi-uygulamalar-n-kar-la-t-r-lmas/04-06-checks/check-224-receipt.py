"""224 raporu ve mevcut uygulamaların kalıcı önizlemede bağımsız denetimi."""
import hashlib,json,sqlite3
from pathlib import Path
from arsiv import pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
r=json.loads((p/'dem-224-full-62412215.json').read_text()); folder=Path(r['preview']); data=json.loads((folder/'records.json').read_text()); html=(folder/'index.html').read_text();m=json.loads((folder/'manifest.json').read_text());db=sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True)
assert m['renderer_version']==31 and hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()==r['preview_manifest_sha256']
assert db.execute('select event_at,common_event_key from practice_event where id=?',('0406-2025-224-report',)).fetchone()==('2025-07-03','tbmm-28-3-224-kadin-rapor')
assert any(x['id']=='0406-2025-224-report' and x['event_at']=='2025-07-03' for x in data['practice_event'])
assert db.execute('select state,relation_id from practice_candidate where id=?',('0406-2025-224-candidate',)).fetchone()==('eligible','0406-2025-224-relation')
for prefix in ('party','comparison'):
 for ident in ('0406-101831-relation','0406-2025-224-relation','0406-2025-103465-relation'):
  assert f'id="{prefix}-practice-{ident}"' in html
 start=html.index(f'id="{prefix}-practice-0406-2025-224-relation"');end=html.index('</article>',start)
 for finding in ('0406-224-result-f','0406-224-contribution-f','0406-224-link-f'): assert f'data-finding-id="{finding}"' in html[start:end]
source=Path('data/practices/sources/dem/objects/ed1e950a9d23850333dd94cd3fbae9acf4747da5861019c1b14b0ea5ed891bb0/original.pdf')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='ed1e950a9d23850333dd94cd3fbae9acf4747da5861019c1b14b0ea5ed891bb0'
assert '03.07.2025' in pdf_page_text(source,54) and 'Adalet KAYA Özgül SAKİ' in pdf_page_text(source,1001)
db.close();print('REPORT_DATE_SIGNATURE_NINE_EVENTS_BOTH_VIEWS_OK',r['preview_manifest_sha256'])
