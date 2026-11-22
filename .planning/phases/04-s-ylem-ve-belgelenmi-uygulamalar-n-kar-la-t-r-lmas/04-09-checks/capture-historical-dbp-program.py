"""Preserve two old DBP site captures with distinct document identities."""

from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/dbp')
now = datetime.now(timezone.utc).isoformat()
paths = set()
entries = []


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)
    paths.add(path)


tuzuk = 'http://www.dbp.org.tr:80/index/partidetay/demokratik-bolgeler-partisi-tuzugu'
assets = (
    (2016,'20161207040346',tuzuk,'2016-tuzuk','DBP tüzüğü, 7 Aralık 2016 arşiv nüshası',
     '2d1afe46faaf2f370951e390d7c48235ab45d63506b28a2b9f4a7fddb6c1f083',[
        ('title','Arşiv sayfasının tüzük başlığı','DEMOKRATİK BÖLGELER PARTİSİ TÜZÜĞÜ'),
        ('article-1','1. madde parti adı','DEMOKRATİK B&Ouml;LGELER PARTİSİ dir.'),
     ]),
    (2019,'20190807211055',tuzuk+'-12476027','2019-program','DBP programı, 7 Ağustos 2019 arşiv nüshası',
     '4bc50fc4fe1ac4b1d260b7f14079e387ed2b3acee70b1ca061ef4324240e1036',[
        ('menu','Eski sitedeki tüzük sayfa başlığı','DEMOKRATİK BÖLGELER PARTİSİ TÜZÜĞÜ'),
        ('title','Sayfanın içindeki program belgesi başlığı','DEMOKRATİK B&Ouml;LGELER PARTİSİ PROGRAMI'),
        ('contents','Programın içindekiler başlığı','İ&Ccedil;İNDEKİLER:'),
        ('end','Spor bölümünde gövdenin son cümlesi','Sporu meta haline getirmekten kurtararak bu alanda sağlanan haksız kazan&ccedil; engellenecektir.'),
     ]),
)
for year,stamp,url,slug,title,expected,passages in assets:
    file=stage/f'dbp-{year}-archived.body'
    raw=file.read_bytes()
    digest=sha256(raw).hexdigest()
    assert digest==expected
    text=html_source_text(raw)
    advertised='https://web.archive.org/web/'+stamp+'id_/'+url
    doc='0409-old-site-'+slug
    version=doc+'-v1'
    original=f'objects/{digest}/original.html.bin'
    readable=f'objects/{digest}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,'html',legacy=False))
    accessed=datetime.fromtimestamp(file.stat().st_mtime,timezone.utc).isoformat()
    add('document',id=doc,party_id='dbp',title=title,source_kind='party')
    add('document_version',id=version,document_id=doc,original_url=url,final_url=advertised,
        document_date=None,date_precision='unknown',date_unknown_reason='Arşiv yakalama günü biliniyor. Metin kabul ve yayım günü ayrı kaynak gerektiriyor.',
        version_label=f'Eski DBP sitesi arşiv yakalaması {stamp}.',accessed_at=accessed,verified_at=now,
        mime='text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=version,publisher='Demokratik Bölgeler Partisi',author=None,kind='party_publication',
        published_at=None,date_precision='unknown',social_handle=None,public_url=advertised,
        basis=f'Eski parti alan adı ve gövde başlığı. {stamp} Wayback yakalamasının zaman damgası.')
    view=build_view(raw,advertised,root,fetch_assets=False)
    view['version_id']=version
    validate_view(root,view)
    add('archive_view',**view)
    manifest=root/view['manifest_path']
    paths.add(manifest)
    paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
    for suffix,section,exact in passages:
        assert exact in text
        add('passage',id=doc+'-'+suffix,version_id=version,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=None,printed_page=None)
    if year == 2019:
        title_start=text.index('<p><strong>'+passages[1][2])
        program_start=21701
        assert title_start<text.index('<p>SPOR</p>',title_start)<program_start
        assert 'GİRİŞ' in text[program_start:program_start+80]
        program_end=text.index('</p>',text.index(passages[-1][2]))+len('</p>')
        paragraphs=[]
        for match in re.finditer(r'<p\b[^>]*>(.*?)</p>',text,re.I|re.S):
            if program_start<=match.start()<program_end:
                normalized=' '.join(unescape(re.sub(r'<[^>]+>','',match[1])).split())
                if normalized:
                    paragraphs.append((match.start(),normalized))
        headings={21701,28556,32807,42198,46527,58003,79661,84739,90726,94189,97229,101989,
                  108431,115731,122473,127084,133707,140794,144773,147721,150950,155666,
                  157750,159908,168229,170034,170775,173952,180300,184056,186054,187266,189883}
        selected=[(position,heading) for position,heading in paragraphs if position in headings]
        assert len(selected)==33
        sections=[]
        for index,(start,heading) in enumerate(selected):
            end=selected[index+1][0] if index+1<len(selected) else program_end
            normalized='\n'.join(p for offset,p in paragraphs if start<=offset<end)
            sections.append(dict(section=heading,source_character_start=start,source_character_end_exclusive=end,
                normalized_sha256=sha256(normalized.encode()).hexdigest(),normalized_words=len(normalized.split()),state='pending'))
        queue=dict(version_id=version,source_sha256=digest,capture_timestamp=stamp,body_start=program_start,body_end=program_end,
            title_source_character_start=title_start,sections=sections,
            boundary='Başlık, içindekiler ve gövdenin sonu kontrol edildi. Bölüm okuması sırada. Kabul, yayımlanma ve güncel yürürlük için ayrı kanıt gerekiyor.')
        with (checks/'historical-dbp-program-reading-queue.json').open('x') as stream:
            stream.write(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')

out=checks/'historical-dbp-program-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id='dbp',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0409-historical-dbp-program-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
