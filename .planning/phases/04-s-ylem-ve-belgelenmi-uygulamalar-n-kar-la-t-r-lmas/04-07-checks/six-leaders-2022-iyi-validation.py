import importlib.util,json,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('harness',c.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=c;h.SOURCE=h.DATA/'practices/sources/iyi'
p=c/'six-leaders-2022-iyi-draft.json';r=c/'six-leaders-2022-iyi-review-draft.json';assert h.sha(p)=='c52f2914e2bf9309f42a78c41507936d8fd191af6bc66aa01176bd39a783a846' and h.sha(r)=='bac9620248b5556473ff32cbf52e316b78bd03acf756954bc52458d587cc1cd9'
records=json.loads(p.read_text())['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(20,12,0)
receipt=h.main(p,r,'six-leaders-2022-iyi','0407-six-leaders-2022-event','0407-agenda-104-2881-relation',None,expected_party='iyi',namespace='gsd-0407')
folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 row=db.execute('select common_event_key,event_at,title,scope_context,occurrence_basis from practice_event where id=?',('0407-six-leaders-2022-event',)).fetchone()
 assert row==('six-leaders-2022-10-02-chp-second-round-meeting','2022-10-02','Altı liderin CHP Genel Merkezindeki ikinci tur ilk toplantısı','Altı siyasi parti liderinin 2 Ekim 2022 tarihinde CHP Genel Merkezindeki ikinci tur ilk toplantısı.','2 Ekim 2022’de CHP’nin ev sahipliğinde yapılan ikinci turun ilk toplantısını 2 Ekim ortak açıklaması ve Independent Türkçe’nin tarihli haberi belgeliyor. Katılımcılar arasında Temel Karamollaoğlu, Gültekin Uysal ve Meral Akşener vardı.')
 assert db.execute('select actor_id,authority_passage_id from practice_contribution where id=?',('0407-six-leaders-2022-contribution',)).fetchone()==('0407-six-leaders-2022-aksener-actor','0407-six-leaders-2022-arrival')
 assert db.execute('select state,relation_id from practice_candidate where id=?',('0407-six-leaders-2022-candidate',)).fetchone()==('unmatched',None)
html=(folder/'index.html').read_text()
for v in ('party','comparison'):
 a=html.index(f'id="{v}-unmatched-0407-six-leaders-2022-candidate"');z=html.index('</article>',a);assert 'data-finding-id="0407-six-leaders-2022-finding"' in html[a:z]
print('IYI_TWENTY_EVENTS_BOTH_VIEWS_OK',flush=True)
