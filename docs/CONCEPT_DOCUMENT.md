# MinimalERP - Proje Konsept ve Tasarım Dokümanı

## 📋 Yönetici Özeti

**MinimalERP**, Türkiye'deki KOBİ'ler için özel olarak tasarlanmış, yapay zeka destekli, minimal ve kullanıcı dostu bir ERP çözümüdür. Odoo'nun modüler yapısından ilham alarak, karmaşıklığı minimumda tutarken AI'ın gücüyle işletmelere gerçek değer katmayı hedefler.

### Temel Farklar

| Özellik | Geleneksel ERP | MinimalERP |
|---------|---------------|------------|
| Modül Sayısı | 50+ modül | 3 temel modül |
| Kurulum Süresi | 3-6 ay | 1 gün |
| Öğrenme Eğrisi | Haftalarca | Saatler |
| AI Entegrasyonu | Ek ücret | Temel özellik |
| Türkiye Uyumu | Ek paket | Standart |
| Maliyeti | 100K+ TL/yıl | 10K TL/yıl |

---

## 🎯 Hedef Kitle

### Birincil Hedef
- 5-50 çalışanlı KOBİ'ler
- Yıllık cirosu 5M-50M TL arası işletmeler
- Toptan/perakende ticaret firmaları
- İmalat ve üretim şirketleri
- Hizmet sektörü işletmeleri

### İkincil Hedef
- Startup'lar (hızlı büyüyen)
- E-ticaret işletmeleri
- Franchise zincirleri

---

## 🏗️ Sistem Mimarisi

### Teknoloji Stack

```
┌─────────────────────────────────────────────────┐
│           Frontend (React/Vue.js)               │
│  - Tailwind CSS + shadcn/ui                     │
│  - Chart.js / Apache ECharts                    │
│  - Responsive & Mobile-first                    │
└─────────────────────────────────────────────────┘
                      ↕ REST API
┌─────────────────────────────────────────────────┐
│           Backend (FastAPI/Python)              │
│  - Authentication & Authorization               │
│  - Business Logic                               │
│  - AI Service Orchestration                     │
└─────────────────────────────────────────────────┘
          ↕                    ↕
┌──────────────────┐  ┌───────────────────────────┐
│   PostgreSQL     │  │    AI/ML Services         │
│   - Main DB      │  │  - OCR (Tesseract+GPT)    │
│   - ACID         │  │  - Forecasting (Prophet)   │
│   - JSON support │  │  - Anomaly (Isolation)     │
└──────────────────┘  │  - Classification (sklearn)│
                      └───────────────────────────┘
          ↕
┌─────────────────────────────────────────────────┐
│              Redis (Cache & Queue)              │
│  - Session management                           │
│  - Celery task queue                            │
│  - Rate limiting                                │
└─────────────────────────────────────────────────┘
          ↕
┌─────────────────────────────────────────────────┐
│         External Integrations                   │
│  - GİB (e-Fatura, e-Arşiv, e-Defter)           │
│  - Turkish Banks                                │
│  - Payment Gateways (PayTR, iyzico)            │
│  - SMS Providers (Netgsm, etc.)                │
└─────────────────────────────────────────────────┘
```

---

## 📦 Modül Detayları

### 1. 💰 AI-Powered Smart Accounting & Finance

#### Temel Fonksiyonlar

**1.1. Genel Muhasebe**
- Tek Düzen Hesap Planı (TDHP) entegrasyonu
- Otomatik yevmiye defteri
- Mizan raporu
- Bilanço ve gelir tablosu
- Çok para birimi desteği

**1.2. e-Dönüşüm Entegrasyonları**
```
GİB Entegrasyonları:
├── e-Fatura (satış/alış)
├── e-Arşiv Fatura
├── e-İrsaliye
├── e-Defter
└── e-Müstahsil Makbuzu
```

**1.3. Cari Hesap Yönetimi**
- Müşteri/Tedarikçi takibi
- Vadeli ödeme yönetimi
- Otomatik mutabakat
- Risk analizi (AI)

#### AI Özellikleri

**🤖 1. Otomatik Belge Tanıma (OCR)**

**Problem:** Fatura ve makbuzların manuel girişi zaman alıcı ve hata yapılması kolay.

