# Factory Control System

Endüstriyel fabrikalar için yapay zekâ destekli, modüler yönetim sisteminin **web arayüzü (1. aşama)**.

Akış: **Admin Girişi → Ana Kontrol Paneli → Modül Seçimi**

| Modül           | Durum                                                  |
| --------------- | ------------------------------------------------------ |
| Kamera Yönetimi | Arayüz hazır (örnek veri + simüle edilmiş KKD tespiti) |
| İş Kartları     | "Yakında" sayfası                                      |
| Drone Yönetimi  | "Yakında" sayfası                                      |

> **Prototip uyarısı:** Bu aşamada gerçek kimlik doğrulama, kamera bağlantısı veya yapay zekâ modeli yoktur.
> "Demo Modu" girişi **hiçbir güvenlik sağlamaz**. Kamera görüntüleri yer tutucudur, tespit ve ihlaller simüle edilmiştir; arayüzde de bu şekilde etiketlenir.

Proje, [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) şablonu (MIT) temel alınarak geliştirilmiştir.

---

## Teknolojiler

React 19 · Vite · TypeScript · TanStack Router (dosya tabanlı) · TanStack Query · TanStack Table · Tailwind CSS 4 · shadcn/ui (Radix) · Zustand · Zod · React Hook Form · date-fns

---

## Windows'ta kurulum ve çalıştırma

### 1. Gereksinimler

- **Node.js 20 LTS veya üzeri** (22 LTS önerilir) — <https://nodejs.org> adresinden "LTS" Windows Installer (.msi) ile kurun. npm, Node.js ile birlikte gelir.
- **Git** (isteğe bağlı) — <https://git-scm.com/download/win>

Kurulumu doğrulamak için PowerShell veya Komut İstemi'ni açın:

```powershell
node -v
npm -v
```

### 2. Bağımlılıkları yükleme

Proje klasöründe (ör. `C:\Projeler\isg360`) PowerShell açın:

```powershell
cd C:\Projeler\isg360
npm install
```

> PowerShell "betik çalıştırma devre dışı" (`npm.ps1 cannot be loaded`) hatası verirse `npm.cmd install` kullanın
> veya Komut İstemi (cmd) üzerinden çalıştırın.

### 3. Ortam değişkenleri (isteğe bağlı)

Varsayılan ayarlarla dosya oluşturmanıza gerek yoktur. Değiştirmek isterseniz:

```powershell
Copy-Item .env.example .env.local
```

| Değişken            | Varsayılan                     | Açıklama                                                |
| ------------------- | ------------------------------ | ------------------------------------------------------- |
| `VITE_DATA_SOURCE`  | `mock`                         | `mock`: örnek veri · `api`: FastAPI backend (henüz yok) |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend temel adresi                                    |

### 4. Geliştirme sunucusunu başlatma

```powershell
npm run dev
```

Tarayıcıda <http://localhost:5173> adresini açın ve **"Demo Modu ile Giriş"** butonunu kullanın.

### 5. Production build

```powershell
npm run build
npm run preview
```

`npm run build` TypeScript kontrolünü yapar ve çıktıyı `dist/` klasörüne üretir. `npm run preview` bu çıktıyı <http://localhost:4173> adresinde sunar.

### Diğer komutlar

| Komut                             | Açıklama                                            |
| --------------------------------- | --------------------------------------------------- |
| `npm run typecheck`               | Yalnızca TypeScript kontrolü                        |
| `npm run lint`                    | ESLint                                              |
| `npm run format` / `format:check` | Prettier ile biçimlendirme / kontrol                |
| `npm run test:browser:install`    | Testler için Playwright Chromium kurulumu (bir kez) |
| `npm test`                        | Vitest tarayıcı testleri (headless)                 |
| `npm run knip`                    | Kullanılmayan dosya/bağımlılık analizi              |

---

## Klasör mimarisi

