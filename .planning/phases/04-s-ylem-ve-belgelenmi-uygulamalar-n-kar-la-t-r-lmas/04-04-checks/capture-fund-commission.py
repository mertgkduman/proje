"""Archive the 14 October 2026 Plan and Budget Committee transcript."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import pdf_page_text, readable_bytes

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-parti')
source = stage/'fund5472.pdf'
raw = source.read_bytes()
digest = sha256(raw).hexdigest()
assert digest == 'bb6077353f49dbf12c19679e9c883f302ef70165b2010c8bf9390be48e50789b'
original = f'objects/{digest}/original.pdf'
readable = f'objects/{digest}/readable.html'
for name,content in ((original,raw),(readable,readable_bytes(raw,'pdf',legacy=False))):
    path = root/name
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==content
    else:
        path.write_bytes(content)
document='0404-fund-commission-5472'
version=document+'-v1'
url='https://tbmm.gov.tr/Tutanaklar/TutanakGoster/5472'
now=datetime.now(timezone.utc).isoformat()
entries=[]


def add(table, **row):
    entries.append(dict(kind=table,values=row))


def between(page, start, end):
    body=pdf_page_text(root/original,page)
    left=body.index(start)
    right=body.index(end,left)+len(end)
    return body[left:right]


add('document',id=document,party_id='yeni-parti',title='14 Ekim 2026 Plan ve Bütçe Komisyonu 2. toplantı tutanağı',
    source_kind='official')
add('document_version',id=version,document_id=document,original_url=url,final_url=url,document_date='2026-10-14',
    date_precision='day',date_unknown_reason=None,version_label='TBMM özgün tam tutanağı.',
    accessed_at=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
    mime='application/pdf',sha256=digest,original_path=original,readable_path=readable)
add('source_attribution',version_id=version,publisher='TBMM',author=None,kind='official',published_at=None,
    date_precision='unknown',social_handle=None,public_url=url,basis='Kapakta kurum ve toplantı tarihi.')
selected=(
    ('cover','Toplantı kapağındaki tarih',0,'14 Ekim 2026 Çarşamba'),
    ('ari','Cavit Arı’nın iki teklifin birlikte görüşülmesi çağrısı',6,
     between(6,'Yine bu konuyla ilgili Komisyon üyemiz','birlikte görüşülmesini de ayrıca talep ediyoruz.')),
    ('spk','SPK İkinci Başkanı Ahmet Aksu’nun açılış ve tespit açıklaması',49,
     between(49,'Bir diğer konu da şuydu: Bu Tera portföyü','savunmasını alıyor şirketin.')),
    ('takasbank','Takasbank Genel Müdürü Yunus Arıncı’nın TLY zaman çizgisi',50,
     between(50,'TLY fonu 7 Temmuz 2025 tarihine kadar','cezalar verdi vesaire... Yani süreç bu Sayın Vekilim.')),
    ('takasbank-basis','Takasbank’ın açıklamasında KAP dayanağı',50,'Biz KAP\'ı baz alıyoruz açıkçası.'),
    ('usta','Erhan Usta’nın yaptırım bülteniyle karşılaştırması',51,
     between(51,'Değerli arkadaşlar, bakın şu Sermaye Piyasası Kurulu bülteni.','7/7/2025 tarihinden itibaren işlem görmesi.')),
    ('merge-motion','Başkanın Yeni Parti önergesini tanıtması ve dört imza',55,
     between(55,'Şimdi, Yeni Partinin birleştirme önergesi vardır','Ahmet Vehbi Bakırlıoğlu\nManisa')),
    ('karabat','Özgür Karabat’ın raporlama ve bağımsız denetim gerekçesi',55,
     between(55,'Örneğin, burada raporlama, bağımsız denetim','iki kanun metninin birleştirerek görüşülmesini öneriyoruz.')),
    ('merge-result','Birleştirme önergesinin oylaması',55,
     between(55,'BAŞKAN MEHMET MUŞ - Önergeyi oylarınıza sunuyorum','Alt komisyon önergesini işleme alacağım.')),
    ('subcommission','Ayrı alt komisyon önergesi ve oylaması',55,
     between(55,'Alt komisyon önergesini işleme alacağım.','Önerge kabul edilmemiştir.')),
    ('result','Komisyonun 2/3939 teklifinin tümü hakkındaki sonucu',101,
     'Teklifin tümünü oylarınıza sunuyorum: Kabul edenler... Etmeyenler... Kabul edilmiştir.'),
)
for suffix,section,page,exact in selected:
    assert exact in pdf_page_text(root/original,page),suffix
    add('passage',id=document+'-'+suffix,version_id=version,exact=exact,prefix=None,suffix=None,article=None,
        section=section,pdf_page_index=page,printed_page=str(page+1))
with (checks/'fund-commission-source-records.json').open('x') as stream:
    stream.write(json.dumps(dict(party_id='yeni-parti',entries=entries),ensure_ascii=False,indent=2)+'\n')
print(len(entries),root/original,root/readable)
