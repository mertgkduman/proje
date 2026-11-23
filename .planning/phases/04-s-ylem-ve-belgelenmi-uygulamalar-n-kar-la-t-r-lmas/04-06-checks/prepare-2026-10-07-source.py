"""7 Ekim TBMM grup konuşması için kaynak ve tam eşleşen pasajlar."""
import hashlib,json
from pathlib import Path
from arsiv import html_source_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks'); root=Path('data/practices/sources/dem')
captures=json.loads((p/'2026-10-07-fon-captures.json').read_text()); entries=[]
for c in captures:
 doc='0406-2026-10-07-'+c['id']; version=doc+'-v1'; raw=(root/c['original_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==c['sha256']
 entries.extend([{'kind':'document','values':dict(id=doc,party_id='dem',title='7 Ekim 2026 TBMM 3. Birleşim '+('tam tutanağı' if c['id']=='full' else 'özeti'),source_kind='official')},{'kind':'document_version','values':dict(id=version,document_id=doc,original_url=c['original_url'],final_url=c['final_url'],document_date='2026-10-07',date_precision='day',date_unknown_reason=None,version_label='TBMM erişimindeki birleşim kaydı.',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'])},{'kind':'source_attribution','values':dict(version_id=version,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=c['original_url'],basis='TBMM birleşim kaydı; konuşmalar sahiplerine ve tarihe atfedilir.')},{'kind':'archive_view','values':c['view']}])
full=next(c for c in captures if c['id']=='full'); text=html_source_text((root/full['original_path']).read_bytes());ver='0406-2026-10-07-full-v1'
for name,exact,section in [
 ('yilmaz-role','CUMHURBAŞKANI YARDIMCISI CEVDET YILMAZ - Sayın Meclis Başkan Vekilim','Cumhurbaşkanı Yardımcısının konuşmacı kimliği'),
 ('yilmaz-system','finans piyasalarımızda sistemik bir risk söz konusu değildir.','Yılmaz sistemik risk değerlendirmesi'),
 ('yilmaz-fund','bu süreçte oluşan özel zararlar için hazine kaynağının kullanılmayacağıdır.','Yılmaz Hazine kaynağı açıklaması'),
 ('kocyigit-role','DEM PARTİ GRUBU ADINA GÜLÜSTAN KILIÇ KOÇYİĞİT (Kars)','Koçyiğit DEM grubu adına'),
 ('kocyigit-commission','Mecliste bir araştırma komisyonu kurulsun ve Meclis sürece el koysun','Koçyiğit komisyon talebi'),
 ('kocyigit-transparency','sistemi şeffaf, açık, denetlenebilir hâle getirmedikçe','Koçyiğit şeffaflık değerlendirmesi'),
 ('kocyigit-system','Burada sistemsel bir sorun var','Koçyiğit sistemsel sorun değerlendirmesi'),
 ('kocyigit-payment','yatırımcının parasını ne zaman alacağını bilmesi','Koçyiğit ödeme takvimi talebi'),
 ('temelli-role','DEM PARTİ GRUBU ADINA SEZAİ TEMELLİ (Muş)','Temelli DEM grubu adına'),
 ('temelli-commission','gerçekten, ciddiyetle bir komisyon kurulmasıdır.','Temelli komisyon talebi')]:
 assert exact in text,(name,exact)
 entries.append({'kind':'passage','values':dict(id='0406-2026-10-07-'+name+'-p',version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)})
out=p/'2026-10-07-fon-source-records.json';out.write_text(json.dumps(dict(party_id='dem',entries=entries),ensure_ascii=False,indent=2)+'\n');print('FUND_SOURCE_RECORDS',hashlib.sha256(out.read_bytes()).hexdigest(),len(entries))
