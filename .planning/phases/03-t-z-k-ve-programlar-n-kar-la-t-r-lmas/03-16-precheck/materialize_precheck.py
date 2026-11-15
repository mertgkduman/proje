"""Assemble authored precheck judgments with real immutable IDs, never import."""
import collections
import datetime as dt
import hashlib
import json
import pathlib
import re
import inspect_sources as s

OUT = pathlib.Path(__file__).resolve().parent
P14 = OUT.parent / '03-14-checks'
NOW = dt.datetime.now(dt.timezone.utc).isoformat()
ORDER = ['yeni-parti','tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat']
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):
    return str(path.relative_to(s.ROOT))
def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

manifest = json.loads((s.ROOT/'data/releases'/s.RELEASE/'manifest.json').read_text())
assert json.loads((s.ROOT/'data/current.json').read_text())['release_id'] == s.RELEASE
baseline = {'release_id': s.RELEASE, 'taxonomy_version':4, 'renderer_version':22,
            'manifest':manifest, 'records':{}}
for f in ['records.json','records.sqlite3']:
    digest = sha(s.ROOT/'data/releases'/s.RELEASE/f)
    assert digest == manifest['files'][f]
    baseline['records'][f] = digest

semantic = {(x['subject_kind'],x['subject_id']):x for x in s.D['comparison_semantic_review']}
by_pair = collections.defaultdict(list)
for f in s.D['comparison_field']:
    by_pair[(f['summary_finding_id'],f['quote_finding_id'])].append(f)
reviews = collections.defaultdict(list)
for x in s.D['review']:
    reviews[(x['kind'],x['subject_id'])].append(x)

packages = []
for p in sorted((s.ROOT/'data/comparisons').glob('*semantic.json')):
    if p.name == '03-synthesis-semantic.json':
        continue
    d = json.loads(p.read_text())
    decisions = d['decisions']
    invalid = []
    for x in decisions:
        if (x.get('result') != 'reviewed' or not x.get('reason') or
            x.get('subject_id') not in s.I.get(x.get('subject_kind'), {}) or
            any(i not in s.I['passage'] for i in x.get('passage_ids', []))):
            invalid.append(x)
    packages.append({'path':rel(p), 'sha256':sha(p), 'historical_top_status':d.get('status'),
                     'note':d.get('note'), 'decision_count':len(decisions),
                     'decision_kinds':dict(collections.Counter(x.get('subject_kind') for x in decisions)),
                     'outcomes':dict(collections.Counter(x.get('result') for x in decisions)),
                     'invalid_decisions':invalid,
                     'original_review_time_range': [min((x['reviewed_at'] for x in decisions),default=None),max((x['reviewed_at'] for x in decisions),default=None)],
                     'research_log':d.get('research_log'),
                     'historical_pairs':d.get('historical_pairs')})

def trace_field(f):
    direct = semantic.get(('comparison_field',f['id']))
    inherited = [semantic[('comparison_field',g['id'])] for g in by_pair[(f['summary_finding_id'],f['quote_finding_id'])]
                 if ('comparison_field',g['id']) in semantic and g['id'] != f['id']]
    fr = reviews[('finding',f['summary_finding_id'])] + reviews[('finding',f['quote_finding_id'])]
    return {'kind': 'direct_semantic' if direct else 'same_findings_prior_semantic' if inherited else 'finding_reviews_only' if fr else 'untraced',
            'direct':direct, 'inherited':inherited, 'finding_reviews':fr}

parties=[]
for party in ORDER:
    rows=s.selected(party)
    ids={r['id'] for r in rows}
    ff=[f for f in s.D['comparison_field'] if f['row_id'] in ids]
    ii=[i for i in s.D['comparison_source_inventory'] if i['taxonomy_version']==4 and i['party_id']==party]
    parties.append({'party_id':party,'topic_count':len({r['topic_id'] for r in rows}),'row_count':len(rows),
                    'states':dict(collections.Counter(r['state'] for r in rows)),
                    'roles':dict(collections.Counter(r['source_role'] for r in rows)),
                    'levels':dict(collections.Counter(r['level'] for r in rows)),
                    'field_count':len(ff),'field_review_provenance':dict(collections.Counter(trace_field(f)['kind'] for f in ff)),
                    'finding_review_only_fields':[dict(f, finding_reviews=trace_field(f)['finding_reviews']) for f in ff if trace_field(f)['kind']=='finding_reviews_only'],
                    'untraced_fields':[f['id'] for f in ff if trace_field(f)['kind']=='untraced'],
                    'open_substantive_rows':[r['id'] for r in rows if r['state'] in ['not_researched','in_progress']],
                    'inventory_sections':len(ii), 'unmatched_headings':[i for i in ii if json.loads(i['unmatched_headings'])],
                    'selected_versions':sorted({r['version_id'] for r in rows if r['version_id']}),
                    'missing_ids':sorted({r['missing_id'] for r in rows if r['missing_id']}),
                    'scope_ids':sorted({r['scope_id'] for r in rows if r['scope_id']})})

