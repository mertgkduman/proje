"""62457807 kalıcı snapshotta geçmiş olaylar ve iki görünümü ayrıca denetle."""
import hashlib,json,sqlite3
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks'); rec=json.loads((p/'dem-5367-62457807.json').read_text());folder=Path(rec['preview'])
assert hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()==rec['preview_manifest_sha256']
report=(folder/'index.html').read_text(); data=json.loads((folder/'records.json').read_text());db=sqlite3.connect(f'file:{folder/"records.sqlite3"}?mode=ro',uri=True)
for event in ('0406-2026-23464-commission','0406-2026-7573-vote','0406-2026-mdkd-report'):
 assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone() and any(x['id']==event for x in data['practice_event'])
for prefix in ('party','comparison'):
 for candidate,finding in [('0406-2026-23464-kaya-unmatched','0406-2026-23464-kaya-f'),('0406-2026-23464-commission-unmatched','0406-2026-23464-commission-f'),('0406-2026-7573-unmatched','0406-2026-7573-f'),('0406-2026-mdkd-dem-unmatched','0406-2026-mdkd-tally-f')]:
  start=report.index('id="'+prefix+'-unmatched-'+candidate+'"');end=report.index('</article>',start);assert 'data-finding-id="'+finding+'"' in report[start:end]
 for relation in ('0406-silopi-dem-relation','0406-silopi-hedep-relation'):
  assert db.execute('select result_finding_id from practice_relation where id=?',(relation,)).fetchone()==(None,)
  assert 'id="'+prefix+'-practice-'+relation+'"' in report
db.close();print('PREVIOUS_KAYA_BALLOT_SILOPI_AND_NEW_DISPUTE_BOTH_VIEWS_OK',rec['preview_manifest_sha256'])
