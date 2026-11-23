import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, "src")
import uygulamalar as rules
D=Path(__file__).parent
read=lambda x: json.loads(Path(x).read_text())
package=read(D/"karinca-9093-union-draft.json")
previous=read(D/"karinca-9093-union-review-draft.json")
base=read("data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json")
entries,records=package["entries"],package["practice_records"]
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
items=[
 ("qral-9705","question",0,"11 Şubat 2024 tarihinde Bakanlığınıza bağlı Gaziantep Zeugma Müzesi Kültür Merkezi’nde","İmzalı soru","Karaca, Gaziantepte kamuya bağlı merkezde gösterilmesi beklenen oyunu soruyor."),
 ("qral-9705","answer",1,"Oyunun iptal edilmesine yönelik Genel Müdürlükçe herhangi bir işlem yapılmamış","Bakanlık yanıtı","Bakanlık yanıtı yalnız Devlet Tiyatroları Genel Müdürlüğünün işlemine ilişkin açıklama yapıyor."),
 ("karinca-9093","question",0,"2021 yılının haziran ayında Liman-İş sendikasına başvurarak sendikalaşma sürecini başlatan","İmzalı soru","Bayhan, Karınca Lojistikteki sendikalaşma sürecini sorusunda anlatıyor."),
 ("karinca-9093","answer",0,"ilgili işkolu tespit kararına karşı itiraz davası açıldığı, davanın derdest olduğu görülmüştür.","Bakanlık yanıtı","Bakanlık, karar aleyhine davanın yanıt tarihinde derdest olduğunu bildiriyor.")]
for name,role,page,exact,section,point in items:
 pid="0410-emep-"+name+"-"+role+"-visual-p";vid="0410-emep-"+name+"-"+role+"-v1";eid="0410-"+name+"-event"
 entries.append(dict(kind="passage",values=dict(id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)))
 entries.append(dict(kind="manual_passage",values=dict(passage_id=pid,checked_at=now,method="Özgün taranmış PDF sayfası Poppler ile görüntülendi ve görsel okundu.",reason="Sayfada makinece çıkarılabilen metin katmanı yoktur.")))
 records["practice_event_evidence"].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage="action",concrete_basis="TBMM özgün soru veya bakanlık yanıtı; sayfa görsel olarak okundu.",limitation="İddia ve yanıt kurumlarına atfedilir; dava veya idari işlemin sonraki sonucu çıkarılmaz.",epistemic_type="claim"))
 records["practice_evidence_assessment"].append(dict(event_id=eid,passage_id=pid,stage="action",basis_kind="document"))
data=copy.deepcopy(base)
for e in entries:
 if e["values"] not in data.setdefault(e["kind"],[]): data[e["kind"]].append(e["values"])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x["passage_id"] for x in records["practice_event_evidence"]},party_id="emep")
passages={p["id"]:p for p in data["passage"]};old={(r["subject_kind"],r["subject_id"]):r for r in previous["practice_source_review"]};reviews=[]
for key,(ids,parties) in sorted(targets.items()):
 row=copy.deepcopy(old.get(key)); pp=[passages[x] for x in sorted(ids)]
 if row is None:
  row=dict(subject_kind=key[0],subject_id=key[1],reviewer_kind="agent",reviewed_at=now,supported_claim="TBMM özgün taranmış PDF sayfası görsel okundu.",limitations="Görsel sayfalar kaynak kurum ve tarih sınırında değerlendirilir.",result="reviewed",reason=key[0]+" / "+key[1]+" özgün sayfa görsel okundu.")
 else:
  oldids=set(json.loads(row["passage_ids"]));assert oldids<=ids
  if oldids==ids:
   reviews.append(row);continue
  row["reason"]+=" Eklenen özgün PDF sayfaları yeniden görsel okundu."
 row["source_version_ids"]=json.dumps(sorted({p["version_id"] for p in pp}));row["passage_ids"]=json.dumps([p["id"] for p in pp]);row["inspected_sections"]=json.dumps(sorted({p["section"] for p in pp}),ensure_ascii=False);reviews.append(row)
rules.validate_practice_source_review(data,reviews,party_id="emep",target_keys=set(targets))
refs=[{k:r[k] for k in ("subject_kind","subject_id")} for r in reviews];package["source_review_refs"]=refs
for name,obj in [("visual-passages-preserved-union-draft.json",package),("visual-passages-preserved-union-review-draft.json",dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open("x") as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n")
print("VISUAL_SEMANTIC_PASS",len(reviews))
