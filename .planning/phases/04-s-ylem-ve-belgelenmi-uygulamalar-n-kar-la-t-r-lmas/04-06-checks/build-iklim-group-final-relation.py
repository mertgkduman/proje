"""Aynı teklif hakkında önceki grup çağrısı ve sonraki kişisel oyu sınırlarıyla bağla."""
import datetime,hashlib,json
from pathlib import Path
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-iklim-group-final-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='6e98b8a1a312c439b9076602c704cf5b1661080fc98e3a76ff938981645d2c81' and sha(rp)=='a8556fd440f59412b678e32b0864ba65eff66b96d50cfaefb61e672c2e4d6486'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();entries=[]
records={k:[] for k in ('practice_statement','practice_relation','practice_candidate_revision')}
def add(category,**v):entries.append(dict(kind=category,values=v))
def finding(ident,text,refs,provenance='summary',pair=None):
 add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=pair or ident,text=text,provenance=provenance,epistemic_type='claim')
 for pid in refs:add('finding_evidence',finding_id=ident,passage_id=pid,role='support');add('verification',finding_id=ident,passage_id=pid,checked_at=when,result='confirmed',reason='Ayrı tarihlerdeki grup konuşması ve kesin kişisel oy kaynakları okundu.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Çağrı ile kişisel oy arasındaki benzerlik ve işlem farkı ayrı gösterildi.')
quote=q('quote');target='0406-iklim-73-group-akin-finding';sp='0406-iklim-73-group-akin-call'
finding(quote,'biz bu yasanın çekilmesini istiyoruz; gerçek anlamda iklim kanununun çıkarılması için çalışma yapılmasını istiyoruz.',[sp],'quote',target)
records['practice_statement'].append(dict(id=q('statement'),party_id='dem',topic_id='doga-ekoloji',taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2025-04-08',date_precision='day',version_id='0406-iklim-73-floor-v1',period_basis='8 Nisan 2025 73. birleşimde İbrahim Akın’a DEM Grubu adına verilen söz.',uncertainty_reason=None,comparison_row_id='04-03-v3-0305-dem-program-doga-row'))
explanation=q('explanation'); result=None
finding(explanation,'İbrahim Akın, 8 Nisan 2025’te DEM Grubu adına 2/2927 teklifinin geri çekilmesini istedi; 2 Temmuz kesin açık oy cetvelinde aynı teklifin tümüne kişisel ret oyu kaydedildi. Her ikisi de aynı teklife karşı tutumu gösterir; geri çekme çağrısı ile kişisel ret oyu farklı işlemlerdir. Bu karşılaştırma grup oyunu, çağrının yerine getirildiğini veya kanunun çevresel sonucunu göstermez.',['0406-iklim-73-group-akin-role',sp,'0406-iklim-final-law-number','0406-iklim-final-akin-vote','0406-iklim-final-akin-online'])
scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09';candidate=next(x for x in pkg['practice_records']['practice_candidate'] if x['id']=='0406-iklim-final-candidate')
reason='8 Nisan grup konuşmasındaki geri çekilme çağrısı ve 2 Temmuz kişisel ret oyu aynı 2/2927 teklifine karşı tutumlardır; işlem türleri farklıdır.'
records['practice_relation'].append(dict(id=q('relation'),statement_id=q('statement'),event_id='0406-iklim-final-event',party_id='dem',topic_id='doga-ekoloji',scope_id=scope,comparability_reason=reason,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='8 Nisan 2025 DEM grubu adına konuşma; 2 Temmuz 2025 kesin açık oy cetveli.',authority_context='Akın ilk işlemde grup adına konuştu; ikinci işlemde kayıtlı oyu kendi kişisel oyudur.',uncertainty_reason='Geri çekme ile ret farklı işlemlerdir; grup oyu, geri çekilme gerçekleşmesi ve çevresel sonuç çıkarılamaz.'))
records['practice_candidate_revision'].append(dict(id=q('eligible'),candidate_id=candidate['id'],recorded_at=when,event_id=candidate['event_id'],relation_id=q('relation'),state='eligible',reason=reason,passage_ids=candidate['passage_ids']))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-iklim-73-group-62581767/releases/8e0384c214bd4efe8c2975c3b89d8a72/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('IKLIM_GROUP_FINAL_RELATION_SEMANTIC_PASS',flush=True)
targets=practice_review_package_targets(data,records,[],'dem');passages={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({passages[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({passages[x]['section'] for x in refs})),supported_claim='8 Nisan grup konuşması ve 2 Temmuz kişisel oy karşılaştırması: '+kind+' / '+ident,limitations='Çağrı ve kişisel oy farklı işlemlerdir; grup oyu ve çevresel sonuç gösterilmez.',result='reviewed',reason='Özgün grup sıfatı, çağrı ve kesin oy cetveli ayrı okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('iklim-group-final-relation-dem-draft.json',pkg),('iklim-group-final-relation-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
