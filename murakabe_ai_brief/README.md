# Murakabe — AI Handover Kit

Bu klasörü başka bir yapay zekâ aracına (ChatGPT/Claude/Copilot) vererek projeyi onunla devam ettirebilirsiniz.

## İçerikler
- brand_config.json — marka adı, slogan, modüller, renkler, tipografi
- assets/ — logo ve görsel varlıklar (SVG/PNG)
- landing.jsx — tek sayfa site başlangıcı
- prompt_system.txt — modele yapıştırılacak sistem talimatı
- prompt_task.txt — ilk görev talimatı (servis + Next.js + Docker)
- tokens/colors CSS ve JSON için `murakabe_brand_kit_v1` klasöründen aktarılmıştır (varsa)

## Nasıl kullanılır (3 adım)
1) **Dosyaları ekle:** AI aracına dosya yüklemeyi kullanarak bu klasörü ZIP olarak yükleyin.
2) **Sistem talimatı:** `prompt_system.txt` içeriğini modelin "system" / "developer" alanına yapıştırın.
3) **Görev:** `prompt_task.txt` içeriğini kullanıcı mesajı olarak gönderin. Ek olarak özel isteklerinizi mesajın altına yazın.

### Dikkat
- Modelden çıktı alırken, `brand_config.json` ı referans almasını, değişken adlarında markayı kullanmasını ve renkleri Tailwind config'e aktarmasını isteyin.
- Koddan sonra kısa README ve `docker-compose.yml` mutlaka olmalı.
- Gizli anahtarlar `.env` dosyasına ve `.env.example` a taşınmalı.

Yüklenme tarihi: 2025-11-12T10:55:32.141446Z
