from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'prepare-six-leaders-nov-2022.py').read_text()
s=s.replace('six-leaders-nov-2022-source-records.json','six-leaders-nov-2022-v2-source-records.json')
s=s.replace('six-leaders-nov-2022-draft.json','six-leaders-nov-2022-v2-draft.json').replace('six-leaders-nov-2022-review-draft.json','six-leaders-nov-2022-v2-review-draft.json')
s=s.replace("sp=[src+'plan-present',src+'prior-date',src+'meetingplan-role'],quote=src+'plan-present'", "sp=[src+'meetingplan-present',src+'meetingplan-role'],quote=src+'meetingplan-present'")
s=s.replace("sp=[src+'meetingplan-next',src+'prior-date',src+'meetingplan-role']", "sp=[src+'meetingplan-next',src+'meetingplan-role']")
s=s.replace("extras=[src+'chp-leaders',src+'chp-kaya',src+'joint-heading']", "extras=[src+'saadet-present']").replace("extras=[src+'joint-heading']", "extras=[src+'saadet-meeting']")
s=s.replace('14 Kasım altı lider ortak açıklamasının CHP haftalık bültenindeki aktarımı.','14 Kasım altı lider ortak açıklamasının Karar haberindeki aktarımı.').replace('14 Kasım ortak açıklama, CHP bülteni ve tarihli Karar haberi.','14 Kasım ortak açıklamasının tarihli Karar aktarımı.')
(p/'prepare-six-leaders-nov-2022-v2.py').write_text(s)
