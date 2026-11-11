"""Gerçek parti belgelerinin güvenli ve okunur çevrimdışı türevleri."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

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

