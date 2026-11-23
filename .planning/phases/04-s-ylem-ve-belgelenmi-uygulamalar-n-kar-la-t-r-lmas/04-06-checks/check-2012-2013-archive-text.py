"""İki tarihli parti sitesi yakalamasının ana metnini boşluk normalizasyonuyla karşılaştırır."""
import hashlib
from html.parser import HTMLParser
from pathlib import Path
root=Path(__file__).resolve().parents[4]/'data/practices/sources/dem/objects'
class Content(HTMLParser):
    def __init__(self): super().__init__(); self.depth=0; self.parts=[]
    def handle_starttag(self,t,a):
        if t=='div' and dict(a).get('id')=='post-54': self.depth=1
        elif self.depth and t=='div': self.depth+=1
    def handle_endtag(self,t):
        if self.depth and t=='div': self.depth-=1
    def handle_data(self,d):
        if self.depth and d.strip(): self.parts.append(d.strip())
texts=[]
for digest in ('8a0478f4dc358fbdbaeeddfad02a437c8a3135f7768982d2e151e4d9bc3522ed','b07ad6f9eb2aa214838d8616158f9c63d8f32ffd91ee6d5187ce1b6111071b31'):
    raw=(root/digest/'original.html.bin').read_bytes(); assert hashlib.sha256(raw).hexdigest()==digest
    p=Content();p.feed(raw.decode('utf-8')); text=' '.join(p.parts)
    first='Küresel Statüko Sarsılıyor'; last='bu konulardaki kararlarına tam olarak saygı gösterilecek ortam yaratılmalıdır.'
    start=text.index(first); end=text.index(last,start)+len(last)
    texts.append(' '.join(text[start:end].split()))
assert texts[0]==texts[1]
print('TWO_CAPTURE_BODY_NORMALIZED_TEXT_MATCH',len(texts[0]),hashlib.sha256(texts[0].encode()).hexdigest())
