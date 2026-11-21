# İstanbul geniş taslağı staging paket kontrolü

İzole `/tmp/gsd-0404-program-staging` tabanında `stage-istanbul.py` ile 202 kaynak yolu kontrol edildi: 190 mevcut dosya eşit bayt, 12 yeni dosya; çakışmada yalnız eşit bayt kabul edildi. Repo ve staging kod ve envanter kimliği Aydın staging kontrolündeki aynı kopyadır. Paket SHA256 `b73aee55eaf58551bb79221ae5adda8f5cc07c35976f43601f1cd7e210ea3172`, review SHA256 `e2481b9c9c856f416d3c1e5d1421a1787bfcd67d37cae829fc06fd8233b516cc`.

`python3 src/arsiv.py practice-check --input data/practices/package-istanbul-draft.json --inventory data/practices/04-inventory.json` session 1568 gerçek çıkış 0 `PRACTICE_INPUT_OK`. Aynı paket ve review ile source-check session 53702 çalışıyor, preview henüz başlamadı. Bu yalnız paket kontrolüdür; kanonik yayın ve kapsam kapanışı değildir.