**Çözüm:**
```python
# Kullanım senaryosu:
1. Kullanıcı fatura fotoğrafı çeker veya PDF yükler
2. Tesseract OCR ile metin çıkarılır
3. GPT-4 Vision ile yapılandırılmış data elde edilir
4. Otomatik fatura oluşturulur
5. Anomali kontrolü yapılır
```

**Teknik Detay:**
- Tesseract OCR (Türkçe dil desteği)
- OpenAI GPT-4 Vision API
- Confidence score: %95+
- İşlem süresi: ~3-5 saniye/belge

**Örnek Output:**
```json
{
  "invoice_number": "AAA2024000001",
  "invoice_date": "2024-11-12",
  "partner": {
    "name": "ABC Ticaret Ltd. Şti.",
    "tax_number": "1234567890",
    "tax_office": "Kadıköy"
  },
  "lines": [
    {
      "description": "Ürün A",
      "quantity": 10,
      "unit_price": 100.00,
      "vat_rate": 20,
      "total": 1200.00
    }
  ],
  "confidence": 0.97
}
```

**🤖 2. Nakit Akışı Tahmini**

**Problem:** İşletmeler nakit sıkışıklığını öngöremez.

**Çözüm:**
```python
# Model: Facebook Prophet
# Input: Son 12 ay nakit akışı verisi
# Output: 30-90 gün nakit akışı tahmini

Tahmin edilen metrikler:
├── Günlük nakit giriş (gelir)
├── Günlük nakit çıkış (gider)
├── Net nakit akışı
├── Kümülatif bakiye
└── Kritik tarihler (nakit eksilmesi riski)
```

**Görselleştirme:**
```
Nakit Akış Grafiği:
     ↑ (TL)
200K │     ┌───────────┐
150K │   ┌─┘           │
100K │ ┌─┘             └─┐
 50K │─┘                 └──────
   0 └─────────────────────────→
     Nov  Dec  Jan  Feb  (Zaman)

     ─── Gerçekleşen
     ··· Tahmin (güven aralığı ile)
     !   Kritik uyarı noktası
```

**Kullanım Senaryosu:**
1. CFO dashboard'da "Nakit Akışı Tahmini" widget'ı açar
2. 30 gün sonraki durum görüntülenir
3. Kritik tarih 15 gün sonra tespit edilir
4. Sistem otomatik öneri: "20 Aralık'ta 50K TL nakit açığı öngörülüyor. Müşteri tahsilatlarını öne alın."

**🤖 3. Finansal Anomali Tespiti**

**Problem:** Çift girişler, hatalı tutarlar, şüpheli işlemler manuel kontrol gerektirir.

**Çözüm:**
```python
# Model: Isolation Forest
# Anomali türleri:
├── Çift fatura girişi
├── Anormal tutar (örn: 100K yerine 1M)
├── Olağandışı sıklık (günde 100 fatura)
├── Şüpheli cari hareketleri
└── KDV oranı tutarsızlığı
```

**Anomali Skoru:**
```
0.0-0.3: Normal
0.3-0.6: Şüpheli (manuel kontrol)
0.6-1.0: Yüksek risk (otomatik bloke)
```

**Dashboard:**
```
🔴 Yüksek Risk Anomaliler (3)
  └── Fatura #AAA2024000123
      Tutar: 1,250,000 TL (normal: ~50K)
      Skor: 0.87
      Öneri: "Bu tutar normal aralığın 25 katı"

🟡 Orta Risk Anomaliler (7)
🟢 Düşük Risk (12)
```

**🤖 4. Akıllı Kategorizasyon**

**Problem:** Gider ve gelirler manuel kategorize edilir.

**Çözüm:**
```python
# NLP ile otomatik kategorizasyon
# Model: Fine-tuned BERT (Turkish)

Örnek:
"Ankara ofis kira ödemesi" → Kira Giderleri
"Çalışan maaş ödemesi" → Personel Giderleri
"Araç yakıt alımı" → Ulaşım Giderleri
```

---

### 2. 📈 AI-Driven Sales & CRM

#### Temel Fonksiyonlar

**2.1. Müşteri Yönetimi**
- Müşteri profilleri
- İletişim geçmişi
- Segmentasyon
- 360° müşteri görünümü

**2.2. Satış Süreci**
```
Satış Hunisi:
Lead → Fırsat → Teklif → Sipariş → Fatura → Tahsilat
  ↓      ↓       ↓        ↓        ↓         ↓
(AI Scoring) (AI Forecast) (AI Suggestions)
```

