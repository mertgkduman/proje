from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
from uygulamalar import validate_practices,practice_review_targets,validate_practice_source_review

folder=Path(sys.argv[1])
def read(path):
    return json.loads(path.read_text())
def encode(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
template=json.loads(subprocess.check_output(['git','show','1b0c653:data/practices/04-tip.json']))
latest=read(Path('data/practices/04-inventory.json'))
base_release=latest['base_release']
base=read(Path('data/releases')/base_release/'records.json')
records={k:[] for k in template['practice_records']}
for k in ('practice_variant_contract','practice_coverage_contract','practice_evidence_contract'):
    records[k]=template['practice_records'][k]
records['practice_contract']=base['practice_contract']
inherited_events={e['id'] for e in base['practice_event']}
records['practice_evidence_assessment']=[e for e in template['practice_records']['practice_evidence_assessment']
    if e['event_id'] in inherited_events]
entries=read(folder/'chair-rotation-source-records.json')['entries']
stamp=datetime.now(timezone.utc).isoformat()
party='yeni-yol'
topic='merkez-kurul-olusumu'
stem='0408-chair-rotation'
event=stem+'-event'
statement=stem+'-statement'
relation=stem+'-relation'
dispute=stem+'-dispute'
passage={r['id']:r for r in base['passage']}
passage.update((e['values']['id'],e['values']) for e in entries if e['kind']=='passage')
versions={r['id']:r for r in base['document_version']}
versions.update((e['values']['id'],e['values']) for e in entries if e['kind']=='document_version')
quote_p=stem+'-babacan-rotation'
plan_p=stem+'-anka-plan'
reported_date_p=stem+'-urfadasin-date'
outcome_p=stem+'-urfagazetesi-outcome'
registry_p='0206-yeni-yol-chair'
summary=stem+'-statement-summary'
quote=stem+'-statement-quote'
result=stem+'-result'
explanation=stem+'-explanation'
dispute_id=stem+'-dispute-summary'
reason='İlk dönem başkanlık ve görev devri zinciri. Tüzüğün tam metni, karar aslı ve diğer organlar araştırılıyor.'
for lane, refs in [('statement',[quote_p]),('event',[plan_p,reported_date_p,outcome_p,registry_p])]:
    cell=next(c for c in latest['cells'] if (c['party_id'],c['topic_id'],c['research_kind'])==(party,topic,lane))
    scope=cell['cell_id']
    records['practice_scope_v2'].append(dict(id=scope,**{k:cell[k] for k in
        ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},boundary_reason=reason))
    if lane=='event':
        event_scope=scope
    for pid in refs:
        p=passage[pid]; version=versions[p['version_id']]; url=version['final_url']
        attempt=stem+'-read-'+pid
        records['practice_scope_source'].append(dict(scope_id=scope,version_id=version['id'],
            inspected_sections=encode([p['section'] or 'Sicil sayfasında Genel Başkanı alanı']),inspected_at=stamp))
        records['practice_attempt_v2'].append(dict(id=attempt,scope_id=scope,attempted_at=stamp,query=url,url=url,result='examined',
            reason=f'{pid} kaynağında görev, yayın günü veya belgenin kapsadığı işlem incelendi.',source_version_id=version['id']))
        records['practice_lead'].append(dict(id='lead-'+attempt,scope_id=scope,url=url,
            relevance_reason='Genel başkanlık düzeni ve bildirilen devre ilişkin kaynak.',state='examined',attempt_ids=encode([attempt])))
def add(table,**row):
    entries.append(dict(kind=table,values=row))
def finding(identity,text,refs,description,provenance='summary',pair=None):
    add('finding',id=identity,party_id=party,heading='Belgelenmiş uygulamalar',pair_id=pair or identity,
        text=text,provenance=provenance,epistemic_type='claim')
    for pid in refs:
        add('finding_evidence',finding_id=identity,passage_id=pid,role='support')
        add('verification',finding_id=identity,passage_id=pid,checked_at=stamp,result='confirmed',reason=description)
    add('review',id='review-'+identity,kind='finding',subject_id=identity,reviewer_kind='agent',
        reviewed_at=stamp,result='reviewed',reason=description)
finding(summary,'DEVA Genel Başkanı Ali Babacan, Yeni Yol’un yönetim görevlerinin birer yıl süreyle bileşenler arasında dönüşümlü yürütülmesini öngördüklerini açıkladı.',
        [quote_p],'14 Ocak 2025 VOA görüşmesinde konuşmacı ve yönetim görevi kapsamı kontrol edildi.')
finding(quote,passage[quote_p]['exact'],[quote_p],'Babacan’a atfedilen kısa doğrudan ifade özgün HTML metniyle aynı.',
        provenance='quote',pair=summary)
finding(result,'Şanlıurfa Gazetesi, Celal Mümtaz Akıncı’nın ardından İzzettin Küçük’ün Yeni Yol genel başkanlığına getirildiğini bildirdi. Erişilen Yargıtay bilgi sayfasında da Küçük genel başkan olarak kayıtlı.',
        [outcome_p,registry_p],'Yerel haberin sonucu ile sicilin başkan alanı ayrı okundu. Sicil devir tarihini vermiyor.')
finding(explanation,'Bir yıl önce bileşen genel başkanının tarif ettiği dönüşüm, Akıncı’nın ardından Gelecek Partisi’nden Küçük’ün genel başkanlığa geçtiği yönündeki kaynaklarla karşılaştırılabilir. Tam mutabakat metni ve yetkili kurulun karar aslı açık.',
        [quote_p,reported_date_p,outcome_p],'Aynı tüzel parti görevi karşılaştırıldı. Grup başkanlığı ayrı görev.')
finding(dispute_id,'Küçük, devri Yönetim Kurulu kararına bağladı ve başlangıcı 13 Ocak olarak açıkladı. ANKA’nın 14 Ocak haberinde Kurucular Kurulu eliyle seçim bekleniyordu. Karar aslı ve iki kurulun süreçteki rolleri araştırılıyor.',
        [plan_p,reported_date_p],'Sonraki kişinin beyanı ve önceki ileriye dönük haber birbirinin kesin reddi olarak okunmadı.')
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=summary,quote_finding_id=quote,statement_at='2025-01-14',date_precision='day',
    version_id=passage[quote_p]['version_id'],period_basis='VOA Türkçe’nin yayın günü. Açıklamayı DEVA Genel Başkanı bileşen sıfatıyla yaptı.',
    uncertainty_reason='Dönüşümlü görev düzeninin yazılı dayanağı ve yürürlük kapsamı açık.',
    comparison_row_id='04-03-v3-0307-yeni-yol-merkez-kurul-olusumu-charter'))
