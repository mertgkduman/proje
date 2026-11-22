import hashlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import readable_bytes

phase = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
root = Path('data/practices/sources/yeni-parti')
reading = json.loads((phase / 'party-api-003-reading.json').read_text())
excerpts = {
    281: "Erdoğan'ın Husilerle ilgili ve Yemen'le ilgili görüşlerinde büyük bir dalgalanma var.",
    280: 'YENİ Parti Genel Başkanı Özgür Özel, eski Başbakan Bülent Ecevit’in vefatının 20’nci yıl dönümünde Devlet Mezarlığı’ndaki kabri başında düzenlenen anma törenine katıldı.',
    279: 'Avrupa İnsan Hakları Mahkemesi kararlarınca 3 kez siyasi amaçlarla yapıldığı, siyasi rakiplerine siyaset yaptırmamak üzere hukukun kullanıldığı yönünde kararları var.',
    278: 'emeklilikte adalet olsun ama emekli de insanlık onuruna yakışır ve emeğinin karşılığı bir maaş alsın',
    277: 'Sağlık Bakanlığı bu açığı nasıl vermiştir ve bu açığın kapatılması için ne yapılmaktadır ve bunun sonucunda zarar gören hastalarımız için ne yapılmıştır?',
}
entries = []
for item in reading['documents']:
    number = item['id']
    digest = item['sha256']
    folder = root / 'objects' / digest
    raw = (folder / 'original.html.bin').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == digest
    data = json.loads(raw)
    exact = excerpts[number]
    span = item['source_section_ranges']
    assert exact in data['icerik'][span['char_start']:span['char_end']]
    assert exact.encode() in raw
    readable = readable_bytes(raw, 'html', legacy=False)
    path = folder / 'readable.html'
    if path.exists():
        assert path.read_bytes() == readable
    else:
        path.write_bytes(readable)
    ident = f'0404-yeni-parti-haber-{number}'
    created = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
    day = created.astimezone(timezone(timedelta(hours=3))).date().isoformat()
    checked = datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows = [
        ('document', dict(id=ident, party_id='yeni-parti', title=item['title'], source_kind='party')),
        ('document_version', dict(id=ident+'-v1', document_id=ident, original_url=item['url'], final_url=item['url'], document_date=day, version_label='Kamuya açık JSON; created_at '+item['created_at']+' (Türkiye günü '+day+'); yayın zamanı ayrıca belirlenmedi.', accessed_at=item['accessed_at'], verified_at=checked, mime='application/json', sha256=digest, original_path='objects/'+digest+'/original.html.bin', readable_path='objects/'+digest+'/readable.html', date_precision='day', date_unknown_reason=None)),
        ('passage', dict(id=ident+'-003-p', version_id=ident+'-v1', exact=exact, prefix=None, suffix=None, article=None, section='Parti yayını; 003 okuma dilimi', pdf_page_index=None, printed_page=None)),
        ('source_attribution', dict(version_id=ident+'-v1', kind='party_publication', publisher='Yeni Parti', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=item['url'], basis='Parti JSON içeriği ve created_at okundu; oluşturulma zamanı ayrı yayın tarihi değildir.')),
    ]
    entries.extend(dict(kind=kind, values=values) for kind, values in rows)

output = phase / 'party-api-003-source-records-draft.json'
assert not output.exists()
output.write_text(json.dumps(dict(status='draft_unvalidated', source_root=str(root), entries=entries), ensure_ascii=False, indent=2)+'\n')
print(output, len(entries))
