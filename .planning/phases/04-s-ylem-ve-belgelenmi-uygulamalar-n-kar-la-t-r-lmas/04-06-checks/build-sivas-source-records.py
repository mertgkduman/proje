"""İki ayrı Sivas dosyası ve 104. birleşim pasajları için DEM kaynakları."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text, pdf_page_text

c = Path(__file__).resolve().parent
root = c.parents[3]
source = root / 'data/practices/sources/dem'
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
floor_sha = '84c36043d410905c0227bc2ed17339ecd2fbc94fe0a58c6d0f40ea5afe57a679'
floor = html_source_text((source/'objects'/floor_sha/'original.html.bin').read_bytes())
items = {
    '2880': ('d1daa28a-b3d8-4931-9ff2-0197d0c87865', 'bec28cfdde2e71b7a30092a382e68b46c1c1465177e6e1adb7bf50635d7df0e9', '1088ac64-4a0e-4cec-8c09-42a4798b285c', '006514177494ce36425199898bf6f7808e76ff157bf3e0a839e9e529aaeae0c9'),
    '2883': ('0478e3f8-6442-4936-bb9d-0197d0d5c671', '849d68838d8cf068fe4be63bbed167aceebe02befbc263925027a03c2f66e5a7', '9bea65b6-eaac-4531-881c-b19edeb41044', '3160f2199192d8f80d1108b25f015331928b0e562d8b8e072d90cbe63e836255'),
}
entries = []
def entry(kind, **v): entries.append(dict(kind=kind, values=v))
def passage(ident, version, exact, section, index=None):
    entry('passage', id=ident, version_id=version, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=index, printed_page=None)
for num, (regid, regsha, pdfid, pdfsha) in items.items():
    prefix = '0406-sivas-'+num+'-'
    regurl = 'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/'+regid
    pdfurl = 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/'+pdfid+'.pdf'
    capture = json.loads((c/('sivas-'+num+'-detail-capture.json')).read_text())[0]
    for suffix, sha, url, mime, filename in [('register',regsha,regurl,'text/html','original.html.bin'),('signed',pdfsha,pdfurl,'application/pdf','original.pdf')]:
        doc=prefix+suffix; version=doc+'-v1'; path=source/'objects'/sha/filename
        assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
        entry('document', id=doc, party_id='dem', title='TBMM '+num+(' esas sicili' if suffix=='register' else ' imzalı önerge'), source_kind='official')
        entry('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date='2025-07-02', date_precision='day', date_unknown_reason=None, version_label='2 Temmuz 2025 TBMM işlemi', accessed_at=now, verified_at=now, mime=mime, sha256=sha, original_path='objects/'+sha+'/'+filename, readable_path='objects/'+sha+'/readable.html')
        if suffix=='register':
            view=dict(capture['view']); view['version_id']=version; entry('archive_view', **view)
            raw=html_source_text(path.read_bytes())
            for name, exact in [('number','10 / '+num),('date','02/07/2025'),('status','G&#xFC;ndemde')]:
                assert exact in raw
                passage(prefix+'register-'+name, version, exact, 'TBMM esas kaydı '+name)
        else:
            assert '10/'+num in pdf_page_text(path,0)
            passage(prefix+'signed-number',version,'10/'+num,'İmzalı dosya esas numarası',0)
    if num=='2880':
        extracts=[('floor-call','2 Temmuz 2025 tarihinde Kars Milletvekili Grup Başkan Vekili Gülüstan Kılıç Koçyiğit ve Muş Milletvekili Grup Başkan Vekili Sezai Temelli tarafından, Sivas katliamının tüm boyutlarıyla araştırılması amacıyla Türkiye Büyük Millet Meclisine verilmiş olan -12618 grup numaralı- Meclis araştırması önergesinin','DEM Sivas önergesini veren grup başkanvekilleri'),('floor-role','DEM PARTİ GRUBU ADINA ONUR DÜŞÜNMEZ (Hakkâri)','DEM grubu adına konuşmacı'),('floor-speech','Bu Meclis bir ülkenin kendi karanlığıyla yüzleşmesine öncülük edebilir.','DEM grubu adına araştırmanın gerekçesi'),('floor-no-quorum','Karar yeter sayısı yoktur.','İlk oylamada karar yeter sayısı yokluğu'),('floor-retry','BAŞKAN - Önerge kabul edilmemiştir, karar yeter sayısı vardır.','İkinci oylamanın sonucu')]
    else:
        extracts=[('floor-call','1263 sıra no.lu Meclis araştırması önergesinin','CHP grup önerisinin gündem talebi'),('floor-role','DEM PARTİ GRUBU ADINA SEVİLAY ÇELENK (Diyarbakır)','DEM grubu adına konuşmacı'),('floor-speech','hiçbirinden vazgeçmeden farklı inançlara hatta inançsızlığa, din ve dünya görüşlerine saygı','DEM grup konuşmasında inançlara saygı'),('floor-retry','BAŞKAN - Cumhuriyet Halk Partisi grup önerisini oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Öneri kabul edilmemiştir.','CHP grup önerisinin sonucu')]
    for name,exact,section in extracts:
        assert exact in floor,(num,name)
        passage(prefix+name,'0406-iklim-final-floor-v1',exact,section)
(c/'sivas-2880-2883-source-records.json').write_text(json.dumps({'party_id':'dem','entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('SIVAS_SOURCE_RECORDS_OK',len(entries))
