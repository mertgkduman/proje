import unittest
import tempfile
import shutil
import ctypes
import json
import os
from pathlib import Path
import arsiv
from unittest.mock import Mock, patch


class PDFReuseTest(unittest.TestCase):
    pdf = arsiv.ROOT / 'data/objects/b90474ccaee06fd969319cdfccafc645a949f7bf8f2a7020efa1f305969f7cbc/original.pdf'

    def setUp(self):
        self.clear_caches()
        self.addCleanup(self.clear_caches)

    @staticmethod
    def clear_caches():
        for name in ('_load_pdf_libraries', '_pdf_page_text'):
            cached = getattr(arsiv, name, None)
            if cached is not None:
                cached.cache_clear()

    @staticmethod
    def instrumented_load(parsers):
        real_load = ctypes.CDLL

        def load(path):
            library = real_load(path)
            if 'poppler' in path:
                parse = library.poppler_document_new_from_file
                parse.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p]
                parse.restype = ctypes.c_void_p
                library.poppler_document_new_from_file = Mock(wraps=parse)
                parsers.append(library.poppler_document_new_from_file)
            return library
        return load

    def test_same_page_reuses_real_libraries_and_parser(self):
        parsers = []
        with patch('arsiv.ctypes.CDLL', side_effect=self.instrumented_load(parsers)) as loader, \
                patch('arsiv.sha', wraps=arsiv.sha) as digest:
            first = arsiv.pdf_page_text(self.pdf, 0)
            self.assertTrue(first.strip())
            self.assertEqual(arsiv.pdf_page_text(self.pdf, 0), first)
            with self.subTest(work='library'):
                self.assertEqual(loader.call_count, 3)
            with self.subTest(work='parser'):
                self.assertEqual(sum(parse.call_count for parse in parsers), 1)
            with self.subTest(work='current_bytes'):
                self.assertEqual(digest.call_count, 2)
            self.assertTrue(arsiv.pdf_page_exists(self.pdf, 0))
            self.assertFalse(arsiv.pdf_page_exists(self.pdf, 10000))
            self.assertEqual(loader.call_count, 3)
            self.assertEqual(sum(parse.call_count for parse in parsers), 3)

    def test_changed_bytes_with_same_size_and_mtime_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'copy.pdf'
            shutil.copyfile(self.pdf, path)
            first = arsiv.pdf_page_text(path, 0)
            before = path.stat()
            path.write_bytes(b'x' * before.st_size)
            os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertEqual(path.stat().st_size, before.st_size)
            self.assertEqual(path.stat().st_mtime_ns, before.st_mtime_ns)
            with self.assertRaisesRegex(ValueError, 'PDF açılamadı'):
                arsiv.pdf_page_text(path, 0)
            shutil.copyfile(self.pdf, path)
            self.assertEqual(arsiv.pdf_page_text(path, 0), first)

    def test_warm_cache_checks_dependencies_before_path_access(self):
        arsiv.pdf_page_text(self.pdf, 0)
        with patch('arsiv.ctypes.util.find_library', return_value=None), \
                patch.object(Path, 'resolve', side_effect=AssertionError('Dosyaya erişildi')), \
                patch.object(Path, 'read_bytes', side_effect=AssertionError('Dosyaya erişildi')):
            for path in (self.pdf, 'missing.pdf'):
                with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Poppler-glib.*eksik: poppler-glib'):
                    arsiv.pdf_page_text(path, 0)
        self.assertTrue(arsiv.pdf_page_text(self.pdf, 0).strip())

    def test_failed_library_load_is_retried(self):
        resolver = ctypes.util.find_library
        real_load = ctypes.CDLL
        with patch('arsiv.ctypes.util.find_library', wraps=resolver) as find:
            with patch('arsiv.ctypes.CDLL', side_effect=OSError('geçici yükleme hatası')):
                with self.assertRaisesRegex(ValueError, 'Poppler-glib.*eksik: poppler-glib'):
                    arsiv.pdf_page_text(self.pdf, 0)
            with patch('arsiv.ctypes.CDLL', wraps=real_load) as loader:
                self.assertTrue(arsiv.pdf_page_text(self.pdf, 0).strip())
                self.assertEqual(loader.call_count, 3)
            self.assertEqual(find.call_count, 4)

    def test_failed_parse_is_retried_after_file_repair(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'copy.pdf'
            path.write_bytes(b'invalid PDF')
            parsers = []
            with patch('arsiv.ctypes.CDLL', side_effect=self.instrumented_load(parsers)):
                for _ in range(2):
                    with self.assertRaisesRegex(ValueError, 'PDF açılamadı'):
                        arsiv.pdf_page_text(path, 0)
                self.assertEqual(sum(parse.call_count for parse in parsers), 2)
                shutil.copyfile(self.pdf, path)
                self.assertTrue(arsiv.pdf_page_text(path, 0).strip())
                self.assertEqual(sum(parse.call_count for parse in parsers), 3)

    def test_missing_file_keeps_pdf_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'PDF açılamadı'):
                arsiv.pdf_page_text(Path(tmp) / 'missing.pdf', 0)