**2.3. Teklif Yönetimi**
- Hızlı teklif oluşturma
- Şablon desteği
- E-posta entegrasyonu
- Takip hatırlatmaları

#### AI Özellikleri

**🤖 1. Lead Scoring (Potansiyel Müşteri Puanlama)**

**Problem:** Hangi lead'lere odaklanmalı?

**Çözüm:**
```python
# Model: Random Forest Classifier
# Features:
├── İletişim sıklığı
├── Web site aktivitesi
├── E-posta açılma oranı
├── Sektör/şirket büyüklüğü
├── Teklif talep sayısı
└── Geçmiş etkileşimler

# Skor: 0-100
90-100: Sıcak (hemen ara!)
70-89:  Ilık (haftalık takip)
50-69:  Soğuk (aylık bilgilendirme)
0-49:   Düşük (pazarlama listesi)
```

**Dashboard:**
```
🔥 Sıcak Lead'ler (8)
  └── ABC Holding
      Skor: 94/100
      Kapanma olasılığı: %87
      Tahmini değer: 250K TL
      Önerilen aksiyon: "Bugün ara, demo ayarla"

🌡️ Ilık Lead'ler (23)
❄️ Soğuk Lead'ler (45)
```

**🤖 2. Satış Tahminleme**

**Problem:** Bu ay kaç TL satış yapacağız?

**Çözüm:**
```python
# Model: LSTM (Long Short-Term Memory)
# Input:
├── 12 aylık satış verisi
├── Mevsimsellik faktörleri
├── Açık teklifler
├── Pipeline değeri
└── Ekonomik göstergeler (opsiyonel)

# Output:
├── Gelecek 30/60/90 gün tahmini
├── En iyi/en kötü senaryo
└── Güven aralığı
```

**Görselleştirme:**
```
Satış Tahmin Grafiği:
     ↑ (TL)
600K │           ╱╲
500K │         ╱    ╲
400K │   ╱────╯      ╲
300K │──╯              ╲___
     └─────────────────────→
     Son 3 ay    Tahmin 3 ay

     ─── Gerçekleşen
     ··· Tahmin (optimistik)
     ─ ─ Tahmin (pesimistik)
```

**🤖 3. Otomatik Müşteri İletişimi**

**Problem:** Takip e-postaları unutuluyor.

**Çözüm:**
```python
# Trigger-based automation:

Senaryolar:
├── Teklif gönderildi → 3 gün sonra takip
├── Teklif reddedildi → 1 ay sonra yeni teklif
├── Müşteri 30 gün inaktif → Re-engagement
└── Sipariş teslim edildi → Memnuniyet anketi
```

**Örnek:**
```
📧 Otomatik E-posta (AI-Generated)

Konu: ABC Teklifimiz Hakkında

Sayın [Müşteri],

[Tarih] tarihinde gönderdiğimiz [Ürün] teklifimiz
hakkında görüşlerinizi almak isteriz.

Sorularınız için: ...

[İsim]
[Pozisyon]

---
✏️ AI tarafından oluşturuldu, gönderilmeden önce
düzenleyebilirsiniz.
```

**🤖 4. Ürün Tavsiyeleri (Cross-sell/Up-sell)**

**Problem:** Müşteriye hangi ürünü önereceğiz?

**Çözüm:**
```python
# Model: Collaborative Filtering
# Benzeri müşterilerin satın aldığı ürünler

Örnek:
Müşteri A → Ürün X satın aldı
Benzer müşteriler (B, C, D) → Ürün Y de aldı
Sistem önerisi: "Müşteri A'ya Ürün Y'yi öner"

Conversion rate: %15-25 artış
```

---

### 3. 📦 AI-Optimized Inventory & Stock

#### Temel Fonksiyonlar

**3.1. Stok Takibi**
- Ürün giriş/çıkış
- Barkod okuma
- Seri/lot takibi
- Çoklu depo yönetimi

**3.2. Sayım İşlemleri**
- Periyodik sayım
- Mobil uygulama desteği
- Sayım farkları otomatik düzeltme

#### AI Özellikleri

**🤖 1. Talep Tahmini (Demand Forecasting)**

**Problem:** Hangi üründen ne kadar stoklamalı?

