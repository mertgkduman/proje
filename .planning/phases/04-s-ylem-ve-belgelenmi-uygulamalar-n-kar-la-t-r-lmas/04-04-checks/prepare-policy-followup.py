import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / 'src'))
from arsiv import html_source_text
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/policy-followup-records-draft.json')
sources = [
 dict(id='0404-barinma-oylama-ikincil', digest='db13f4aded14574e053d3c46aa5068bbc5cb5d7c1b01d7917182bff3ed2d5c98', url='https://www.referandom.com/onergeler/barinma-krizinin-nedenleri-ve-sonuclari', date=None, accessed='2026-11-21T20:42:48.886541+00:00', publisher='Referandom', title='Barınma Krizinin Nedenleri ve Sonuçları: Araştırma Önergesi', exact='Önergenin Genel Kurulda görüşülmesini öneren grup önerisi 7 Ağustos 2026', section='Grup önerisinin görüşülmesine ilişkin ikincil kaynak'),
 dict(id='0404-fon-aciklama', digest='b40111718d0ddebf351225fbbc4cb1803f30ce0ce72c8868c4ccc38e6340c021', url='https://gazeteoksijen.com/turkiye/fon-kriziyle-ilgili-yeni-partiden-kanun-teklifi-zarar-sorumlularin-mal-varliklariyla-karsilansin-290188', date='2026-09-21', accessed='2026-11-21T20:42:51.156503+00:00', publisher='Gazete Oksijen', title='Fon kriziyle ilgili Yeni Parti’den kanun teklifi', exact='bu hafta içinde Meclis', section='Hazırlanıp sunulması planlanan kanun teklifine dair açıklama'),
]
entries = []
for s in sources:
 raw = (root/'objects'/s['digest']/'original.html.bin').read_bytes()
 assert hashlib.sha256(raw).hexdigest() == s['digest']
 assert s['exact'] in html_source_text(raw), s['id']
 view = build_view(raw, s['url'], root, fetch_assets=False, http_charset='utf-8')
 view['version_id'] = s['id']+'-v1'
 validate_view(root, view)
 precision = 'day' if s['date'] else 'unknown'
 values = [
  ('document', dict(id=s['id'], party_id='yeni-parti', title=s['title'], source_kind='journalism')),
  ('document_version', dict(id=s['id']+'-v1', document_id=s['id'], original_url=s['url'], final_url=s['url'], document_date=s['date'], version_label='Yakalanan HTML', accessed_at=s['accessed'], verified_at=s['accessed'], mime='text/html', sha256=s['digest'], original_path='objects/'+s['digest']+'/original.html.bin', readable_path='objects/'+s['digest']+'/readable.html', date_precision=precision, date_unknown_reason=None if s['date'] else 'Sayfanın yayımlanma tarihi belirtilmiyor; atfedilen oylama tarihi sayfada ayrıca yer alıyor.')),
  ('archive_view', view),
  ('passage', dict(id=s['id']+'-p', version_id=s['id']+'-v1', exact=s['exact'], prefix=None, suffix=None, article=None, section=s['section'], pdf_page_index=None, printed_page=None)),
  ('source_attribution', dict(version_id=s['id']+'-v1', kind='journalism', publisher=s['publisher'], author=None, social_handle=None, published_at=s['date'], date_precision=precision, public_url=s['url'], basis='Kaynak sayfasındaki yayıncı ve varsa tarih incelendi.')),
 ]
 entries.extend(dict(kind=k, values=v) for k,v in values)
out.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=entries), ensure_ascii=False, indent=2)+'\n')
print('PREPARED', len(sources), len(entries), out)
