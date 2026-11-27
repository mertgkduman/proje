"""Load checked financial evidence into an existing archive workspace."""
from __future__ import annotations

import argparse
from contextlib import closing
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

import arsiv
from arsiv_gorunum import build_view, visible_html_text

HEADING = "Finansman ve harcamalar"
COURT = "https://siyasipartikararlar.anayasa.gov.tr"


def install_decision(data_root: Path, directory: Path, source: dict) -> tuple[dict, str, dict, str]:
    """Materialize the decision HTML supplied in a preserved official response."""
    name = source["response"]
    if Path(name).name != name:
        raise ValueError("Karar yanıtı dosya yolu geçersiz")
    raw = gzip.decompress((directory / name).read_bytes())
    if hashlib.sha256(raw).hexdigest() != source["response_sha256"]:
        raise ValueError("Karar yanıtının özeti değişmiş")
    response = json.loads(raw)
    if response["total"] != 1 or len(response["data"]) != 1:
        raise ValueError("Tek bir karar yanıtı gerekli")
    case = response["data"][0]
    for key in ("id", "esasNo", "kararNo", "resmiGazeteTarihi", "kararTarihi"):
        if case[key] != source[key]:
            raise ValueError("Karar kimliği değişmiş")
    if not case.get("icerik") or case.get("kararTuruLabel") != "Siyasi Parti Mali Denetim":
        raise ValueError("Mali denetim karar metni gerekli")
    original = case["icerik"].encode("utf-8")
    sha = hashlib.sha256(original).hexdigest()
    folder = data_root / "objects" / sha
    folder.mkdir(parents=True, exist_ok=True)
    files = {
        "original.html.bin": original,
        "readable.html": arsiv.readable_bytes(original, "html", legacy=False),
    }
    for filename, content in files.items():
        target = folder / filename
        if target.exists():
            if target.read_bytes() != content:
                raise ValueError("Arşiv nesnesinin içeriği değişmiş")
        else:
            with target.open("xb") as stream:
                stream.write(content)
    url = f"{COURT}/kbb/SP/{case['kararNo']}/2"
    fields = {
        "original_url": url,
        "final_url": url,
        "document_date": case["resmiGazeteTarihi"],
        "date_precision": "day",
        "version_label": f"E.{case['esasNo']} K.{case['kararNo']}",
        "accessed_at": source["captured_at"],
        "verified_at": source["captured_at"],
        "mime": "text/html",
        "sha256": sha,
        "original_path": str((folder / "original.html.bin").relative_to(data_root)),
        "readable_path": str((folder / "readable.html").relative_to(data_root)),
    }
    return fields, url, build_view(original, url, data_root, fetch_assets=False), visible_html_text(original)


