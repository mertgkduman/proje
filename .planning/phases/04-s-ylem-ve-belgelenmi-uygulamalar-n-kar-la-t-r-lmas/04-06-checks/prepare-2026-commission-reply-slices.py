"""Komisyonda DEM sorusu ve bakan yardımcısı yanıtı için gerçek PDF pasajları."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text
root=Path('data/practices/sources/dem');p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');c=json.loads((p/'2026-commission-5480-capture.json').read_text());text=pdf_page_text((root/c['original_path']).resolve(),31)
question="Türkiye Suudi Arabistan saflarında Yemen'deki savaşa dâhil olacak mı, olacaksa ne şekilde? Bence net değildi cevap, o\nyüzden tekrar sorma ihtiyacı duydum."
answer="DIŞİŞLERİ BAKAN YARDIMCISI ZEKİ LEVENT GÜMRÜKÇÜ - Yani çok açık cevap vermem gerekirse bu aşamada Mekke\nSavunma İttifakı çerçevesinde böyle bir öngörümüz asla olmadığı gibi bir asker konuşlandırması da söz konusu değil. Anlaşma\nonaylandıktan sonra 2'nci maddede kayıtlı hususlar çerçevesinde, bir defa Birleşmiş Milletler 51'inci maddesinin tanıdığı meşru\nmüdafaa hakkı çerçevesinde ve yapılabilecek objektif değerlendirmeyi müteakiben katılacağız. Bu aşamada sizin sorunuza cevaben\nböyle bir öngörü, böyle bir planlama bulunmamakta."
assert question in text and answer in text
ident='0406-tbmm-2026-commission-5480';v=ident+'-v1';entries=[]
def add(k,x):entries.append(dict(kind=k,values=x))
add('document',dict(id=ident,party_id='dem',title='27 Ekim 2026 Dışişleri Komisyonu tutanağı',source_kind='official'))
add('document_version',dict(id=v,document_id=ident,original_url=c['original_url'],final_url=c['final_url'],document_date=c['document_date'],version_label='Komisyonun 24. toplantı tutanağı',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='application/pdf',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
for suffix,exact,section in [('question',question,'Akça Cupolo Yemen sorusu'),('reply',answer,'Gümrükçü Yemen yanıtı')]:
 add('passage',dict(id=ident+'-'+suffix+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=31,printed_page=None))
add('source_attribution',dict(version_id=v,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=c['document_date'],date_precision='day',public_url=c['final_url'],basis='Tutanak indeks 31 soru ve yanıtı konuşmacıları ve zamansal sınırıyla okundu.'))
(p/'2026-commission-reply-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,limitation='İlgili diyalog okundu; 35 sayfalık tutanağın tümü henüz okunmadı.'),ensure_ascii=False,indent=2)+'\n');print('COMMISSION_REPLY_SLICES_DRAFT',len(entries))
