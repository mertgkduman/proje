from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here = Path(__file__).resolve().parent
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()
def add(table, **row): entries.append({'kind': table, 'values': row})
def put(rel, raw):
    path = root / rel; path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == raw
    else: path.write_bytes(raw)
    paths.add(str(path))
sources = [
 ('speech', '/tmp/saadet-budget-2025-speech.html', 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/40/Tam/3fe5757b-0729-48f3-b6af-1c65d70b0d36.html', 'html', '2024-12-20', [
  ('authority', '20 Aralık oturumunda Kaya konuşmasının grup sıfatı', 'SAADET PARTİSİ GRUBU ADINA BÜLENT KAYA (İstanbul)', None),
  ('stance', 'Kayanın 2025 bütçesine ilişkin grup tutumu', 'bu bütçeye "ret" oyu vereceğimizi ifade ederek', None)]),
 ('vote', '/tmp/saadet-budget-2025-40.pdf', 'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/40/Basilmis/9bdf06af-4371-4ab5-940a-df3674e01db0.pdf', 'pdf', '2024-12-21', [
  ('proposal', '2025 bütçesi 1/278 ve 162 sıra sayısı', '2025 Yılı Merkezi Yönetim Bütçe Kanunu Teklifi (1/278)', 150),
  ('kaya', 'Kaya kesin oy satırı: 162 bütçe ve 163 kesin hesap', 'İstanbul Kaya Bülent YENİ YOL Ret Ret', 159),
  ('totals', '162 bütçesi sonuçları', 'Kullanılan Oy Sayısı : 567\nKabul : 317\nRet : 249\nÇekimser : 1', 151),
  ('closure', '40. birleşimin 01.03 kapanışı', 'Kapanma Saati: 01.03', 151)]),
 ('law', '/tmp/saadet-7535-law.html', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/KanunMetni/743b1489-bca3-4793-99ea-9aceed7dc737.htm', 'html', '2024-12-21', [
  ('number', '2025 bütçesi kanun numarası', '7535', None),
  ('adopt', 'Bütçe kanunu kabul tarihi', '21/12/2024', None)]),
]
for key, filename, url, ext, day, anchors in sources:
    source=Path(filename); raw=source.read_bytes(); digest=sha256(raw).hexdigest()
    doc='0411-budget-1278-'+key; vid=doc+'-v1'
    original=f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable=f'objects/{digest}/readable.html'; put(original,raw); put(readable,readable_bytes(raw,ext,legacy=False))
    add('document',id=doc,party_id='saadet',title='2025 bütçe oyu ve konuşması: '+key,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',
        date_unknown_reason=None,version_label='TBMM 40. birleşimi 20 Aralık açıldı, bütçe 21 Aralık kabul edildi.' if key=='vote' else 'TBMM özgün nüshası.',
        accessed_at=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        mime='application/pdf' if ext=='pdf' else 'text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',
        social_handle=None,public_url=url,basis='Birleşim ve kabul tarihi bilinir; özgün çevrimiçi nüshanın yayımlanma tarihi belirlenmedi.')
    if ext=='html':
        view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view)
        manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
    for suffix,section,exact,page in anchors:
        body=html_source_text(raw) if page is None else pdf_page_text(root/original,page)
        assert exact in body,(key,suffix,repr(exact))
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
(here/'budget-1278-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-budget1278-paths').write_text('\n'.join(sorted(paths))+'\n')
print('source entries',len(entries),'paths',len(paths))