authored=json.loads((OUT/'authored_checks.json').read_text())
used_sources=set(); used_passages=set(); used_scopes=set(); used_missing=set(); used_attempts=set()
checks=[]
all_synth = {x['id']:x for x in s.D['comparison_synthesis'] if x['taxonomy_version']==4}
for c in authored['checks']:
    rowids=set(c.get('rows',[]))
    for q in c.get('row_patterns',[]):
        matches=[r['id'] for r in s.selected(q['party']) if re.search(q['pattern'],r['id'])]
        assert matches,(c['id'],'Empty row selector',q)
        rowids.update(matches)
    rowids.update(r['id'] for r in s.ROWS.values() if r['topic_id'] in c.get('topic_rows',[]))
    if 'change_page_selector' in c:
        sel=c['change_page_selector']
        for change in s.D['comparison_change']:
            a=s.I['passage'][change['after_passage_id']];b=s.I['passage'][change['before_passage_id']]
            if change['row_id'] in s.ROWS and s.ROWS[change['row_id']]['party_id']==sel['party'] and a['version_id']==sel['after_version'] and b['version_id']==sel['before_version'] and a['pdf_page_index']==b['pdf_page_index']==sel['page']:
                rowids.add(change['row_id'])
    unknown=rowids-set(s.ROWS)
    if unknown:
        raise ValueError((c['id'],'Unknown selected rows',unknown))
    packets=[]
    for rid in sorted(rowids):
        r=s.ROWS[rid];v=dict(r);v['fields']=[]
        if r['version_id']:used_sources.add(r['version_id'])
        if r['scope_id']:used_scopes.add(r['scope_id'])
        if r['missing_id']:used_missing.add(r['missing_id'])
        for f in s.D['comparison_field']:
            if f['row_id']!=rid or ('field_filter' in c and f['id'] not in c['field_filter']):continue
            x=dict(f);x['summary']=s.I['finding'][f['summary_finding_id']]['text']
            x['summary_passage_ids']=[e['passage_id'] for e in s.D['finding_evidence'] if e['finding_id']==f['summary_finding_id']]
            x['quote_passage_ids']=[e['passage_id'] for e in s.D['finding_evidence'] if e['finding_id']==f['quote_finding_id']]
            used_passages.update(x['summary_passage_ids']+x['quote_passage_ids'])
            x['review_provenance']=trace_field(f)
            v['fields'].append(x)
        v['changes']=[x for x in s.D['comparison_change'] if x['row_id']==rid]
        for x in v['changes']:used_passages.update([x['before_passage_id'],x['after_passage_id']])
        packets.append(v)
    synthesis=[]
    for sid in c.get('synthesis',[]):
        assert sid in all_synth,(c['id'],sid)
        item=dict(all_synth[sid]);r=semantic[('comparison_synthesis',sid)]
        item['original_semantic_review']=r
        item['typed_proof']=json.loads(r['reason'])
        item['passage_evidence']=[x['passage_id'] for x in s.D['comparison_synthesis_evidence'] if x['synthesis_id']==sid]
        used_passages.update(item['passage_evidence'])
        for side in item['typed_proof']['sides']:
            if side['support']=='scope':used_scopes.update(side['refs'])
            if side['support']=='missing':
                used_missing.update(x for x in side['refs'] if x in s.I['missing'])
                used_attempts.update(x for x in side['refs'] if x in s.I['attempt'])
        synthesis.append(item)
    downstream=[]
    for sid in all_synth:
        r=semantic[('comparison_synthesis',sid)]
        proof=json.loads(r['reason'])
        if any(side['row_id'] in rowids for side in proof['sides']):downstream.append(sid)
    result={k:v for k,v in c.items() if k not in ['rows','row_patterns','topic_rows','field_filter','synthesis','change_page_selector']}
    result.update({'reviewer_kind':'agent','result':'documentary_limitation_preserved' if c['id']=='SR22' else 'supported_with_stated_scope',
                   'selected_rows':packets,'inspected_synthesis':synthesis,
                   'dependent_claim_ids_for_trace_not_blanket_reapproval':downstream,
                   'new_semantic_defects':[], 'recorded_at':NOW})
    used_missing.update(c.get('extra_missing_ids',[]));used_sources.update(c.get('extra_version_ids',[]))
    checks.append(result)
