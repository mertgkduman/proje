"""Hakkâri olayı için eklenebilir aday; input/source/preview kapıları çalıştırılmadı."""
import datetime
import json
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
def read(name):return json.loads((checks/name).read_text())
all_entries=read('institutional-source-slices-draft.json')['entries']+read('hakkari-rounds-source-slices-draft.json')['entries']
prefixes=('0406-calli','0406-hakkari-round')
entries=[]
for e in all_entries:
 v=e['values'];key=v.get('id') or v.get('version_id','')
 if key.startswith(prefixes):entries.append(e)
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def add(record_kind,**values):entries.append(dict(kind=record_kind,values=values))
def finding(ident,text,passages):
 add('finding',id=ident,party_id='dem',heading='Söylem ve uygulama',pair_id=ident,text=text,provenance='summary',epistemic_type='claim')
 for p in passages:
  add('finding_evidence',finding_id=ident,passage_id=p,role='support')
  add('verification',finding_id=ident,passage_id=p,checked_at=now,result='confirmed',reason='İlgili özgün kaynak pasajı ve olayın açıklanan kapsamı incelendi.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Haber ile aktarılan taraf beyanı ayrılarak bağlam okundu.')
round1='0406-hakkari-round1-alt-p';round2='0406-hakkari-round2-p';claim='0406-calli-p';claim_detail='0406-calli-list-p';reply='0406-calli-reply-p';statement='0305-dem-secim-yontem-to-yerel-aday-dem-passage'
calli=next(c for c in read('institutional-captures.json') if c['id']=='calli');exact='44 kişinin ismi, ilave edilmiştir.'
assert exact in html_source_text((Path('data/practices/sources/dem')/calli['original_path']).read_bytes())
add('passage',id=claim_detail,version_id='0406-calli-v1',exact=exact,prefix=None,suffix=None,article=None,section='Çallı ikinci tur listesi iddiası',pdf_page_index=None,printed_page=None)
finding('0406-hakkari-rounds-result','Yüksekova Haber, ilk turda Çallı ve Akış için sırasıyla 272 ve 240 oy bildirirken Yüksekova Halkın Sesi ikinci tur sonunda Akış ile Tekçe’nin aday seçildiğini aktardı.',[round1,round2])
finding('0406-hakkari-rounds-link','Hakkâri aday ön seçimi tüzükte düzenlenen yerel aday belirleme konusuyla ilgilidir; tüzük nüshasının olay döneminde yürürlüğü ve ilgili seçim yönergesi doğrulanmadı.',[statement,round1,round2])
finding('0406-hakkari-dispute-finding','Çallı itirazının reddedildiğini ve listeye sonradan kişi eklendiğini ileri sürdü; il örgütü itirazı dayanıksız bulduğunu ve kararını tebliğ ettiğini açıkladı.',[claim,claim_detail,reply])
for fid in ('0305-dem-secim-yontem-to-yerel-aday-dem-summary','0305-dem-secim-yontem-to-yerel-aday-dem-quote'):
 add('verification',finding_id=fid,passage_id=statement,checked_at=now,result='confirmed',reason='Faz 3 tüzük Madde 59 PDF sayfası ve ilgili pasaj yeniden okundu; olay tarihindeki yürürlük bilinmiyor.')
