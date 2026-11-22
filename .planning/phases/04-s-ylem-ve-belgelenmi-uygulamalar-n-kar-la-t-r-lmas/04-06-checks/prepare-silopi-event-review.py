"""Silopi adayının gerçek pasaj ve alternatiflerine dayalı kaynak incelemesi."""
import datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from uygulamalar import practice_review_targets,validate_practice_source_review
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks'); d=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text()); f=json.loads((p/'silopi-event-fragment-draft.json').read_text())
for x in f['entries']:
 if x['kind'] in ('document','document_version','passage','finding','finding_evidence'):d.setdefault(x['kind'],[]).append(x['values'])
for kind,rows in f['practice_records'].items():d.setdefault(kind,[]).extend(rows)
targets=practice_review_targets(d,f['practice_records']);passages={x['id']:x for x in d['passage']};now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
for (kind,identity),(refs,parties) in targets.items():
 ps=sorted(refs); sections=[passages[q]['section'] for q in ps]; versions=list(dict.fromkeys(passages[q]['version_id'] for q in ps))
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(versions,ensure_ascii=False),passage_ids=json.dumps(ps,ensure_ascii=False),inspected_sections=json.dumps(sections,ensure_ascii=False),supported_claim='Sevk ve parti ihraç duyurusu ile iki tüzük alternatifine ilişkin '+kind+' / '+identity+' kaydı, ilgili kaynak ve tarihlerle sınırlıdır.',limitations='Parti duyurusunu yineleyen DHA haberi bağımsız karar kanıtı değildir; özgün kurul kararı, savunma ve tüzük yürürlük sırası bilinmiyor. Ormanlı’nın 3 Temmuz sözü karar öncesidir.',result='reviewed',reason='Tüzükteki yaptırım, tarihli haberler ve parti bildirimi ayrı aşamalarda okundu: '+identity))
validate_practice_source_review(d,reviews,selection=f['practice_records'],party_id='dem')
(p/'silopi-event-review-draft.json').write_text(json.dumps(dict(practice_source_review=reviews,source_review_refs=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in reviews]),ensure_ascii=False,indent=2)+'\n');print('SILOPI_SOURCE_REVIEW_IN_MEMORY_OK',len(reviews))
