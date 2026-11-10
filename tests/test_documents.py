import unittest
import tempfile
import shutil
from pathlib import Path
import arsiv
from unittest.mock import patch


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
                db.close()
                arsiv.record(work, 'document', dict(id='shared-tip', party_id='tip', title='Shared', source_kind='official'))
                source.update(id='shared-tip-v1', document_id='shared-tip', original_url='https://example.org/shared', final_url='https://example.org/shared')
                self.assertEqual(arsiv.record(work, 'document_version', source), 'shared-tip-v1')
                db = arsiv.connect(work / 'records.sqlite3')
                self.assertEqual(db.execute("SELECT d.party_id FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id='shared-tip-v1'").fetchone()[0], 'tip')
                self.assertEqual(db.execute("SELECT COUNT(*) FROM document_version WHERE sha256=?", (source['sha256'],)).fetchone()[0], 2)
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
