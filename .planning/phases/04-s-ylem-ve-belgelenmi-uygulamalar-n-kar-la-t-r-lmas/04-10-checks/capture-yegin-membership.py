import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "src")
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
root = Path("data/practices/sources/emep")
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
sources = [
 ("party", "/tmp/gsd0410-yegin-party.html", "https://www.emep.org/kararlari-hukuki-degil-siyasidir-ve-yarginin-iktidarin-donemsel-ihtiyaclari-dogrultusunda-islediginin-acik-gostergesidir", "party_publication", "Emek Partisi", "Selma Gürkan", "Parti üyelik işlemi üzerine açıklama", "Partimiz Genel Başkan Yardımcısı ve Genel Yönetim Kurulu üyesi Umut Yeğin’ in Cumhurbaşkanı’ na hakaret ettiği gerekçesi ile ceza verildiği öne sürülerek Yargıtay Cumhuriyet Başsavcılığı tarafından üyeliği düşürülmüştür.", "Parti açıklaması 16 Mayıs 2022; kayıt kaybı, itiraz ve hukuki değerlendirme ayrıdır."),
 ("news", "/tmp/gsd0410-yegin-republication.html", "https://www.gercekhaberci.com/gundem/saymaz-kaftancioglu-nun-il-baskanligi-dusurulebilir/163089", "journalism", "Gerçek Haberci", "İsmail Saymaz aktarımı", "Saymaz haberinin üyelik işlemine ilişkin aktarımı", "Cezanın onanması üzerine Yargıtay Cumhuriyet Başsavcılığı'na bağlı Siyasi Partiler Sicil Bürosu, 30 Mart 2021'de Yeğin'in parti üyeliğini düşürdü.", "16 Mayıs 2022 yayımı; haber İsmail Saymaz'ın avukat İlke Işık ile görüşmesine dayanan yazısını aktarıyor, iki bağımsız tanıklık sayılmaz. 24 Temmuz 2025 güncellemesi var; özgün mahkeme kararı elde değil."),
]
entries=[]
for role, path, url, kind, publisher, author, title, exact, basis in sources:
 raw=Path(path).read_bytes(); sha=hashlib.sha256(raw).hexdigest(); obj=root/"objects"/sha; obj.mkdir(parents=True,exist_ok=True)
 for name,content in [("original.html.bin",raw),("readable.html",readable_bytes(raw,"html",legacy=False))]:
  dest=obj/name
  if dest.exists(): assert dest.read_bytes()==content
  else: dest.write_bytes(content)
 ident="0410-yegin-membership-"+role; version=ident+"-v1"; view=build_view(raw,url,root,fetch_assets=False,http_charset="utf-8"); view["version_id"]=version; validate_view(root,view); assert exact in html_source_text(raw)
 entries.extend([dict(kind="document",values=dict(id=ident,party_id="emep",title=title,source_kind="party" if kind=="party_publication" else "journalism")),dict(kind="document_version",values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date="2022-05-16",date_precision="day",date_unknown_reason=None,version_label=title,accessed_at=now,verified_at=now,mime="text/html",sha256=sha,original_path="objects/"+sha+"/original.html.bin",readable_path="objects/"+sha+"/readable.html")),dict(kind="archive_view",values=view),dict(kind="source_attribution",values=dict(version_id=version,kind=kind,publisher=publisher,author=author,social_handle=None,published_at="2022-05-16",date_precision="day",public_url=url,basis=basis)),dict(kind="passage",values=dict(id=ident+"-p",version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=None,printed_page=None))]); print(role,sha,view["view_id"])
out=Path(__file__).parent/"yegin-membership-source-draft.json"
with out.open("x") as f: json.dump(dict(entries=entries,status="source_read_package_pending",note="Parti açıklaması ve Saymaz aktarımı farklı kökenlerdir; mahkeme aslı ve istinafın sonucu açık."),f,ensure_ascii=False,indent=2); f.write("\n")
