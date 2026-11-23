"""4114 tutanağındaki beş ayrı DEM önergesini mevcut çifte ekler."""
import datetime, hashlib, json, re
from pathlib import Path
from arsiv import pdf_page_text

c = Path(__file__).resolve().parent
root = c.parents[3]
p, r = root/'data/practices/04-dem.json', root/'data/practices/04-dem-review.json'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(p) == 'a2abfd368da20d88a3296cf72cedc42a3faf0f6ae92930901c6b5ae13b12b32b'
assert sha(r) == 'e1f2512884d7bf10669be84c65ca726623d18227faee83482864db9b0bdf8426'
pkg, review = json.loads(p.read_text()), json.loads(r.read_text())
h = '977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826'
f = root/'data/practices/sources/dem/objects'/h/'original.pdf'
assert sha(f) == h
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
doc, ver = '0406-4114-iklim', '0406-4114-iklim-v1'
url = 'https://tbmm.gov.tr/Tutanaklar/TutanakGoster/4114'
scope = 'practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09'
def add(kind, **values): pkg['practice_records'].setdefault(kind, []).append(values)
def entry(entry_kind, **values): pkg['entries'].append(dict(kind=entry_kind, values=values))
entry('document', id=doc, party_id='dem', title='26 Şubat 2025 Çevre Komisyonu tutanağı', source_kind='official')
entry('document_version', id=ver, document_id=doc, original_url=url, final_url=url,
      document_date='2025-02-26', date_precision='day', date_unknown_reason=None,
      version_label='TBMM özgün tam tutanağı.', accessed_at=now, verified_at=now,
      mime='application/pdf', sha256=h, original_path=f'objects/{h}/original.pdf',
      readable_path=f'objects/{h}/readable.html')
entry('source_attribution', version_id=ver, publisher='TBMM', author=None, kind='official',
      published_at=None, date_precision='unknown', social_handle=None, public_url=url,
      basis='Komisyon tutanağının kapağı ve toplantı tarihi.')
add('practice_scope_v2', id=scope, party_id='dem', topic_id='doga-ekoloji', taxonomy_version=4,
    period_start='2012-11-30', cutoff_at='2026-11-10T14:38:46.154751+00:00',
    research_kind='event', boundary_reason='Yalnız 26 Şubat 2025 ilk beş maddeye ilişkin komisyon önergeleri; konu araştırması sürüyor.')
for n, page in enumerate((32,34,35,35,36), 1):
    text = pdf_page_text(f, page)
    starts = list(re.finditer(r'Çevre Komisyonu Başkanlığına\s+Görüşülmekte olan', text))
    start = starts[1 if n == 4 else 0].start()
    endmatch = re.search(r'kabul\s+edilmemiştir\.', text[start:], re.I)
    assert endmatch
    passage = text[start:start+endmatch.end()]
    assert all(name in passage for name in ('Ayten Kordu','İbrahim Akın','Perihan Koca'))
    assert re.search(rf'{n}[’\x27]', passage)
    base = f'0406-4114-madde{n}'
    pid, event, finding, candidate, contrib = [base+'-'+s for s in ('passage','event','finding','candidate','contribution')]
    title = f'DEM’in 2/2927 {n}. madde çıkarma önergesi'
    context = f'Ayten Kordu, İbrahim Akın ve Perihan Koca, İklim Kanunu Teklifi’nin {n}. maddesinin çıkarılmasını önerdi; Çevre Komisyonu önergeyi kabul etmedi.'
    claim = context + ' Önergenin gerekçesindeki değerlendirmeler imzacılara aittir; bu işlem Genel Kurul sonucu veya isimli oy değildir.'
    entry('passage', id=pid, version_id=ver, exact=passage, prefix=None, suffix=None, article=None,
          section=f'{n}. madde çıkarma önergesi ve ayrı ret', pdf_page_index=page, printed_page=str(page+1))
    entry('finding', id=finding, party_id='dem', heading='Belgelenmiş uygulamalar', pair_id=finding,
          text=claim, provenance='summary', epistemic_type='claim')
    entry('finding_evidence', finding_id=finding, passage_id=pid, role='support')
    entry('verification', finding_id=finding, passage_id=pid, checked_at=now, result='confirmed', reason='Ayrı önerge ve ret tutanakta okundu.')
    entry('review', id='review-'+finding, kind='finding', subject_id=finding, reviewer_kind='agent', reviewed_at=now,
          result='reviewed', reason='İmzacılar, ayrı önerge ve komisyon ret kararı okundu.')
    add('practice_event', id=event, common_event_key=f'tbmm-komisyon-4114-2-2927-madde{n}-dem-cikarma',
        event_at='2025-02-26', date_precision='day', date_unknown_reason=None, title=title,
        scope_context=context, occurrence_basis='TBMM Çevre Komisyonu tutanağı.')
    add('practice_event_evidence', event_id=event, passage_id=pid, supported_point=f'{n}. madde çıkarma önergesi ve ret',
        stage='result', concrete_basis='26 Şubat 2025 komisyon tutanağı.', limitation='Gerekçe atıflı görüştür; Genel Kurul sonucu veya isimli oy değildir.', epistemic_type='claim')
    add('practice_evidence_assessment', event_id=event, passage_id=pid, stage='result', basis_kind='document')
    add('practice_contribution', id=contrib, event_id=event, party_id='dem', actor_id='0406-dem-institution', contribution_kind='task',
        finding_id=finding, authority_passage_id=None, membership_passage_id=None,
        responsibility_limit='Üç milletvekilinin ayrı önergesi ve komisyon reddi; Genel Kurul kararı değil.')
    add('practice_candidate', id=candidate, scope_id=scope, event_id=event, relation_id=None, state='unmatched',
        reason='Bu belirli madde önergesi için önceki tarihli bağımsız parti söylemi araştırması açık; sonraki 198 şerhi öncül değildir.', passage_ids=json.dumps([pid]))
    for kind, ident in [('practice_event_evidence',event+'|'+pid+'|result'),('practice_event',event),('practice_contribution',contrib),('practice_contribution.finding_id',contrib),('practice_candidate',candidate)]:
        review['practice_source_review'].append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=now,
          source_version_ids=json.dumps([ver]), passage_ids=json.dumps([pid]), inspected_sections=json.dumps([f'{n}. madde çıkarma önergesi ve ret'],ensure_ascii=False),
          supported_claim=context, limitations='Komisyon önergesi ve reddi; Genel Kurul sonucu ve isimli oy ayrıdır.', result='reviewed', reason='Özgün TBMM tutanağında imza ve sonuç okundu.'))
add('practice_attempt_v2', id='0406-4114-first-five-reading', scope_id=scope, attempted_at=now,
    query='26 Şubat 2025 2/2927 DEM ilk beş madde çıkarma önergeleri', url=url, result='examined',
    reason='57 sayfanın metin katmanı okundu; ilk beş ayrı önerge ve ret kaydedildi, kalan önergeler kapsamda açık.', source_version_id=ver)
add('practice_scope_source', scope_id=scope, version_id=ver,
    inspected_sections=json.dumps(['PDF 0–56 metin katmanı','PDF 32, 34–36 ilk beş önerge ve ayrı retleri'],ensure_ascii=False), inspected_at=now)
review['source_review_refs'] = [dict(subject_kind=x['subject_kind'], subject_id=x['subject_id']) for x in review['practice_source_review']]
for name, obj in [('4114-first-five-draft.json',pkg),('4114-first-five-review-draft.json',review)]:
    path=c/name; path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,sha(path))
