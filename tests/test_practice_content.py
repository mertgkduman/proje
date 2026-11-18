"""Regression checks for the open practice timeline."""
import copy
import json
import unittest

import arsiv


class PracticeContent(unittest.TestCase):
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
