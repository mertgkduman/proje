"""Keep each dispute visible through its existing relation explanation."""
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
for src, dest, pairs in [
    ('package-kayseri-draft-v2.json', 'package-kayseri-draft-v3.json', [('0404-kayseri-relationship','0404-kayseri-dispute-summary')]),
    ('package-gaziantep-draft.json', 'package-gaziantep-draft-v2.json', [('0404-kayseri-relationship','0404-kayseri-dispute-summary'), ('0404-gaziantep-relation','0404-gaziantep-dispute')]),
    ('package-mugla-draft.json', 'package-mugla-draft-v2.json', [('0404-kayseri-relationship','0404-kayseri-dispute-summary'), ('0404-gaziantep-relation','0404-gaziantep-dispute'), ('0404-mugla-relation','0404-mugla-dispute')]),
]:
    pkg = json.loads((p/src).read_text())
    entries = pkg['entries']
    if src.startswith('package-mugla'):
        latest = json.loads((p/'source-records-draft-v8.json').read_text())['entries']
        replacement = next(e for e in latest if e['kind']=='passage' and e['values']['id']=='0404-mugla-itiraz-p')
        entries[:] = [replacement if e['kind']=='passage' and e['values']['id']=='0404-mugla-itiraz-p' else e for e in entries]
        # The explanation must cite the statement as well as the event.
        for kind, values in [
            ('finding_evidence',dict(finding_id='0404-mugla-relation',passage_id='0105-speech-p',role='support')),
            ('verification',dict(finding_id='0404-mugla-relation',passage_id='0105-speech-p',checked_at='2026-11-21T19:10:05+00:00',result='confirmed',reason='Örgüt başkanlarının doğrudan seçimi hakkındaki 4 Ağustos beyanı okundu.'))
        ]: entries.append(dict(kind=kind, values=values))
    for relation_id, dispute_id in pairs:
        primary = next(e['values'] for e in entries if e['kind']=='finding' and e['values']['id']==relation_id)
        secondary = next(e['values'] for e in entries if e['kind']=='finding' and e['values']['id']==dispute_id)
        primary['text'] += ' ' + secondary['text']
        for e in list(entries):
            v = e['values']
            if e['kind'] in ('finding_evidence','verification') and v.get('finding_id')==dispute_id:
                new = dict(v, finding_id=relation_id)
                if not any(x['kind']==e['kind'] and x['values'].get('finding_id')==relation_id and x['values'].get('passage_id')==new['passage_id'] for x in entries):
                    entries.append(dict(kind=e['kind'], values=new))
        for d in pkg['practice_records']['practice_dispute']:
            if d['summary_finding_id']==dispute_id: d['summary_finding_id']=relation_id
        entries[:] = [e for e in entries if not (e['kind']=='finding' and e['values'].get('id')==dispute_id or e['kind'] in ('finding_evidence','verification') and e['values'].get('finding_id')==dispute_id or e['kind']=='review' and e['values'].get('subject_id')==dispute_id)]
    (p/dest).write_text(json.dumps(pkg, ensure_ascii=False, indent=2)+'\n')
    print('COMBINED', dest)
