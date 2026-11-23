"""2012 parti sitesi ile Agos aktarımını değiştirmeden seçili farkları karşılaştırır."""
import hashlib, json
from difflib import SequenceMatcher
from html.parser import HTMLParser
from pathlib import Path
c=Path(__file__).resolve().parent
root=c.parents[3]/'data/practices/sources/dem/objects'
class Content(HTMLParser):
    def __init__(self, ident): super().__init__(); self.ident=ident; self.depth=0; self.parts=[]
    def handle_starttag(self, tag, attrs):
        if tag=='div' and dict(attrs).get('id')==self.ident: self.depth=1
        elif self.depth and tag=='div': self.depth+=1
    def handle_endtag(self, tag):
        if self.depth and tag=='div': self.depth-=1
    def handle_data(self, data):
        if self.depth and data.strip(): self.parts.append(data.strip())
def extract(digest,ident):
    raw=(root/digest/'original.html.bin').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest
    p=Content(ident); p.feed(raw.decode('utf-8')); text=' '.join(p.parts)
    marker='Küresel Statüko Sarsılıyor'; assert marker in text
    return text[text.index(marker):]
site=extract('8a0478f4dc358fbdbaeeddfad02a437c8a3135f7768982d2e151e4d9bc3522ed','post-54')
agos=extract('69b09e485c4f250d42824a69d3e058bf354ad144d9014b1c1e290cc3062a8b50','gallery-3431')
left='ekonomik büyüme yerine sürdürülebilirliği temel alan yeşil ekonomik dönüşüme'
right='ekonomik büyüme yerine sürdürülebilir bir gelişmeyi temel alan yeşil ekonomik dönüşüme'
assert left in site and right in agos
assert 'bunları yaparken doğayı korumak ve ülkenin biyolojik kapasitesini artırmak' in site
assert 'bunları yaparken ülkenin biyolojik kapasitesini artırmak' in agos
tokens1,tokens2=site.split(),agos.split()
score=SequenceMatcher(None,tokens1,tokens2,autojunk=True).ratio()
print(json.dumps({'site_tokens':len(tokens1),'agos_tokens':len(tokens2),'similarity':score,
 'method':'HTML gövdesi, ilk ortak başlıktan sonraki boşlukla ayrılmış kelimeler; SequenceMatcher autojunk=True',
 'limits':'Site paylaşım metnini içerir; yüksek benzerlik tam metin eşitliği değildir. Yayın ve yürürlük tarihlerini göstermez.',
 'selected_difference':'Ekonomi bölümünde sürdürülebilirliği / sürdürülebilir bir gelişmeyi ve doğayı korumak ifadesi farkı.'},ensure_ascii=False,indent=2))
