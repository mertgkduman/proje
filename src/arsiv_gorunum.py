"""Özgün HTML baytlarından scriptsiz, yerel varlıklı sürümlü belge görünümü."""
import hashlib
import html
import http.client
import ipaddress
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import socket
import ssl
import urllib.parse
import urllib.request

FORMAT_VERSION=1
CSP="default-src 'none'; script-src 'none'; style-src 'self' 'unsafe-inline'; img-src 'self'; font-src 'self'; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
VIEW_TABLES={'archive_view':'version_id TEXT PRIMARY KEY REFERENCES document_version(id), view_id TEXT NOT NULL, format_version INTEGER NOT NULL, source_sha256 TEXT NOT NULL, index_path TEXT NOT NULL, manifest_path TEXT NOT NULL, manifest_sha256 TEXT NOT NULL'}
SAFE_TAGS=set('html head body title header footer main nav aside section article div span p h1 h2 h3 h4 h5 h6 ul ol li dl dt dd a img picture source style link meta br hr b strong i em small sup sub blockquote pre code table thead tbody tfoot tr td th caption colgroup col figure figcaption details summary time noscript'.split())
VOID=set('img source link meta br hr col'.split())
DROP=set('script iframe frame frameset object embed svg math template canvas video audio'.split())
DROP_VOID={'embed','frame'}
ALLOWED_ATTRS=set('id class lang dir title alt width height role aria-label aria-labelledby aria-hidden aria-expanded colspan rowspan scope start value datetime open'.split())
MAX_ASSETS=40
MAX_ASSET=8*1024*1024
MAX_TOTAL=32*1024*1024
STATIC_ASSET_HOSTS={'fonts.googleapis.com','fonts.gstatic.com','cdn.jsdelivr.net','cdnjs.cloudflare.com','unpkg.com'}
MAX_REDIRECTS=5


def digest(value): return hashlib.sha256(value).hexdigest()


def fetch_asset(url, allowed):
    """Validate every hop and connect only to an already validated address."""
    for hop in range(MAX_REDIRECTS+1):
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.hostname not in allowed or parsed.username or parsed.password:
            raise ValueError('Varlık yönlendirmesi kapsam dışında')
        port=parsed.port or (443 if parsed.scheme=='https' else 80)
        addresses=socket.getaddrinfo(parsed.hostname,port,type=socket.SOCK_STREAM)
        def public(address):
            ip=ipaddress.ip_address(address.split('%')[0])
            return ip.is_global and not (ip.is_multicast or ip.is_reserved or ip.is_unspecified)
        if not addresses or any(not public(a[4][0]) for a in addresses):
            raise ValueError('Varlık adresi genel ağda değil')
        address=addresses[0][4][0]
        connection=http.client.HTTPConnection(parsed.hostname,port,timeout=15)
        try:
            sock=socket.create_connection((address,port),timeout=15)
            if parsed.scheme=='https':
                try: sock=ssl.create_default_context().wrap_socket(sock,server_hostname=parsed.hostname)
                except Exception:
                    sock.close()
                    raise
            connection.sock=sock
            target=urllib.parse.urlunsplit(('', '', parsed.path or '/', parsed.query, ''))
            connection.request('GET',target,headers={'User-Agent':'Mozilla/5.0 proje-arastirma/1.0'})
            response=connection.getresponse()
            if response.status in (301,302,303,307,308):
                location=response.getheader('Location')
                if not location or hop==MAX_REDIRECTS: raise ValueError('Varlık yönlendirmesi geçersiz veya sınırı aşıyor')
                url=urllib.parse.urljoin(url,location)
                continue
            if not 200<=response.status<300: raise ValueError('Varlık HTTP hatası: '+str(response.status))
            return response.read(MAX_ASSET+1),response.headers.get_content_type(),url
        finally:
            connection.close()
    raise ValueError('Varlık yönlendirme sınırı')


