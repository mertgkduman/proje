---
schema_version: 1
open_count: 0
waived_count: 0
fixed_count: 7
total_count: 7
last_updated: 2026-11-18T07:45:55.945Z
---

# Broken Windows Ledger

> Cross-phase defect register. With `workflow.windows_enforce` enabled, `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 01 | deviation | src/arsiv.py |  | YSK 2023 faaliyet raporu okundu; PDF henüz arşiv ve pasaj kaydına bağlanmadı. | fixed |  | 2026-11-10T14:57:24.597Z | 2026-11-10T15:11:30.167Z |
| 2 | 02 | deviation | tests/test_dates.py |  | Faz 1 testleri yalıtılmış eski release tabanına sabitlendi. | fixed |  | 2026-11-11T15:13:33.375Z | 2026-11-11T15:13:49.470Z |
| 3 | 02 | deviation | src/dosyalar.py |  | Kısmi kuruluş araştırmasının makbuz etiketi ve Türkçe alan adları düzeltildi. | fixed |  | 2026-11-11T15:13:56.526Z | 2026-11-11T15:13:57.110Z |
| 4 | 02 | deviation | src/dosyalar.py |  | Resmî site ve sicil alanlarında kaynak sahipliği denetimi eklendi. | fixed |  | 2026-11-11T15:13:57.756Z | 2026-11-11T15:13:58.362Z |
| 5 | 03 | deviation | data/comparisons/03-taxonomy.json |  | Türkçe casefold ofsetiyle hatalı seçilen konu pasajları gerçek kaynak başlıklarına düzeltildi; başarısız yayın adayı kullanılmadı. | fixed |  | 2026-11-13T08:32:04.272Z | 2026-11-13T08:32:08.994Z |
| 6 | 04 | deviation | src/arsiv.py |  | Versioned evidence export and audit required changes to the shared archive adapter. | fixed |  | 2026-11-18T07:45:25.475Z | 2026-11-18T07:45:55.444Z |
| 7 | 04 | deviation | tests/test_comparisons.py |  | Updated the active stylesheet expectation while retaining frozen-asset checks. | fixed |  | 2026-11-18T07:45:25.940Z | 2026-11-18T07:45:55.945Z |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "01",
    "file": "src/arsiv.py",
    "line": null,
    "description": "YSK 2023 faaliyet raporu okundu; PDF henüz arşiv ve pasaj kaydına bağlanmadı.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-10T14:57:24.597Z",
    "resolved_at": "2026-11-10T15:11:30.167Z",
    "milestone": "v1.0"
  },
  {
    "id": 2,
    "kind": "deviation",
    "phase": "02",
    "file": "tests/test_dates.py",
    "line": null,
    "description": "Faz 1 testleri yalıtılmış eski release tabanına sabitlendi.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-11T15:13:33.375Z",
    "resolved_at": "2026-11-11T15:13:49.470Z",
    "milestone": "v1.0"
  },
  {
    "id": 3,
    "kind": "deviation",
    "phase": "02",
    "file": "src/dosyalar.py",
    "line": null,
    "description": "Kısmi kuruluş araştırmasının makbuz etiketi ve Türkçe alan adları düzeltildi.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-11T15:13:56.526Z",
    "resolved_at": "2026-11-11T15:13:57.110Z",
    "milestone": "v1.0"
  },
  {
    "id": 4,
    "kind": "deviation",
    "phase": "02",
    "file": "src/dosyalar.py",
    "line": null,
    "description": "Resmî site ve sicil alanlarında kaynak sahipliği denetimi eklendi.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-11T15:13:57.756Z",
    "resolved_at": "2026-11-11T15:13:58.362Z",
    "milestone": "v1.0"
  },
  {
    "id": 5,
    "kind": "deviation",
    "phase": "03",
    "file": "data/comparisons/03-taxonomy.json",
    "line": null,
    "description": "Türkçe casefold ofsetiyle hatalı seçilen konu pasajları gerçek kaynak başlıklarına düzeltildi; başarısız yayın adayı kullanılmadı.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-13T08:32:04.272Z",
    "resolved_at": "2026-11-13T08:32:08.994Z",
    "milestone": "v1.0"
  },
  {
    "id": 6,
    "kind": "deviation",
    "phase": "04",
    "file": "src/arsiv.py",
    "line": null,
    "description": "Versioned evidence export and audit required changes to the shared archive adapter.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-18T07:45:25.475Z",
    "resolved_at": "2026-11-18T07:45:55.444Z",
    "milestone": "v1.0"
  },
  {
    "id": 7,
    "kind": "deviation",
    "phase": "04",
    "file": "tests/test_comparisons.py",
    "line": null,
    "description": "Updated the active stylesheet expectation while retaining frozen-asset checks.",
    "status": "fixed",
    "reason": "",
    "recorded_at": "2026-11-18T07:45:25.940Z",
    "resolved_at": "2026-11-18T07:45:55.945Z",
    "milestone": "v1.0"
  }
]
````