class WarmAuditTest(unittest.TestCase):
    def test_corruption_after_successful_audit_is_rejected_independently(self):
        release = '26de2a4efc584b5b9f81ea67dcb8d65c'
        source = arsiv.DATA
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / 'data'
            folder = data / 'releases' / release
            shutil.copytree(source / 'releases' / release, folder)
            records = json.loads((folder / 'records.json').read_text())
            for version in records['document_version']:
                for field in ('original_path', 'readable_path'):
                    target = data / version[field]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(source / version[field], target)
            pdf = next(v for v in records['document_version'] if v['original_path'].endswith('.pdf'))
            manifest_path = folder / 'manifest.json'
            manifest = json.loads(manifest_path.read_text())
            manifest['files']['index.html'] = '0' * 64
            corruptions = (
                (data / pdf['original_path'], b'corrupt', 'Arşiv özeti eşleşmiyor'),
                (data / pdf['readable_path'], b'corrupt', 'Okunabilir arşiv özgün belgeden farklı'),
                (folder / 'index.html', b'corrupt', 'Manifest özeti eşleşmiyor'),
                (manifest_path, json.dumps(manifest).encode(), 'Manifest özeti eşleşmiyor'),
            )
            with patch.object(arsiv, 'DATA', data):
                self.assertEqual(arsiv.audit_release(release), release)
                for path, corrupt, error in corruptions:
                    with self.subTest(path=path.relative_to(data)):
                        original = path.read_bytes()
                        try:
                            path.write_bytes(corrupt)
                            with self.assertRaisesRegex(ValueError, error):
                                arsiv.audit_release(release)
                        finally:
                            path.write_bytes(original)
                        self.assertEqual(arsiv.audit_release(release), release)


class DocumentContract(unittest.TestCase):
    def test_missing_pdf_library_has_actionable_error(self):
        with patch('arsiv.ctypes.util.find_library', return_value=None), self.assertRaisesRegex(ValueError, 'Poppler-glib.*gobject|Poppler-glib.*eksik'):
            arsiv.pdf_page_text('missing.pdf', 0)

    def test_identical_bytes_keep_document_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                db = arsiv.connect(work / 'records.sqlite3')
                source = dict(db.execute("SELECT * FROM document_version WHERE id='registry-365-v1'").fetchone())
                previous_count=db.execute('SELECT COUNT(*) FROM document_version WHERE sha256=?',(source['sha256'],)).fetchone()[0]
                db.close()
                arsiv.record(work, 'document', dict(id='shared-tip', party_id='tip', title='Shared', source_kind='official'))
                source.update(id='shared-tip-v1', document_id='shared-tip', original_url='https://example.org/shared', final_url='https://example.org/shared')
                self.assertEqual(arsiv.record(work, 'document_version', source), 'shared-tip-v1')
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute("SELECT d.party_id FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id='shared-tip-v1'").fetchone()[0], 'tip')
                self.assertEqual(db.execute("SELECT COUNT(*) FROM document_version WHERE sha256=?", (source['sha256'],)).fetchone()[0], previous_count+1)
                db.close()
            finally:
                arsiv.DATA = old

    def test_pilot_document_headings_have_attempt_backed_results(self):
        data = arsiv.export_db(arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3', 'test')
        for heading in ('Tüzük', 'Program'):
            relevant = [m for m in data['missing'] if m['party_id'] == 'yeni-parti' and m['heading'] == heading]
            self.assertTrue(relevant)
            self.assertTrue(all(any(a['id'] == m['attempt_id'] for a in data['attempt']) for m in relevant))

    def test_wrong_party_evidence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
                work = arsiv.open_workspace(tmp)
                db = arsiv.connect(work / 'records.sqlite3')
                db.execute("UPDATE finding SET party_id='tip' WHERE id='kurulus-quote'")
                db.commit()
                db.close()
                with self.assertRaises(ValueError):
                    arsiv.export_db(work / 'records.sqlite3', 'test')
            finally:
                arsiv.DATA = old
