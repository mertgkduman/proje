"""Archive the signed 10/4343 motion and the distinct same-day vote."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/yeni-yol')
now=datetime.now(timezone.utc).isoformat()
entries,paths=[],set()


def add(table,**row):
    entries.append(dict(kind=table,values=row))


def save(relative,raw):
    p=root/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        assert p.read_bytes()==raw
    else:
        p.write_bytes(raw)
    paths.add(p)


day='2026-07-01'
assets=(
    ('signed.pdf','signed','10/4343 imzalı Meclis araştırması önergesi',day,
    'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T10/WebOnergeMetni/06aaf0d8-d39d-4d78-a1ad-769d5761c35f.pdf',
    '8d817fa6cc09c5b7bda2b48dd5d8b9eebb323032645877b53ea475599ce4016d',[
        ('id','İlk sayfada esas numarası',0,None,'10/4343'),
        ('concern','İkinci sayfada küçük yatırımcının korunması gerekçesi',1,None,
         'küçük yatırımcının kronik sorunlarına da işaret etmektedir.'),
        ('objective','Üçüncü sayfada yatırımcı tazmini ve araştırma çağrısı',2,None,
         'Yatırımcı tazmin mekanizmalarının güçlendirilmesi'),
        ('signature','Dördüncü sayfada ilk imza sahibinin adı',3,None,'SADULLAH KISACIK'),
    ]),
    ('plenary.pdf','floor','108. Birleşim basılı Genel Kurul tutanağı',day,
    'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/108/Basilmis/8c78bb73-5fa2-43ca-965a-aa0deaac261e.pdf',
    '64997aaa954056faaeea620b8d5519d03f44b5269922388a8c9340560369fa79',[
        ('authority','Kısacık’ın Yeni Yol grup konuşması',81,'980','YENİ YOL GRUBU ADINA SADULLAH KISACIK (Adana)'),
        ('agenda','Bülent Kaya’nın aynı gün görüşme önerisi',81,'980',
         'görüşmelerin 1/7/2026 Çarşamba günkü birleşimde yapılması önerilmiştir.'),
        ('goal','Kısacık’ın araştırma komisyonu çağrısı',82,'981',
         'bir araştırma komisyonu kurulmasını yüce Meclisin takdirlerine sunuyor'),
        ('iyi-role','Ayyüce Türkeş Taş’ın İYİ Parti Grup sıfatı',83,'982',
         'İYİ PARTİ GRUBU ADINA AYYÜCE TÜRKEŞ TAŞ (Adana)'),
        ('iyi-support','Taş’ın sözlü desteği',83,'982','kesinlikle destekliyoruz.'),
        ('dem-role','İbrahim Akın’ın DEM Parti Grup sıfatı',83,'982',
         'DEM PARTİ GRUBU ADINA İBRAHİM AKIN (İzmir)'),
        ('dem-support','Akın’ın sözlü desteği',84,'983','desteklemek gerektiğini düşünüyorum.'),
        ('quorum1','3. oturum ilk karar yeter sayısı açıklaması',87,'986',
         'BAŞKAN - Karar yeter sayısı yoktur.'),
        ('quorum2','4. oturum ikinci karar yeter sayısı açıklaması',88,'987',
         'BAŞKAN - Karar yeter sayısı yoktur.'),
        ('decision','5. oturum üçüncü elektronik oylama ve başkanın ilanı',89,'988',
         '(Elektronik cihazla oylama yapıldı)\nBAŞKAN - Öneri kabul edilmemiştir, karar yeter sayısı vardır.'),
    ]),
    ('detail.html','detail','TBMM 10/4343 esas kaydı',None,
    'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/0ebca8bc-932a-4ca1-ad49-019f6a25dc7a',
    '6a86c9117cdd11636a702a8f6da45f3a1214e76d94694b8c900093e7644370cd',[
        ('id','Esas numarası',None,None,'<td>10 / 4343</td>'),
        ('filed','Başkanlığa geliş tarihi',None,None,'<td>01/07/2026</td>'),
        ('pending','Erişim anındaki esas dosyası durumu',None,None,'<td>G&#xFC;ndemde</td>'),
    ]),
    ('summary.html','summary','108. Birleşim Genel Kurul özeti',day,
    'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/108/Ozet/faeaec55-ce05-4a4d-8f4c-9ccb14e1d284.html',
    '28a4680a696490574a67fd3a9839b142c1402631b553bbad1d2d68daf0ec6eaf',[
        ('result','Özette aynı gün görüşme önerileri',None,None,'yapılan görüşmelerden sonra kabul edilmedi.'),
    ]),
    ('oct07.html','oct07','7 Ekim 2026 Genel Kurul tam tutanağı','2026-10-07',
    'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/3/Tam/5e3c67e6-7f96-4c37-9401-393802259f00.html',
    '248d35a6070a1858effe9173b47f9a2824c090fa85f74fa1fb5ae2eab6631a1c',[
        ('role','Bülent Kaya’nın Yeni Yol grup sıfatı',None,None,'YENİ YOL GRUBU ADINA BÜLENT KAYA (İstanbul)'),
        ('plan','Kaya’nın fon işlemleri için araştırma komisyonu çağrısı',None,None,
         'kurulacak bir araştırma komisyonunda mutlaka ve mutlaka ortaya koymalı.'),
        ('followup','Kaya’nın komisyon talebini sürdüreceği açıklaması',None,None,
         'bu konudaki taleplerimize devam edeceğimizi ifade ediyor'),
    ]),
)
for filename,key,title,date,url,h,specs in assets:
    source=stage/filename
    raw=source.read_bytes()
    assert sha256(raw).hexdigest()==h
    pdf=filename.endswith('.pdf')
    doc='0408-fund-july-'+key
    vid=doc+'-v1'
    original=f'objects/{h}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{h}/readable.html'
    save(original,raw)
    common=Path('data/practices/sources/dem')/readable
    save(readable,common.read_bytes() if key in ('floor','oct07') and common.is_file() else readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='yeni-yol',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'TBMM işlem dosyası ilk yayın günü açıklamıyor.',
        version_label='TBMM özgün belgesi.',accessed_at=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=h,
        original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',
        published_at=None,date_precision='unknown',social_handle=None,public_url=url,
        basis='TBMM birleşim ve evrak kimlikleri asıl belgede okundu.')
    if not pdf:
        charset='windows-1254' if key in ('summary','oct07') else None
        view=build_view(raw,url,root,fetch_assets=False,http_charset=charset)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/f for f in json.loads(manifest.read_bytes())['files'])
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
    for suffix,section,page,printed,exact in specs:
        body=pdf_page_text(root/original,page) if pdf else html_source_text(raw)
        manual=not body.strip() and pdf
        assert manual or exact in body,(key,suffix)
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,
            pdf_page_index=page,printed_page=printed)
        if manual:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='PDF özgün sayfası Poppler görüntüsünde okundu.',
                reason='Özgün sayfanın metin katmanı boş. Kısa alıntı görselden doğrulandı.')
(checks/'fund-july-source-records.json').write_text(json.dumps(dict(party_id='yeni-yol',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
