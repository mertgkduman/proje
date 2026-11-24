from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'divan-atalay-source-records.json')
party=aux['party_id']
package=read(here/'olive-oil-draft.json')
review=read(here/'olive-oil-review-draft.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
records=package['practice_records']
when=datetime.now(timezone.utc).isoformat()
passages={r['id']:r for r in snapshot['passage']}
passages.update({e['values']['id']:e['values'] for e in entries if e['kind']=='passage'})
versions={r['id']:r for r in snapshot['document_version']}
versions.update({e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'})
tasks={}
def new(table,**row):
    entries.append(dict(kind=table,values=row))
def finding(id,body,refs,reason,pair=None):
    new('finding',id=id,party_id=party,heading='Belgelenmiş uygulamalar',text=body,pair_id=pair or id,
        provenance='quote' if pair else 'summary',epistemic_type='claim')
    for pid in refs:
        new('finding_evidence',finding_id=id,passage_id=pid,role='support')
        new('verification',finding_id=id,passage_id=pid,checked_at=when,result='confirmed',reason=reason)
    new('review',id='review-'+id,kind='finding',subject_id=id,reviewer_kind='agent',
        reviewed_at=when,result='reviewed',reason=reason)
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Parti duyurusu, arşivli tüzük ve yargı ile Meclis kaynakları okundu.'))
    return sid
def readings(topic,lane,refs):
    sid=scope_for(topic,lane)
    grouped={}
    for pid in refs:
        p=passages[pid]
        grouped.setdefault(p['version_id'],set()).add(p['section'])
    for vid,sections in grouped.items():
        existing=[r for r in records['practice_scope_source'] if (r['scope_id'],r['version_id'])==(sid,vid)]
        if existing and set(json.loads(existing[-1]['inspected_sections']))>=sections:
            continue
        if existing:
            sections.update(json.loads(existing[-1]['inspected_sections']))
            if existing[-1]['inspected_at']==when:
                existing[-1]['inspected_sections']=encoded(sorted(sections))
                continue
        url=versions[vid]['final_url']
        aid=f'divan-atalay-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Görev dağılımı veya Can Atalay dosyasının tarihli kaynağı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Tarihli özgün kurum veya parti kaydı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((here / 'olive-oil-draft.json').read_bytes()).hexdigest() == '607a85fdcfecbf97bdeb5556facf9a5bc3fba5cc0ee4ed8d0f83fdca4d58a351'
assert sha256((here / 'olive-oil-review-draft.json').read_bytes()).hexdigest() == '1a5d0ceec3d179f00e81f8f1ea3e71047981a54f4cd0a4acc71671c1d6d714c1'


def register_statement(stem, topic, day, read_basis, comparison_row, short, references, limit):
    sid, target, quote = (stem + suffix for suffix in ('-statement', '-target', '-quote'))
    finding(target, short, references, read_basis)
    excerpt = passages[references[0]]['exact']
    finding(quote, excerpt, references[:1], read_basis, pair=target)
    records['practice_statement'].append(dict(
        id=sid, party_id=party, topic_id=topic, taxonomy_version=4, summary_finding_id=target,
        quote_finding_id=quote, statement_at=day, date_precision='day' if day else 'unknown',
        version_id=passages[references[0]]['version_id'], period_basis=read_basis,
        uncertainty_reason=limit, comparison_row_id=comparison_row))
    readings(topic, 'statement', references)
    for kind, claim in (('practice_statement', short), ('practice_statement.summary_finding_id', short),
                        ('practice_statement.quote_finding_id', excerpt)):
        task(kind, sid, claim, limit)
    return sid, target, short, references


def compare(stem, topic, eid, statement, compare_text, temporal, authority, limit, outcome=None):
    sid, target, short, statement_refs = statement
    event_refs = [row['passage_id'] for row in records['practice_event_evidence'] if row['event_id'] == eid]
    scope = readings(topic, 'event', event_refs)
    rid = stem + '-relation'
    explanation = stem + '-explanation'
    finding(explanation, compare_text + ' ' + limit, statement_refs + event_refs, limit)
    result = None
    if outcome:
        result = stem + '-result'
        result_refs = [row['passage_id'] for row in records['practice_event_evidence']
                       if row['event_id'] == eid and row['stage'] == 'result']
        finding(result, outcome, result_refs, limit)
        task('practice_relation.result_finding_id', rid, outcome, limit)
    records['practice_relation'].append(dict(
        id=rid, statement_id=sid, event_id=eid, party_id=party, topic_id=topic, scope_id=scope,
        comparability_reason=compare_text, target_finding_id=target, result_finding_id=result,
        explanation_finding_id=explanation, temporal_context=temporal, authority_context=authority,
        uncertainty_reason=limit))
    records['practice_candidate'].append(dict(
        id=stem + '-candidate', scope_id=scope, event_id=eid, relation_id=rid,
        state='eligible', reason=compare_text, passage_ids=encoded(event_refs)))
    for kind, claim in (('practice_relation', compare_text), ('practice_relation.target_finding_id', short),
                        ('practice_relation.explanation_finding_id', compare_text)):
        task(kind, rid, claim, limit)
    return scope


divan = '0412-divan'
divan_topic = 'orgut-olusturma'
divan_limit = ('2023 toplantısının imzalı karar tutanağı, tek tek GİK onayları ve arşiv tüzüğünün '
               'o tarihteki yürürlük durumu açık. Sözcülük, parti duyurusundaki görev adıyla korunuyor.')
divan_statement = register_statement(
    divan, divan_topic, None, 'Tüzük Madde 50/C, 18 Haziran 2022 arşiv nüshası.',
    '04-03-v3-0312-demokrat-1-084-orgut-olusturma-row',
    'Arşivli tüzüğe göre Genel Başkan, Genel Sekreter ve Mali İşler Başkanı dâhil 14 üyeyi GİK’in onayına ayrı ayrı sunar.',
    ['0312-demokrat-1-084-orgut-olusturma-p', '0312-demokrat-1-084-orgut-olusturma-context'],
    divan_limit)
divan_event = event(
    divan + '-notice', '2023-07-22', 'Demokrat Parti Başkanlık Divanı görev dağılımı duyurusu',
    'DP Basın Merkezi, Gültekin Uysal başkanlığındaki toplantının ardından Başkanlık Divanı görev değişikliklerini yayımladı.',
    [(divan + '-notice-meeting', 'initiative', 'party_announcement', 'DP Basın Merkezi toplantıyı 22 Temmuz tarihli yayında bildirdi.'),
     (divan + '-notice-secretariat', 'initiative', 'party_announcement', 'Yayın Ertan Küçükay’ı Genel Sekreter olarak adlandırdı.'),
     (divan + '-notice-spokesperson', 'initiative', 'party_announcement', 'Yayın Haydar Altıntaş’ın sözcülüğe görevlendirildiğini bildirdi.')],
    divan_limit)
compare(divan + '-notice', divan_topic, divan_event, divan_statement,
        'Arşiv tüzüğündeki Genel Sekreterlik ve GİK onayı hükmü, aynı görev adını taşıyan yeni görev dağılımı duyurusuyla karşılaştırıldı.',
        'Tüzük nüshası 18 Haziran 2022’de arşivlenmiş. Duyuru 22 Temmuz 2023 tarihli.',
        'Tüzük onay yetkisini GİK’e verir. Görev dağılımı Genel Başkan ve GİK toplantısı bağlamında Parti Basın Merkezi tarafından bildirildi.',
        divan_limit)

atalay = '0412-atalay'
topic = 'anayasal-denetim'
call_limit = ('9 Kasım 2023 açıklaması parti sitesindeki Haydar Altıntaş’a ait. Yargıtay daire üyelerine '
              'ilişkin ayrı yasal işlem ve açıklamanın sonraki işlemlere etkisi için belge açık.')
call = register_statement(
    atalay, topic, '2023-11-09', 'Demokrat Parti, Altıntaş açıklaması, 9 Kasım 2023.',
    '04-03-v3-0313-demokrat-anayasal-denetim',
    'Altıntaş, AYM’nin Can Atalay kararının uygulanmamasını eleştirdi ve ilgili Yargıtay daire mensupları hakkında yasal işlem istedi.',
    [atalay + '-statement-position', atalay + '-statement-case'], call_limit)
chamber_limit = ('8 Kasım işlemi AYM’nin daha sonra yayımlanan §17 aktarımından izleniyor. Yargıtay’ın imzalı '
                 'karar nüshası ve savcılık sonucu açık. Açıklama 9 Kasım’da yayımlandı.')
chamber = event(
    atalay + '-chamber', '2023-11-08', 'Yargıtay 3. Ceza Dairesinin 8 Kasım işlemi',
    'AYM, Yargıtay 3. Ceza Dairesinin 8 Kasım’da AYM kararına uyulmamasına, işlemlerin başlatılması için TBMM’ye örnek gönderilmesine ve AYM üyeleri hakkında suç duyurusuna karar verdiğini kaydetti.',
    [(atalay + '-aym-chamber', 'action', 'document', 'AYM §17, Yargıtay 3. Ceza Dairesinin 8 Kasım karar gününü ve içeriğini aktardı.'),
     (atalay + '-aym-complaint', 'result', 'document', 'AYM §17, AYM üyeleri hakkında suç duyurusunda bulunulması kararını aktardı.')],
    chamber_limit)
chamber_refs = [atalay + '-aym-chamber', atalay + '-aym-complaint']
scope = readings(topic, 'event', chamber_refs)
key = atalay + '-chamber-candidate'
records['practice_candidate'].append(dict(
    id=key, scope_id=scope, event_id=chamber, relation_id=None, state='unmatched',
    reason=chamber_limit, passage_ids=encoded(chamber_refs)))
task('practice_candidate', key, '8 Kasım işlemine öncel veya eşzamanlı özgül parti söylemi arayışı açık.', chamber_limit)

judgment_limit = 'Hükümde yeniden yargılama ve tahliyeyi sağlama işlemleri için kararın gönderilmesi yer alıyor. İnfaz ve daire mensupları hakkındaki yasal işlem ayrı araştırma konusu.'
judgment = event(
    atalay + '-judgment', '2023-12-21', 'AYM’nin Can Atalay (3) hak ihlali kararı',
    'AYM Genel Kurulu, 2023/99744 başvurusunda üç hak bakımından ihlal kararı verdi. Karar 27 Aralık’ta yayımlandı.',
    [(atalay + '-aym-initial', 'initiative', 'document', 'Kararın §10 bölümü 25 Ekim 2023 tarihli önceki AYM kararını anıyor.'),
     (atalay + '-aym-publication', 'action', 'document', '27 Aralık 2023 tarihli Resmî Gazete özgün nüshası 21 Aralık kararını yayımladı.'),
     (atalay + '-aym-decision', 'result', 'document', 'Hüküm B.1 ve B.2, bireysel başvuru, seçilme ve kişi hürriyeti haklarına ilişkin ihlal kararlarını içeriyor.'),
     (atalay + '-aym-majority', 'result', 'document', 'Hüküm B.2 seçilme ve kişi hürriyeti ihlallerinde oyçokluğunu gösteriyor.'),
     (atalay + '-aym-order', 'result', 'document', 'Hüküm C, giderim işlemleri için İstanbul 13. Ağır Ceza Mahkemesine gönderimi içeriyor.')],
    judgment_limit)
compare(atalay + '-judgment', topic, judgment, call,
        'Altıntaş’ın AYM kararının uygulanmaması eleştirisi, aynı kararın uygulanmasını inceleyen sonraki AYM hükmüyle karşılaştırıldı.',
        'Önceki AYM kararı 25 Ekim, açıklama 9 Kasım, ikinci AYM kararı 21 Aralık, Resmî Gazete yayımı 27 Aralık.',
        'AYM Genel Kurulu bireysel başvuruyu karara bağladı. Altıntaş milletvekili ve parti sözcüsü olarak kamuoyuna seslendi.',
        judgment_limit + ' ' + call_limit,
        'AYM, 2023/99744 başvurusunda bireysel başvuru hakkının oybirliği, seçilme ve kişi hürriyeti haklarının oyçokluğuyla ihlal edildiğine karar verdi.')

minutes_limit = ('Tutanak 3/835 yazısının okunmasını ve Başkanın açıklamasını belgeliyor. İşlemin hukuki geçerliliği '
                 'hakkındaki sonraki AYM norm denetimi ayrı kaynak zincirinde izleniyor.')
minutes = event(
    atalay + '-reading', '2024-01-30', 'TBMM’de Can Atalay’a ilişkin 3/835 yazısının okunması',
    '54. Birleşimde oturum başkanı Yargıtay 3. Ceza Dairesi yazısını okuttu ve milletvekilliğinin düştüğünü açıkladı.',
    [(atalay + '-tbmm-reading', 'action', 'document', '30 Ocak tutanağının 1048. sayfasında 3/835 yazısının okunması kayıtlı.'),
     (atalay + '-tbmm-case', 'action', 'document', 'Yargıtay yazısı 3 Ocak tarihli 2024/1 Değişik İş sayılı kararı gönderiyor.'),
     (atalay + '-tbmm-notice', 'result', 'document', 'Oturum başkanı 1049. sayfada milletvekilliğinin düştüğünü açıkladı.')],
    minutes_limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-2-54-3-835-okunma-2024-01-30'
compare(atalay + '-reading', topic, minutes, call,
        'Altıntaş’ın Kasım ayında AYM kararının uygulanması konusundaki itirazı, aynı Atalay dosyasının Meclisteki sonraki usul işlemiyle karşılaştırıldı.',
        'Açıklama 9 Kasım. Genel Kurulda okunan ayrı Yargıtay karar yazısı 3 Ocak 2024, okutma 30 Ocak 2024.',
        'Yargıtay Ceza Dairesi yazıyı gönderdi. TBMM oturum başkanı yazıyı okuttu ve açıklamada bulundu. Altıntaş’ın sonraki işlemdeki katkısı açık.',
        minutes_limit + ' ' + call_limit,
        'Başkan, yazının okunmasının ardından Can Atalay’ın milletvekilliğinin düştüğünü açıkladı. Tutanak işlemi bu sırayla kaydetti.')
norm_limit = ('AYM’nin 22 Şubat E.2024/43 K.2024/65 hükmü 1 Ağustos 2024’te yayımlandı. '
              'İdari veya Meclis sicilinde daha sonraki uygulama ve başvurudaki 125 kişinin tam imza listesi açık.')
norm = event(
    atalay + '-norm', '2024-02-22', 'AYM’nin Can Atalay’ın Meclisteki işlemine ilişkin norm denetimi',
    'AYM çoğunluğu, 30 Ocak’ta yazının okunmasıyla oluşan fiilî durum hakkında karar verilmesine yer olmadığına hükmetti.',
    [(atalay + '-norm-publication', 'action', 'document', 'E.2024/43 K.2024/65, 1 Ağustos 2024 tarihli Resmî Gazete’de yayımlandı.'),
     (atalay + '-norm-reason', 'action', 'document', 'Karar gerekçesi Yargıtay yazısı okunarak fiilî durum oluşturulduğunu değerlendiriyor.'),
     (atalay + '-norm-reason-legal', 'result', 'document', 'Gerekçe §24, Yargıtay kararına hukuki değer atfedilemeyeceğini belirtiyor.'),
     (atalay + '-norm-result', 'result', 'document', 'Hükümde, dört üyenin karşıoyuyla ve oyçokluğuyla karar verilmesine yer olmadığı yazıyor.')],
    norm_limit)
compare(atalay + '-norm', topic, norm, call,
        'Altıntaş’ın önceki AYM kararının uygulanmasına ilişkin itirazı, aynı dosyadaki Meclis işleminin sonraki anayasal denetimiyle karşılaştırıldı.',
        '3/835 yazısı 30 Ocak’ta okundu. Karar tarihi 22 Şubat, yayımlanma tarihi 1 Ağustos 2024.',
        'Hüküm AYM’ye ait. Altıntaş’ın başvuruya katkısı veya hüküm üzerindeki etkisi açık.',
        norm_limit + ' ' + call_limit,
        'AYM çoğunluğu, oluşan fiilî durum için karar verilmesine yer olmadığına hükmetti. Gerekçe, Yargıtay yazısına hukuki değer atfedilemeyeceğini belirtti.')

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot, records, [entry['values']['id'] for entry in entries if entry['kind']=='passage'], party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak metni, tarihi ve iddia sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('divan-atalay-draft.json',package),('divan-atalay-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