class Resources:
    def __init__(self, url, enabled):
        self.url=url; self.enabled=enabled; self.assets={}; self.urls={}; self.total=0; self.limitations=[]

    def asset(self, value, base, css=False):
        url=urllib.parse.urljoin(base,value)
        if url in self.urls:return self.urls[url]
        parsed=urllib.parse.urlsplit(url)
        allowed={urllib.parse.urlsplit(self.url).hostname,*STATIC_ASSET_HOSTS}
        if not self.enabled or parsed.scheme not in ('https','http') or not parsed.hostname or parsed.hostname not in allowed or parsed.username or parsed.password:
            self.limitations.append('Yerelleştirilmeyen kaynak: '+url[:250]); return None
        if len(self.assets)>=MAX_ASSETS or self.total>=MAX_TOTAL:
            self.limitations.append('Varlık sayısı/boyut sınırı: '+url[:250]); return None
        self.urls[url]=None
        try:
            value,mime,final=fetch_asset(url,allowed)
            if len(value)>MAX_ASSET or self.total+len(value)>MAX_TOTAL:raise ValueError('Varlık boyutu sınırı')
            if css:
                if mime!='text/css':raise ValueError('CSS türü bekleniyordu')
                value=self.css(value.decode('utf-8',errors='replace'),final,in_asset=True).encode()
                extension='css'
            else:
                types={'image/png':'png','image/jpeg':'jpg','image/gif':'gif','image/webp':'webp','image/x-icon':'ico','font/woff2':'woff2','font/woff':'woff','font/ttf':'ttf','font/otf':'otf','application/font-sfnt':'ttf','application/octet-stream':'woff2'}
                extension=types.get(mime)
                if not extension:raise ValueError('Pasif varlık türü desteklenmiyor: '+mime)
                # SVG and HTML are deliberately never accepted as image/font assets.
                if value.lstrip().startswith((b'<',b'<!')):raise ValueError('Aktif/işaretleme varlığı reddedildi')
            path='assets/'+digest(value)+'.'+extension
            self.assets[path]=value; self.urls[url]=path; self.total+=len(value)
            return path
        except Exception as exc:
            self.limitations.append('Kaynak alınamadı: '+url[:200]+' — '+str(exc)[:160]); return None

    def css(self, text, base, in_asset=False):
        # Strip comments before tokens, escape-based obfuscation and executable legacy CSS.
        text=re.sub(r'/\*.*?\*/','',text,flags=re.S)
        text=re.sub(r'@import\b[^;]*(?:;|$)','',text,flags=re.I)
        text=re.sub(r'[^{};]*(?:expression\s*\(|behavior\s*:|-moz-binding\s*:)[^;}]*;?','',text,flags=re.I)
        if '\\' in text:
            self.limitations.append('CSS kaçış karakteri içeren bildirimler çıkarıldı.')
            # Bildirim çıkarılırken kuralın kapanış parantezi korunmalıdır;
            # aksi halde ikon font CSS'si binlerce iç içe kurala dönüşür.
            text=re.sub(r'[^{};]*\\[^;}]*;?','',text)
        def replace(match):
            raw=next(x for x in match.groups() if x is not None).strip()
            asset=self.asset(raw,base)
            return 'url("'+(asset.removeprefix('assets/') if in_asset else asset)+'")' if asset else 'none'
        return re.sub(r'url\s*\(\s*(?:"([^"]*)"|\x27([^\x27]*)\x27|([^)]*))\s*\)',replace,text,flags=re.I|re.S).replace('</style','')


