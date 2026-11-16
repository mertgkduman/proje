"""Closed archives stay read-only while live workspace readers see commits."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

import arsiv


class ArchiveReadonlyTest(unittest.TestCase):
    def test_real_closed_snapshot_matches_ordinary_readonly_queries(self):
        folder = arsiv.DATA / 'releases/3a3021c8e81749c3834462d1a0d81231'
        path = folder / 'records.sqlite3'
        before = arsiv.sha(path)
        expected = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
        actual = arsiv.connect_readonly(path)
        try:
            for table in ('party', 'document_version', 'passage', 'finding', 'comparison_row', 'comparison_field'):
                query = 'SELECT COUNT(*) FROM ' + table
                self.assertEqual(actual.execute(query).fetchone()[0], expected.execute(query).fetchone()[0])
            self.assertEqual(actual.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        finally:
            actual.close()
            expected.close()
        self.assertEqual(arsiv.sha(path), before)

    def test_workspace_and_unpublished_staging_readers_observe_new_commits(self):
        with tempfile.TemporaryDirectory() as directory:
            old = arsiv.DATA
            arsiv.DATA = Path(directory)
            try:
                for relative in ('work/records.sqlite3', '.staging/' + 'a' * 32 + '/records.sqlite3',
                                 'releases/' + 'b' * 32 + '/records.sqlite3'):
                    with self.subTest(path=relative):
                        path = arsiv.DATA / relative
                        path.parent.mkdir(parents=True)
                        writer = sqlite3.connect(path)
                        writer.execute('CREATE TABLE counter(value INTEGER)')
                        writer.execute('INSERT INTO counter VALUES (1)')
                        writer.commit()
                        reader = arsiv.connect_readonly(path)
                        try:
                            self.assertEqual(reader.execute('SELECT COUNT(*) FROM counter').fetchone()[0], 1)
                            writer.execute('INSERT INTO counter VALUES (2)')
                            writer.commit()
                            self.assertEqual(reader.execute('SELECT COUNT(*) FROM counter').fetchone()[0], 2)
                        finally:
                            reader.close()
                            writer.close()
            finally:
                arsiv.DATA = old

    def test_closed_snapshot_connection_rejects_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            old = arsiv.DATA
            arsiv.DATA = Path(directory)
            try:
                folder = arsiv.DATA / 'releases' / ('c' * 32)
                folder.mkdir(parents=True)
                path = folder / 'records.sqlite3'
                writer = sqlite3.connect(path)
                writer.execute('CREATE TABLE counter(value INTEGER)')
                writer.execute('INSERT INTO counter VALUES (1)')
                writer.commit()
                writer.close()
                (folder / 'manifest.json').write_text(json.dumps({'release_id': folder.name}))
                reader = arsiv.connect_readonly(path)
                try:
                    with self.assertRaisesRegex(sqlite3.OperationalError, 'readonly'):
                        reader.execute('DELETE FROM counter')
                    self.assertEqual(reader.execute('SELECT COUNT(*) FROM counter').fetchone()[0], 1)
                finally:
                    reader.close()
            finally:
                arsiv.DATA = old
