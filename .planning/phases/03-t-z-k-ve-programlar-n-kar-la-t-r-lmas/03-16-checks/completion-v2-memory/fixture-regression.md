# Real closed-release regression

Command: `PYTHONPATH=src:tests python -m unittest test_audit_memory -v`

The fixture follows seven existing closed releases, invoking the real audit,
source, snapshot, descent, and renderer validators. The profile hook records
whether audit frames hold a snapshot-shaped dictionary at entry to `export_db`;
it neither retains the payloads nor replaces the validators. The initial RED
used the `exported` local name to identify snapshots; the test was subsequently
strengthened to detect the snapshot shape independent of its local name.

Before the fix the retention test failed in 12.592 seconds, reporting:

```text
AssertionError: True is not false : [[False], [False, True],
 [False, True, True], [False, True, True, True],
 [False, True, True, True, True], [False, True, True, True, True, True],
 [False, True, True, True, True, True, True]]
```

Each additional `True` is a previously exported descendant snapshot still
held by an audit frame. After the fix both the retention test and the test
which corrupts an ancestor and creates a cycle in a temporary copy passed:

```text
Ran 2 tests in 16.047s

OK
```

This small regression proves the lifetime mechanism and preservation of the
two failure checks. The separately logged large-candidate audit is required to
show whether the actual failed boundary is resolved under the memory limit.
