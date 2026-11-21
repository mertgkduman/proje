import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
specs = [
    ('104683', '93ecb54a5c7fc54120d85000f6f7c1d8ba37ae013b7652a4e10fc814985c95a0', 'https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/d1ebf2ae-d7fd-40ca-a759-01a1446123b7', '10 / 4683', 'Kad&#x131;na y&#xF6;nelik &#x15F;iddetin', '10/4683 kadına yönelik şiddet araştırma önergesi'),
    ('749746', 'f1440dc19710b02a15d803c4f99a13bf4fe6f619f1ed8c874c1ebc6ffd1f6452', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/c1c96224-192e-42eb-a3e8-01a0f1bcb328', '7 / 49746', 'Kad&#x131;na y&#xF6;nelik &#x15F;iddet olaylar&#x131;', '7/49746 kadına yönelik şiddet yazılı sorusu'),
]
entries = []
for num, digest, url, number, start, title in specs:
    capture = Path('/tmp/gsd-0404-'+num+'.html'); raw = capture.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    folder = root/'objects'/digest; folder.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = folder/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0404-tbmm-kadina-siddet-'+num
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8'); view['version_id'] = ident+'-v1'; validate_view(root, view)
    text = html_source_text(raw); i = text.find(start); j = text.find('</td>', i)
    assert i >= 0 and j > i and number in text
    accessed = datetime.fromtimestamp(capture.stat().st_mtime, timezone.utc).isoformat(timespec='seconds'); checked = datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows = [
        ('document', dict(id=ident, party_id='yeni-parti', title=title, source_kind='official')),
        ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url.replace('www.tbmm.gov.tr', 'tbmm.gov.tr'), document_date=None, version_label='TBMM dinamik kayıt sayfası; yakalanan HTML', accessed_at=accessed, verified_at=checked, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='unknown', date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; önerge tarihi ayrı kaydedilir.')),
        ('archive_view', view), ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=text[i:j], prefix=None, suffix=None, article=None, section=title+' özeti', pdf_page_index=None, printed_page=None)),
        ('source_attribution', dict(version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM kurumsal başlığı ve kayıt künyesi incelendi.')),
    ]
    entries += [dict(kind=k, values=v) for k,v in rows]
    print(num, view['view_id'])
p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/violence-records-draft.json')
p.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=entries), ensure_ascii=False, indent=2)+'\n')
