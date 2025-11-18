# MinimalERP - Hızlı Başlangıç Kılavuzu

## 🎯 Hoş Geldiniz!

MinimalERP'yi seçtiğiniz için teşekkür ederiz! Bu kılavuz, sistemi 30 dakikada çalıştırmanıza yardımcı olacak.

## 📋 Gereksinimler

Başlamadan önce sisteminizde bunların yüklü olduğundan emin olun:

- ✅ Python 3.11 veya üzeri
- ✅ PostgreSQL 15 veya üzeri
- ✅ Redis 7 veya üzeri
- ✅ Git

## 🚀 5 Adımda Kurulum

### Adım 1: Projeyi İndirin

```bash
# Git ile klonlayın
git clone https://github.com/minimalerp/minimalerp.git
cd minimalerp

# Veya ZIP olarak indirip çıkartın
```

### Adım 2: Virtual Environment Oluşturun

```bash
# Virtual environment oluştur
python -m venv venv

# Aktif et (Linux/Mac)
source venv/bin/activate

# Aktif et (Windows)
venv\Scripts\activate
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
# Production bağımlılıkları
pip install -r requirements.txt

# (Opsiyonel) Development bağımlılıkları
pip install -r requirements-dev.txt
```

### Adım 4: Veritabanını Hazırlayın

```bash
# PostgreSQL'de veritabanı oluşturun
createdb minimalerp

# Veya psql ile:
psql -U postgres
CREATE DATABASE minimalerp;
\q
```

### Adım 5: Yapılandırma

```bash
# .env dosyasını kopyalayın
cp .env.example .env

# .env dosyasını düzenleyin
nano .env  # veya tercih ettiğiniz editör

# Minimum gerekli ayarlar:
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/minimalerp
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-32-character-secret-key-here
```

## ▶️ Uygulamayı Başlatın

### Geliştirme Modu

```bash
# Backend'i başlatın
python core/main.py

# Veya uvicorn ile:
uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
```

### Tarayıcıda Açın

```
http://localhost:8000
```

API Dokümantasyonu:
```
http://localhost:8000/docs
```

## 🐳 Docker ile Kurulum (Önerilen)

Daha kolay kurulum için Docker kullanabilirsiniz:

```bash
# Tüm servisleri başlatın
docker-compose up -d

# Logları izleyin
docker-compose logs -f

# Durdurma
docker-compose down
```

Servisler:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Flower (Celery): http://localhost:5555
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 🎨 İlk Kullanıcıyı Oluşturun

```bash
# Management komutu ile
python manage.py createsuperuser

# Bilgileri girin:
Email: admin@sirketiniz.com
Şifre: ********
Şifre (tekrar): ********

✅ Süper kullanıcı oluşturuldu!
```

## 🏢 Şirket Bilgilerini Girin

İlk girişten sonra:

1. **Dashboard** → **Ayarlar** → **Şirket Bilgileri**
2. Zorunlu alanları doldurun:
   - Şirket adı
   - Vergi numarası
   - Vergi dairesi
   - Adres bilgileri
3. **Kaydet**

## 🔧 GİB Entegrasyonu (e-Fatura)

e-Fatura kullanacaksanız:

1. **Ayarlar** → **Entegrasyonlar** → **GİB**
2. GİB kullanıcı bilgilerinizi girin:
   - Kullanıcı adı
   - Şifre
   - Ortam: Test / Canlı
3. **Bağlantıyı Test Et**
4. ✅ Bağlantı başarılı ise **Kaydet**

## 📚 Sonraki Adımlar

### 1. Cari Hesapları Ekleyin

**Muhasebe** → **Cari Hesaplar** → **Yeni Ekle**

- Müşterilerinizi ekleyin
- Tedarikçilerinizi ekleyin

### 2. Ürünleri Tanımlayın

**Stok** → **Ürünler** → **Yeni Ürün**

- Ürün bilgileri
- Barkod (varsa)
- KDV oranı

### 3. İlk Faturanızı Oluşturun

**Muhasebe** → **Faturalar** → **Yeni Fatura**

- Cari hesap seçin
- Ürünleri ekleyin
- Kaydet ve GİB'e gönder

### 4. AI Özelliklerini Aktif Edin

**Ayarlar** → **AI Özellikleri**

- ✅ Nakit Akışı Tahmini
- ✅ Satış Tahminleme
- ✅ Anomali Tespiti
- ✅ OCR (Belge Okuma)

### 5. İlk OCR Denemesi

**Muhasebe** → **Faturalar** → **Belge Yükle**

1. Fatura fotoğrafı/PDF yükleyin
2. AI otomatik okuyacak
3. Kontrol edin ve kaydedin

## 🆘 Sorun Giderme

### PostgreSQL bağlanamıyor

```bash
# PostgreSQL çalışıyor mu?
sudo systemctl status postgresql

# Başlat
sudo systemctl start postgresql

# Kullanıcı şifresini sıfırla
sudo -u postgres psql
ALTER USER postgres PASSWORD 'yeni_sifre';
```

### Redis bağlanamıyor

```bash
# Redis çalışıyor mu?
sudo systemctl status redis

# Başlat
sudo systemctl start redis
```

### Port zaten kullanımda

```bash
# 8000 portunu kullanan programı bul
lsof -i :8000

# Süreci sonlandır
kill -9 <PID>
```

### Bağımlılık hataları

```bash
# Önbelleği temizle ve yeniden yükle
pip cache purge
pip install --no-cache-dir -r requirements.txt
```

## 📞 Yardım ve Destek

### Dokümantasyon
- 📖 [Tam Dokümantasyon](docs/)
- 🎥 [Video Tutorials](https://youtube.com/@minimalerp)
- 💬 [Forum](https://forum.minimalerp.com.tr)

### Topluluk
- Discord: https://discord.gg/minimalerp
- GitHub Issues: https://github.com/minimalerp/minimalerp/issues

### Profesyonel Destek
- 📧 Email: support@minimalerp.com.tr
- 📞 Telefon: 0850 XXX XX XX (9:00-18:00)
- 💬 Canlı Chat: https://minimalerp.com.tr

## ✅ Kontrol Listesi

İlk kurulum tamamlandığında:

- [ ] Uygulama çalışıyor (http://localhost:8000)
- [ ] Süper kullanıcı oluşturuldu
- [ ] Şirket bilgileri girildi
- [ ] En az 1 cari hesap eklendi
- [ ] En az 1 ürün tanımlandı
- [ ] İlk fatura oluşturuldu
- [ ] AI özellikleri test edildi

## 🎉 Tebrikler!

MinimalERP'yi başarıyla kurdunuz! Artık AI destekli akıllı iş yönetimi yapabilirsiniz.

**Mutlu kullanımlar!** 🚀

---

**İpucu:** Demo verisi yüklemek ister misiniz?

```bash
python manage.py loaddata demo_data.json
```

Bu komut örnek müşteriler, ürünler ve faturalar yükler.
