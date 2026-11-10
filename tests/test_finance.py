import json
import shutil
import tempfile
import unittest
from pathlib import Path

import arsiv
from rapor import render_report


class FinanceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
        self.work = arsiv.open_workspace(self.tmp.name)
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        self.db.execute("INSERT INTO document VALUES ('finance-fixture','yeni-parti','Test raporu','news')")
        self.db.execute("INSERT INTO document_version (id,document_id,original_url,final_url,document_date,accessed_at,verified_at,mime,sha256,original_path,readable_path,date_precision) SELECT 'finance-fixture','finance-fixture',original_url,final_url,'2026-10-24',accessed_at,verified_at,mime,sha256,original_path,readable_path,'day' FROM document_version LIMIT 1")
        self.db.execute("INSERT INTO passage (id,version_id,exact) VALUES ('finance-fixture','finance-fixture','Test döneminde 0 TL')")
        self.db.commit()
        self.row = dict(id='f1',party_id='yeni-parti',version_id='finance-fixture',category='gelir',amount='0',currency='TRY',period_start='2026-08-01',period_end='2026-10-23',organization_scope='Kocaeli il örgütü',published_at='2026-10-24',passage_id='finance-fixture',missing_id=None)

    def tearDown(self):
        self.db.close()
        arsiv.DATA = self.old
        self.tmp.cleanup()

    def test_identity_period_and_required_metadata(self):
        arsiv.check_financial(self.db, self.row)
        for changes in ({'party_id':'tip'}, {'period_start':'2009-01-01'}, {'period_end':'2026-11-11'}, {'currency':''}, {'organization_scope':''}, {'amount':0.0}, {'version_id':'missing'}, {'passage_id':'missing'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                arsiv.check_financial(self.db, dict(self.row, **changes))

    def test_null_and_documented_zero_are_distinct(self):
        self.db.close()
        arsiv.record_financial(self.work, self.row)
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        payload = arsiv.export_db(self.work / 'records.sqlite3', 'fixture')
        self.assertEqual(next(r['amount'] for r in json.loads(json.dumps(payload))['financial'] if r['id']=='f1'), '0')
        self.assertIn('0 TRY', render_report(payload))
        with self.assertRaises(ValueError): arsiv.check_financial(self.db, dict(self.row, id='f2', amount=None))

    def test_current_pilot_has_researched_finance(self):
        release = arsiv.current()
        arsiv.audit_finance(arsiv.DATA / 'releases' / release / 'records.sqlite3')

