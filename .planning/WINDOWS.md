---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-11-10T14:57:24.597Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | deviation | src/arsiv.py |  | YSK 2023 faaliyet raporu okundu; PDF henüz arşiv ve pasaj kaydına bağlanmadı. | open |  | 2026-11-10T14:57:24.597Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "01",
    "file": "src/arsiv.py",
    "line": null,
    "description": "YSK 2023 faaliyet raporu okundu; PDF henüz arşiv ve pasaj kaydına bağlanmadı.",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-11-10T14:57:24.597Z",
    "resolved_at": null,
    "milestone": "v1.0"
  }
]
````
