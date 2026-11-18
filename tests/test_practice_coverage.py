"""Coverage must be derived from the selected archive, not a package claim."""
import copy
import json
import unittest

import arsiv
import uygulamalar


class PracticeCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release = arsiv.current()
        cls.data = json.loads((arsiv.DATA / 'releases' / cls.release / 'records.json').read_text())

    def test_inventory_is_the_selected_universe(self):
        self.assertTrue(hasattr(uygulamalar, 'build_practice_inventory'), 'canonical inventory builder is required')
        self.assertTrue(hasattr(uygulamalar, 'validate_practice_coverage'), 'canonical coverage validator is required')
        from uygulamalar import build_practice_inventory, validate_practice_coverage
        inventory = build_practice_inventory(self.data)
        selection = json.loads(max(self.data['comparison_completion_revision'], key=lambda x: x['epoch'])['selection'])
        topics = {x['topic_id'] for x in selection['topics']}
        parties = {x['party_id'] for x in self.data['scope_party']}
        expected = {(p, t, k) for p in parties for t in topics for k in ('statement', 'event')}
        actual = {(x['party_id'], x['topic_id'], x['research_kind']) for x in inventory['cells']}
        self.assertEqual(actual, expected)
        self.assertEqual(len(inventory['cells']), len(expected))
        self.assertTrue(all(x['state'] == 'not_researched' for x in inventory['cells']))
        self.assertTrue(validate_practice_coverage(self.data, inventory))
        narrowed = copy.deepcopy(inventory)
        narrowed['cells'].pop()
        with self.assertRaises(ValueError):
            validate_practice_coverage(self.data, narrowed)

    def test_real_archived_chain_is_bounded(self):
        closure = next(x for x in self.data['closure'] if x['id'] == '0105-organ-closure')
        attempt = next(x for x in self.data['attempt'] if x['id'] == '0105-cesme-access')
        self.assertEqual(attempt['source_version_id'], '0105-cesme-v1')
        self.assertIn('doğrulanamadı', closure['residual_leads'])
        self.assertTrue(any(x['closure_id'] == closure['id'] for x in self.data['reopen']))


if __name__ == '__main__':
    unittest.main()