class PassiveHTML(HTMLParser):
    def __init__(self,resources,local_links):
        super().__init__(convert_charrefs=True)
        self.resources=resources; self.local_links=local_links; self.parts=[]; self.block=[]; self.in_style=False; self.style=[]

    def handle_starttag(self,tag,attrs):
        if self.block:
            if tag in DROP and tag not in DROP_VOID:self.block.append(tag)
            return
        if tag in DROP_VOID:return
        if tag in DROP:self.block.append(tag); return
        if tag not in SAFE_TAGS:return
        values=dict(attrs)
        if tag=='meta':
            if values.get('charset'):self.parts.append('<meta charset="utf-8">')
            elif values.get('name','').lower()=='viewport':self.parts.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
            return
        if tag=='link':
            if values.get('rel','').lower()=='stylesheet':
                asset=self.resources.asset(values.get('href',''),self.resources.url,css=True)
                if asset:self.parts.append('<link rel="stylesheet" href="'+asset+'">')
            return
        if tag=='style':self.in_style=True;self.style=[];return
        output=[]
        for key,value in attrs:
            if value is None:
                if key=='open':output.append('open')
                continue
            if key in ALLOWED_ATTRS:output.append(key+'="'+html.escape(value,quote=True)+'"')
            elif key=='style':output.append('style="'+html.escape(self.resources.css(value,self.resources.url),quote=True)+'"')
            elif key=='href' and tag=='a':
                if value.startswith('#'):target=value
                else:
                    absolute=urllib.parse.urljoin(self.resources.url,value)
                    parsed=urllib.parse.urlsplit(absolute)
                    target=self.local_links.get(absolute,absolute) if parsed.scheme in ('http','https') and parsed.hostname and not parsed.username and not parsed.password else None
                if target:output.append('href="'+html.escape(target,quote=True)+'"')
            elif key=='src' and tag=='img':
                asset=self.resources.asset(value,self.resources.url)
                if asset:output.append('src="'+asset+'"')
        if tag=='source':return # srcset and media cannot introduce remote requests.
        self.parts.append('<'+tag+(' '+' '.join(output) if output else '')+'>')
        if tag=='head':self.parts.append('<meta http-equiv="Content-Security-Policy" content="'+html.escape(CSP,quote=True)+'">')

    def handle_endtag(self,tag):
        if self.block:
            if tag==self.block[-1]:self.block.pop()
            return
        if tag=='style' and self.in_style:
            self.parts.append('<style>'+self.resources.css(''.join(self.style),self.resources.url)+'</style>');self.in_style=False;return
        if tag in SAFE_TAGS and tag not in VOID:self.parts.append('</'+tag+'>')

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_data(self,data):
        if self.block:return
        if self.in_style:self.style.append(data)
        else:self.parts.append(html.escape(data))


def build_view(content,url,data_root,fetch_assets=True,local_links=None):
    from arsiv import safe_url
    safe_url(url)
    resources=Resources(url,fetch_assets)
    # Logos and document images must not lose the shared asset budget to
    # stylesheet font variants before the body is parsed.
    class Images(HTMLParser):
        def handle_starttag(self,tag,attrs):
            if tag=='img' and (src:=dict(attrs).get('src')):
                resources.asset(src,url)
    images=Images();images.feed(content.decode('utf-8',errors='replace'));images.close()
    parser=PassiveHTML(resources,local_links or {})
    parser.feed(content.decode('utf-8',errors='replace'));parser.close()
    output='<!doctype html>'+''.join(parser.parts)
    # The derivative is always UTF-8, including legacy http-equiv sources.
    # Put its encoding before long titles/styles so browser sniffing cannot
    # fall back to a single-byte charset after sanitization removes the source meta.
    output=re.sub(r'<meta charset="[^"]*">','',output)
    if '<head' not in output:
        output='<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="'+html.escape(CSP,quote=True)+'">'+output
    else:
        output=re.sub(r'(<head(?: [^>]*)?>)',r'\1<meta charset="utf-8">',output,count=1)
    # Static layout additions only; source handlers/scripts remain absent.
    output=output.replace('</head>','<style>html{overflow-wrap:anywhere}img{max-width:100%;height:auto}*{animation:none!important;transition:none!important}.reveal{opacity:1!important;transform:none!important}.elementor-tab-content,[role="tabpanel"]{display:block!important;height:auto!important;opacity:1!important;visibility:visible!important}</style></head>')
    files={'index.html':output.encode(),**resources.assets}
    hashes={p:digest(value) for p,value in files.items()}
    source_hash=digest(content)
    view_id=digest(json.dumps({'source':source_hash,'format':FORMAT_VERSION,'files':hashes},sort_keys=True).encode())[:32]
    relative='views/'+view_id
    folder=Path(data_root)/relative
    folder.mkdir(parents=True,exist_ok=True)
    manifest=dict(view_id=view_id,format_version=FORMAT_VERSION,source_sha256=source_hash,source_url=url,files=hashes,asset_sources=resources.urls,limitations=list(dict.fromkeys(resources.limitations)),csp=CSP)
    files['manifest.json']=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    for name,value in files.items():
        target=folder/name;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=value:raise ValueError('Değişmez arşiv görünümü farklı')
        if not target.exists():target.write_bytes(value)
    return dict(view_id=view_id,format_version=FORMAT_VERSION,source_sha256=source_hash,index_path=relative+'/index.html',manifest_path=relative+'/manifest.json',manifest_sha256=digest(files['manifest.json']))


