import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / 'src'))
from arsiv import html_source_text
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/yeni-parti')
out = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/october-referral-records-draft.json')
sources = [
 dict(id='0404-oguzeli-sevk', digest='204089737068f530fb165b15d69a2dbed0857ccbd63e7a8c12578143b38f8b86', url='https://www.referansgazetesi.com.tr/yeni-parti-gaziantepte-flas-karar-eski-belediye-baskanina-ihrac-soku', date='2026-10-20', accessed='2026-11-21T20:37:54.774195+00:00', publisher='Referans Gazetesi', author='Ayhan Duman', title='Yeni Parti Gaziantep’te flaş karar! Eski Belediye Başkanına ihraç şoku', exact='Söz konusu sevkin ardından gözler İl Disiplin Kurulundan çıkacak karara çevrildi.', section='Sevk sonrası disiplin kurulu kararı beklentisi'),
 dict(id='0404-agustos-kongre-takvim', digest='c683116dc47978125f27e6acc66bc4db0098c6e94d59e37cb7bc1c07ee79da3d', url='https://gazeteoksijen.com/turkiye/yeni-parti-kongre-takvimini-acikladi-286490', date='2026-08-19', accessed='2026-11-21T20:37:55.116800+00:00', publisher='Gazete Oksijen', author=None, title='Yeni Parti kongre takvimini açıkladı', exact='26 Ağustos: Üye çizelgelerinin askıya çıkarılması ve itiraz sürecinin başlaması', section='19 Ağustos tarihli planlanan kongre takvimi'),
]
entries = []
for s in sources:
 raw = (root / 'objects' / s['digest'] / 'original.html.bin').read_bytes()
 assert hashlib.sha256(raw).hexdigest() == s['digest']
 assert s['exact'] in html_source_text(raw), s['id']
 view = build_view(raw, s['url'], root, fetch_assets=False, http_charset='utf-8')
 view['version_id'] = s['id'] + '-v1'
 validate_view(root, view)
 version = dict(id=s['id']+'-v1', document_id=s['id'], original_url=s['url'], final_url=s['url'], document_date=s['date'], version_label='Yayımlanan haber; yakalanan HTML', accessed_at=s['accessed'], verified_at=s['accessed'], mime='text/html', sha256=s['digest'], original_path='objects/'+s['digest']+'/original.html.bin', readable_path='objects/'+s['digest']+'/readable.html', date_precision='day', date_unknown_reason=None)
 passage = dict(id=s['id']+'-p', version_id=version['id'], exact=s['exact'], prefix=None, suffix=None, article=None, section=s['section'], pdf_page_index=None, printed_page=None)
 attribution = dict(version_id=version['id'], kind='journalism', publisher=s['publisher'], author=s['author'], social_handle=None, published_at=s['date'], date_precision='day', public_url=s['url'], basis='Kaynak sayfasındaki yayıncı, tarih ve varsa yazar künyesi incelendi.')
 entries.extend([dict(kind='document', values=dict(id=s['id'], party_id='yeni-parti', title=s['title'], source_kind='journalism')), dict(kind='document_version', values=version), dict(kind='archive_view', values=view), dict(kind='passage', values=passage), dict(kind='source_attribution', values=attribution)])
out.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=entries), ensure_ascii=False, indent=2)+'\n')
print('PREPARED', len(sources), len(entries), out)
