import hashlib,json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks'); inventory=json.loads(Path('data/practices/04-inventory.json').read_text())
for path,digest in [('data/objects/b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e/original.html.bin','b3709f52e07f6d65797d021f571c2b97eca5ac02771a633fe55aafec4130518e'),('data/practices/sources/yeni-parti/objects/ba51c913e2e9057d8c78da61b60e8c78dc9e1724aa059de7a566279c3fa2373b/original.html.bin','ba51c913e2e9057d8c78da61b60e8c78dc9e1724aa059de7a566279c3fa2373b'),('data/practices/sources/yeni-parti/objects/afafe91b796da18984d3bd76a6ffec49b404eafedb8fcde8603b91bee514964b/original.html.bin','afafe91b796da18984d3bd76a6ffec49b404eafedb8fcde8603b91bee514964b')]:assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
cells=[c for c in inventory['cells'] if c['party_id']=='yeni-parti' and c['topic_id']=='tbmm-grup'];assert len(cells)==2
scopes={c['research_kind']:c['cell_id'] for c in cells};now=datetime.now(timezone.utc).isoformat(timespec='seconds');r={k:[] for k in ('practice_scope_v2','practice_attempt_v2','practice_lead','practice_scope_source','practice_candidate')}
for c in cells:r['practice_scope_v2'].append(dict(id=c['cell_id'],party_id=c['party_id'],topic_id=c['topic_id'],taxonomy_version=c['taxonomy_version'],period_start=c['period_start'],cutoff_at=c['cutoff_at'],research_kind=c['research_kind'],boundary_reason='TBMM grubunun tüzük ve kuruluş dönemi seçimleri incelendi; sonraki kararlar ve ilgili kaynaklar araştırılmaya devam ediyor.'))
sources=[('statement','epm-charter-v1','https://yenipartiyiz.biz/parti-tuzugu','TBMM grubu başkanvekilleri ve grup yönetim kurulu hükümleri okundu.',['TBMM grubu organlarının belirlenmesi ve görevleri']),('event','0404-grup-kurulus-dunya-v1','https://www.dunya.com/gundem/yeni-partinin-grup-baskan-vekilleri-pm-ve-ydk-uyeleri-belli-oldu-haberi-833547','24 Temmuz kapalı grup başkanvekili seçimi Dünya haberinden okundu.',['Kapalı grup başkanvekilleri seçimi']),('event','0404-grup-yonetim-ekonomim-v1','https://www.ekonomim.com/gundem/yeni-parti-ilk-kapali-grup-toplantisini-gerceklestirdi-tbmm-grup-yonetimi-belirlendi-haberi-908682','28 Temmuz TBMM grup yönetimi Ekonomim haberinden okundu.',['TBMM toplantısı','Grup yönetim kurulu üyeleri'])]
for kind,version,url,note,sections in sources:
    scope=scopes[kind];ident='0404-grup-inceleme-'+version
    r['practice_attempt_v2'].append(dict(id=ident,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=note,source_version_id=version))
    r['practice_lead'].append(dict(id='lead-'+ident,scope_id=scope,url=url,relevance_reason=note,state='examined',attempt_ids=json.dumps([ident],ensure_ascii=False)))
    r['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now))
for suffix,event,relation,passages in [('0724','0404-tbmm-grup-secim-0724-event','0404-tbmm-grup-secim-0724-iliski-id',['0404-grup-kurulus-dunya-p']),('0728','0404-tbmm-grup-yonetim-0728-event','0404-tbmm-grup-yonetim-0728-iliski-id',['0404-grup-yonetim-ekonomim-context-p','0404-grup-yonetim-ekonomim-p'])]:
    r['practice_candidate'].append(dict(id='0404-grup-'+suffix+'-candidate',scope_id=scopes['event'],event_id=event,relation_id=relation,state='eligible',reason='TBMM grubu organlarının belirlenmesi haber kaynaklı, tarihli ve bu kapsamla ilişkilidir.',passage_ids=json.dumps(passages,ensure_ascii=False)))
(p/'group-coverage-draft.json').write_text(json.dumps(dict(status='open_partial',practice_records=r),ensure_ascii=False,indent=2)+'\n')
print(scopes)
