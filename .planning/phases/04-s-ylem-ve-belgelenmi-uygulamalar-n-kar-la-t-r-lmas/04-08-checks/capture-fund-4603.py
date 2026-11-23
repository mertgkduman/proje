"""Archive the signed 10/4603 motion and its separate agenda vote."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/yeni-yol')
now=datetime.now(timezone.utc).isoformat()
entries,paths=[],set()


def add(table,**row):
    entries.append(dict(kind=table,values=row))


def save(relative,raw):
    p=root/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        assert p.read_bytes()==raw
    else:
        p.write_bytes(raw)
    paths.add(p)


day = '2026-10-08'
prefix = '0408-fund-4603-'
sources = (
    ('4603-detail.html','detail','TBMM 10/4603 esas kaydı',None,
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/0ee13dab-286f-4760-92f8-01a116348ed2',
     'b719459c1f901a6909bb3aa926a49a6009f5ab8f71792d09d7b40290d2da2ef0', (
        ('id','10/4603 esas numarası',None,'<td>10 / 4603</td>'),
        ('filed','TBMM Başkanlığına geliş 6 Ekim 2026',None,'<td>06/10/2026</td>'),
        ('status','Erişilen esas dosyası durumu',None,'<td>G&#xFC;ndemde</td>'),
        ('owner','Araştırma önergesi sahibi ve diğer imzacılar',None,'Adana Milletvekili Sadullah K&#x131;sac&#x131;k ve 19 Milletvekili'),
        ('party','İlk imzacının TBMM kaydındaki grup kimliği',None,
         'Sadullah KISACIK</a></td>\n                                        <td>Yeni Yol Partisi</td>'),
    )),
    ('4603.pdf','signed','10/4603 imzalı Meclis araştırması önergesi','2026-10-06',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/f5d4bf49-10ea-4887-92b0-9f3c4eff1fa9.pdf',
     '82d70de8dffd013ad79eafd5116e0e476548d63a47338e6be9d8367c12610382', (
        ('id','İmzalı kapak, 10/4603 esas numarası',0,'10/4603'),
        ('purpose','Gerekçe, haksız kazançların geri alınması ve denetim incelemesi',1,
         'haksız kazançların geri alınmasına yönelik hukuki imkânların ve denetim kurumlarının zafiyetlerinin'),
        ('signature','İmza cetveli, Sadullah Kısacık satırı',2,'SADULLAH KISACIK'),
    )),
    ('oct08-tam.raw','floor','8 Ekim 2026 TBMM 4. Birleşim tam tutanağı',day,
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/4/Tam/a78ffde7-97e0-4bb8-b6ea-6582538fbefb.html',
     '8fa9f978a5242784bfd8585a02f5b4346caf162becc8ecc254916a08962111b8', (
        ('role','Sadullah Kısacık’ın Yeni Yol grup sıfatı',None,'YENİ YOL GRUBU ADINA SADULLAH KISACIK (Adana)'),
    )),
    ('oct08-ozet.raw','summary','8 Ekim 2026 TBMM 4. Birleşim işlem özeti',day,
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/4/Ozet/7eb77611-f009-4a79-afa7-f1394eb71798.html',
     'ff5bd3a434870ee7de0e0690394604368a49ced75831c2ad94ea79fac93397f8', (
        ('motion','İşlem özetinde 6 Ekim başvurusu ve imzacı',None,'6/10/2026 tarihinde Adana Milletvekili Sadullah Kısacık ve 19 milletvekili'),
        ('result','Özette aynı gün görüşme önerilerinin sonucu',None,'önerileri yapılan görüşmelerden sonra kabul edilmedi.'),
    )),
)

for filename, key, title, date, url, digest, specs in sources:
    src = stage/filename
    raw = src.read_bytes()
    assert sha256(raw).hexdigest() == digest, filename
    pdf = filename.endswith('.pdf')
    doc = prefix+key
    vid = doc+'-v1'
    original = f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, 'pdf' if pdf else 'html', legacy=False))
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=date,
        date_precision='day' if date else 'unknown',
        date_unknown_reason=None if date else 'TBMM dosyasının ilk yayımlandığı gün açık değil. Geliş tarihi ayrı pasajda.',
        version_label='Erişilen özgün TBMM kaydı.', mime='application/pdf' if pdf else 'text/html',
        accessed_at=datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).isoformat(), verified_at=now,
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher='TBMM', author=None, kind='official',
        published_at=None, date_precision='unknown', social_handle=None, public_url=url,
        basis='TBMM birleşim ve evrak kimlikleri asıl belgede okundu.')
    if pdf:
        assert tuple(pdf_page_text(root/original, i).strip() for i in range(3)) == ('10/4603', '', '')
    else:
        view = build_view(raw, url, root, fetch_assets=False)
        manifest = root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        view['version_id'] = vid
        validate_view(root, view)
        add('archive_view', **view)
        body = html_source_text(raw)
    if key == 'floor':
        role = body.index('YENİ YOL GRUBU ADINA SADULLAH KISACIK (Adana)')
        agenda = '8/10/2026 Perşembe günkü birleşimde yapılması önerilmiştir.'
        agenda_start = body.rindex(agenda, 0, role)
        start = body.rindex('Adana Milletvekili Sadullah Kısacık ve 19 milletvekili',0,agenda_start)
        vote = 'Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'
        vote_start = body.index(vote, role)
        other = body.index('İYİ Parti Grubunun İç Tüzük', vote_start)
        assert start < agenda_start < role < vote_start < other
        specs += (
            ('agenda','Yeni Yol’un 6 Ekim başvurusu için 8 Ekim ön görüşme önerisi',None,body[start:agenda_start+len(agenda)]),
            ('decision','Yeni Yol’un ön görüşme önerisine ilişkin başkanın ilk oturum oylaması',None,body[vote_start:vote_start+len(vote)]),
        )
    for suffix, section, page, exact in specs:
        if not pdf:
            assert exact in body, (key, suffix)
        pid = doc+'-'+suffix
        add('passage', id=pid, version_id=vid, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=page, printed_page=None)
        if page in (1, 2):
            add('manual_passage', passage_id=pid, checked_at=now,
                method='Özgün PDF sayfası Poppler görüntüsünden okundu.',
                reason='İlgili sayfada metin katmanı yok. Gerekçe ve imza tablosu görsel olarak okundu.')
out = checks/'fund-4603-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='yeni-yol', entries=entries), ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0408-fund-4603-source-paths').write_text('\n'.join(sorted(map(str, paths)))+'\n')
print(len(entries), len(paths), sha256(out.read_bytes()).hexdigest())