for mid in used_missing:used_attempts.add(s.I['missing'][mid]['attempt_id'])
for p in used_passages:used_sources.add(s.I['passage'][p]['version_id'])
for sc in used_scopes:used_sources.add(s.I['comparison_review_scope'][sc]['version_id'])

sources=[]
newly_read={'epm-charter-v1','epm-program-v1','0203-tip-charter-v1','0203-tip-charter2022-v1','0203-tip-program-v1',
            '0204-dem-charter-v1','0204-dem-charter-older-v1','0204-dem-policies-v1','0205-iyi-charter-download-v1',
            '0205-iyi-charter-istanbul-v1','0205-iyi-program-page-v1','0206-yeni-yol-registry-v1','0206-yeni-yol-founding-v1',
            '0207-dbp-charter-v1','0308-dbp-bdp-charter-blog-v1','0207-dbp-bdp-charter-v1','0207-dbp-bdp-program-v1',
            '0208-emep-program-charter-v1','0208-emep-charter-pdf-v1','0209-saadet-current-charter-v1',
            '0209-saadet-current-program-v1','0210-demokrat-charter-archive-v1','0210-demokrat-program-archive-v1',
            '0210-demokrat-old1985-v1','0210-demokrat-democracy-program2-v1'}
for vid in sorted(used_sources):
    v=dict(s.I['document_version'][vid]);p=s.ROOT/'data'/v['original_path']
    v['root_relative_original_path']=rel(p)
    v['computed_sha256']=sha(p);assert v['computed_sha256']==v['sha256']
    v['attributions']=[x for x in s.D['source_attribution'] if x['version_id']==vid]
    v['reading_provenance']='relevant_original_context_read_this_run' if vid in newly_read else 'prior_source_reading_reused_plus_current_binding_check'
    sources.append(v)

artifacts=[]
for p in sorted((s.ROOT/'data/comparisons').glob('*v4*.json')):
    d=json.loads(p.read_text());artifacts.append({'path':rel(p),'sha256':sha(p),'status':d.get('status'),
    'taxonomy_version':d.get('taxonomy_version'),'counts':{k:len(v) for k,v in d.items() if isinstance(v,list)}})
prior_names=['phase16-source-probe-handoff.md','row-partition-and-phase15-handoff.md','emep-locator-independent.md',
 'v3-v4-row-lineage.json','v3-v4-synthesis-lineage.json','v4-batch-replacement-lineage.json',
 'v4-batch-independent-audit.md','dependent-claims-independent-audit.md','sparse-topic-independent-review.json',
 'charter-last-authored-review.json','policy-more-authored-review.json','income-scope-matrix.md','medical-deep-review.md',
 'dem-historical-identity.md']
prior=[{'path':rel(P14/n),'sha256':sha(P14/n)} for n in prior_names]
images=[{'path':rel(p),'sha256':sha(p)} for p in sorted(OUT.glob('*.png'))]
for n in ['gsd-0314-tip2022-index22-white.png','gsd-0314-tip2022-index8.png']:
    images.append({'path':rel(P14/n),'sha256':sha(P14/n)})

