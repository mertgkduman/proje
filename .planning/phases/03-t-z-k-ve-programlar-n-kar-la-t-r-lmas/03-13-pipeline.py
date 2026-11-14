import datetime
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

part=int(sys.argv[1]); expected=sys.argv[2]
root=Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
checks=root/'03-13-checks'; token=uuid.uuid4().hex; owner=os.getpid(); host=socket.gethostname()
result_path=checks/f'program{part}-pipeline.result.json'
(checks/f'program{part}-pipeline.run.json').write_text(json.dumps(dict(started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=owner,owner_token=token,host=host,expected_base=expected))+'\n')
def run(name,argv,marker=None):
    with (checks/(name+'.log')).open('wb') as log:
        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
        (checks/(name+'.run.json')).write_text(json.dumps(dict(started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=owner,child_pid=child.pid,owner_token=token,host=host,argv=argv))+'\n')
        code=child.wait()
    (checks/(name+'.exit')).write_text(str(code)+'\n')
    out=(checks/(name+'.log')).read_text(errors='replace')
    if code or marker and marker not in out: raise RuntimeError(f'{name}: exit={code}, required={marker}')
    return out.strip()
def hashes():
    subprocess.run(['sha256sum','-c',str(checks/f'program{part}.sha256')],stdin=subprocess.DEVNULL,check=True,stdout=subprocess.DEVNULL)
try:
    check=checks/f'program{part}-check'
    while not check.with_suffix('.exit').exists(): time.sleep(10)
    if check.with_suffix('.exit').read_text().strip()!='0' or 'COMPARISON_INPUT_OK' not in check.with_suffix('.log').read_text(): raise RuntimeError('Frozen official check not passed')
    subprocess.run(['bash','/tmp/gsd-03-root-pin.sh'],stdin=subprocess.DEVNULL,check=True)
    hashes()
    if json.loads(Path('data/current.json').read_text())['release_id']!=expected: raise RuntimeError('Current release changed before workspace')
    workspace=run(f'program{part}-workspace',['python3','src/arsiv.py','workspace','--scratch','/tmp']).splitlines()[-1]
    if not workspace.startswith('/tmp/proje-work-'): raise RuntimeError('Unexpected workspace path: '+workspace)
    hashes()
    run(f'program{part}-load',['python3','src/arsiv.py','comparison-load','--workspace',workspace,'--input',f'data/comparisons/03-demokrat-program-{part}.json'],'COMPARISON_LOAD_OK')
    hashes()
    release=run(f'program{part}-publish',['python3','src/arsiv.py','publish','--workspace',workspace,'--refresh']).splitlines()[-1]
    if len(release)!=32 or any(x not in '0123456789abcdef' for x in release): raise RuntimeError('Unexpected release ID: '+release)
    (checks/f'program{part}-accepted.json').write_text(json.dumps(dict(release=release,workspace=workspace,base=expected,owner_token=token))+'\n')
    if json.loads(Path('data/current.json').read_text())['release_id']!=release: raise RuntimeError('Published release not current')
    hashes()
    run(f'program{part}-audit',['python3','src/arsiv.py','audit','--release',release,'--phase','3','--stage','partial'],'PHASE3_AUDIT_OK')
    run(f'program{part}-report',['python3',str(root/'03-08-checks/report-check.py'),release,f'data/comparisons/03-demokrat-program-{part}.json'],'REPORT_LINK_CHECK_OK')
    if part==2:
        payload=json.loads(Path('data/comparisons/03-demokrat-program-2.json').read_text())
        published=json.loads(Path('data/releases',release,'records.json').read_text())
        present_findings={r['values']['id'] for r in payload['records'] if r['kind']=='finding'}
        extra_findings={r['values']['finding_id'] for r in payload['records'] if r['kind']=='finding_evidence'}-present_findings
        existing_fields={r['values']['id'] for r in payload['records'] if r['kind']=='comparison_field'}
        for field in published['comparison_field']:
            if field['id'] not in existing_fields and extra_findings.intersection((field['summary_finding_id'],field['quote_finding_id'])):
                payload['records'].append(dict(kind='comparison_field',values=field))
                ids={field['summary_finding_id'],field['quote_finding_id']}
                for finding in published['finding']:
                    if finding['id'] in ids and finding['id'] not in present_findings:
                        payload['records'].append(dict(kind='finding',values=finding)); present_findings.add(finding['id'])
                existing_evidence={(r['values']['finding_id'],r['values']['passage_id']) for r in payload['records'] if r['kind']=='finding_evidence'}
                for evidence in published['finding_evidence']:
                    if evidence['finding_id'] in ids and (evidence['finding_id'],evidence['passage_id']) not in existing_evidence:
                        payload['records'].append(dict(kind='finding_evidence',values=evidence))
        known={r['values']['id'] for r in payload['records'] if r['kind']=='comparison_row'}
        needed={r['values']['row_id'] for r in payload['records'] if r['kind']=='comparison_field'}-known
        added=0
        for row in published['comparison_row']:
            if row['id'] in needed: payload['records'].append(dict(kind='comparison_row',values=row)); added+=1
        if added!=len(needed): raise RuntimeError('Supplemental published rows missing')
        supplemental=checks/'program2-report-input.json'
        supplemental.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
        run('program2-report-all-fields',['python3',str(root/'03-08-checks/report-check.py'),release,str(supplemental)],'REPORT_LINK_CHECK_OK')
    hashes()
    result_path.write_text(json.dumps(dict(status='pass',release=release,workspace=workspace,owner_pid=owner,owner_token=token,host=host))+'\n')
except Exception as exc:
    result_path.write_text(json.dumps(dict(status='failed',error=str(exc),owner_pid=owner,owner_token=token,host=host))+'\n')
    raise
