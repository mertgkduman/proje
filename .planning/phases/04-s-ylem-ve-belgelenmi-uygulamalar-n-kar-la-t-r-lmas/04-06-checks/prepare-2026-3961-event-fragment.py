"""Mekke anlaşması görüşme ve oylamasında DEM katkısı için aday zincir."""
import datetime,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
entries=json.loads((p/'2026-3961-source-slices-draft.json').read_text())['entries']; now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def add(k,**v):entries.append(dict(kind=k,values=v))
speech='0406-tbmm-2026-3961-p'; speaker='0406-2026-3961-speaker-p'; vote='0406-tbmm-2026-3961-vote-p'; yes='0406-2026-3961-accept-p'; no='0406-2026-3961-reject-p'; news='0406-tbmm-2026-3961-news-p'; target='0305-dem-program-dis-politika-passage'; ctx='0305-dem-program-dis-politika-context-passage'
def finding(ident,text,ps):
 add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=ident,text=text,provenance='summary',epistemic_type='claim')
 for q in ps:
  add('finding_evidence',finding_id=ident,passage_id=q,role='support');add('verification',finding_id=ident,passage_id=q,checked_at=now,result='confirmed',reason='Tutanak veya cetvelin ilgili özgün metni ve tarihli bağlamı okundu.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti adına konuşma, bireysel oy ve Genel Kurul toplamı ayrı değerlendirildi.')
finding('0406-2026-3961-position-f','Sezai Temelli DEM grubu adına görüşmede anlaşmaya karşı çıktığını söyledi.',[speaker,speech])
finding('0406-2026-3961-vote-f','Kesin açık oylama cetveli Sezai Temelli için ret; Genel Kurul toplamında 277 kabul ve 118 ret gösterir.',[vote,yes,no])
finding('0406-2026-3961-link-f','DEM ek belgesindeki barışçı dış politika hedefi ile grubun anlaşmaya karşı görüşü ilişkilidir; Meclis kararı ve kişisel oy aynı işlem değildir.',[target,ctx,speaker,speech,vote,yes,no])
for fid,q in [('0305-dem-program-dis-politika-summary',target),('0305-dem-program-dis-politika-summary',ctx),('0305-dem-program-dis-politika-quote',target)]:
 add('verification',finding_id=fid,passage_id=q,checked_at=now,result='confirmed',reason='Parti ekindeki hedef ve çevre bağlamı okundu; belge tarihi ve toplantı kökeni açık.')
event='0406-2026-3961-vote'; scope='practice-db7cdd8fdb852fa28d1789156b1269e7dbb70fe6d714feda69e848b3e4f756b3'; statement='0406-dem-dis-politika-statement'; relation='0406-2026-3961-relation'
evs=[(speaker,'initiative','DEM grubu adına konuşmacı','Tutanak Temelli’yi DEM grubu adına konuşmacı olarak gösterir.'),(speech,'initiative','Anlaşmaya karşı görüş','Temelli anlaşmaya ve NATO bağlantılı anlaşmalara karşı olduklarını söyler.'),(vote,'result','Temelli’nin kesin ret oyu','İsimli cetvel Temelli için sonuç sütununda RET gösterir.'),(yes,'result','Genel Kurul kabul toplamı','Kesin cetvel 277 kabul kaydeder.'),(no,'result','Genel Kurul ret toplamı','Kesin cetvel 118 ret kaydeder.')]
r={
 'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='dis-politika',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Bir anlaşma görüşmesi ve oylaması; dış politika kapsamı araştırması sürüyor.')],
 'practice_event':[dict(id=event,common_event_key='tbmm-28-5-014-2-3961-mekke-7597',event_at='2026-11-05',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem 5. yasama yılı 14. birleşim; 2/3961 ve 295 sıra sayılı teklif',title='Mekke Anlaşması uygun bulma teklifinin oylaması',occurrence_basis='TBMM tutanağı ve isimli kesin açık oylama cetveli.')],
 'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='Genel Kurul toplamı partiye atfedilmez; tek kişilik oy grup talimatı veya başka milletvekillerinin oyu değildir.',epistemic_type='claim') for q,stage,point,basis in evs],
 'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind='document') for q,stage,point,basis in evs],
 'practice_contribution':[dict(id='0406-2026-3961-contribution',event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='objection',finding_id='0406-2026-3961-position-f',authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grubu adına konuşma; Temelli’nin bireysel oyu ve Meclisin toplam sonucu ayrı kaydedilir.')],
 'practice_statement':[dict(id=statement,party_id='dem',topic_id='dis-politika',taxonomy_version=4,summary_finding_id='0305-dem-program-dis-politika-summary',quote_finding_id='0305-dem-program-dis-politika-quote',statement_at=None,date_precision='unknown',version_id='0204-dem-policies-v1',period_basis='Parti sitesinde yayımlanan programatik ek; bağımsız tam program değildir.',uncertainty_reason='Ek belgenin kesin tarihi ve toplantı kökeni bilinmiyor.',comparison_row_id='04-03-v3-0305-dem-program-dis-politika-row')],
 'practice_relation':[dict(id=relation,statement_id=statement,event_id=event,party_id='dem',topic_id='dis-politika',scope_id=scope,comparability_reason='Ek belgedeki barışçı dış politika ve askerî güç gösterisinden uzaklaşma hedefi, anlaşmaya ilişkin grup görüşüyle aynı dış politika alanındadır.',target_finding_id='0305-dem-program-dis-politika-summary',result_finding_id='0406-2026-3961-vote-f',explanation_finding_id='0406-2026-3961-link-f',temporal_context='Grup konuşması ve açık oylama 5 Kasım 2026; ek belgenin kesin tarihi açık.',authority_context='DEM grubu adına konuşma ve bir milletvekilinin bireysel oyu; teklifin kabulü Genel Kurulun ortak işlemidir.',uncertainty_reason='Oylama çatışma sonucu, anlaşmanın sonraki uygulanması veya tüm parti üyelerinin oy yönü değildir.')]
}
(p/'2026-3961-event-fragment-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,practice_records=r,remaining='Kaynak incelemesi ve giriş/kaynak/önizleme kapıları bekleniyor.'),ensure_ascii=False,indent=2)+'\n')
print('3961_EVENT_FRAGMENT_DRAFT',len(entries),sum(map(len,r.values())))
