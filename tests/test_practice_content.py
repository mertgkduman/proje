"""Regression checks for the open practice timeline."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from test_practice_tracer import tracer_input
from uygulamalar import _load_practice_copy

import arsiv


class PracticeContent(unittest.TestCase):
    def test_unmatched_statement_search_survives_load_export_and_views(self):
        base = '9003e475ee5d49b29a1310c0bfe2007d'
        package = tracer_input(base)
        records = package['practice_records']
        records['practice_variant_contract'] = [dict(version=1)]
        records['practice_scope'] = [dict(id='speech-scope', party_id='yeni-parti', topic_id='organ-secim-yontemi', taxonomy_version=4, period_start='2026-07-24', cutoff_at='2026-11-10T14:38:46.154751+00:00', research_kind='statement', state='not_researched', boundary_reason='Bu kapsam henüz taranmadı.')]
        records['practice_attempt'] = []
        records['practice_unmatched'] = [dict(id='unmatched-1', event_id='tracer-cesme', party_id='yeni-parti', topic_id='organ-secim-yontemi', statement_scope_id='speech-scope', statement_search_state='not_researched', reason='Söylem taranmadı.')]
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            shutil.copyfile(arsiv.DATA / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
            try:
                _load_practice_copy(work, package, base)
            except (ValueError, arsiv.sqlite3.Error) as exc:
                self.fail('Versioned unmatched records must load through the real adapter: ' + str(exc))
            exported = arsiv.export_db(work / 'records.sqlite3', 'fixture')
            self.assertEqual(exported['practice_unmatched'], records['practice_unmatched'])
            html = arsiv.render_comparison_snapshot(exported, arsiv.render_report)
            for prefix in ('party', 'comparison'):
                self.assertIn('id="' + prefix + '-unmatched-unmatched-1"', html)
            self.assertIn('Henüz incelenmedi', html)

    def test_renderer_26_reproduces_current_archive(self):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(arsiv.render_comparison_snapshot(data, arsiv.render_v26_report).encode('utf-8'),
                         (folder / 'index.html').read_bytes())

    def test_statement_once_and_events_in_date_order_in_both_views(self):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        event = data['practice_event'][0]
        relation = data['practice_relation'][0]
        evidence = data['practice_event_evidence'][0]
        for suffix, date in [('later', '2026-10-01'), ('earlier', '2026-09-01')]:
            data['practice_event'].append(dict(event, id=suffix, title='Olay ' + suffix, event_at=date))
            data['practice_relation'].append(dict(relation, id=suffix, event_id=suffix))
            data['practice_event_evidence'].append(dict(evidence, event_id=suffix))
        html = arsiv.render_comparison_snapshot(data, arsiv.render_report)
        for prefix in ('party', 'comparison'):
            self.assertLess(html.index('id="' + prefix + '-practice-earlier"'),
                            html.index('id="' + prefix + '-practice-later"'))
        self.assertEqual(html.count('data-finding-id="tracer-speech-quote"'), 2)


if __name__ == '__main__':
    unittest.main()
