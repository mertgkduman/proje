Staged 160 original, readable and view paths; package ed150ecf6f9fce233a7d280591cc611d94882be83ad40bf1f39ea11f1d1382f2; review 6d8c225a3f93ba23de2aa868cd8eddcc1f82876dcd98b55bbca84dcd003a0e22
Traceback (most recent call last):
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/sikmakas-validation.py", line 160, in <module>
    main(Path(arguments[0]).resolve(), Path(arguments[1]).resolve(), *arguments[2:])
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/sikmakas-validation.py", line 110, in main
    check(receipt_name, 'input', ['practice-check','--input',str(package_path),'--inventory',str(staged_inventory)],
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/sikmakas-validation.py", line 63, in check
    require(code == 0, f'{name}: exit {code}')
  File "/hpc/group/pfisterlab/mg551/storage/proje/.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks/sikmakas-validation.py", line 23, in require
    raise RuntimeError(message)
RuntimeError: input: exit 1