def load_finance(work: Path, package_path: Path) -> int:
    """Stage, validate and atomically include a finance package in the workspace."""
    arsiv.assert_lock(work)
    with (work / ".finance.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _load_finance(work, package_path)


def _load_finance(work: Path, package_path: Path) -> int:
    arsiv.assert_lock(work)
    data_root = arsiv.DATA.resolve()
    raw_package = package_path.read_bytes()
    package = json.loads(raw_package)
    if package.get("schema") != "proje-finansman-v1":
        raise ValueError("Geçersiz mali paket")
    directory = package_path.parent / "sources"
    import_id = hashlib.sha256(raw_package).hexdigest()
    workspace_db = work / "records.sqlite3"
    with closing(arsiv.connect_readonly(workspace_db)) as database:
        has_receipts = database.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='finance_intake'"
        ).fetchone()
        if has_receipts and database.execute(
            "SELECT 1 FROM finance_intake WHERE package_sha256=?", (import_id,)
        ).fetchone():
            return len(package["rows"])

    with tempfile.TemporaryDirectory(prefix="finance-import-", dir=work) as scratch:
        stage = Path(scratch)
        shutil.copyfile(work / "workspace.json", stage / "workspace.json")
        db_path = stage / "records.sqlite3"
        shutil.copyfile(workspace_db, db_path)
        versions = {}
        for source in package["sources"]:
            key = source["key"]
            fields, url, view, text = install_decision(data_root, directory, source)
            arsiv.record(stage, "document", {
                "id": key, "party_id": source["party"], "title": source["title"], "source_kind": "official",
            })
            version = key + "-v1"
            arsiv.record(stage, "document_version", {"id": version, "document_id": key, **fields})
            arsiv.record(stage, "source_attribution", {
                "version_id": version, "kind": "official", "publisher": "Anayasa Mahkemesi",
                "author": None, "social_handle": None, "published_at": fields["document_date"],
                "date_precision": "day", "public_url": url,
                "basis": "AYM Kararlar Bilgi Bankası yanıtındaki karar metni ve Resmî Gazete künyesi saklandı.",
            })
            arsiv.record(stage, "archive_view", {"version_id": version, **view})
            arsiv.record(stage, "dossier_source", {
                "party_id": source["party"], "heading": HEADING, "version_id": version,
                "reason": "Kesin hesap kararının mali bulguları veya denetim sonucu.",
            })
            arsiv.record(stage, "version_context", {
                "version_id": version, "date_precision": "unknown",
                "date_unknown_reason": "Karar, hesap yılını bildirir. Belgenin yürürlük dönemi gün hassasiyetinde belirtilmemiştir.",
            })
            versions[key] = (version, fields["document_date"], source["party"], text)

        periods = set()
        for row in package["rows"]:
            version, published, party, text = versions[row["source"]]
            if " ".join(row["passage"].split()) not in text:
                raise ValueError(f"Karar metninde kaynak pasajı bulunamadı ({row['id']})")
            identifier = row["id"]
            passage = identifier + "-pasaj"
            arsiv.record(stage, "passage", {
                "id": passage, "version_id": version, "exact": row["passage"],
                "section": row["section"],
            })
            period = (version, row["period_start"], row["period_end"])
            if period not in periods:
                arsiv.record(stage, "accounting_period", {
                    "id": f"{version}-donem-{row['period_start']}", "party_id": party, "passage_id": passage,
                    "period_start": row["period_start"], "period_end": row["period_end"], "date_precision": "day",
                })
                periods.add(period)
            arsiv.record(stage, "review", {
                "id": identifier + "-inceleme", "kind": "financial", "subject_id": identifier,
                "reviewer_kind": "agent", "reviewed_at": package["checked_at"], "result": "reviewed",
                "reason": row["review_note"],
            })
            arsiv.record(stage, "financial", {
                "id": identifier, "party_id": party, "version_id": version,
                "category": row["category"], "amount": row["amount"], "currency": "TRY",
                "period_start": row["period_start"], "period_end": row["period_end"],
                "organization_scope": row["scope"], "published_at": published, "passage_id": passage,
                "missing_id": None, "number_format": "tr",
            })

        for gap in package["gaps"]:
            attempt = gap["id"] + "-arama"
            status = gap["status"]
            kind, result = {
                "Bulunamadı": ("search", "no_result"), "Doğrulanamadı": ("verification", "inconclusive"),
            }[status]
            common = {"party_id": gap["party"], "topic_id": gap["topic_id"], "heading": HEADING}
            source_version = None
            if gap.get("source"):
                source_version, _, _, text = versions[gap["source"]]
                if " ".join(gap["passage"].split()) not in text:
                    raise ValueError(f"Karar metninde eksik bilgi pasajı bulunamadı ({gap['id']})")
                arsiv.record(stage, "passage", {
                    "id": gap["id"] + "-pasaj", "version_id": source_version,
                    "exact": gap["passage"], "section": "Hüküm",
                })
            arsiv.record_attempt(stage, {
                **common, "id": attempt, "type": kind, "query": gap["query"], "attempted_at": package["checked_at"],
                "result": result, "reason": gap["reason"],
                "source_version_id": source_version,
            })
            arsiv.record_missing(stage, {
                **common, "id": gap["id"], "status": status, "attempt_id": attempt, "reason": gap["reason"],
            })
        with closing(arsiv.connect(db_path)) as database, database:
            database.execute("CREATE TABLE IF NOT EXISTS finance_intake (package_sha256 TEXT PRIMARY KEY)")
            database.execute("INSERT INTO finance_intake VALUES (?)", (import_id,))
            for party in package["parties"]:
                database.execute(
                    "INSERT INTO research_state VALUES (?,?,?) ON CONFLICT(party_id,heading) DO UPDATE SET state=excluded.state",
                    (party, HEADING, "reviewed"),
                )
        arsiv.audit_finance(db_path, storage_root=data_root)
        arsiv.assert_lock(work)
        os.replace(db_path, workspace_db)
    return len(package["rows"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    arguments = parser.parse_args()
    arsiv.DATA = arguments.data.resolve()
    print(load_finance(arguments.workspace, arguments.input))