```
src/
├── config/              Uygulama sabitleri (app.ts) ve tipli ortam değişkenleri (env.ts)
├── modules/registry.ts  Modül kaydı — panel kartları, sidebar ve komut menüsü buradan beslenir
├── types/               Modüller arası ortak tipler (EntityId, FactoryZone, EntityRef…)
├── services/
│   ├── http-client.ts   Ortak axios istemcisi (FastAPI için)
│   └── auth/            Kimlik doğrulama sözleşmesi + demo / sunucu uygulaması
├── stores/auth-store.ts Oturum durumu (yalnızca parolasız oturum özeti, sessionStorage)
├── mocks/               Merkezi örnek veri katmanı (kameralar, tespitler, ihlaller, bölgeler)
├── features/            Modül bazlı özellikler
│   ├── auth/            Giriş ekranı
│   ├── dashboard/       Ana kontrol paneli (modül kartları)
│   ├── cameras/         Kamera Yönetimi — bağımsız feature
│   │   ├── api/         CameraService arayüzü, mock ve HTTP uygulamaları, query key'ler
│   │   ├── hooks/       React Query hook'ları (bileşenlerin tek veri erişim noktası)
│   │   ├── config/      KKD sınıf kaydı (ppe-classes.ts), durum etiketleri/renkleri
│   │   ├── lib/         Saf yardımcılar (filtreleme, KKD özetleri) + testleri
│   │   ├── components/  Grid, kutucuk, detay paneli, KKD paneli, ihlal listesi/tablosu…
│   │   └── types.ts     Kamera, tespit, ihlal ve sistem durumu modelleri
│   ├── work-orders/     İş Kartları ("Yakında")
│   ├── drones/          Drone Yönetimi ("Yakında")
│   └── errors/          Hata sayfaları
├── components/          Ortak bileşenler (layout, data-table, ui/ = shadcn)
├── routes/              TanStack Router dosya tabanlı rotalar (routeTree.gen.ts otomatik üretilir)
├── context/ hooks/ lib/ Tema, yerleşim, arama ve genel yardımcılar
└── styles/              Tailwind ve tema renk değişkenleri (koyu tema öncelikli)
```

### Rotalar

| Rota           | Açıklama                                                                      |
| -------------- | ----------------------------------------------------------------------------- |
| `/sign-in`     | Yönetici girişi (form doğrulama + Demo Modu)                                  |
| `/`            | Ana kontrol paneli                                                            |
| `/cameras`     | Kamera Yönetimi (`?camera=cam-01` detay paneli, `?tab=history` ihlal geçmişi) |
| `/work-orders` | İş Kartları — Yakında                                                         |
| `/drones`      | Drone Yönetimi — Yakında                                                      |

`_authenticated` altındaki tüm rotalar oturum kontrolü yapar; oturum yoksa kullanıcı `/sign-in?redirect=…` sayfasına yönlendirilir.

---

## Genişletme rehberi

### Veri kaynağını backend'e bağlamak

Bileşenler veri kaynağını bilmez; yalnızca `features/cameras/hooks` içindeki hook'ları kullanır.
Hook'lar `CameraService` arayüzünü çağırır ve uygulama `VITE_DATA_SOURCE` değerine göre seçilir:

- `mock-camera-service.ts` → `src/mocks/` verisi
- `http-camera-service.ts` → FastAPI uç noktaları (taslak sözleşme dosyada belgelenmiştir)

FastAPI hazır olduğunda `VITE_DATA_SOURCE=api` yapmak ve sözleşmeyi netleştirmek yeterlidir; bileşen değişikliği gerekmez.

### Yeni KKD sınıfı eklemek

1. `features/cameras/types.ts` → `PpeClassId` birleşimine kimliği ekleyin.
2. `features/cameras/config/ppe-classes.ts` → etiket, ikon, YOLO sınıf adları ve `enabled: true`.

Eldiven, gözlük ve iş ayakkabısı tanımlı ancak `enabled: false` (arayüzde "planlanan" olarak görünür).

### Gerçek kamera görüntüsü

`SimulatedFeed` bileşeni yer tutucudur. RTSP akışları tarayıcıda doğrudan oynatılamadığından backend'de
WebRTC/HLS'e dönüştürülmesi gerekir; ardından bu bileşen bir video oynatıcıyla değiştirilir.
Tespit kutusu katmanı (normalize edilmiş `BoundingBox`) aynen kullanılabilir.

### Yeni modül eklemek

1. `modules/registry.ts` içine kayıt ekleyin (sidebar, panel ve komut menüsü otomatik güncellenir).
2. `features/<modül>/` altında kamera modülüyle aynı katman yapısını kurun (`api/`, `hooks/`, `components/`, `types.ts`).
3. `routes/_authenticated/<modül>/index.tsx` rotasını oluşturun.

Modüller arası bağlantılar için `types/factory.ts` içindeki `FactoryZone` (ortak bölge) ve `EntityRef`
(ör. ihlal → düzeltici faaliyet iş kartı; `PpeViolation.links`) kullanılır.

---

## Bu aşamada bulunmayanlar (backend gerektirir)

- Gerçek kullanıcı doğrulama, yetkilendirme ve oturum yönetimi (httpOnly çerez önerilir)
- FastAPI backend ve PostgreSQL veritabanı
- RTSP IP kamera bağlantısı ve canlı video akışı (WebRTC/HLS dönüşümü)
- YOLO tabanlı KKD tespiti ve model eğitimi
- Gerçek zamanlı bildirimler (WebSocket/SSE); şu an bildirimler örnek veridir
- İhlal durum değişikliklerinin kalıcı saklanması (mock modda sayfa yenilenince sıfırlanır)
- İş Kartları ve Drone Yönetimi modüllerinin işlevleri
- Docker Compose yapılandırması

---

## Lisans

[MIT](LICENSE) — şablonun orijinal lisansı korunmuştur.
