Staged 146 original, readable and view paths; package 63882f6b0fea1c9b89fc72674d873e1df7b8ed467bd6e13a6ec3e3eab004b2f9; review 17abed313f73cc04b444991a96d0f136d73924382cf920e46f12f3553c44c9aa
Traceback (most recent call last):
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 154, in <module>
    main(Path(arguments[0]).resolve(), Path(arguments[1]).resolve(), *arguments[2:])
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 110, in main
    check(receipt_name, 'input', ['practice-check','--input',str(package_path),'--inventory',str(staged_inventory)],
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 63, in check
    require(code == 0, f'{name}: exit {code}')
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/iklim-validation.py", line 23, in require
    raise RuntimeError(message)
RuntimeError: input: exit 1
