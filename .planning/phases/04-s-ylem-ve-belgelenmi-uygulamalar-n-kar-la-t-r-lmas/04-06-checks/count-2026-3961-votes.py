"""Kesin cetvelde DEM etiketli satırları sonuç ve kaynak sütunlarıyla say."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

class Rows(HTMLParser):
    def __init__(self):
        super().__init__(); self.row = None; self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
    def handle_data(self, data):
        if self.row is not None and data.strip(): self.row.append(data.strip())
    def handle_endtag(self, tag):
        if tag == 'tr' and self.row is not None:
            if 'Halkların Eşitlik ve Demokrasi Partisi' in self.row: self.rows.append(self.row)
            self.row = None

path = Path('data/practices/sources/dem/objects/dee8048e3732d2414f3db05c106dfa60b39b8d7a92cff70bb31198527e0939da/original.html.bin')
parser = Rows(); parser.feed(path.read_bytes().decode('cp1254'))
assert len(parser.rows) == 56 and all(len(row) == 9 for row in parser.rows)
counts = Counter((row[4],row[5],row[6]) for row in parser.rows)
assert counts == {('KATILMADI','-','KATILMADI'):34, ('RET','-','RET'):21, ('KATILMADI','RET','RET'):1}
print('Sistem / Pusula / Sonuç:', dict(counts))
