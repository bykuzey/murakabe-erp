# GitHub Repository Kurulum Rehberi

## 🚀 Adım 1: GitHub'da Repository Oluşturma

### Yöntem 1: GitHub Web Arayüzü (Önerilen)

1. GitHub.com'a giriş yapın
2. Sağ üst köşedeki **"+"** butonuna tıklayın
3. **"New repository"** seçeneğini seçin
4. Repository bilgilerini doldurun:
   - **Repository name**: `murakabe-erp` (veya istediğiniz isim)
   - **Description**: `Murakabe AI - Yapay Zeka Destekli İşletme Yönetim Platformu`
   - **Visibility**: Public veya Private seçin
   - **⚠️ ÖNEMLİ**: "Initialize this repository with a README" seçeneğini **İŞARETLEMEYİN**
5. **"Create repository"** butonuna tıklayın

### Yöntem 2: GitHub CLI (Eğer kuruluysa)

```bash
gh repo create murakabe-erp --public --description "Murakabe AI - Yapay Zeka Destekli İşletme Yönetim Platformu"
```

---

## 🔗 Adım 2: Remote Repository Ekleme

GitHub'da repository oluşturduktan sonra, aşağıdaki komutları çalıştırın:

```bash
cd /opt/murakabe-erp

# Remote ekle (YOUR_USERNAME'i kendi GitHub kullanıcı adınızla değiştirin)
git remote add origin https://github.com/YOUR_USERNAME/murakabe-erp.git

# Veya SSH kullanıyorsanız:
# git remote add origin git@github.com:YOUR_USERNAME/murakabe-erp.git

# Remote'un doğru eklendiğini kontrol edin
git remote -v
```

---

## 📤 Adım 3: Kodları GitHub'a Gönderme

```bash
# Ana branch'i push edin
git push -u origin main

# Eğer branch adı 'master' ise:
# git push -u origin master
```

---

## ✅ Adım 4: Doğrulama

1. GitHub repository sayfanıza gidin
2. Tüm dosyaların yüklendiğini kontrol edin
3. README.md dosyasının düzgün göründüğünü kontrol edin

---

## 🔧 Ek Ayarlar

### Git Kullanıcı Bilgilerini Ayarlama

```bash
git config --global user.name "Adınız Soyadınız"
git config --global user.email "email@example.com"
```

### Branch Adını Kontrol Etme

```bash
git branch
# Eğer 'master' görüyorsanız ve 'main' kullanmak istiyorsanız:
git branch -m master main
```

---

## 📝 Sonraki Adımlar

1. **GitHub Actions** kurulumu (CI/CD için)
2. **Issues** ve **Projects** yönetimi
3. **Releases** oluşturma
4. **Contributors** ekleme
5. **License** dosyası ekleme (MIT, Apache, vb.)

---

## 🆘 Sorun Giderme

### "remote origin already exists" hatası
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/murakabe-erp.git
```

### "Permission denied" hatası
- GitHub'da SSH key'inizi eklediğinizden emin olun
- Veya HTTPS kullanın ve Personal Access Token kullanın

### "Branch 'main' has no upstream branch" hatası
```bash
git push --set-upstream origin main
```

---

**Not**: Bu rehberi takip ederek repository'nizi GitHub'a başarıyla yükleyebilirsiniz.

