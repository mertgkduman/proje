import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');root=Path('data/practices/sources/tip')
r=json.loads((p/'kadigil-katilim-capture.json').read_text())[0];sha=r['sha256'];url=r['url'];raw=(root/'objects'/sha/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
doc='0405-tip-kadigil-bio';vid=doc+'-v1'; exact='25 Haziran 2021’de CHP’den istifa ederek Türkiye İşçi Partisi’ne (TİP) katıldı; 2021’den bu yana TİP Parti Sözcüsü’dür.'
assert exact in html_source_text(raw)
entries=[dict(kind='document',values=dict(id=doc,party_id='tip',title='Sera Kadıgil — Parti Sözcüsü',source_kind='party')),
 dict(kind='document_version',values=dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date=None,version_label='Parti biyografisi erişim anı',accessed_at=r['accessed_at'],verified_at=r['accessed_at'],mime='text/html',sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',date_precision='unknown',date_unknown_reason='Biyografi sayfasında yayın tarihi ayrıca saptanmadı.')),
 dict(kind='archive_view',values=r['view']),
 dict(kind='source_attribution',values=dict(version_id=vid,kind='party_publication',publisher='Türkiye İşçi Partisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Partinin resmî biyografi sayfasındaki özgeçmiş ve tarih okundu.')),
 dict(kind='passage',values=dict(id=doc+'-authority-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Partiye katılım ve sözcülük',pdf_page_index=None,printed_page=None)),
 dict(kind='passage',values=dict(id=doc+'-identity-p',version_id=vid,exact='1984’te İstanbul’da doğan Saliha Sera Kadıgil',prefix=None,suffix=None,article=None,section='Biyografi ve kimlik',pdf_page_index=None,printed_page=None))]
(p/'kadigil-identity-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n');print('DRAFT_ONLY',len(entries))
