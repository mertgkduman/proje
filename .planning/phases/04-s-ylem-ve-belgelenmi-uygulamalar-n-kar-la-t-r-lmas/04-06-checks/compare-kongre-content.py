from html.parser import HTMLParser
from pathlib import Path
import hashlib

class PageContent(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif tag == "div" and "page-content" in dict(attrs).get("class", "").split():
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, text):
        if self.depth:
            self.parts.append(text)

root = Path("data/.staging/gsd-0406-dem-silopi-62402330/objects")
paths = [root / "0ba81cd43ab9b5455db4a77ca66fc4bdf08df72a3dcb4fd40405ab977cc8ec45/original.html.bin", Path("data/practices/sources/dem/objects/3561d414c56eb9e903bb2cb3b256e879328b02ab6ca3527b87919f928dba4413/original.html.bin")]
texts = []
for path in paths:
    parser = PageContent()
    parser.feed(path.read_bytes().decode("utf8"))
    texts.append("".join(parser.parts))
assert texts[0] == texts[1]
assert len(texts[0]) == 87388
assert hashlib.sha256(texts[0].encode()).hexdigest() == "7b9c0e915739727031ffb618ba2fc8b517fdd7a6abbf1f7f667329162b473673"
print("CONTENT_MATCH", len(texts[0]))
