"""Gerçek parti belgelerinin güvenli ve okunur çevrimdışı türevleri."""
import hashlib
import importlib.util
import json
import socket
from pathlib import Path
import tempfile
import unittest
import io
from email.message import Message
from unittest.mock import patch

import arsiv

CHARTER='b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e'
PROGRAM='58fa220ab814bd82a4c8d0d233bf55ab268eb9f856750cd88abc544e17ceba1b'


class ArchiveViews(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('arsiv_gorunum'), 'HTML kodu yerine pasif belge görünümü gerekli')
        import arsiv_gorunum
        return arsiv_gorunum

    def test_passive_document_retains_layout_and_removes_active_requests(self):
        m=self.module()
        source='''<!doctype html><html><head><title>Belge</title><style>h1{color:red} @import "https://evil.invalid/x";p{background:url(https://evil.invalid/y)}</style><meta http-equiv="refresh" content="0;url=https://evil.invalid"></head><body onload="alert(1)"><h1>Parti Tüzüğü</h1><script>window.BAD=true</script><iframe src="https://evil.invalid"></iframe><form action="https://evil.invalid"><input name="secret"><p>Okunur metin</p></form><a href="javascript:alert(1)">Tıkla</a><img src="file:///etc/passwd"><svg onload="alert(1)"></svg></body></html>'''
        with tempfile.TemporaryDirectory() as tmp:
            row=m.build_view(source.encode(), 'https://example.org/tuzuk', Path(tmp), fetch_assets=False)
            text=(Path(tmp)/row['index_path']).read_text()
            self.assertIn('<h1>Parti Tüzüğü</h1>',text)
            self.assertIn('h1{color:red}',text)
            self.assertIn('Okunur metin',text)
            for bad in ('<script','onload=', '<form','<iframe','<input','<svg','javascript:','file:///','@import','https://evil.invalid'):
                self.assertNotIn(bad,text)
            self.assertIn('Content-Security-Policy',text)
            self.assertTrue(m.validate_view(Path(tmp),row))
            (Path(tmp)/row['index_path']).write_text(text+'tampered')
            with self.assertRaises(ValueError):m.validate_view(Path(tmp),row)

    def test_utf8_is_declared_early_for_legacy_meta_and_headless_fragments(self):
        m=self.module()
        body='İstanbul, özgürlük ve eşitlik; BARIŞ VE DEMOKRASİ PARTİSİ PROGRAMI'
        sources=[('<html><head><title>'+('Uzun başlık '*200)+'</title>'
                  '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
                  '</head><body>'+body+'</body></html>'),'<p>'+body+'</p>']
        for source in sources:
            with self.subTest(head='<head>' in source), tempfile.TemporaryDirectory() as tmp:
                raw=source.encode('utf-8')
                row=m.build_view(raw,'https://example.org/program',Path(tmp),fetch_assets=False)
                rendered=(Path(tmp)/row['index_path']).read_bytes()
                self.assertIn(b'<meta charset="utf-8">',rendered[:1024])
                self.assertIn(body,rendered.decode('utf-8'))
                self.assertEqual(row['source_sha256'],hashlib.sha256(raw).hexdigest())
                self.assertTrue(m.validate_view(Path(tmp),row))

    def test_known_static_css_cdn_is_localized_while_script_mime_is_rejected(self):
        m=self.module()
        def response(request,timeout):
            value=io.BytesIO(b'h1{color:red}')
            value.headers=Message()
            value.headers['Content-Type']='application/javascript' if request.full_url.endswith('.js') else 'text/css'
            value.geturl=lambda:request.full_url
            return value
        resources=m.Resources('https://tip.org.tr/tuzuk/',True)
        def fetch(url,allowed):
            value=response(__import__('urllib.request').request.Request(url),15)
            return value.read(),value.headers.get_content_type(),url
        with patch('arsiv_gorunum.fetch_asset',side_effect=fetch):
            local=resources.asset('https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',resources.url,css=True)
            self.assertTrue(local.endswith('.css'))
            self.assertEqual(resources.assets[local],b'h1{color:red}')
            self.assertIsNone(resources.asset('https://cdn.jsdelivr.net/bad.js',resources.url,css=True))
            self.assertIsNone(resources.asset('https://evil.invalid/style.css',resources.url,css=True))
        cleaned=resources.css(r'.fa-a:before{content:"\f001"}.fa-b:before{content:"\f002"}.safe{color:red}','https://tip.org.tr/')
        self.assertEqual(cleaned.count('{'),cleaned.count('}'))
        self.assertIn('.safe{color:red}',cleaned)
        self.assertNotIn('\\',cleaned)

    def test_static_panels_stay_readable_and_images_precede_font_budget(self):
        m=self.module()
        source=b'<html><head><link rel="stylesheet" href="/style.css"></head><body><img src="/logo.png"><div class="elementor-tab-content" style="display:none">Program bolumu</div></body></html>'
        requested=[]
        def response(request,timeout):
            url=request.full_url;requested.append(url)
            content=(''.join('.f'+str(i)+'{src:url(/font'+str(i)+'.woff)}' for i in range(45))).encode() if url.endswith('.css') else b'local-static-asset'
            value=io.BytesIO(content);value.headers=Message();value.headers['Content-Type']='text/css' if url.endswith('.css') else 'image/png' if url.endswith('.png') else 'font/woff';value.geturl=lambda:url
            return value
        def fetch(url,allowed):
            value=response(__import__('urllib.request').request.Request(url),15)
            return value.read(),value.headers.get_content_type(),url
        with tempfile.TemporaryDirectory() as tmp, patch('arsiv_gorunum.fetch_asset',side_effect=fetch):
            row=m.build_view(source,'https://example.org/program',Path(tmp))
            text=(Path(tmp)/row['index_path']).read_text()
            self.assertEqual(requested[0],'https://example.org/logo.png')
            self.assertRegex(text,r'elementor-tab-content[^}]*display:block!important')
            self.assertIn('.png"',text)
            self.assertTrue(m.validate_view(Path(tmp),row))

    def test_asset_redirect_rejects_private_target_before_connection(self):
        m=self.module()
        class Response:
            status=302
            def getheader(self,name): return 'http://127.0.0.1/private'
        class Connection:
            def __init__(self,*args,**kwargs): self.sock=None
            def request(self,*args,**kwargs): pass
            def getresponse(self): return Response()
            def close(self): pass
        dns=lambda host,port,**kwargs: [(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',port))]
        with patch.object(m.socket,'getaddrinfo',side_effect=dns), patch.object(m.socket,'create_connection') as connect, patch.object(m.http.client,'HTTPConnection',Connection):
            with self.assertRaises(ValueError):m.fetch_asset('http://example.org/image',{'example.org'})
            connect.assert_called_once_with(('93.184.216.34',80),timeout=15)

    def test_asset_dns_private_and_mixed_answers_are_rejected(self):
        m=self.module()
        for addresses in [('127.0.0.1',),('93.184.216.34','10.1.2.3')]:
            answers=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,80)) for ip in addresses]
            with self.subTest(addresses=addresses), patch.object(m.socket,'getaddrinfo',return_value=answers), patch.object(m.socket,'create_connection') as connect:
                with self.assertRaises(ValueError):m.fetch_asset('http://example.org/image',{'example.org'})
                connect.assert_not_called()

    def test_allowed_redirect_host_re_resolves_and_rejects_private_ip(self):
        m=self.module()
        class Response:
            status=302
            def getheader(self,name): return '/private'
        class Connection:
            def __init__(self,*args,**kwargs): self.sock=None
            def request(self,*args,**kwargs): pass
            def getresponse(self): return Response()
            def close(self): pass
        answers=lambda ip:[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,80))]
        with patch.object(m.socket,'getaddrinfo',side_effect=[answers('93.184.216.34'),answers('127.0.0.1')]), patch.object(m.socket,'create_connection') as connect, patch.object(m.http.client,'HTTPConnection',Connection):
            with self.assertRaises(ValueError):m.fetch_asset('http://example.org/image',{'example.org'})
            connect.assert_called_once_with(('93.184.216.34',80),timeout=15)

    def test_void_embed_does_not_hide_following_content(self):
        m=self.module()
        raw=b'<html><body><p>before</p><embed src="x"><p>after</p></body></html>'
        with tempfile.TemporaryDirectory() as tmp:
            row=m.build_view(raw,'https://example.org/',Path(tmp),fetch_assets=False)
            text=(Path(tmp)/row['index_path']).read_text()
            self.assertIn('<p>after</p></body></html>',text)
            self.assertNotIn('<embed',text)
            self.assertTrue(m.validate_view(Path(tmp),row))

    def test_correct_canonical_charter_and_program_render_as_separate_documents(self):
        m=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            paths=[]
            for digest,canonical,title,body in ((CHARTER,'parti-tuzugu','Parti Tüzüğü','Madde 54'),(PROGRAM,'parti-programi','Parti Programı','DEĞİŞİM ÇAĞRISI')):
                original=arsiv.DATA/'objects'/digest/'original.html.bin'
                before=original.read_bytes()
                self.assertIn(('https://yenipartiyiz.biz/'+canonical).encode(),before)
                row=m.build_view(before,'https://yenipartiyiz.biz/'+canonical,Path(tmp),fetch_assets=False)
                text=(Path(tmp)/row['index_path']).read_text()
                self.assertIn('<title>'+title+' — Yeni Parti</title>',text)
                self.assertIn(body,text)
                self.assertNotIn('&lt;!DOCTYPE',text)
                self.assertNotIn('<pre>',text)
                self.assertEqual(original.read_bytes(),before)
                self.assertEqual(row['source_sha256'],digest)
                paths.append(row['index_path'])
            self.assertNotEqual(*paths)

    def test_real_input_links_original_hashes_and_valid_local_assets(self):
        m=self.module()
        payload=json.loads((arsiv.DATA/'dossiers/261111-epm-yeni-parti.json').read_text())
        views=[r['values'] for r in payload['records'] if r['kind']=='archive_view']
        self.assertEqual({r['source_sha256'] for r in views},{CHARTER,PROGRAM})
        for row in views:
            self.assertTrue(m.validate_view(arsiv.DATA,row))
            manifest=json.loads((arsiv.DATA/row['manifest_path']).read_text())
            self.assertTrue(any(p.endswith('.png') for p in manifest['files']))
            self.assertTrue(any(p.endswith('.ttf') for p in manifest['files']))
            text=(arsiv.DATA/row['index_path']).read_text()
            self.assertIn('../../objects/',text)
            self.assertIn('/original.pdf',text)