def validate_view(data_root,row):
    from arsiv import safe_path,sha
    if row['format_version']!=FORMAT_VERSION or not re.fullmatch(r'[0-9a-f]{32}',row['view_id']) or row['index_path']!='views/'+row['view_id']+'/index.html' or row['manifest_path']!='views/'+row['view_id']+'/manifest.json':raise ValueError('Geçersiz arşiv görünümü yolu')
    path=safe_path(data_root,row['manifest_path'])
    if sha(path)!=row['manifest_sha256']:raise ValueError('Görünüm manifest özeti eşleşmiyor')
    manifest=json.loads(path.read_text())
    if any(manifest[k]!=row[k] for k in ('view_id','source_sha256','format_version')) or 'index.html' not in manifest['files']:raise ValueError('Görünüm kaynak ilişkisi bozuk')
    for name,value in manifest['files'].items():
        if name!='index.html' and not re.fullmatch(r'assets/[0-9a-f]{64}\.(?:css|png|jpg|gif|webp|ico|woff2|woff|ttf|otf)',name):raise ValueError('Görünüm varlık yolu geçersiz')
        if sha(safe_path(path.parent,name))!=value:raise ValueError('Görünüm/varlık özeti eşleşmiyor')
    if manifest.get('csp')!=CSP:raise ValueError('Pasif görünüm CSP sözleşmesi eksik')
    content=safe_path(path.parent,'index.html').read_text()
    if '<meta http-equiv="Content-Security-Policy" content="'+html.escape(CSP,quote=True)+'">' not in content:raise ValueError('Görünümde pasif CSP eksik')
    class Check(HTMLParser):
        def handle_starttag(self,tag,attrs):
            if tag not in SAFE_TAGS or tag in ('source',):raise ValueError('Görünümde etkin öğe var')
            values=dict(attrs)
            for key,value in attrs:
                if key.startswith('on') or key in ('srcset','srcdoc','action','formaction','ping'):raise ValueError('Görünümde etkin özellik var')
                if (key=='src' or (tag=='link' and key=='href')) and value not in manifest['files']:raise ValueError('Görünüm yerel varlık dışına erişiyor')
                if key=='href' and tag=='a' and not (value.startswith('#') or re.fullmatch(r'../../objects/[0-9a-f]{64}/original\.pdf',value)):
                    from arsiv import safe_url
                    safe_url(value)
            if tag=='meta' and values.get('http-equiv') and values['http-equiv']!='Content-Security-Policy':raise ValueError('Görünüm yönlendirme metası içeriyor')
    checker=Check();checker.feed(content)
    return True
