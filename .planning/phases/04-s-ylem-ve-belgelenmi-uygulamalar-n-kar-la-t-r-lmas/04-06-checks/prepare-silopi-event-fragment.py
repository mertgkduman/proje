"""İki tüzük alternatifiyle Silopi sevk/ihraç bildirimine ait aday zincir."""
import datetime,json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');read=lambda n:json.loads((p/n).read_text())
entries=[x for x in read('institutional-source-slices-draft.json')['entries'] if (x['values'].get('id') or x['values'].get('version_id','')).startswith(('0406-silopi','0406-silopi-dha'))]
for item in entries:
 if item['kind']=='source_attribution' and item['values']['version_id']=='0406-silopi-v1':
  item['values']['publisher']='HALKLARIN EŞİTLİK VE DEMOKRASİ PARTİSİ'
  item['values']['basis']='Açıklama Demokratik Yerel Yönetimler Kuruluna atfedilir; aynı www.demparti.org.tr ana makinesinde tam hukuki adı taşıyan 11 Aralık 2023 parti yayını yayıncı ilişkisini destekler.'
entries+=read('silopi-reply-slices-draft.json')['entries'];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def add(k,**v):entries.append(dict(kind=k,values=v))
official='0406-silopi-p'; init='0406-silopi-dha-p'; reply='0406-silopi-reply-3jul-p'; result='0406-silopi-dha-result-p'
exact='DEM Parti Yerel Yönetimler Kurulu tarafından yapılan açıklamada, görev süreci içerisinde parti politikalarına ve yerel yönetim anlayışına aykırı hareket ettiği gerekçesiyle 2 Temmuz’da kesin ihraç istemiyle Merkez Disiplin Kurulu’na sevk edilen Silopi Belediye Başkanı Jiyan Ormanlı’nın, partiden ihraç edildiğini duyuruldu.'
raw=Path('data/practices/sources/dem/objects/6a26f8ff9851aea9fb06131e12ca142a67cf0873f2562f702d34d35ae579b090/original.html.bin').read_text();assert exact in raw
add('passage',id=result,version_id='0406-silopi-dha-v1',exact=exact,prefix=None,suffix=None,article=None,section='DHA: parti bildirimine atfedilen ihraç',pdf_page_index=None,printed_page=None)
def finding(ident,text,ps):
 add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=ident,text=text,provenance='summary',epistemic_type='claim')
 for q in ps:
  add('finding_evidence',finding_id=ident,passage_id=q,role='support');add('verification',finding_id=ident,passage_id=q,checked_at=now,result='confirmed',reason='Haber veya parti açıklaması, kaynak ve süreç evresiyle birlikte okundu.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti bildirimi, haber aktarımı ve kişisel yanıt tarihlerine göre ayrı tutuldu.')
finding('0406-silopi-announcement-f','DHA, DEM Yerel Yönetimler Kurulunun Ormanlı’nın partiden ihracını duyurduğunu aktardı.',[result])
targets={x:'0305-dem-disiplin-yaptirim-'+x+'-passage' for x in ('dem','hedep')}
for short,q in targets.items():
 finding('0406-silopi-'+short+'-link-f',short.upper()+' kısa adlı tüzükte kesin çıkarma yaptırımı yer alır; parti bildiriminde Ormanlı hakkında ihraç bildirildi. Bu, nüshanın olay tarihinde yürürlükte olduğunu veya usulün doğrulandığını göstermez.',[q,result])
 for form in ('summary','quote'):
  add('verification',finding_id='0305-dem-disiplin-yaptirim-'+short+'-'+form,passage_id=q,checked_at=now,result='confirmed',reason='Tüzük nüshasında yaptırımlar ve alternatif nüshanın farkı okundu; dönemsel yürürlük açık.')
