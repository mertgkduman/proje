"""10/4830 ve 10/4918 resmi kaynakları; taslak değil gerçek pasajlar."""
import json
import hashlib
import re
from pathlib import Path
from arsiv import html_source_text, pdf_page_text

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
root = Path('data/practices/sources/dem')
capture = json.loads((checks/'2026-fon-4830-4918-views.json').read_text())
entries = []
for item in capture['records']:
    ident = item['id']
    pdf = ident.endswith('pdf')
    number = ident.removesuffix('pdf')
    doc = '0406-fund-'+ident
    ver = doc+'-v1'
    path = Path(item['path'])
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    entries.append(dict(kind='document', values=dict(id=doc, party_id='dem', title='10/'+number+(' imzalı araştırma önergesi' if pdf else ' TBMM işlem kaydı'), source_kind='official')))
    entries.append(dict(kind='document_version', values=dict(id=ver, document_id=doc, original_url=item['url'], final_url=item['url'], document_date='2026-10-20' if pdf else None, date_precision='day' if pdf else 'unknown', date_unknown_reason=None if pdf else 'İşlem kaydının ilk yayın tarihi belirtilmiyor.', version_label='TBMM özgün belgesi.', accessed_at=capture['accessed_at'], verified_at=capture['accessed_at'], mime='application/pdf' if pdf else 'text/html', sha256=item['sha256'], original_path=str(path.relative_to(root)), readable_path=item['readable_path'])))
    entries.append(dict(kind='source_attribution', values=dict(version_id=ver, publisher='TBMM', author=None, kind='official', published_at=None, date_precision='unknown', social_handle=None, public_url=item['url'], basis='TBMM kayıt ve imzalı belge; önerge iddiaları sahiplerine atfedilir.')))
    if not pdf:
        entries.append(dict(kind='archive_view', values=item['view']))
        text = html_source_text(raw)
        name = 'Bitlis Milletvekili H&#xFC;seyin Olan ve 19 Milletvekili' if number=='4830' else '&#x15E;&#x131;rnak Milletvekili Mehmet Zeki &#x130;rmez ve 19 Milletvekili'
        summary = re.search(r'<td>Sermaye piyasalar&#x131;nda ya&#x15F;anan manip&#xFC;lasyon.*?</td>', text).group()
        specs = [('number','<td>10 / '+number+'</td>','Esas numarası'), ('filed','<td>21/10/2026</td>','Başkanlığa geliş'), ('owner',name,'İlk imza sahibi ve sayı'), ('party','Halklar&#x131;n E&#x15F;itlik Ve Demokrasi Partisi','İmza sahibinin parti bilgisi'), ('summary',summary,'Araştırma isteğinin TBMM özeti'), ('pending','<td>G&#xFC;ndemde</td>','Erişim anındaki dosya durumu')]
        for label, exact, section in specs:
            assert exact in text, (ident,label)
            entries.append(dict(kind='passage', values=dict(id=doc+'-'+label+'-p', version_id=ver, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)))
    else:
        exact = '10/'+number
        assert exact in pdf_page_text(str(path.resolve()),0)
        entries.append(dict(kind='passage', values=dict(id=doc+'-number-p', version_id=ver, exact=exact, prefix=None, suffix=None, article=None, section='İmzalı belgenin esas numarası', pdf_page_index=0, printed_page=None)))
out = checks/'fund-inquiries-source-records.json'
out.write_text(json.dumps(dict(party_id='dem', entries=entries),ensure_ascii=False,indent=2)+'\n')
print('INQUIRIES_SOURCE_RECORDS',len(entries),hashlib.sha256(out.read_bytes()).hexdigest())
