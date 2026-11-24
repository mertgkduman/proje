from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here = Path(__file__).resolve().parent
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()
def add(table, **row): entries.append({'kind': table, 'values': row})
def put(rel, raw):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == raw
    else: path.write_bytes(raw)
    paths.add(str(path))
sources = [
 ('registry', here/'forum-860-registry-original.html', 'https://tbmm.gov.tr/Denetim/Genel-Gorusme-Onergesi-Detay/d70137be-4e19-41cd-82b0-0193afcf71ee', None, [
  ('number','TBMM genel görüşme sicil numarası','8 / 60'),
  ('date','Başkanlığa geliş tarihi','03/12/2024'),
  ('status','Sicilde erişimde görülen durum','G&#xFC;ndemde')]),
 ('session', here/'forum-860-26-session-original.html', 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/26/Tam/82d7c933-565b-49d1-b30c-c39dfb3411ef.html', '2024-12-03', [
  ('schedule','Grubun aynı gün ön görüşme önerisi','Grup Başkan Vekili İstanbul Milletvekili Bülent Kaya tarafından, İsrail\'le ticareti protesto eden gençlerin tutuklanması olayında yaşanan hukuk garabetinin tahlili ve alınacak tedbirlerin müzakere edilmesi amacıyla 3/12/2024 tarihinde Türkiye Büyük Millet Meclisi Başkanlığına verilmiş olan genel görüşme önergesinin ön görüşmelerinin, Genel Kurulun 3 Aralık 2024 Salı günkü birleşiminde yapılmasına ilişkin önerisi'),
  ('authority','Kaya dönemsel grup sıfatı','SAADET PARTİSİ GRUBU ADINA BÜLENT KAYA (İstanbul)'),
  ('demand','Kayanın genel görüşme açılmasına ilişkin talebi','Bu konuda bir genel görüşme açılması talebimizin Genel Kurulca kabul edilmesini'),
  ('vote','Aynı gün grup gündem önerisinin elektronik oylaması','(Elektronik cihazla oylama yapıldı)'),
  ('result','Aynı gündem önerisinin sonucu','Öneri kabul edilmemiştir.')]),
]
for key, filename, url, day, anchors in sources:
    raw=filename.read_bytes(); digest=sha256(raw).hexdigest(); doc='0411-forum-860-'+key; vid=doc+'-v1'
    original=f'objects/{digest}/original.html.bin'; readable=f'objects/{digest}/readable.html'
    put(original,raw); put(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title='8/60 genel görüşme ve grup gündem önerisi: '+key,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Sicilin çevrimiçi nüsha yayımlanma tarihi bilinmiyor; başvuru tarihi sicil pasajında.',version_label='TBMM özgün kaydı.',accessed_at=datetime.fromtimestamp(filename.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='İşlem günü ile erişilen nüshanın yayımlanma tarihi ayrı tutuldu.')
    view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view)
    manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
    body=html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix,repr(exact))
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
(here/'forum-860-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-forum860-paths').write_text('\n'.join(sorted(paths))+'\n')
print('source entries',len(entries),'paths',len(paths))
