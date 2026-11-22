import ctypes
import ctypes.util
import sys
from pathlib import Path

pdf=Path(sys.argv[1]).resolve();page_index=int(sys.argv[2]);output=Path(sys.argv[3])
pop=ctypes.CDLL(ctypes.util.find_library('poppler-glib'));obj=ctypes.CDLL(ctypes.util.find_library('gobject-2.0'));cairo=ctypes.CDLL(ctypes.util.find_library('cairo'))
pop.poppler_document_new_from_file.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_void_p];pop.poppler_document_new_from_file.restype=ctypes.c_void_p
pop.poppler_document_get_page.argtypes=[ctypes.c_void_p,ctypes.c_int];pop.poppler_document_get_page.restype=ctypes.c_void_p
pop.poppler_page_get_size.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_double),ctypes.POINTER(ctypes.c_double)]
pop.poppler_page_render.argtypes=[ctypes.c_void_p,ctypes.c_void_p]
obj.g_object_unref.argtypes=[ctypes.c_void_p]
cairo.cairo_image_surface_create.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.c_int];cairo.cairo_image_surface_create.restype=ctypes.c_void_p
cairo.cairo_create.argtypes=[ctypes.c_void_p];cairo.cairo_create.restype=ctypes.c_void_p
cairo.cairo_scale.argtypes=[ctypes.c_void_p,ctypes.c_double,ctypes.c_double]
cairo.cairo_surface_write_to_png.argtypes=[ctypes.c_void_p,ctypes.c_char_p];cairo.cairo_surface_write_to_png.restype=ctypes.c_int
cairo.cairo_destroy.argtypes=[ctypes.c_void_p];cairo.cairo_surface_destroy.argtypes=[ctypes.c_void_p]
doc=pop.poppler_document_new_from_file(pdf.as_uri().encode(),None,None);assert doc
page=pop.poppler_document_get_page(doc,page_index);assert page
w=ctypes.c_double();h=ctypes.c_double();pop.poppler_page_get_size(page,ctypes.byref(w),ctypes.byref(h));scale=2.0
surface=cairo.cairo_image_surface_create(0,int(w.value*scale),int(h.value*scale));ctx=cairo.cairo_create(surface);cairo.cairo_scale(ctx,scale,scale);pop.poppler_page_render(page,ctx);assert cairo.cairo_surface_write_to_png(surface,str(output).encode())==0
cairo.cairo_destroy(ctx);cairo.cairo_surface_destroy(surface);obj.g_object_unref(page);obj.g_object_unref(doc)
print('PAGE_RENDERED',page_index,output)
