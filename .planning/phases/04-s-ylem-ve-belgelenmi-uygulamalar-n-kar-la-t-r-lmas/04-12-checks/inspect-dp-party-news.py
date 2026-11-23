"""Extract the visible listing and dated article text from archived HTML."""

from datetime import date
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import re


class ArticleText(HTMLParser):
    """Preserve paragraph boundaries in the article body."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.drop = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.drop += 1
        if tag in ('br', 'hr') and not self.drop:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.drop -= 1
        if tag in ('p', 'li', 'div', 'h1', 'h2', 'h3', 'h4', 'tr') and not self.drop:
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.drop:
            self.parts.append(data)

    def text(self):
        return '\n'.join(' '.join(line.split()) for line in ''.join(self.parts).splitlines() if line.strip())


def list_articles(raw):
    text = raw.decode('utf-8')
    section = text.split('id="page">', 1)[1].split('<nav class="page-list"', 1)[0]
    pattern = r'<div class="in">\s*<a href="(https://www\.dp\.org\.tr/haber/[^"]+)">\s*<p>(.*?)</p>'
    rows = re.findall(pattern, section, re.S)
    assert rows and len(rows) == len({url for url, _ in rows})
    return [
        dict(position=number, url=url, listing_title=unescape(unescape(' '.join(label.split()))))
        for number, (url, label) in enumerate(rows, 1)
    ]


def article(raw):
    section = raw.decode('utf-8').split('<div class="bottom haber-d">', 1)[1].split('</section>', 1)[0]
    stamp = re.search(r'<div class="mt-2 date ml-auto"[^>]+>(\d{2})/(\d{2})/(\d{4})</div>', section)
    day, month, year = map(int, stamp.groups())
    reader = ArticleText()
    reader.feed(section[section.index('<h1>'):])
    reader.close()
    return date(year, month, day).isoformat(), reader.text()


def digest(raw):
    return sha256(raw).hexdigest()
