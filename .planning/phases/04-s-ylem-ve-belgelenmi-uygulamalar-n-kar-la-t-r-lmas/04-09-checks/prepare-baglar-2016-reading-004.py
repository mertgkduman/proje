import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import pdf_page_text
c=Path(__file__).resolve().parent
pdf=c/'baglar-2016-original.pdf'
assert hashlib.sha256(pdf.read_bytes()).hexdigest()=='8364a09ace89fc806e5d65ea578e6eef8054bcaf54f3d41ddf9c7c5e298ffca1'
notes={
19:'2016/17, 6 Ocak: 234 parselde akaryakıt LPG CNG istasyonu için 1/1000 plan değişikliği komisyon raporu meclisçe mevcutların oybirliğiyle kabul edildi. Belirtilen üst ölçekli 2015/551 kararının aslı, onaylı plan ve uygulama ayrı.',
20:'2016/18, 6 Ocak: çevre ve sağlık komisyonu 447 gıda tüketim noktasını denetlediğini, uygunsuz ürünlerin ele geçirilip imha edildiğini ve kimi işyerlerine yasal işlem yapıldığını aktarır; meclis raporu oybirliğiyle kabul etti. Denetim tarihi, tekil tutanaklar, yaptırımlar ve sayı dökümü bağımsız belgelenmedi; önerilen eğitim ve bildirimlerin gerçekleşmesi gösterilmez.',
21:'2016/19, 7 Ocak: kadın-erkek eşitlik komisyonu 5 Nisan Mahallesinde ağırlığı erkek görüşmecilerin çatışma, istihdam, madde kullanımı ve temizlik hakkındaki aktarımlarını raporladı; rapor kabul edildi. Yakınmalar komisyonca aktarılan görüşlerdir, ruhsat iptali veya çözüm kararı gösterilmez.',
22:'2016/20, 7 Ocak: halkla ilişkiler komisyonu Kardelen Kadın Evi-1 danışmanlıkları, grup çalışmaları ve seminerlerinden söz eder, meclis raporu oybirliğiyle kabul eder. Mevcut 2015/214 eğitim raporu ve kadın konukevi kaydıyla farklı tarih ve ayrı karar; bireysel yararlanma, hizmetin başlama tarihi ve sonraki sürekliliği açık.',
23:'2016/21, 7 Ocak: kadın sorunları komisyonu Alipınar kadınlarının pazar, aydınlatma, istihdam ve madde bağımlılığıyla ilgili istek ve anlatılarını raporladı. Meclisin raporu kabulü istenen pazarın kurulması veya hizmetlerin yerine getirilmesi değildir.',
24:'2016/22, 7 Ocak: kültür komisyonu Yunus Emrede yaklaşık 40 çocukla sokak/duvar boyama, basket potası ve top verildiğini aktarır; başka mahallelerde devam önerilir, rapor oybirliğiyle kabul edildi. Etkinliğin kesin günü ve gelecekteki uygulama ayrı.',
25:'2016/23, 7 Ocak: iki meclis üyesinin önergesi üzerine 18 parkın eski ve yeni adları komisyon raporunda listelenir; rapor ve ardından meclis kabulü ayrı oybirlikleri olarak kaydedilir. İsimlerin sahada değiştirilmesi veya tüm üyelerin partileri karardan çıkmaz.',
26:'2016/24, 8 Ocak: Bağcılar yeni imar yollarının incelenmesi önergesi imar komisyonuna sevk edildi; nihai karar ve yol yapımı gösterilmez.',
27:'2016/25, 8 Ocak: Fatih Mahallesinde çocuklara sokak boyaması önergesi kültür komisyonuna sevk edildi; önceki Yunus Emre etkinliği ayrı, Fatih etkinliğinin yapılması açık.',
28:'2016/26, 8 Ocak: gezici pazarlarda çalışan kadınların sorunlarının incelenmesi önergesi kadın-erkek eşitlik komisyonuna sevk edildi; araştırmanın tamamlanması veya alınmış tedbir ayrı.'}
pages=[]
for i,note in notes.items():
 text=pdf_page_text(str(pdf),i); pages.append({'pdf_page_index':i,'source_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'text_characters':len(text),'reading':note})
out={'reviewer_kind':'agent','checked_at':'2026-11-24','source_url':'https://www.baglar.bel.tr/Content/uploads/650ee114-c24f-482a-b241-4a4036f5aff2.pdf','original_path':str(pdf),'original_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages_total':252,'reading_method':'Sıfır tabanlı 19–28 PDF indekslerinin Poppler metin katmanı sırayla tamamen okundu. Bu makbuzda görsel kontrol yapılmadı.','text_characters_read':sum(x['text_characters'] for x in pages),'pages':pages,'limits':['Kararlar belediye meclisi işlemleridir; parti direktifi, parti grubu kararı veya belirsiz kişisel oy olarak sunulmaz.','Komisyon anlatısı, raporun kabulü, fiilî faaliyet ve bireysel sonuçlar birbirinden ayrıdır; parti ve belediye yetkisi karıştırılmaz.','29 ve sonraki PDF indeksleri okunmadı; tüm kapsam kapanmadı.'],'next_leads':['29 indeksinden sırayla devam.','2016/20 Kardelen raporunu önceki 2015/214 ve konukevi kayıtlarıyla mükerrerlik ve özgül ek bilgi açısından karşılaştır.','2016/18 için denetim tutanakları ve 2016/23 için uygulama belgeleri ayrı aranabilir.'],'closure_refs':[]}
with (c/'baglar-council-2016-reading-004.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('DBP_BAGLAR_2016_READING_004_OK',len(pages),out['text_characters_read'])
