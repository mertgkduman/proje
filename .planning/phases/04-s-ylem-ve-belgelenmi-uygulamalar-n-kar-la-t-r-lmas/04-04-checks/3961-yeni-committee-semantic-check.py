import hashlib, html, json, pathlib, re
from datetime import date
p=pathlib.Path(__file__).parent
c=json.loads((p/"3961-yeni-committee-candidate.json").read_text())
sha=lambda x:hashlib.sha256(pathlib.Path(x).read_bytes()).hexdigest()
assert sha(c["base"]["path"])==c["base"]["sha256"]
assert sha(c["document"]["existing_original"])==c["document"]["sha256"]
for ref in (c["statement"]["source"],c["independent_confirmation"]):
 assert ref["status"]==200 and sha(ref["file"])==ref["sha256"]
 text=html.unescape(html.unescape(pathlib.Path(ref["file"]).read_text(errors="replace")))
 for token in (("Özgür Özel", "Yemen çöllerine", "Yeni Parti") if ref is c["statement"]["source"] else ("Talih Özcan","Utku Çakırözer","muhalefet şerhi")):
  assert token.casefold().replace("i\u0307", "i") in text.casefold().replace("i\u0307", "i"),token
assert date.fromisoformat(c["statement"]["date"])<date.fromisoformat(c["event"]["date"])<=date.fromisoformat(c["document"]["report_date"])
base=json.loads(pathlib.Path(c["base"]["path"]).read_text())
for x in base["practice_records"]["practice_event"]:
 s=json.dumps(x,ensure_ascii=False).casefold()
 assert not ("3961" in s and ("şerh" in s or "serh" in s)),x
assert c["event"]["identity_pdf_page_index"]==23 and c["event"]["name_date_pdf_page_index"]==25
print(json.dumps({"result":"PASS_LIMITED","candidate_sha256":sha(p/"3961-yeni-committee-candidate.json"),"base_sha256":sha(c["base"]["path"]),"checked":"source hashes, dated order, attributed names, candidate identity anchors, existing event duplication","manual_review":"report image excerpts checked by researcher, independent readback still needed","not_checked":"project schema, source registry, preview and renderer, causal claim or personal vote"},ensure_ascii=False,indent=2))
