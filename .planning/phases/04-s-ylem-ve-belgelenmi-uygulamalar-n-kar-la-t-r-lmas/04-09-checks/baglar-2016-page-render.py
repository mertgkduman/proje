"""Yerel özgün PDF'nin seçilen sıfır tabanlı sayfasını geçici PNG'ye aktar."""
import ctypes,ctypes.util,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_libraries
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-09-checks/baglar-2016-original.pdf').resolve()
pop,obj,glib=pdf_libraries(); cairo=ctypes.CDLL(ctypes.util.find_library('cairo'))
pop.poppler_page_get_size.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double)]
pop.poppler_page_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
cairo.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int];cairo.cairo_image_surface_create.restype=ctypes.c_void_p
cairo.cairo_create.argtypes=[ctypes.c_void_p];cairo.cairo_create.restype=ctypes.c_void_p
cairo.cairo_set_source_rgb.argtypes=[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double]
cairo.cairo_paint.argtypes=[ctypes.c_void_p];cairo.cairo_scale.argtypes=[ctypes.c_void_p,ctypes.c_double,ctypes.c_double]
cairo.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p];cairo.cairo_surface_write_to_png.restype=ctypes.c_int
cairo.cairo_destroy.argtypes=[ctypes.c_void_p];cairo.cairo_surface_destroy.argtypes=[ctypes.c_void_p]
doc=pop.poppler_document_new_from_file(p.as_uri().encode(),None,None);assert doc
index=int(sys.argv[1]) if len(sys.argv)>1 else 0
page=pop.poppler_document_get_page(doc,index);assert page
w=ctypes.c_double();h=ctypes.c_double();pop.poppler_page_get_size(page,ctypes.byref(w),ctypes.byref(h));scale=2
surface=cairo.cairo_image_surface_create(0,int(w.value*scale+1),int(h.value*scale+1));ctx=cairo.cairo_create(surface)
cairo.cairo_set_source_rgb(ctx,1,1,1);cairo.cairo_paint(ctx);cairo.cairo_scale(ctx,scale,scale);pop.poppler_page_render(page,ctx)
output=f'/tmp/gsd-dbp-baglar-2016-index-{index}.png'.encode()
assert cairo.cairo_surface_write_to_png(surface,output)==0
cairo.cairo_destroy(ctx);cairo.cairo_surface_destroy(surface);obj.g_object_unref(page);obj.g_object_unref(doc)
print('RENDER_OK',index,output.decode(),w.value,h.value)
