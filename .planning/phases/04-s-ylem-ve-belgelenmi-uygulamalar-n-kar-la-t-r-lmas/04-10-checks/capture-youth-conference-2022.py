import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,"src")
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path("data/practices/sources/emep"); raw=Path("/tmp/gsd0410-youth2022-party.html").read_bytes(); url="https://www.emep.org/emek-gencligi-9-konferansinda-konusan-ercument-akdeniz-1-mayis-halkin-siyaset-meydanidir"; sha=hashlib.sha256(raw).hexdigest(); obj=root/"objects"/sha; obj.mkdir(parents=True,exist_ok=True)
for name,content in [("original.html.bin",raw),("readable.html",readable_bytes(raw,"html",legacy=False))]:
 d=obj/name
 if d.exists(): assert d.read_bytes()==content
 else: d.write_bytes(content)
version="0410-youth9-conference-reprint-v1"; ident="0410-youth9-conference-reprint"; view=build_view(raw,url,root,fetch_assets=False,http_charset="utf-8"); view["version_id"]=version; validate_view(root,view); exact="Emek Gençliği 9. Konferansı Ankara’da gerçekleşti."; assert exact in html_source_text(raw); now=datetime.now(timezone.utc).isoformat(timespec="seconds")
entries=[dict(kind="document",values=dict(id=ident,party_id="emep",title="Emek Gençliği dokuzuncu konferansı: Evrensel haberinin parti sitesindeki aktarımı",source_kind="news")),dict(kind="document_version",values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date="2022-04-11",date_precision="day",date_unknown_reason=None,version_label="11 Nisan parti sitesindeki haber aktarımı",accessed_at=now,verified_at=now,mime="text/html",sha256=sha,original_path="objects/"+sha+"/original.html.bin",readable_path="objects/"+sha+"/readable.html")),dict(kind="archive_view",values=view),dict(kind="source_attribution",values=dict(version_id=version,kind="journalism",publisher="Evrensel; yeniden yayın Emek Partisi",author="Evrensel haber merkezi",social_handle=None,published_at="2022-04-11",date_precision="day",public_url=url,basis="Parti sitesindeki 11 Nisan aktarımı metin sonunda Evrensel Gazetesi kaynak atfı taşır; aynı haber Evrensel ve Duvar tekrarlarında tek habercilik zinciridir. 10 Nisan haber tarihi konferansın kesin günüyle eşitlenmedi.")),dict(kind="passage",values=dict(id=ident+"-p",version_id=version,exact=exact,prefix=None,suffix=None,article=None,section="Dokuzuncu gençlik konferansı haberi",pdf_page_index=None,printed_page=None))]
out=Path(__file__).parent/"youth-conference-2022-source-draft.json"
with out.open("x") as f: json.dump(dict(entries=entries,status="source_read_package_pending",note="Evrensel özgünü 10.04.2022, parti yeniden yayını 11.04.2022; toplantı günü ve bağımsız ikinci haber açık."),f,ensure_ascii=False,indent=2); f.write("\n")
print(sha,view["view_id"])
