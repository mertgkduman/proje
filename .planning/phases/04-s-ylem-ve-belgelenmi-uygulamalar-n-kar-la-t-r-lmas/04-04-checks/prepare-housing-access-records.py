import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
specs = [
    ('3952', 'a91657281014ffd719ec751e1a841d168d95fd91a328d6342b19443de4957ab7', 'https://tbmm.gov.tr/Yasama/KanunTeklifi/d026dc83-3d6c-42f1-8ac0-01a13ff8e1d8', '2 / 3952', 'Teklif ile, kamu kurumlar&#x131;nca', '2/3952 öğrenci barınma desteği kanun teklifi'),
    ('104686', '8c55bf6c468640f54f44d5f834b6637527f373160a5f797a7f91fd05911b2d6f', 'https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/30dc341b-9222-4a0e-85a3-01a14467c33d', '10 / 4686', 'Konut kiralar&#x131;n&#x131;n hane gelirleri', '10/4686 kira etkileri araştırma önergesi'),
    ('752416', 'ec230d864f8938f750c36f326bdfd705e66d90a735cdd24905823b1bdcc885ae', 'https://www.tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/4809b13c-21c0-4890-ab38-01a1a5753575', '7 / 52416', 'Diyarbak&#x131;r&#x27;da engelli bireylere', '7/52416 Diyarbakır erişilebilirlik yazılı soru önergesi'),
]
all_entries = []
for num, digest, url, number, start, title in specs:
    capture = Path('/tmp/gsd-0404-'+num+'.html')
    raw = capture.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    folder = root/'objects'/digest
    folder.mkdir(parents=True, exist_ok=True)
    for name, content in [('original.html.bin', raw), ('readable.html', readable_bytes(raw, 'html', legacy=False))]:
        dest = folder/name
        if dest.exists(): assert dest.read_bytes() == content
        else: dest.write_bytes(content)
    ident = '0404-tbmm-housing-access-'+num
    view = build_view(raw, url, root, fetch_assets=False, http_charset='utf-8')
    view['version_id'] = ident+'-v1'
    validate_view(root, view)
    text = html_source_text(raw)
    i = text.find(start); j = text.find('</td>', i)
    assert i >= 0 and j > i and number in text
    accessed = datetime.fromtimestamp(capture.stat().st_mtime, timezone.utc).isoformat(timespec='seconds')
    verified = datetime.now(timezone.utc).isoformat(timespec='seconds')
    entries = [
        ('document', dict(id=ident, party_id='yeni-parti', title=title, source_kind='official')),
        ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=url, final_url=url.replace('www.tbmm.gov.tr', 'tbmm.gov.tr'), document_date=None, version_label='TBMM dinamik kayıt sayfası; yakalanan HTML', accessed_at=accessed, verified_at=verified, mime='text/html', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='unknown', date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; önerge tarihi ayrı kaydedilir.')),
        ('archive_view', view),
        ('passage', dict(id=ident+'-p', version_id=ident+'-v1', exact=text[i:j], prefix=None, suffix=None, article=None, section=title+' özeti', pdf_page_index=None, printed_page=None)),
        ('source_attribution', dict(version_id=ident+'-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='TBMM kurumsal başlığı ve kayıt künyesi incelendi.')),
    ]
    all_entries += [dict(kind=k, values=v) for k,v in entries]
    print(num, digest, view['view_id'])
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/housing-access-records-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=all_entries), ensure_ascii=False, indent=2)+'\n')
