Staged 146 original, readable and view paths; package 9cfdd9044d899557c83584f0df1146d0fc6a666b52a09265b09bbb446aa48f39; review 27ec38bb5b01d6b0f544820c3edc416105c398ebe67b30beea2e9206eeee49d5
Traceback (most recent call last):
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 154, in <module>
    main(Path(arguments[0]).resolve(), Path(arguments[1]).resolve(), *arguments[2:])
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 112, in main
    check(receipt_name, 'source', ['practice-source-check','--input',str(package_path),'--review',str(review_path)],
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 63, in check
    require(code == 0, f'{name}: exit {code}')
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 23, in require
    raise RuntimeError(message)
RuntimeError: source: exit 1
