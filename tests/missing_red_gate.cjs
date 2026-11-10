const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
test('access failure requires identified source', () => {
  const run = spawnSync('python3', ['tests/run.py', '--pattern', 'test_missing.py'], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stdout + run.stderr);
});