**Çözüm:**
```python
# Model: Prophet + LSTM Hybrid
# Faktörler:
├── Geçmiş satış trendi
├── Mevsimsellik
├── Kampanya etkileri
├── Dış faktörler (tatil günleri)
└── Ekonomik göstergeler

# Output: Gelecek 90 gün talep tahmini
```

**Örnek Rapor:**
```
📦 Ürün: Widget A
───────────────────────────────────
Mevcut stok:        150 adet
30 günlük tahmin:   280 adet
Stok bitim tarihi:  ~16 gün

⚠️ Öneri: 200 adet sipariş verin
   Sipariş tarihi: Bugün
   Teslim süresi: 10 gün
   Risk: Düşük
```

**🤖 2. Otomatik Sipariş Noktası**

**Problem:** Sipariş noktasını manuel hesaplama.

**Çözüm:**
```python
# Dinamik sipariş noktası:
Sipariş noktası = (Günlük satış * Tedarik süresi) + Güvenlik stoğu

# AI optimizasyonu:
├── Günlük satış: AI ile tahmin
├── Tedarik süresi: Geçmiş veriden ortalama
├── Güvenlik stoğu: Risk toleransına göre
└── Sürekli güncelleme (haftalık)
```

**Otomatik Sipariş Akışı:**
```
1. Stok → Sipariş noktası
2. Sistem uyarı oluşturur
3. (Opsiyonel) Otomatik sipariş e-postası
4. Tedarikçi onayı
5. Sipariş takibi
```

**🤖 3. Ölü Stok Tespiti**

**Problem:** Hareket görmeyen stoklar tespit edilemiyor.

**Çözüm:**
```python
# Ölü stok kriterleri:
├── Son 90 günde satış yok
├── Mevcut stok > 6 aylık tahmin
├── Ürün yaşam döngüsü sonu
└── Hasar/eskime riski

# Öneriler:
├── İndirimli satış kampanyası
├── Paketleme (bundle)
├── Tedarikçiye iade
└── Imha (son çare)
```

**Ölü Stok Raporu:**
```
📊 Ölü Stok Analizi
───────────────────────────────────
Toplam stok değeri:    1,250,000 TL
Ölü stok değeri:         125,000 TL (10%)

🔴 Kritik (>6 ay):      45,000 TL (15 ürün)
🟡 Risk (3-6 ay):       80,000 TL (32 ürün)

💡 Öneriler:
1. Ürün X'de %30 kampanya → ~25K kurtarma
2. Ürün Y + Z paketi → Bundle fırsatı
```

**🤖 4. Depo Optimizasyonu**

**Problem:** Sık satılan ürünler uzak raflarda.

**Çözüm:**
```python
# ABC Analizi + AI:
A sınıfı (yüksek ciro, %20 ürün, %80 gelir)
  → En erişilebilir raflar

B sınıfı (orta ciro, %30 ürün, %15 gelir)
  → Orta erişilebilirlik

C sınıfı (düşük ciro, %50 ürün, %5 gelir)
  → Arka raflar

# Dinamik: Aylık güncelleme
```

---

## 🇹🇷 Türkiye'ye Özel Entegrasyonlar

### 1. GİB (Gelir İdaresi Başkanlığı) Entegrasyonları

#### e-Fatura Sistemi

**Akış:**
```
MinimalERP → GİB SOAP API → e-Fatura Platformu

Adımlar:
1. Fatura oluştur (MinimalERP)
2. UBL-TR formatına çevir
3. Dijital imzala
4. GİB'e gönder (SOAP)
5. Onay bekle
6. Durum güncelle
```

**Desteklenen İşlemler:**
- Fatura gönderimi
- Fatura sorgulama
- Yanıt alma
- İptal/düzeltme
- Toplu gönderim

#### e-Arşiv Fatura

```
Kullanım senaryosu:
- Perakende satışlar
- e-Fatura mükellefi olmayan alıcılar
- GİB'e raporlama
```

#### e-Defter

```
Otomatik e-Defter oluşturma:
├── Yevmiye defteri
├── Büyük defter
├── Envanter defteri
└── Aylık özet
```

### 2. Türk Bankaları Entegrasyonu

**Desteklenen Bankalar:**
```
├── Garanti BBVA
├── İş Bankası
├── Yapı Kredi
├── Akbank
├── Ziraat Bankası
└── (Diğerleri ekleniyor...)
```