records['practice_event'].append(dict(id=event,common_event_key='yeni-yol-tuzel-genel-baskanlik-devri-2026-01-13',
    event_at='2026-01-13',date_precision='day',date_unknown_reason=None,title='Yeni Yol genel başkanlık devri',
    scope_context='13 Ocak, Küçük’ün daha sonra bildirdiği görevi devralma günü. Karar ve haber tarihleri ayrı.',
    occurrence_basis='Tarihli yerel haberler görev devrini aktarıyor. Genel başkanı ayrıca sicil kaydı gösteriyor.'))
for pid,stage,point,basis,limit in [
    (outcome_p,'action','Yerel haber Akıncı’dan Küçük’e genel başkanlık devrini bildirdi.','17 Ocak tarihli haberde önceki ve sonraki başkan açıkça adlandırılıyor.','Haber seçim veya karar tutanağını yayımlamıyor.'),
    (reported_date_p,'result','Küçük, 13 Ocak itibarıyla genel başkanlığı devraldığını açıkladı.','16 Ocak tarihli haberde kişinin kendi sözleri aktarılıyor.','13 Ocak yürürlük günü alıntıya dayanıyor. Başka belgeyle tutulmuş kurul günü açık.'),
    (registry_p,'result','Erişilen Yargıtay bilgi sayfası İzzettin Küçük’ü genel başkan gösteriyor.','Sicilin Genel Başkanı alanı okundu.','Sicil tarihsel göreve başlama günü veya seçim usulü vermez.')]:
    records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,stage=stage,
        supported_point=point,concrete_basis=basis,limitation=limit,epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,
        basis_kind='document' if pid==registry_p else 'independent_report'))
records['practice_relation'].append(dict(id=relation,statement_id=statement,event_id=event,party_id=party,topic_id=topic,
    scope_id=event_scope,target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,
    comparability_reason='Her iki kayıt Yeni Yol tüzel kişiliğinin genel başkanlık görevinde bileşenler arası dönüşümle ilgili.',
    temporal_context='14 Ocak 2025 açıklaması ile bildirilen 13 Ocak 2026 görev başlangıcı ayrı.',
    authority_context='Babacan DEVA Genel Başkanı. Küçük devri Yeni Yol Yönetim Kurulu kararına atfediyor. TBMM grup başkanlığı ayrı.',
    uncertainty_reason='Tam tüzük ve karar aslı görülmedi. İki haberin atıf yaptığı kurul rolleri açık.'))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=event_scope,event_id=event,
    relation_id=relation,state='eligible',reason='Genel başkanlık devri ve önceki yönetim açıklaması kaynakla bağlı.',
    passage_ids=encode([outcome_p,reported_date_p])))
