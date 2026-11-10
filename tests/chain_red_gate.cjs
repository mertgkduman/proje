const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
test('pending lead blocks closure', () => {
  const run = spawnSync('python3', ['tests/run.py', '--pattern', 'test_chain.py'], { encoding: 'utf8' });
  assert.equal(run.status, 0, run.stdout + run.stderr);
});
