import argparse
from pathlib import Path
import sys
import unittest

root = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(root / 'src'), str(root / 'tests')]
p = argparse.ArgumentParser()
p.add_argument('--pattern', default='test_*.py')
args = p.parse_args()
suite = unittest.defaultTestLoader.discover(str(root / 'tests'), pattern=args.pattern)
count = suite.countTestCases()
if not count:
    print('Test bulunamadı', file=sys.stderr)
    raise SystemExit(2)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): raise SystemExit(1)
print(f'TESTS_OK count={count}')
