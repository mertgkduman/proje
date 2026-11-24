"""Link catalogued sections to completed source-page readings."""

from hashlib import sha256
import json
from pathlib import Path
import re

from arsiv import pdf_page_exists, pdf_page_text

checks = Path(__file__).resolve().parent
data = Path("data")
queue_path = data / "practices/04-demokrat-tranches.json"
queue = json.loads(queue_path.read_bytes())
inventory = json.loads((data / "practices/04-inventory.json").read_bytes())
by_id = {source["id"]: source for source in inventory["source_collections"]}
checked = {}
for role, filename in (
    ("charter", "dp-charter-archive-reading-queue.json"),
    ("program", "dp-program-archive-reading-queue.json"),
):
    path = checks / filename
    reading = json.loads(path.read_bytes())
    pages = reading.get("pages")
    if pages is None:
        assert all(read["state"] == "examined" for read in reading["reads"])
        pages = [page for read in reading["reads"] for page in read["pages"]]
        assert reading["remaining_pages"] == 0
    else:
        assert all(page["state"] == "examined" for page in pages)
    digest = reading["source_sha256"]
    original = data / "objects" / digest / "original.pdf"
    assert sha256(original.read_bytes()).hexdigest() == digest
    assert len(pages) == reading["page_count"] and not pdf_page_exists(original, len(pages))
    assert [page["pdf_page_index"] for page in pages] == list(range(len(pages)))
    for index, page in enumerate(pages):
        assert sha256(pdf_page_text(original, index).encode()).hexdigest() == page["source_text_sha256"]
    version = reading.get("source_version_id", reading.get("version_id"))
    time = reading.get("checked_at", reading.get("processed_at"))
    checked[role] = (version, time, pages, filename)

mapped = []
unknown = []
for row in queue["source_queue"]:
    source = by_id[row["inventory_id"]]
    role = row["source_role"]
    page_match = re.fullmatch(r"PDF (indeksi )?(\d+)", source["page_range"] or "")
    if role not in checked or page_match is None:
        unknown.append(row["inventory_id"])
        continue
    assert source["section"] == row["section"] and source["party_id"] == queue["party_id"]
    assert source["full_text_available"] == 1 and source["missing_id"] is None
    assert row["state"] == "pending" and row["processed_at"] is None
    version, when, pages, reading_receipt = checked[role]
    index = int(page_match[2]) - (0 if page_match[1] else 1)
    assert row["version_id"] == version == source["version_id"] and 0 <= index < len(pages)
    row.update(state="read", processed_at=when, reading_receipts=[reading_receipt])
    mapped.append(dict(inventory_id=row["inventory_id"], version_id=version,
                       page_range=source["page_range"], pdf_page_index=index,
                       source_text_sha256=pages[index]["source_text_sha256"],
                       reading_receipt=reading_receipt))

assert len(mapped) == 169 and len(unknown) == 14
assert all(row["state"] == "pending" and row["processed_at"] is None and not row["closure_refs"]
           for row in queue["tranches"])
receipt = dict(
    party_id=queue["party_id"],
    method="Envanterdeki fiziksel PDF sayfa işaretleri, önceden okunmuş tam nüshaların sayfa makbuzlarıyla eşlendi.",
    full_pdf_readings={role: {"version_id": version, "page_count": len(pages), "receipt": filename}
                       for role, (version, _, pages, filename) in checked.items()},
    matched_sections=mapped, pending_inventory_ids=unknown,
    scope_closures=0)

(checks / "demokrat-read-pdf-sections.json").write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
queue_path.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")
print("DP_SOURCE_SECTIONS_READ", len(mapped), "PENDING", len(unknown))
