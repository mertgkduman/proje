"""Canlı DEM çiftinden ayrı ve doğrulama bekleyen 10/3465 adayı üretir."""
import datetime
import hashlib
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
data = Path('data/practices')
base = (data/'04-dem.json').read_bytes()
review_data = (data/'04-dem-review.json').read_bytes()
assert hashlib.sha256(base).hexdigest() == '0f6dfd2a4fe726f54f122b5fee49836ec4bfd4c7062c35d254ceb93368ee25b3'
assert hashlib.sha256(review_data).hexdigest() == '49e49e8846a358907aee694f1a8a8dc7042b743cf179a7449a0e7d979b39af24'
package, review = json.loads(base), json.loads(review_data)
entries = json.loads((p/'tbmm-2025-24-extended-source-slices-draft.json').read_text())['entries']
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
speaker, support, speech, outcome = ['0406-tbmm-2025-24-'+x+'-p' for x in ('speaker','support','media-speech','declined')]
target, context = '0305-dem-program-basin-yerel-passage', '0305-dem-program-basin-yerel-context-passage'
summary, quote = '0305-dem-program-basin-yerel-summary', '0305-dem-program-basin-yerel-quote'
event, statement, relation, contribution = '0406-2025-103465-gundem', '0406-dem-basin-yerel-statement', '0406-2025-103465-relation', '0406-2025-103465-contribution'
scope = 'practice-33fce432b340885da50a844c295fd2cb8aef5ce118cd8573d928f7e3588cc0de'
def add(entry_kind, **values): entries.append({'kind':entry_kind, 'values':values})
def finding(ident, text, passages):
    add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=ident,text=text,provenance='summary',epistemic_type='claim')
    for x in passages:
        add('finding_evidence',finding_id=ident,passage_id=x,role='support')
        add('verification',finding_id=ident,passage_id=x,checked_at=now,result='confirmed',reason='Özgün tutanak ve tarihli bağlam okundu.')
    add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Grup beyanı, takvim sonucu ve araştırma önergesi ayrıldı.')
finding('0406-103465-contribution-f','Ceylan Akça Cupolo, DEM grubu adına Yeni Yol takvim önerisine evet diyeceklerini belirtti ve medya alanında öneriler sundu.',[speaker,support,speech])
finding('0406-103465-result-f','Başkan, Yeni Yol’un araştırma önergesini o gün ön görüşme takvimine alma önerisinin kabul edilmediğini duyurdu.',[outcome])
finding('0406-103465-link-f','Yerel basını güçlendirme söylemi ile kamu ilanları ve medya ortamına ilişkin grup görüşü aynı genel alandadır; destek beyanı bireysel oy veya gerçekleşmiş harcama değildir.',[target,context,speaker,support,speech,outcome])
for fid, q in [(summary,target),(summary,context),(quote,target)]:
    add('verification',finding_id=fid,passage_id=q,checked_at=now,result='confirmed',reason='Parti ekinde yerel basın hedefi ve bağlam okundu; tarih ve toplantı kökeni kesin değil.')