result={'artifact_kind':'agent_source_second_reading_precheck','not_importer':True,'not_phase_acceptance':True,
 'reviewer_kind':'agent','reviewer_task':'/root/precheck_03_sources',
 'model':{'resolved_by_parent':'gpt-6.1-sol','reasoning_effort_resolved_by_parent':'xhigh','automatic_astra_used':False,
          'note':'Parent supplied CLI resolution; this subtask did not switch models or launch agents.'},
 'actual_reading_time':{'clock_observed_during_reading':'2026-11-15T12:38:37Z','packaged_at':NOW,
                      'note':'These are this run timestamps, not inherited 13/14 November review times. Original review dates remain inside provenance.'},
 'baseline':baseline,'method':authored['method'],
 'sample_rationale':[
  'Party coverage comes from all nine package/scope closures; the risk sample then covers conditions that are easy to lose in summaries rather than a fixed quota.',
  'Charter risks span membership, central and local elections, oversight, views/discipline/appeals and other bodies; programme risks span principle/target/instrument and beneficiary/threshold/model conditions.',
  'Multiple textual versions, proposal versus body, historical versus current and programme gaps with supplements are deliberately crossed.',
  'Sparse topics inspect the actual one-positive and status-only structure without fabricating a second positive party.',
  'Prior full readings and independent source14 packets are reused with their exact boundaries. This run does not claim to reread every page.'
 ],
 'party_closure_audit':parties,'semantic_package_audit':packages,'v4_artifacts':artifacts,
 'same_hash_copy_facts':[{'versions':[dict(s.I['document_version'][a]),dict(s.I['document_version'][b])],
                         'same_sha256':s.I['document_version'][a]['sha256']==s.I['document_version'][b]['sha256'],
                         'meaning':'Different URLs, same archived bytes. No change, chronology or legal currency follows.'}
                        for a,b in [('0209-saadet-program-v1','0209-saadet-current-program-v1'),('0209-saadet-charter-v1','0209-saadet-current-charter-v1')]],
 'prior_reading_artifacts':prior,'checks':checks,'source_versions':sources,
 'passages':[dict(s.I['passage'][pid], exact_excerpt=s.I['passage'][pid]['exact'][:500]) for pid in sorted(used_passages)],
 'scopes':[s.I['comparison_review_scope'][i] for i in sorted(used_scopes)],
 'missing':[s.I['missing'][i] for i in sorted(used_missing)],'attempts':[s.I['attempt'][i] for i in sorted(used_attempts)],
 'retained_locator_images':images,
 'defects':[],
 'documentary_uncertainties':[
  'DEM/HEDEP order, TİP HTML/PDF order, DBP historical copies and EMEP proposal/body adoption or order are not legal currency evidence.',
  'DEM/DBP/Yeni Yol full programme gaps remain real acquisition limits; supplements or historical text do not remove them.',
  'DYP1985 printed99–100 are absent in this copy; current metadata is a copy-specific gap rather than absence of party policy.',
  'The Demokrat17/II heading placement does not decide exclusivity; the Md20/Md25 implementation relationship is not specified.',
  'Historical semantic package in_progress headers are not current row states; their reviewed decisions remain historical evidence, not a new human acceptance.'
 ],
 'outside_this_precheck':['03-16 complete technical gate and its negative fixtures','formal phase verification','human UAT and eight raw unclassified/unresolved assumptions','three descriptor-less unresolved prohibitions','global regression/audit/publication'],
 'recommended_corrections':[],
 'handoff':'No new source semantic defect observed in this explicitly bounded risk sample. Root must review and map this agent package to the formal03-16 source-review contract; do not import it or treat it as human/UAT acceptance.'}
# Exact passage is retained for inspection; no conclusion is derived by this assembler.
dump(OUT/'source-second-reading.json',result)
dump(OUT/'coverage-map.json',{'baseline':baseline['release_id'],'parties':parties,'semantic_packages':packages,
 'counted_semantic_decisions':sum(p['decision_count'] for p in packages),'counted_selected_fields':sum(p['field_count'] for p in parties)})
print(json.dumps({'checks':len(checks),'rows':len({r['id'] for c in checks for r in c['selected_rows']}),
 'fields':len({f['id'] for c in checks for r in c['selected_rows'] for f in r['fields']}),
 'inspected_synthesis':len({z['id'] for c in checks for z in c['inspected_synthesis']}),
 'source_versions':len(sources),'newly_read_source_versions_in_scope':sum(v['reading_provenance'].startswith('relevant') for v in sources),
 'passages':len(used_passages),'scopes':len(used_scopes),'missing':len(used_missing),'attempts':len(used_attempts),
 'package_decisions':sum(p['decision_count'] for p in packages),'completed_at':NOW},ensure_ascii=False))