**Özellikler:**
- Otomatik banka ekstresi çekme
- IBAN doğrulama
- Havale/EFT gönderimi
- Ödeme takibi
- Mutabakat

### 3. Ödeme Sistemleri

**PayTR:**
- Sanal POS
- 3D Secure
- Taksit seçenekleri

**iyzico:**
- Alt işyeri yönetimi
- Marketplace desteği

### 4. KDV ve Vergi Hesaplamaları

**KDV Oranları:**
```python
KDV_ORANLARI = {
    "STANDART": 20,
    "INDIRIMLI_1": 10,
    "INDIRIMLI_2": 1,
    "MUAF": 0
}
```

**Tevkifat:**
```python
TEVKIFAT_ORANLARI = {
    "MAL": {"oran": 2, "kdv_oran": 10},
    "HIZMET": {"oran": 5, "kdv_oran": 10},
    # ...
}
```

---

## 🔒 Güvenlik ve KVKK Uyumu

### Veri Güvenliği

**1. Şifreleme:**
```
- Database: AES-256
- Transit: TLS 1.3
- Hassas alanlar: Fernet (symmetric)
```

**2. Kimlik Doğrulama:**
```
- JWT tokens
- 2FA (SMS/Email)
- SSO desteği (opsiyonel)
- IP kısıtlama
```

**3. Yetkilendirme:**
```
Role-Based Access Control (RBAC):
├── Admin (tam yetki)
├── Finans Müdürü
├── Satış Müdürü
├── Depo Sorumlusu
└── Kullanıcı (sınırlı)
```

### KVKK (Kişisel Verilerin Korunması)

**1. Audit Log:**
```sql
-- Her işlem loglanır:
- Kim?
- Ne yaptı?
- Ne zaman?
- Hangi IP'den?
- Eski/yeni değer
```

**2. Veri Saklama:**
```
- Otomatik arşivleme (10 yıl)
- Silme talepleri (KVKK hakkı)
- Anonimleştirme
```

**3. Raporlama:**
```
- Veri işleme envanteri
- KVKK uyum raporu
- Veri ihlali bildirimi
```

---

## 📱 Kullanıcı Arayüzü ve UX

### Dashboard Tasarımı

