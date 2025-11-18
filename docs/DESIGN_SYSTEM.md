# Murakabe ERP - Design System

## 🎨 Genel Bakış

Murakabe ERP, modern ve tutarlı bir tasarım sistemi kullanır. Tüm bileşenler ve stiller bu sistem üzerine kurulmuştur.

---

## 🎨 Renk Paleti

### Brand Colors
```css
--night-navy: #020617      /* Koyu lacivert - Ana marka rengi */
--orbit-blue: #2563EB       /* Mavi - Primary renk */
--orbit-blue-soft: #DBEAFE  /* Açık mavi - Soft variant */
--orbit-blue-light: #EFF6FF /* Çok açık mavi - Light variant */
--orbit-blue-dark: #1D4ED8  /* Koyu mavi - Dark variant */
--fog-grey: #CBD2DC         /* Gri - Border ve ayırıcılar */
--polar-white: #F9FAFB      /* Beyaz - Background */
```

### Semantic Colors
```css
--success-green: #10B981    /* Başarı - Yeşil */
--danger-red: #EF4444       /* Hata - Kırmızı */
--warning-amber: #F59E0B    /* Uyarı - Turuncu */
--info-blue: #3B82F6        /* Bilgi - Mavi */
```

### Text Colors
```css
--text: #0F172A            /* Ana metin */
--text-secondary: #64748B    /* İkincil metin */
--text-tertiary: #94A3B8   /* Üçüncül metin */
--text-inverse: #FFFFFF     /* Ters metin (beyaz) */
```

---

## 📏 Spacing Scale

8px tabanlı spacing sistemi:

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-2xl: 3rem;     /* 48px */
--spacing-3xl: 4rem;     /* 64px */
```

### Kullanım Örnekleri:
```css
padding: var(--spacing-md);        /* 16px */
margin-bottom: var(--spacing-lg);   /* 24px */
gap: var(--spacing-sm);             /* 8px */
```

---

## 🔤 Typography

### Font Family
```css
--font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Arial, sans-serif;
--font-family-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
```

### Font Sizes
```css
--text-xs: 0.75rem;      /* 12px */
--text-sm: 0.875rem;     /* 14px */
--text-base: 1rem;       /* 16px */
--text-lg: 1.125rem;     /* 18px */
--text-xl: 1.25rem;      /* 20px */
--text-2xl: 1.5rem;      /* 24px */
--text-3xl: 1.875rem;    /* 30px */
--text-4xl: 2.25rem;     /* 36px */
```

### Font Weights
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Line Heights
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

---

## 🔲 Border Radius

```css
--radius-sm: 0.375rem;   /* 6px */
--radius-md: 0.5rem;     /* 8px */
--radius-lg: 0.75rem;    /* 12px */
--radius-xl: 1rem;       /* 16px */
--radius-full: 9999px;   /* Tam yuvarlak */
```

---

## 🌑 Shadows

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

---

## ⚡ Transitions

```css
--transition-fast: 150ms ease;
--transition-base: 200ms ease;
--transition-slow: 300ms ease;
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
/* Small devices (phones) */
@media (min-width: 640px) { /* sm */ }

/* Medium devices (tablets) */
@media (min-width: 768px) { /* md */ }

/* Large devices (desktops) */
@media (min-width: 1024px) { /* lg */ }

/* Extra large devices */
@media (min-width: 1280px) { /* xl */ }
```

---

## 🧩 Bileşenler

### Button

```html
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-secondary">Secondary Button</button>
<button class="btn btn-outline">Outline Button</button>
<button class="btn btn-ghost">Ghost Button</button>
```

**Variants:**
- `btn-primary` - Ana buton (mavi)
- `btn-secondary` - İkincil buton (açık mavi)
- `btn-outline` - Çerçeveli buton
- `btn-ghost` - Şeffaf buton

**Sizes:**
- `btn-sm` - Küçük
- (default) - Orta
- `btn-lg` - Büyük

### Card

```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content</p>
</div>
```

**Variants:**
- `card` - Standart kart
- `card-elevated` - Yüksek gölgeli kart

### Input

```html
<input type="text" class="input" placeholder="Enter text..." />
```

### Badge

```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-danger">Danger</span>
<span class="badge badge-warning">Warning</span>
```

---

## 📐 Layout Utilities

### Container

```html
<div class="container">
  <!-- İçerik -->
</div>
```

Otomatik olarak responsive max-width ayarlar:
- 640px (sm)
- 768px (md)
- 1024px (lg)
- 1280px (xl)

### Grid

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Grid items -->
</div>
```

---

## ♿ Accessibility

### Focus States
Tüm interaktif elementler `:focus-visible` ile keyboard navigasyonu destekler.

### Screen Reader
```html
<span class="sr-only">Screen reader only text</span>
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  /* Animasyonlar devre dışı */
}
```

---

## 🎯 Best Practices

### 1. CSS Variables Kullanımı
✅ **DO:**
```css
color: var(--text);
padding: var(--spacing-md);
border-radius: var(--radius-md);
```

❌ **DON'T:**
```css
color: #0F172A;
padding: 16px;
border-radius: 8px;
```

### 2. Responsive Design
✅ **DO:** Mobile-first yaklaşım
```css
/* Mobile first */
.element {
  padding: var(--spacing-md);
}

/* Desktop */
@media (min-width: 768px) {
  .element {
    padding: var(--spacing-lg);
  }
}
```

### 3. Spacing Consistency
✅ **DO:** Spacing scale kullan
```css
gap: var(--spacing-md);
margin-bottom: var(--spacing-lg);
```

❌ **DON'T:** Rastgele değerler
```css
gap: 13px;
margin-bottom: 27px;
```

### 4. Color Usage
✅ **DO:** Semantic colors kullan
```css
color: var(--success-green);
background: var(--danger-red-light);
```

❌ **DON'T:** Hard-coded colors
```css
color: #10B981;
background: #FEE2E2;
```

---

## 📚 Kaynaklar

- [Inter Font](https://rsms.me/inter/)
- [CSS Variables Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Son Güncelleme**: 2024

