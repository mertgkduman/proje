"""Extract a dated TİP catalog tranche with byte and coverage receipts."""

from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import sys


class PostContent(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.found = False
        self.parts = []
        self.media = []
        self.publication_time = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("property") == "article:published_time":
            self.publication_time = attrs["content"]
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif attrs.get("id") == "postContent":
                assert not self.found
                self.depth = 1
                self.found = True
        if not self.depth:
            return
        if tag == "br":
            self.parts.append("\n")
        if tag in ("img", "iframe", "object"):
            self.media.append({key: attrs[key] for key in ("src", "alt", "data") if key in attrs})

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == "div":
            self.depth -= 1
        if tag in {"p", "li", "h1", "h2", "h3", "h4", "h5", "blockquote", "div"}:
            self.parts.append("\n")

    def handle_data(self, text):
        if self.depth:
            self.parts.append(text)

    def body(self):
        assert self.found and self.depth == 0
        blocks = "".join(self.parts).splitlines()
        return "\n".join(" ".join(block.split()) for block in blocks if block.strip())


def main(tranche, output):
    output.mkdir(exist_ok=True)
    capture = json.loads((tranche / "capture.json").read_bytes())
    items = capture["items"] if isinstance(capture, dict) else capture
    rows = []
    for item in items:
        raw = (tranche / item["path"]).read_bytes()
        assert sha256(raw).hexdigest() == item["sha256"], item["path"]
        parser = PostContent()
        parser.feed(raw.decode("utf-8"))
        assert parser.publication_time.startswith(item["displayed_date"]), item["path"]
        body = parser.body()
        name = f"{item['i']:03d}.txt"
        (output / name).write_text(body)
        rows.append(dict(i=item["i"], publication_time=parser.publication_time,
                         body_characters=len(body), body_sha256=sha256(body.encode()).hexdigest(),
                         text_path=name, original_sha256=item["sha256"], embedded_media=parser.media))
    result = dict(body_characters=sum(row["body_characters"] for row in rows), records=rows)
    (output / "body-digests.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(result["body_characters"], [(r["i"], r["body_characters"], len(r["embedded_media"])) for r in rows])


if __name__ == "__main__":
    main(*(Path(value) for value in sys.argv[1:]))