```
┌─────────────────────────────────────────────────┐
│  MinimalERP            🔔 (3)   👤 Ahmet Yılmaz │
├─────────────────────────────────────────────────┤
│                                                  │
│  💰 Bugünkü Finansal Durum                      │
│  ┌──────────────┬──────────────┬──────────────┐│
│  │  Nakit       │  Alacak      │  Borç        ││
│  │  125,450 TL  │  89,200 TL   │  45,300 TL   ││
│  └──────────────┴──────────────┴──────────────┘│
│                                                  │
│  📊 30 Günlük Nakit Akış Tahmini (AI)           │
│  [Grafik]                                        │
│  ⚠️ 15 gün sonra 50K nakit açığı riski          │
│                                                  │
│  🔥 Bugün Yapılacaklar                          │
│  □ 3 fatura onayı bekliyor                      │
│  □ 5 sıcak lead takip edilmeli                  │
│  □ 2 ürün kritik stok seviyesinde               │
│                                                  │
│  🤖 AI Önerileri                                │
│  💡 ABC Müşteri'den tahsilat yapın (vadesi geçti)│
│  💡 XYZ Ürününde stok yenileyin (10 gün kaldı)  │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Mobil Uygulama

```
Temel özellikler:
├── Fatura fotoğrafı çekme (OCR)
├── Stok sayımı (barkod okuyucu)
├── Müşteri görüşme notları
├── Onay işlemleri
└── Dashboard görüntüleme
```

---

## 🚀 Deployment ve Kurulum

### Kurulum Seçenekleri

**1. SaaS (Önerilen):**
```
- URL: https://minimalerp.com.tr
- Hazır kullanım
- Otomatik güncellemeler
- 99.9% uptime garantisi
```

**2. Self-Hosted (Docker):**
```bash
docker-compose up -d
```

**3. Kubernetes:**
```bash
helm install minimalerp ./charts/minimalerp
```

### Sistem Gereksinimleri

**Minimum:**
- CPU: 2 vCPU
- RAM: 4 GB
- Disk: 20 GB SSD
- PostgreSQL 15+
- Redis 7+

**Önerilen (100 kullanıcı):**
- CPU: 8 vCPU
- RAM: 16 GB
- Disk: 100 GB SSD
- Load balancer
- Database replika

---

## 💰 Fiyatlandırma Modeli

### SaaS Planlar

| Plan | Aylık (TL) | Kullanıcı | Modül | AI Özellik |
|------|------------|-----------|-------|------------|
| **Başlangıç** | 999 | 3 | Temel | Sınırlı |
| **Profesyonel** | 2,999 | 10 | Tümü | Tam |
| **Kurumsal** | Özel | Sınırsız | Tümü + Özel | Tam + Özel |

### Self-Hosted Lisans

```
One-time lisans: 50,000 TL
- Sınırsız kullanıcı
- Kaynak kod erişimi
- 1 yıl destek
```

---

## 📈 Yol Haritası

### Faz 1: MVP (3 ay)
- [x] Core framework
- [x] Accounting modülü (temel)
- [ ] OCR entegrasyonu
- [ ] e-Fatura entegrasyonu
- [ ] Beta test

### Faz 2: AI Özellikleri (3 ay)
- [ ] Nakit akışı tahmini
- [ ] Satış tahminleme
- [ ] Anomali tespiti
- [ ] Lead scoring

### Faz 3: Genişleme (6 ay)
- [ ] Mobil uygulama
- [ ] İleri raporlama
- [ ] API marketplace
- [ ] Entegrasyon ekosistemi

### Faz 4: Ölçeklendirme (devam ediyor)
- [ ] Çok şirket desteği
- [ ] Multi-tenant SaaS
- [ ] Enterprise özellikleri
- [ ] Uluslararası pazar

---

## 🎓 Eğitim ve Destek

### Dokümantasyon
- Kullanıcı kılavuzu
- Video tutorials
- API referansı
- Best practices

### Destek Kanalları
- 📧 Email: support@minimalerp.com.tr
- 💬 Canlı chat (9-18)
- 📞 Telefon: 0850 XXX XX XX
- 🎫 Ticket sistemi

### Eğitim Programı
- Online eğitim (ücretsiz)
- Yerinde eğitim (opsiyonel)
- Sertifikasyon programı

---

## 🏆 Rekabet Avantajları

### vs Odoo
```
✅ Daha basit (3 modül vs 50+)
✅ AI-first yaklaşım
✅ Türkiye'ye özel (hazır)
✅ Daha uygun fiyat
⚠️ Daha az özelleştirme
```

### vs SAP Business One
```
✅ 10x daha ucuz
✅ Kolay kurulum
✅ Modern arayüz
✅ AI özellikleri
⚠️ Daha az enterprise özellik
```

### vs Paraşüt
```
✅ Daha kapsamlı (CRM+Stok)
✅ AI özellikleri
✅ Self-hosted seçenek
⚠️ Yeni (daha az track record)
```

---

## 📊 Başarı Metrikleri

### Teknik Metrikler
- Response time: <200ms (P95)
- Uptime: 99.9%
- AI model accuracy: >90%
- OCR success rate: >95%

### İş Metrikleri
- Fatura girişi: 70% hız artışı
- Anomali tespiti: 85% doğruluk
- Nakit akışı tahmini: ±10% hassasiyet
- Lead conversion: +25%

---

## 🤝 Topluluk ve Katkı

### Açık Kaynak Modeli
```
Core: Açık kaynak (MIT)
AI Models: Açık kaynak
Enterprise: Proprietary
```

### Katkıda Bulunma
- GitHub: github.com/minimalerp/minimalerp
- Discord: discord.gg/minimalerp
- Forum: forum.minimalerp.com.tr

---

## 📝 Sonuç

MinimalERP, Türk KOBİ'lerinin karmaşık ERP sistemlerinden kurtularak, minimal ama güçlü bir çözüme geçişini sağlar. AI entegrasyonu ile rutin işleri otomatikleştirirken, Türkiye'ye özel yasal gereksinimleri karşılar.

**Hedef:** 2025 sonunda 1,000 aktif şirket, 2026 sonunda 10,000 şirket.

---

**Son Güncelleme:** 12 Kasım 2024
**Versiyon:** 1.0
**Hazırlayan:** MinimalERP Team
