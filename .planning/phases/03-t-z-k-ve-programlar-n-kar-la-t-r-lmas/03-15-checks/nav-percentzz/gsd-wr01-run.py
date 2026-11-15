import datetime, json, os, pathlib, socket, subprocess, sys
root=pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
out=root/'.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-15-checks/nav-percentzz'
label=sys.argv[1];probe=sys.argv[2]
metadata={'pid':os.getpid(),'host':socket.gethostname(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'probe':probe,'modes':['exit','hang']}
(out/('wr01-'+label+'-run.json')).write_text(json.dumps(metadata,indent=2)+'\n')
code=0
with (out/('wr01-'+label+'-run.log')).open('w') as log:
 for mode in metadata['modes']:
  result=subprocess.run([sys.executable,'/tmp/gsd-wr01-driver.py',mode,probe,label],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,timeout=35)
  if result.returncode:code=result.returncode;break
(out/('wr01-'+label+'-run.exit')).write_text(str(code)+'\n')
