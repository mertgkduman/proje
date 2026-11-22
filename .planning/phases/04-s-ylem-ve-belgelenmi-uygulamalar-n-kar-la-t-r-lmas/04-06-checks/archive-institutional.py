"""Arşivlenmiş sayfalar: özgün bayt, pasif türev, yerel görünüm ve künye."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0,'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
items=[
 ('silopi','https://www.demparti.org.tr/tr/silopi-belediyesi-halkindir-halkin-kalacak/22169/','2025-08-07','DEM Parti Demokratik Yerel Yönetimler Kurulu'),
 ('silopi_dha','https://www.dha.com.tr/gundem/silopi-belediye-baskani-dem-partiden-ihrac-edildi-2694910','2025-08-07','Demirören Haber Ajansı'),
 ('calli','https://www.hakkariilsesigazetesi.com/sukru-callidan-onemli-secim-karari','2024-01-24','Hakkari İl Sesi'),
 ('calli_reply','https://www.hakkariilsesigazetesi.com/dem-partiden-sukru-callinin-iddialarina-yanit','2024-01-26','Hakkari İl Sesi'),
 ('new_ysp','https://www.yesilsolparti.org/?p=4296','2024-01-10','Yeşil Sol Parti'),
 ('ipek','https://www.demparti.org.tr/tr/zeyni-ipek-kiziltepe-halkinin-iradesine-layik-olamamistir/20622/','2024-12-26','DEM Parti Demokratik Yerel Yönetimler Kurulu'),
 ('women_report','https://tbmm.gov.tr/Haber/Detay?Id=dbc5416a-621c-4283-9304-019789cf4003','2025-06-19','Türkiye Büyük Millet Meclisi'),
]
captures=[]
for name,url,date,publisher in items:
    raw=Path('/tmp/gsd-dem-'+name.replace('_report','-report')+'.html').read_bytes()
    text=html_source_text(raw)
    digest=hashlib.sha256(raw).hexdigest(); folder=root/'objects'/digest; folder.mkdir(parents=True,exist_ok=True)
    for fn,body in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        p=folder/fn
        if p.exists(): assert p.read_bytes()==body
        else: p.write_bytes(body)
    view=build_view(raw,url,root,fetch_assets=False);view['version_id']='0406-'+name.replace('_','-')+'-v1';validate_view(root,view)
    captures.append(dict(id=name,url=url,publisher=publisher,document_date=date,accessed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=digest,characters=len(text),original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',view=view,state='source_reading_in_progress'))
    print(name,digest,len(raw),len(text),view['view_id'],flush=True)
(checks/'institutional-captures.json').write_text(json.dumps(captures,ensure_ascii=False,indent=2)+'\n')
