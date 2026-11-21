import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
verified_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
specs = [
    ('4687', '679bdb2f-a46e-41f2-ba81-01a144692e1f', 'fabd52ee4d48f3054d2a1b53a374710e3b5a59136e9a93fe39625c222a73e619', '&#xC7;ocuk yoksullu&#x11F;u ve &#xE7;ocuk i&#x15F;&#xE7;ili&#x11F;iyle', 'Ayça Taşkent ve 19 milletvekili, 12 Ekim 2026'),
    ('4553', 'e67c5f6e-b36d-4bdb-bac5-01a0f6a6484a', 'd6f0a1dce9a2a6a33057c1afd7b6357df7cd0a23263b5cbfd944bb6e494d75ce', '18 ya&#x15F;&#x131;n alt&#x131;nda &#xE7;al&#x131;&#x15F;mak', 'Turan Taşkın Özer ve 20 milletvekili, 30 Eylül 2026'),
]
all_entries = []
for number, uuid, digest, start, description in specs:
    captured = Path('/tmp/gsd-0404-10' + number + '.html')
    raw = captured.read_bytes()
    accessed_at = datetime.fromtimestamp(captured.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
    assert hashlib.sha256(raw).hexdigest() == digest
    folder = root / 'objects' / digest
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = folder / name
        if dest.exists():
            assert dest.read_bytes() == content
        else:
            dest.write_bytes(content)
    url = 'https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/' + uuid
    ident = '0404-tbmm-cocuk-emegi-' + number
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = ident + '-v1'
    validate_view(root, view)
    text = html_source_text(raw)
    i = text.find(start)
    j = text.find('</td>', i)
    assert i >= 0 and j > i and '10 / ' + number in text
    exact = text[i:j]
    entries = [
        ('document', dict(id=ident, party_id='yeni-parti', title='10/' + number + ' çocuk işçiliği araştırma önergesi', source_kind='official')),
        ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url, document_date=None, version_label='TBMM dinamik kayıt sayfası; yakalanan HTML', accessed_at=accessed_at, verified_at=verified_at, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='unknown', date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; önerge tarihi ayrı kaydedilir.')),
        ('archive_view', view),
        ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='10/'+number+' önerge özeti', pdf_page_index=None, printed_page=None)),
        ('source_attribution', dict(version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM kurumsal başlığı ve önerge künyesi incelendi; '+description)),
    ]
    all_entries.extend(dict(kind=k, values=v) for k,v in entries)
    print(number, digest, repr(exact))
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/child-labor-research-records-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=all_entries), ensure_ascii=False, indent=2)+'\n')