event='0406-silopi-2025-discipline'; scope='practice-b726f103db0f4344c320b6a9fffefad01607e16d6c53e9de6427ad1d5830470c'
evs=[(init,'initiative','2 Temmuz sevk','DHA sevkin 2 Temmuz’da yapıldığını aktarır.'),(reply,'initiative','3 Temmuz açıklaması','Rûdaw Ormanlı’nın görevde olduğunu ve bilgilendirme yapacağını aktardı.'),(official,'initiative','Partinin 6 Ağustos kararı bildirimi','DEM açıklaması 6 Ağustos tarihli disiplin kararını bildirir.'),(result,'initiative','DHA’nın parti ihracı bildirimini aktarması','DHA, Yerel Yönetimler Kurulunun ihraç duyurusunu haberleştirir.')]
r={'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='disiplin-ceza',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Silopi sevki ve ihraç bildirimi; disiplin olayları kapsamı araştırması sürüyor.')],
 'practice_event':[dict(id=event,common_event_key=None,event_at='2025-08-06',date_precision='day',date_unknown_reason=None,scope_context='Silopi Belediye Başkanı Jiyan Ormanlı hakkında parti disiplin süreci',title='Silopi disiplin süreci ve ihraç bildirimi',occurrence_basis='DEM açıklamasında bildirilen karar tarihi ve DHA’nın duyuruyu aktarması.')],
 'practice_event_evidence':[dict(event_id=event,passage_id=q,supported_point=point,stage=stage,concrete_basis=basis,limitation='DHA parti bildirimini aktarıyor; bağımsız karar belgesi veya savunma değildir. 3 Temmuz açıklaması ihraç kararından öncedir.',epistemic_type='claim') for q,stage,point,basis in evs],
 'practice_evidence_assessment':[dict(event_id=event,passage_id=q,stage=stage,basis_kind=('party_announcement' if q in (official,init,result) else 'document')) for q,stage,point,basis in evs],
 'practice_contribution':[dict(id='0406-silopi-contribution',event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id='0406-silopi-announcement-f',authority_passage_id=None,membership_passage_id=None,responsibility_limit='Parti kuruluşu karar ve duyuruyu bildirir; belediye görevinden kendiliğinden ayrılma veya olay iddialarının doğruluğu çıkarılmaz.')],
 'practice_statement':[], 'practice_relation':[]}
for short,q in targets.items():
 sid='0406-silopi-'+short+'-statement'; f='0305-dem-disiplin-yaptirim-'+short
 r['practice_statement'].append(dict(id=sid,party_id='dem',topic_id='disiplin-ceza',taxonomy_version=4,summary_finding_id=f+'-summary',quote_finding_id=f+'-quote',statement_at=None,date_precision='unknown',version_id=('0204-dem-charter-v1' if short=='dem' else '0204-dem-charter-older-v1'),period_basis=short.upper()+' kısa adlı tüzük nüshası.',uncertainty_reason='Nüshanın yürürlük tarihi ve alternatifle sırası bilinmiyor.',comparison_row_id='04-03-v3-'+f+'-row'))
 r['practice_relation'].append(dict(id='0406-silopi-'+short+'-relation',statement_id=sid,event_id=event,party_id='dem',topic_id='disiplin-ceza',scope_id=scope,comparability_reason='Tüzükte kesin çıkarma yaptırımı ile parti ihraç duyurusu aynı disiplin yaptırımı konusundadır.',target_finding_id=f+'-summary',result_finding_id=None,explanation_finding_id='0406-silopi-'+short+'-link-f',temporal_context='Partinin bildirdiği karar 6 Ağustos 2025; iki alternatif tüzüğün olay tarihinde geçerliliği bilinmiyor.',authority_context='Sevk, parti disiplin kurulu kararı iddiası, gazetecilik aktarımı ve kişinin sevk sonrası açıklaması ayrı aşamalardır.',uncertainty_reason='Bağımsız oluş kanıtı, özgün kurul kararı ve savunma yok; DHA parti bildirimini yineler. Bağımsız sonuç ve belediye görevinden ayrılma doğrulanmadı.'))
(p/'silopi-event-fragment-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,practice_records=r,remaining='İki nüsha alternatif kalır; kaynak incelemesi ve üç CLI kapısı bekliyor.'),ensure_ascii=False,indent=2)+'\n');print('SILOPI_EVENT_FRAGMENT_DRAFT',len(entries),sum(map(len,r.values())))
