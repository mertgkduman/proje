"""Read-only helpers for the agent source second reading; not an importer."""
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path('/hpc/group/pfisterlab/mg551/storage/proje')
RELEASE = '27033583248b4951b3fe8e5fd6d77b9f'
D = json.loads((ROOT / 'data/releases' / RELEASE / 'records.json').read_text())
I = {k: {x['id']: x for x in v if 'id' in x} for k, v in D.items() if isinstance(v, list)}
ROWS = {r['id']: r for r in D['comparison_row'] if r['taxonomy_version'] == 4}

def row_packet(row):
    r = dict(row)
    r['fields'] = []
    for f in D['comparison_field']:
        if f['row_id'] != row['id']:
            continue
        item = dict(f)
        item['findings'] = []
        for key in ('summary_finding_id', 'quote_finding_id'):
            finding = dict(I['finding'][f[key]])
            finding['passages'] = [I['passage'][e['passage_id']] for e in D['finding_evidence'] if e['finding_id'] == finding['id']]
            item['findings'].append(finding)
        r['fields'].append(item)
    if r['scope_id']:
        r['scope'] = I['comparison_review_scope'][r['scope_id']]
    if r['missing_id']:
        r['missing'] = I['missing'][r['missing_id']]
        r['attempt'] = I['attempt'][r['missing']['attempt_id']]
    if r['version_id']:
        r['version'] = I['document_version'][r['version_id']]
        r['document'] = I['document'][r['version']['document_id']]
    r['changes'] = [x for x in D['comparison_change'] if x['row_id'] == row['id']]
    return r

def selected(party=None, pattern=None):
    return [r for r in ROWS.values() if (not party or r['party_id'] == party) and (not pattern or re.search(pattern, json.dumps(r, ensure_ascii=False)))]

def synth(topic):
    out = []
    for s in D['comparison_synthesis']:
        if s['taxonomy_version'] != 4 or s['topic_id'] != topic:
            continue
        item = dict(s)
        item['proofs'] = [e for e in D['comparison_synthesis_evidence'] if e['synthesis_id'] == s['id']]
        item['reviews'] = [e for e in D['comparison_semantic_review'] if e['subject_kind'] == 'comparison_synthesis' and e['subject_id'] == s['id']]
        out.append(item)
    return out

def main():
    command, *args = sys.argv[1:]
    if command == 'rows':
        result = [row_packet(r) for r in selected(args[0] if args[0] != '*' else None, args[1])]
    elif command == 'list':
        result = [{'id': r['id'], 'topic': r['topic_id'], 'party': r['party_id'], 'organ': r['organ'], 'version': r['version_id'], 'state': r['state']} for r in selected(args[0] if args[0] != '*' else None, args[1])]
    elif command == 'synth':
        result = synth(args[0])
    elif command == 'get':
        result = I[args[0]][args[1]]
    elif command == 'pdf':
        sys.path.insert(0, str(ROOT / 'src'))
        from arsiv import pdf_page_text
        version = I['document_version'][args[0]]
        print(json.dumps(version, ensure_ascii=False))
        for page in args[1:]:
            print('PDF_INDEX', page)
            print(pdf_page_text(ROOT / 'data' / version['original_path'], int(page)))
        return
    elif command == 'render':
        import ctypes as c
        import ctypes.util
        sys.path.insert(0, str(ROOT / 'src'))
        from arsiv import pdf_libraries
        pop, obj, _ = pdf_libraries()
        cairo = c.CDLL(ctypes.util.find_library('cairo'))
        for name, argtypes, restype in [
            ('cairo_image_surface_create', [c.c_int, c.c_int, c.c_int], c.c_void_p),
            ('cairo_create', [c.c_void_p], c.c_void_p),
            ('cairo_scale', [c.c_void_p, c.c_double, c.c_double], None),
            ('cairo_set_source_rgb', [c.c_void_p, c.c_double, c.c_double, c.c_double], None),
            ('cairo_paint', [c.c_void_p], None),
            ('cairo_surface_write_to_png', [c.c_void_p, c.c_char_p], c.c_int),
            ('cairo_destroy', [c.c_void_p], None),
            ('cairo_surface_destroy', [c.c_void_p], None),
        ]:
            fn = getattr(cairo, name)
            fn.argtypes, fn.restype = argtypes, restype
        pop.poppler_page_render.argtypes = [c.c_void_p, c.c_void_p]
        pop.poppler_page_get_size.argtypes = [c.c_void_p, c.POINTER(c.c_double), c.POINTER(c.c_double)]
        version = I['document_version'][args[0]]
        doc = pop.poppler_document_new_from_file((ROOT / 'data' / version['original_path']).as_uri().encode(), None, None)
        assert doc
        for idx in map(int, args[1:]):
            page = pop.poppler_document_get_page(doc, idx)
            assert page
            w, h = c.c_double(), c.c_double()
            pop.poppler_page_get_size(page, c.byref(w), c.byref(h))
            surface = cairo.cairo_image_surface_create(0, int(w.value*1.7)+1, int(h.value*1.7)+1)
            ctx = cairo.cairo_create(surface)
            cairo.cairo_set_source_rgb(ctx, 1, 1, 1)
            cairo.cairo_paint(ctx)
            cairo.cairo_scale(ctx, 1.7, 1.7)
            pop.poppler_page_render(page, ctx)
            out = pathlib.Path(__file__).parent / f'{args[0]}-index{idx}.png'
            assert cairo.cairo_surface_write_to_png(surface, str(out).encode()) == 0
            print(out)
            cairo.cairo_destroy(ctx)
            cairo.cairo_surface_destroy(surface)
            obj.g_object_unref(page)
        obj.g_object_unref(doc)
        return
    else:
        raise SystemExit('Unknown command')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
