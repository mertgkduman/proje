import ctypes as c
import ctypes.util
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_libraries

pdf = Path(sys.argv[1]).resolve()
out = Path('/tmp/gsd-03-13-scans')
out.mkdir(exist_ok=True)
p, obj, _ = pdf_libraries()
z = c.CDLL(ctypes.util.find_library('cairo'))
z.cairo_image_surface_create.argtypes = [c.c_int, c.c_int, c.c_int]
z.cairo_image_surface_create.restype = c.c_void_p
z.cairo_create.argtypes = [c.c_void_p]
z.cairo_create.restype = c.c_void_p
z.cairo_scale.argtypes = [c.c_void_p, c.c_double, c.c_double]
z.cairo_surface_write_to_png.argtypes = [c.c_void_p, c.c_char_p]
z.cairo_destroy.argtypes = [c.c_void_p]
z.cairo_surface_destroy.argtypes = [c.c_void_p]
p.poppler_page_render.argtypes = [c.c_void_p, c.c_void_p]
p.poppler_page_get_size.argtypes = [c.c_void_p, c.POINTER(c.c_double), c.POINTER(c.c_double)]
d = p.poppler_document_new_from_file(pdf.as_uri().encode(), None, None)
assert d
indices = [int(x)-1 for x in sys.argv[2:]] if len(sys.argv) > 2 else range(p.poppler_document_get_n_pages(d))
for i in indices:
    page = p.poppler_document_get_page(d, i)
    w, h = c.c_double(), c.c_double()
    p.poppler_page_get_size(page, c.byref(w), c.byref(h))
    surface = z.cairo_image_surface_create(0, int(w.value*2)+1, int(h.value*2)+1)
    ctx = z.cairo_create(surface)
    z.cairo_scale(ctx, 2, 2)
    p.poppler_page_render(page, ctx)
    assert not z.cairo_surface_write_to_png(surface, str(out/f'{pdf.parent.name[:8]}-{i+1:03}.png').encode())
    z.cairo_destroy(ctx)
    z.cairo_surface_destroy(surface)
    obj.g_object_unref(page)
obj.g_object_unref(d)
print('RENDER_OK', pdf, out)