points = [(speaker,'initiative','DEM grubu konuşmacısı','Tutanak grup adına Cupolo’yu gösterir.'),(support,'initiative','Grup adına destek niyeti','Konuşmacı önergeye evet diyeceklerini söyler.'),(speech,'initiative','Medya ortamına ilişkin grup görüşü','Konuşmacı medya kurumlarına ilişkin öneriler sunar.'),(outcome,'result','Ön görüşme takvimi sonucu','Başkan önergenin kabul edilmediğini bildirir.')]
records = {
 'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='ifade-basin-ozgurlugu',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 3 Aralık 2025 grup görüşü ve ön görüşme takvimi; konu araştırması sürüyor.')],
 'practice_event':[dict(id=event,common_event_key='tbmm-28-4-24-10-3465-gundem',event_at='2025-12-03',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 4. yasama yılı 24. birleşim; Yeni Yol 10/3465 araştırma önergesinin ön görüşme takvimi',title='Kamu ilanları araştırmasının ön görüşme takvimi',occurrence_basis='TBMM Genel Kurulu birleşim tutanağı.')],
 'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Sözlü grup beyanı isimli oy değildir; takvim sonucu asıl araştırma önergesinin sonucu değildir.',epistemic_type='claim') for q,stage,point,basis in points],
 'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,point,basis in points],
 'practice_contribution':[dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='support',finding_id='0406-103465-contribution-f',authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına sözlü destek niyeti; bireysel oy ve fiilî harcama ayrı.')],
 'practice_statement':[dict(id=statement,party_id='dem',topic_id='ifade-basin-ozgurlugu',taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id='0204-dem-policies-v1',period_basis='Parti sitesinde yayımlanan programatik ek; bağımsız tam program değildir.',uncertainty_reason='Ek belgenin kesin tarihi ve toplantı kökeni bilinmiyor.',comparison_row_id='04-03-v3-0305-dem-program-basin-row')],
 'practice_relation':[dict(id=relation,statement_id=statement,event_id=event,party_id='dem',topic_id='ifade-basin-ozgurlugu',scope_id=scope,comparability_reason='Yerel basını güçlendirme hedefi ile medya ve kamu ilanları üzerine grup görüşü aynı genel alandadır.',target_finding_id=summary,result_finding_id='0406-103465-result-f',explanation_finding_id='0406-103465-link-f',temporal_context='TBMM görüşmesi 3 Aralık 2025; parti ekinin kesin tarihi bilinmiyor.',authority_context='DEM adına grup konuşması ile başkanın Genel Kurul takvim sonucu açıklaması ayrıdır.',uncertainty_reason='Destek beyanı bireysel oy, takvim sonucu araştırmanın kendisinin sonucu ya da fiilî harcama değildir.')]
}
package['entries'] += entries
for kind, rows in records.items(): package['practice_records'].setdefault(kind, []).extend(rows)
versions = {target:'0204-dem-policies-v1',context:'0204-dem-policies-v1',**{q:'0406-tbmm-2025-24-v1' for q,_,_,_ in points}}
sections = {target:'Parti ekinde yerel basın hedefi',context:'Parti ekinde yerel basın bağlamı',**{q:point for q,_,point,_ in points}}
items = [('practice_event_evidence',event+'|'+q+'|'+stage,[q],point) for q,stage,point,_ in points]
items += [('practice_event',event,[speaker,support,speech,outcome],'Grup konuşması ile takvim sonucunu ayırır.'),('practice_statement',statement,[target,context],'Parti eki yerel basını güçlendirme hedefi içerir.'),('practice_statement.summary_finding_id',statement,[target,context],'Özet yerel basın hedefini korur.'),('practice_statement.quote_finding_id',statement,[target],'Alıntı ek belgeden seçilmiştir.'),('practice_relation',relation,[target,context,speaker,support,speech,outcome],'Hedef ve medya görüşü aynı genel alanda; sonuçları farklıdır.'),('practice_relation.target_finding_id',relation,[target,context],'Hedef yerel basını güçlendirme söylemidir.'),('practice_relation.result_finding_id',relation,[outcome],'Sonuç ön görüşme takviminin reddidir.'),('practice_relation.explanation_finding_id',relation,[target,context,speaker,support,speech,outcome],'Beyan ile bireysel oy ve fiilî harcama ayrıdır.'),('practice_contribution',contribution,[speaker,support,speech],'Cupolo DEM grubu adına destek niyeti açıkladı.'),('practice_contribution.finding_id',contribution,[speaker,support,speech],'Katkı bulgusu grup konuşmasıyla sınırlıdır.')]
for kind, ident, passages, claim in items:
    review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(versions[x] for x in passages)),ensure_ascii=False),passage_ids=json.dumps(passages,ensure_ascii=False),inspected_sections=json.dumps([sections[x] for x in passages],ensure_ascii=False),supported_claim=claim,limitations='Parti ekinin tarihi ve toplantı kökeni bilinmiyor; bireysel oy veya harcama sonucu kanıtlanmıyor.',result='reviewed',reason='İlgili kaynak ve sınırları okundu: '+claim))
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']]
assert len(keys)==len(set(keys))
(p/'103465-combined-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
(p/'103465-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('103465_COMBINED_DRAFT',len(entries),len(keys))
