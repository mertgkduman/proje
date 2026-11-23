"""İki tarihsel bildirgenin 76 sayfa metin katmanını karşılaştırır."""
import hashlib, json
from difflib import SequenceMatcher
from pathlib import Path
from arsiv import pdf_page_text
root=Path(__file__).resolve().parents[4]/'data/practices/sources/dem/objects'
digests=('fe2863716a6f0f8ecd3108ac7bc9c91b697fb7f6c4269245ba7726dab78b42a4','8a7cc7d49cb97ffcff20eb4b395f2fac75187b361d2a72cda2c7022bb8e8808b')
texts=[]
for digest in digests:
    p=root/digest/'original.pdf'; assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
    texts.append(' '.join(pdf_page_text(p,i) for i in range(76)))
terms=('YURT DIŞINDAKİ YURTTAŞLARIN SORUNLARINI ÇÖZECEĞİZ','Türkiye Özerk Sanat','1117 sayılı')
for t in terms: assert t.casefold() in texts[0].casefold() and t.casefold() not in texts[1].casefold()
a,b=(t.split() for t in texts)
ratio=SequenceMatcher(None,a,b,autojunk=True).ratio()
print(json.dumps({'sources':list(digests),'pages_compared_per_source':76,'tokens':[len(a),len(b)],'similarity':ratio,
 'missing_in_second_text_layer':list(terms),'limits':'Metin katmanı araması tam görsel sayfa okuması, yayın sırası veya hukukî kimlik kanıtı değildir.'},ensure_ascii=False,indent=2))