scope='practice-9640650066746ae453b52f80faea8171584707e5c82c71d21025392d9728b3fb';event='0406-hakkari-2024-selection'
records={
 'practice_scope_v2':[dict(id=scope,party_id='dem',topic_id='yerel-aday',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Hakkâri 13–14 Ocak ön seçimi ve itiraz; konu araştırması sürüyor.')],
 'practice_event':[dict(id=event,common_event_key='dem-hakkari-2024-01-13-aday-onsecim',event_at='2024-01-13',date_precision='day',date_unknown_reason=None,scope_context='13 Ocak 2024 başlangıç tarihi; 14 Ocak ikinci tur ve sonraki itirazları da kapsayan Hakkâri belediye aday ön seçimi',title='13 Ocak’ta başlayan Hakkâri yerel aday ön seçimi',occurrence_basis='İlk ve ikinci tur yerel gazetelerce gün ve yerle bildirildi; oy tutanakları elde edilmedi.')],
 'practice_event_evidence':[dict(event_id=event,passage_id=round1,supported_point='13 Ocak ilk turdaki Çallı ve Akış oyları',stage='action',concrete_basis='Yerel haber seçim salonunu, katılanları ve ilk tur oy sayılarını bildirir.',limitation='Sandık tutanağı ve delegelerin listesi sunulmadı.',epistemic_type='claim'),dict(event_id=event,passage_id=round2,supported_point='14 Ocak ikinci turda Akış ve Tekçe aday seçildi',stage='result',concrete_basis='Yerel haber ikinci tur sonucunda iki adayı bildirir.',limitation='İkinci turun sayısal oy tutanağı sunulmadı.',epistemic_type='claim')],
 'practice_evidence_assessment':[dict(event_id=event,passage_id=round1,stage='action',basis_kind='independent_report'),dict(event_id=event,passage_id=round2,stage='result',basis_kind='independent_report')],
 'practice_contribution':[dict(id='0406-hakkari-selection-contribution',event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id='0406-hakkari-rounds-result',authority_passage_id=None,membership_passage_id=None,responsibility_limit='Hakkâri belediye adaylığının parti içi ön seçimi; kamu seçimi sonucu değildir.')],
 'practice_statement':[dict(id='0406-hakkari-charter-statement',party_id='dem',topic_id='yerel-aday',taxonomy_version=4,summary_finding_id='0305-dem-secim-yontem-to-yerel-aday-dem-summary',quote_finding_id='0305-dem-secim-yontem-to-yerel-aday-dem-quote',statement_at=None,date_precision='unknown',version_id='0204-dem-charter-v1',period_basis='DEM kısa adlı tüzük Madde 59; kabul ve yürürlük tarihi bilinmiyor.',uncertainty_reason='Nüshanın 2024 ön seçiminde yürürlükte olduğu doğrulanmadı.',comparison_row_id='04-03-v3-0305-dem-secim-yontem-to-yerel-aday-dem-row')],
 'practice_relation':[dict(id='0406-hakkari-selection-relation',statement_id='0406-hakkari-charter-statement',event_id=event,party_id='dem',topic_id='yerel-aday',scope_id=scope,comparability_reason='Her iki kaynak yerel adayların ön seçimle belirlenmesiyle ilgili; somut yönerge ve nüsha yürürlüğü açık.',target_finding_id='0305-dem-secim-yontem-to-yerel-aday-dem-summary',result_finding_id='0406-hakkari-rounds-result',explanation_finding_id='0406-hakkari-rounds-link',temporal_context='Hakkâri oylaması 13–14 Ocak, itiraz ve cevap 15–26 Ocak 2024; tüzüğün tarihi kesin değil.',authority_context='Seçim yöntemi tüzükte PM kararına bağlanır; somut PM kararı veya seçim yönergesi elde edilmedi.',uncertainty_reason='İkinci tur oy farkı beyanlar arasında 10/16, seçim tutanağı ve itiraz kararı eksik.')],
 'practice_dispute':[dict(id='0406-hakkari-selection-dispute',event_id=event,supported_points='İki tur ve aday sonucuna ilişkin somut haberler vardır.',disputed_points='Çallı listeye 44 kişi eklendiğini iddia eder; il örgütü itirazı dayanıksız bulduğunu söyler.',unresolved_points='Delege listeleri, oy tutanağı, itiraz kararı ve ikinci tur oy farkı doğrulanmadı.',summary_finding_id='0406-hakkari-dispute-finding')],
 'practice_dispute_evidence':[dict(dispute_id='0406-hakkari-selection-dispute',passage_id=claim_detail,point='İkinci tur listesine 44 kişi eklendiği iddiası',source_position='Çallı kesinleşen listeye ad eklendiğini ileri sürer.',role='conflict'),dict(dispute_id='0406-hakkari-selection-dispute',passage_id=reply,point='İtiraza ilişkin parti yanıtı',source_position='İl örgütü itirazın dayanıksız bulunduğunu ve tebliğ edildiğini savunur.',role='reply')],
}
out=dict(status='draft_unvalidated',entries=entries,practice_records=records,remaining='Ayrı agent source-review taslağı ve inherited olay değerlendirmeleri birlikte bağlanmalı; input/source/preview kapıları ve konu kapsamı kapanışı yoktur.')
(checks/'hakkari-event-fragment-draft.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('HAKKARI_EVENT_FRAGMENT',len(entries),sum(map(len,records.values())))