records['practice_dispute'].append(dict(id=dispute,event_id=event,summary_finding_id=dispute_id,
    supported_points='Küçük genel başkan olarak bildirildi ve sicilde yer alıyor.',
    disputed_points='ANKA kurul seçimini beklenen işlem olarak, Küçük ise Yönetim Kurulu kararını gerçekleşmiş dayanak olarak aktardı.',
    unresolved_points='Kararın aslı ve kurulların gerçek işlem sırası görülmedi.'))
for pid,role,point,position in [
    (reported_date_p,'support','Küçük, görevi hangi kurul kararına bağladığını ve bildirdiği günü söylüyor.','Görevi devraldığını açıklayan kişi.'),
    (plan_p,'conflict','Önceki haber Kurucular Kurulu tarafından seçim yapacağını öngörüyor.','ANKA’nın 14 Ocak itibarıyla bildirdiği beklenti.')]:
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,role=role,
        point=point,source_position=position))
snapshot=base
for entry in entries:
    snapshot.setdefault(entry['kind'],[]).append(entry['values'])
for table,rows in records.items():
    target=snapshot.setdefault(table,[])
    target.extend(r for r in rows if r not in target)
validate_practices(snapshot)
messages={
 'practice_event':'Tarihli yerel haber, yeni genel başkanı adlandırıyor. 13 Ocak devri Küçük’ün kendi açıklaması.',
 'practice_statement':'14 Ocak 2025 tarihinde Babacan, Yeni Yol yönetimi için yıllık dönüşümü tarif etti.',
 'practice_statement.summary_finding_id':'Söz, DEVA Genel Başkanı’na atfedildi ve yönetim görevlerinin dönüşümüne sınırlandı.',
 'practice_statement.quote_finding_id':'Dönüşümün süresi ve yöntemiyle ilgili kısa alıntı özgün metinle aynı.',
 'practice_relation':'Dönüşüm beyanı ve bir yıl sonraki bildirilen görev değişimi aynı Yeni Yol parti görevinde.',
 'practice_relation.target_finding_id':'Beyan, parti yönetim görevlerinin yıllık ve bileşenler arası dönüşümünü öngörüyor.',
 'practice_relation.result_finding_id':'Yerel haber ve sicil Küçük’ü genel başkan olarak gösteriyor. Sicil başlangıç tarihi vermiyor.',
 'practice_relation.explanation_finding_id':'Genel başkanlık ve TBMM grup başkanlığı ayrı yetki ve işlem. İlişki birinci göreve ait.',
 'practice_dispute':'Kurucular Kurulu beklentisi ile Küçük’ün Yönetim Kurulu açıklaması usulün açık kaldığını gösteriyor.',
 'practice_dispute.summary_finding_id':'Kurul adları, iki ayrı gün ve iki ayrı bilgi konumuyla yazıldı.',
}
reviews=[]
for (kind,identity),(pids,parties) in sorted(practice_review_targets(snapshot,records).items()):
    if party not in parties:
        continue
    inspected=[passage[pid] for pid in sorted(pids)]
    if kind=='practice_event_evidence':
        claim=next(e['supported_point'] for e in records['practice_event_evidence']
            if '|'.join((e['event_id'],e['passage_id'],e['stage']))==identity)
    elif kind=='practice_dispute_evidence':
        claim=next(e['point'] for e in records[kind]
            if '|'.join((e['dispute_id'],e['passage_id'],e['point'],e['role']))==identity)
    else:
        claim=messages[kind]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=stamp,
        source_version_ids=encode(sorted({p['version_id'] for p in inspected})),passage_ids=encode(sorted(pids)),
        inspected_sections=encode(sorted({p['section'] or 'Yargıtay Genel Başkanı alanı' for p in inspected})),
        supported_claim=claim,limitations=reason,result='reviewed',
        reason=f'{kind} hedefinde metin, aktör, gün ve dayanak kapsamı okundu. {claim}'))
validate_practice_source_review(snapshot,reviews,require_coverage=False,party_id=party)
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
payload=dict(contract_version=1,base_release=base_release,party_id=party,taxonomy_version=4,stage='tracer',
    entries=entries,practice_records=records,scope_inventory=template['scope_inventory'],tranches=[],source_review_refs=refs)
for name,value in [('institution-rotation-draft.json',payload),('institution-rotation-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    file=folder/name
    with file.open('x') as out: out.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(file.read_bytes()).hexdigest())
print('review',len(reviews))
