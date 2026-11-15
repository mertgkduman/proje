"""Kısmi denetim, tam snapshot için tam güvenceleri uygulamalıdır."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('phase3_stage_arsiv', os.environ.get('ARSIV_MODULE', str(ROOT / 'src/arsiv.py')))
arsiv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arsiv)


class PhaseThreeStageCompatibility(unittest.TestCase):
    def fixture(self, folder, stage):
        data = {'schema_version': 6, 'comparison_contract': [{'stage': stage, 'taxonomy_version': 4}],
                'comparison_topic': [{'topic_id': 'konu', 'taxonomy_version': 4}], 'comparison_row': []}
        (folder / 'records.json').write_text(json.dumps(data))
        (folder / 'index.html').write_text('')

    def test_partial_request_runs_complete_guards_on_complete_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.fixture(folder, 'complete')
            with patch.object(arsiv, 'validate_comparisons'), patch.object(arsiv, 'validate_changed_topic_reviews'):
                with self.assertRaisesRegex(ValueError, 'dokuz partiyi'):
                    arsiv.validate_phase_three_workspace(folder, 'partial')

    def test_complete_request_rejects_partial_and_tracer_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for stage in ('partial', 'tracer'):
                with self.subTest(stage=stage):
                    self.fixture(folder, stage)
                    with self.assertRaisesRegex(ValueError, 'aşaması uyuşmuyor'):
                        arsiv.validate_phase_three_workspace(folder, 'complete')
