import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
file=Path('data/practices/sources/tip/objects/ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed/original.pdf')
exact='3586 2/3833 Yüksek Öğrenim Kredi ve Yurt Hizmetleri Kanunu ile Yükseköğretim Kurumları Teşkilat\nKanununda Değişiklik Yapılmasına Dair Kanun Teklifi (Türkiye İşçi Partisi Genel Başkanı\nİstanbul Milletvekili Erkan Baş ve 3 Milletvekili)'
assert exact in pdf_page_text(file,207)
entry=dict(kind='passage',values=dict(id='0405-tip-yurt-hukumsuz-p',version_id='0405-tip-sendika-hukumsuz-v1',exact=exact,prefix=None,suffix=None,article=None,section='Hükümsüz teklifler sıra 3586',pdf_page_index=207,printed_page='174'))
(p/'yurt-outcome-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=[entry]),ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',1)
