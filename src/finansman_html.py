"""Render the finance intake as a standalone, source-linked report."""
from argparse import ArgumentParser
from collections import defaultdict
from html import escape
import json
from pathlib import Path

PARTIES = {
    "dbp": "Demokratik Bölgeler Partisi (DBP)",
    "dem": "Halkların Eşitlik ve Demokrasi Partisi (DEM Parti)",
    "demokrat": "Demokrat Parti",
    "emep": "Emek Partisi (EMEP)",
    "iyi": "İYİ Parti",
    "saadet": "Saadet Partisi",
    "tip": "Türkiye İşçi Partisi (TİP)",
    "yeni-parti": "Yeni Parti",
    "yeni-yol": "Yeni Yol",
}

STATUSES = {
    "belgeli": "Belgelendi",
    "kuruluş-öncesi": "Kuruluştan önce",
    "son yayımlanmış doğrulanmış hesap": "Son doğrulanmış hesap",
}

COURT_CASE = "https://siyasipartikararlar.anayasa.gov.tr/kbb/SP/"
STYLES = """
:root {color:#18232c;background:#fbfaf7;font:1rem/1.55 system-ui,sans-serif}
body {max-width:78rem;margin:auto;padding:clamp(1rem,4vw,3rem)}
h1,h2,h3 {line-height:1.25}
a {color:#174773;text-underline-offset:.16em}
a:focus-visible,summary:focus-visible {outline:3px solid #174773;outline-offset:.2rem}
nav ul {display:flex;flex-wrap:wrap;gap:.5rem 1.25rem;list-style:none;padding:0}
section {border-top:1px solid #b4b9ba;margin-block:2rem;padding-top:.75rem}
details {padding-block:.3rem}
summary {cursor:pointer;font-weight:600}
time {white-space:nowrap}
dl {display:grid;grid-template-columns:auto 1fr;gap:.2rem 1rem}
dd {margin:0}
blockquote {margin:0;padding:.75rem;border-inline-start:2px solid #6f7e83;color:#000}
td,th {text-align:start;vertical-align:top;padding:.35rem;border-bottom:1px solid #d5d5ce}
table {border-collapse:collapse;width:100%;table-layout:fixed;overflow-wrap:anywhere}
td:nth-child(2),th:nth-child(2) {width:6.75rem;text-align:end;font-variant-numeric:tabular-nums}
@media(max-width:36rem){body{padding:1rem}td,th{padding:.3rem .15rem}td:nth-child(2),th:nth-child(2){width:5.75rem}}
"""


def amount_tr(value):
    integer, separator, fraction = value.partition(".")
    grouped = f"{int(integer):,}".replace(",", ".")
    return grouped + "," + fraction if separator else grouped


def source_link(source):
    url = COURT_CASE + source["kararNo"] + "/2"
    return f'<a href="{escape(url)}">AYM {escape(source["kararNo"])}</a>'


def render(package):
    sources = {s["key"]: s for s in package["sources"]}
    gaps = {(row["party"], row["topic_id"]): row for row in package["gaps"]}
    by_scope = defaultdict(list)
    for row in package["rows"]:
        by_scope[row["source"], row["scope"]].append(row)

    html = ['<!doctype html><html lang="tr"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Siyasi partilerin kesin hesapları</title>', f"<style>{STYLES}</style>",
            '</head><body><main><h1>Siyasi partilerin kesin hesapları</h1>',
            '<p>2023–2025 hesap dönemleri ve Anayasa Mahkemesi dizininde bulunan daha eski son doğrulanmış hesaplar. '
            'Yayın tarihi ve örgüt kapsamı her kararla birlikte gösterilir.</p>',
            '<nav aria-label="Partiler"><ul>']
    for party in package["parties"]:
        html.append(f'<li><a href="#{escape(party)}">{escape(PARTIES[party])}</a></li>')
    html.append("</ul></nav>")

    for party in package["parties"]:
        html.append(f'<section id="{escape(party)}"><h2>{escape(PARTIES[party])}</h2><dl>')
        coverage = [c for c in package["coverage"] if c["party"] == party]
        for entry in coverage:
            year = entry["year"]
            state = STATUSES.get(entry["status"], entry["status"])
            linked = sources.get(entry.get("source"))
            html.append(f"<dt>{year}</dt><dd>{escape(state)}")
            if linked:
                html.append(f" · {source_link(linked)}")
            if gap := gaps.get((party, f"{year} hesap dönemi")):
                html.append(f"<br>{escape(gap['reason'])}")
                if excerpt := gap.get("passage"):
                    html.append("<details><summary>Kararın hükmü</summary>"
                                f"<blockquote>“{escape(excerpt)}”</blockquote></details>")
            html.append("</dd>")
        html.append("</dl>")

        for entry in coverage:
            if entry["status"] not in {"belgeli", "son yayımlanmış doğrulanmış hesap"}:
                continue
            source = sources[entry["source"]]
            html.append(f'<h3>{escape(source["title"])}</h3>'
                        f'<p>Yayım <time>{escape(source["resmiGazeteTarihi"])}</time> · {source_link(source)}</p>')
            for (key, scope), items in by_scope.items():
                if key != source["key"]:
                    continue
                html.append(f'<details><summary>{escape(scope)}</summary><table><thead><tr>'
                            '<th scope="col">Hesap kalemi ve kaynak pasajı</th>'
                            '<th scope="col">Tutar (TL)</th></tr></thead><tbody>')
                for item in items:
                    html.append(f'<tr id="{escape(item["id"])}"><td><details>'
                                f'<summary>{escape(item["category"])}</summary>'
                                f'<p>{escape(item["section"])}</p><blockquote>“{escape(item["passage"])}”</blockquote>'
                                f'</details></td><td>{amount_tr(item["amount"])}</td></tr>')
                html.append("</tbody></table></details>")
        html.append("</section>")
    return "\n".join(html + ["</main></body></html>", ""])


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(render(json.loads(args.input.read_bytes())), encoding="utf-8")
