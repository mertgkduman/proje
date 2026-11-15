"""Faz 2 CLI tek tam audit'i doğrulayıcıya devreder."""
import contextlib
import io
import sys
import unittest
from unittest.mock import patch

import arsiv
import dosyalar


class PhaseTwoAuditCLI(unittest.TestCase):
    def test_phase_two_delegates_once_and_reports_validated_release(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['arsiv.py', 'audit', '--release', 'current', '--phase', '2']), \
             patch.object(arsiv, 'audit_release', side_effect=AssertionError('mükerrer dış audit')), \
             patch.object(dosyalar, 'validate_phase_two', return_value='abc123') as validate, \
             contextlib.redirect_stdout(output):
            arsiv.main()
        validate.assert_called_once_with('current', None, 'complete')
        self.assertIn('PHASE2_AUDIT_OK abc123', output.getvalue())

    def test_phase_two_does_not_hide_validation_failure(self):
        with patch.object(sys, 'argv', ['arsiv.py', 'audit', '--release', 'current', '--phase', '2']), \
             patch.object(arsiv, 'audit_release', side_effect=AssertionError('mükerrer dış audit')), \
             patch.object(dosyalar, 'validate_phase_two', side_effect=ValueError('kaynak bozuk')):
            with self.assertRaisesRegex(ValueError, 'kaynak bozuk'):
                arsiv.main()
