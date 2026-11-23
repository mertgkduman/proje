"""2012 arşiv yakalamasındaki parti metnini izlenebilir okuma dilimlerine ayırır."""
import hashlib, json
from html.parser import HTMLParser
from pathlib import Path

c = Path(__file__).resolve().parent
root = c.parents[3]
source = root/'data/practices/sources/dem/objects/8a0478f4dc358fbdbaeeddfad02a437c8a3135f7768982d2e151e4d9bc3522ed/original.html.bin'
assert hashlib.sha256(source.read_bytes()).hexdigest() == '8a0478f4dc358fbdbaeeddfad02a437c8a3135f7768982d2e151e4d9bc3522ed'
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.done = False; self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == 'div' and dict(attrs).get('id') == 'post-54': self.depth = 1
        elif self.depth and tag == 'div': self.depth += 1
    def handle_endtag(self, tag):
        if self.depth and tag == 'div':
            self.depth -= 1
            if not self.depth: self.done = True
    def handle_data(self, text):
        if self.depth and text.strip(): self.parts.append(text.strip())
p = Extract(); p.feed(source.read_text()); assert p.done
text = '\n'.join(p.parts)
assert 'Giderek artan bir karbon vergisi' in text
Path('/tmp/gsd-dem-2012-program-extracted.txt').write_text(text)
queue = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
         'capture_at': '2012-12-05T01:34:41Z', 'publication_date': None,
         'text_sha256': hashlib.sha256(text.encode()).hexdigest(), 'characters': len(text),
         'note': 'Arşiv yakalama tarihi yayın veya hukuki yürürlük tarihi değildir; parti kimliği ve kapsam ayrıca araştırılır.',
         'segments': [{'start': i, 'end': min(i+12000, len(text)), 'status': 'pending'} for i in range(0,len(text),12000)]}
out = c/'2012-primary-reading-queue.json'
assert not out.exists(), 'Var olan okuma kuyruğu üzerine yazılamaz.'
out.write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
print('SEGMENTS',len(queue['segments']),'CHARACTERS',len(text),'SHA',queue['text_sha256'])
