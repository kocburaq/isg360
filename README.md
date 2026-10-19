# Factory Control System

Endüstriyel fabrikalar için yapay zekâ destekli, modüler yönetim sistemi.

- **1. aşama:** Web arayüzü (React)
- **2. aşama:** FastAPI backend, SQLite veritabanı ve Kamera Yönetimi'nin API ile çalışması

Akış: **Admin Girişi → Ana Kontrol Paneli → Modül Seçimi**

| Modül           | Durum                                                                    |
| --------------- | ------------------------------------------------------------------------ |
| Kamera Yönetimi | Arayüz + REST API + kalıcı veritabanı (kayıtlar örnek/simülasyon verisi) |
| İş Kartları     | "Yakında" sayfası                                                        |
| Drone Yönetimi  | "Yakında" sayfası                                                        |

> **Güvenlik ve prototip uyarısı**
>
> - Backend API'de **henüz kimlik doğrulama/yetkilendirme yoktur.** Yalnızca yerel geliştirme içindir;
>   `127.0.0.1` üzerinde çalıştırın, ağa veya internete açmayın, gerçek kameralara bağlamayın.
> - Arayüzdeki "Demo Modu" girişi **hiçbir güvenlik sağlamaz**.
> - Kamera ve ihlal kayıtları örnek (simülasyon) verileridir. Gerçek kamera, RTSP akışı veya YOLO modeli bağlı değildir;
>   arayüzde ve API yanıtlarında (`isSimulated`, `source: "simulation"`) bu şekilde etiketlenir.

Proje, [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) şablonu (MIT) temel alınarak geliştirilmiştir.

---

## Teknolojiler

**Frontend:** React 19 · Vite · TypeScript · TanStack Router / Query / Table · Tailwind CSS 4 · shadcn/ui · Zustand · Zod

**Backend:** Python 3.11+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic · SQLite (PostgreSQL'e hazır) · pytest

---

## Windows'ta kurulum ve çalıştırma

### 1. Gereksinimler

- **Node.js 20 LTS veya üzeri** (22 LTS önerilir): <https://nodejs.org>
- **Python 3.11 veya üzeri** (3.12+ önerilir): <https://www.python.org/downloads/windows/>
  (kurulumda _"Add python.exe to PATH"_ seçeneğini işaretleyin)
- **Git** (isteğe bağlı): <https://git-scm.com/download/win>

Kurulumu doğrulamak için PowerShell açın:

```powershell
node -v
npm -v
python --version
```

> PowerShell "betik çalıştırma devre dışı" hatası verirse (`npm.ps1` veya `Activate.ps1 cannot be loaded`):
> `npm` yerine `npm.cmd` kullanın; sanal ortam için aşağıda verilen ve etkinleştirme gerektirmeyen
> `.\.venv\Scripts\python.exe` komutlarını kullanın.

### 2. Frontend kurulumu

Proje klasöründe (ör. `C:\Projeler\isg360`):

```powershell
cd C:\Projeler\isg360
npm install
```

### 3. Backend kurulumu (ilk sefer)

```powershell
cd C:\Projeler\isg360\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m app.db.seed
```

Sırasıyla bu komutlar:

1. Sanal ortamı oluşturur.
2. Bağımlılıkları kurar.
3. Ayar dosyasını oluşturur.
4. Veritabanı tablolarını migration ile kurar (`backend\data\fcs_dev.db`).
5. Örnek kamera ve ihlal verilerini yükler.

Seed komutu tekrar çalıştırılabilir: eksik kayıtları ekler, mevcutları (ör. "İncelendi" yapılmış ihlalleri)
değiştirmez. Örnek veriyi sıfırlamak için `.\.venv\Scripts\python.exe -m app.db.seed --reset` kullanılır.

### 4. Çalıştırma

İki ayrı PowerShell penceresi açın.

**Pencere 1 — Backend (FastAPI):**

```powershell
cd C:\Projeler\isg360\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: <http://localhost:8000/api/v1/health>
- Swagger dokümantasyonu: <http://localhost:8000/docs>

**Pencere 2 — Frontend (API modunda):**

```powershell
cd C:\Projeler\isg360
npm run dev:api
```

Tarayıcıda <http://localhost:5173> adresini açın ve **"Demo Modu ile Giriş"** butonunu kullanın.

**Backend olmadan (mock modu):** `npm run dev` yeterlidir. Arayüz tarayıcı içindeki örnek veriyle çalışır.
Bu modda yapılan değişiklikler sayfa yenilenince sıfırlanır.

### 5. Testler ve kontroller

```powershell
# Frontend
npm run typecheck
npm run lint
npm run test:browser:install   # yalnızca ilk sefer (Playwright Chromium)
npm test
npm run build

# Backend
cd backend
.\.venv\Scripts\python.exe -m pytest
```

---

## Çalışma modları ve ortam değişkenleri

### Frontend (`.env.local` veya `.env.api`)

| Değişken            | Varsayılan                     | Açıklama                                                      |
| ------------------- | ------------------------------ | ------------------------------------------------------------- |
| `VITE_DATA_SOURCE`  | `mock`                         | `mock`: örnek veri (backend gerekmez) · `api`/`http`: FastAPI |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Backend temel adresi                                          |

- `npm run dev` → `.env.example`'daki varsayılanlar, yani **mock** modu.
- `npm run dev:api` → `.env.api` dosyası, yani **API** modu.
- Kalıcı olarak API modunda çalışmak için `.env.example` dosyasını `.env.local` olarak kopyalayıp `VITE_DATA_SOURCE=api` yapın.

### Backend (`backend\.env`)

| Değişken        | Varsayılan                    | Açıklama                                                       |
| --------------- | ----------------------------- | -------------------------------------------------------------- |
| `APP_ENV`       | `development`                 | Yalnızca `development`/`test`; başka değerle uygulama başlamaz |
| `DATABASE_URL`  | `sqlite:///./data/fcs_dev.db` | SQLAlchemy adresi (göreli yol `backend\` klasörüne göre)       |
| `CORS_ORIGINS`  | localhost:5173 / 4173         | İzin verilen frontend origin'leri (`*` reddedilir)             |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1`         | Kabul edilen Host başlıkları (LAN/IP erişimini engeller)       |
| `APP_TIMEZONE`  | `Europe/Istanbul`             | "Bugünkü ihlaller" hesabı için saat dilimi                     |
| `DB_ECHO`       | `false`                       | SQL sorgularını konsola yazdır                                 |

`.env` dosyaları, veritabanı dosyaları ve `.venv` Git'e eklenmez (`.gitignore`).

---

## REST API (`/api/v1`)

| Yöntem   | Yol                  | Açıklama                                                                                   |
| -------- | -------------------- | ------------------------------------------------------------------------------------------ |
| `GET`    | `/health`            | Servis durumları (API, veritabanı; YOLO ve RTSP "simülasyon" olarak raporlanır)            |
| `GET`    | `/cameras`           | Sayfalı liste · `status` (tekrarlanabilir), `zone_id`, `q`, `page`, `page_size`            |
| `GET`    | `/cameras/{id}`      | Kamera ayrıntısı                                                                           |
| `POST`   | `/cameras`           | Kamera ekle (`201`, yeni kamera durumu `unknown`)                                          |
| `PATCH`  | `/cameras/{id}`      | Kısmi güncelleme                                                                           |
| `DELETE` | `/cameras/{id}`      | Sil (`204`); ihlal kaydı olan kamera İSG geçmişi için silinemez (`409`)                    |
| `GET`    | `/violations`        | Sayfalı liste · `camera_id`, `zone_id`, `status`, `severity`, `ppe`, `from`, `to`, `order` |
| `GET`    | `/violations/{id}`   | İhlal ayrıntısı                                                                            |
| `PATCH`  | `/violations/{id}`   | `{ "status": "acknowledged" }` ve/veya `{ "description": "..." }`                          |
| `GET`    | `/dashboard/summary` | Kamera ve ihlal sayıları (bugün, açık, incelenen, çözülen)                                 |
| `GET`    | `/zones`             | Fabrika bölgeleri                                                                          |

- **Liste yanıtı:** `{ "items": [...], "total": 22, "page": 1, "pageSize": 50 }`. JSON alan adları camelCase'tir ve frontend tipleriyle aynıdır.
- **Hata yanıtı (her durumda):** `{ "error": { "code": "not_found", "message": "Kamera bulunamadı: cam-99", "details": null } }`
- **Durum kodları:** `404` bulunamadı · `409` çakışma · `422` doğrulama hatası (`details` alan bazlı) · `500` iç hata (ayrıntı sızdırılmaz)

---

## Klasör mimarisi

```
isg360/
├── src/                         Frontend (React)
│   ├── config/                  Uygulama sabitleri ve tipli ortam değişkenleri (env.ts)
│   ├── modules/registry.ts      Modül kaydı (panel kartları, sidebar, komut menüsü)
│   ├── types/                   Modüller arası ortak tipler (FactoryZone, EntityRef, Paginated…)
│   ├── services/                http-client.ts (axios) · auth/ (demo + sunucu kimlik doğrulama sözleşmesi)
│   ├── mocks/                   Mock modu örnek verisi
│   ├── features/cameras/        Kamera Yönetimi
│   │   ├── api/                 CameraService arayüzü · mock ve HTTP uygulamaları · query key'ler
│   │   ├── hooks/               React Query hook'ları (bileşenlerin tek veri erişim noktası)
│   │   ├── components/          Grid, detay paneli, KKD paneli, ihlal bildirimleri/geçmişi…
│   │   ├── config/ lib/         KKD sınıf kaydı, durum etiketleri, saf yardımcılar
│   │   └── types.ts             Kamera, ihlal, özet modelleri (backend şemalarıyla aynı)
│   ├── features/work-orders/    İş Kartları (Yakında)
│   ├── features/drones/         Drone Yönetimi (Yakında)
│   └── components/ routes/ …    Ortak bileşenler (query-error-state dahil) ve rotalar
│
└── backend/                     Backend (FastAPI)
    ├── app/
    │   ├── main.py              Uygulama fabrikası: CORS, TrustedHost, hata işleyicileri, router
    │   ├── core/                config.py (ortam değişkenleri) · errors.py (tutarlı hata yanıtları)
    │   ├── db/                  base.py (taban model, UTC zaman tipi) · session.py · seed.py
    │   ├── models/              SQLAlchemy modelleri: FactoryZone, Camera, PpeViolation, enum'lar
    │   ├── repositories/        Veritabanı erişimi (yalnızca sorgular)
    │   ├── services/            İş mantığı (doğrulama, çakışma, inceleme kuralları)
    │   ├── schemas/             Pydantic istek/yanıt modelleri (camelCase JSON)
    │   └── api/v1/              HTTP katmanı: endpoints/ + router.py
    ├── alembic/                 Migration'lar (versions/)
    ├── tests/                   pytest (her test geçici SQLite + migration + seed)
    ├── requirements.txt         Çalışma zamanı bağımlılıkları
    └── requirements-dev.txt     Test bağımlılıkları
```

**Backend katmanları:** `api` → `services` → `repositories` → `models`. HTTP katmanı iş kuralı içermez; servisler HTTP'den
bağımsızdır ve hata durumlarında `AppError` fırlatır; repository'ler yalnızca parametreli SQLAlchemy sorguları çalıştırır.
Şablondaki yapıya `repositories/` katmanı eklenmiştir: sorgular tek yerde toplanır ve PostgreSQL geçişi ile
gelecekteki modüller (Drone, İş Kartları) servis mantığına dokunmadan genişletilebilir.

### Veri modeli

- `factory_zones`: Modüller arası ortak bölge (kamera, drone ve iş kartları aynı bölgeyi kullanır).
- `cameras`: id, kod (benzersiz), ad, bölge, konum, durum (`online`/`offline`/`unknown`), son sinyal, akış bilgisi, KKD sınıfları, `is_simulated`, oluşturma/güncelleme zamanları.
- `ppe_violations`: id, kamera, bölge, ihlal türü (`missing_ppe`), eksik KKD listesi, tespit zamanı, güven skoru, önem, inceleme durumu (`open`/`acknowledged`/`resolved`), kaynak (`simulation`/`model`), açıklama, inceleme zamanı, oluşturma/güncelleme zamanları.

Taşınabilirlik için alınan önlemler:

- Enum'lar VARCHAR + CHECK kısıtı olarak saklanır.
- Kısıt adları sabittir.
- Zamanlar UTC tutulur.
- JSON alanları SQLite ve PostgreSQL'de aynı çalışır.

### PostgreSQL'e geçiş

1. `requirements.txt` içindeki `psycopg[binary]` satırını açıp yükleyin.
2. `.env` → `DATABASE_URL=postgresql+psycopg://kullanici:sifre@localhost:5432/fcs`
3. `.\.venv\Scripts\python.exe -m alembic upgrade head` ve ardından `.\.venv\Scripts\python.exe -m app.db.seed`

### Yeni migration oluşturma

Model değiştirildikten sonra:

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "aciklama"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

---

## Genişletme rehberi

- **Yeni backend modülü (ör. drones):** `models/` → `repositories/` → `services/` → `schemas/` → `api/v1/endpoints/drones.py` dosyalarını oluşturun ve router'ı `api/v1/router.py` içinde kaydedin. Ardından migration üretin.
- **Yeni frontend modülü:** `modules/registry.ts` içine kayıt ekleyin, `features/<modül>/` altında kamera modülüyle aynı yapıyı kurun ve rotayı ekleyin.
- **Yeni KKD sınıfı:** Sırasıyla şu yerlere ekleyin: backend `models/enums.py` → `PpeClass`; frontend `features/cameras/types.ts` → `PpeClassId`; `config/ppe-classes.ts`.
- **Gerçek kamera görüntüsü:** `SimulatedFeed` yer tutucudur. RTSP'nin backend'de WebRTC/HLS'e dönüştürülmesi gerekir. Tespit kutusu katmanı (`BoundingBox`) aynen kullanılabilir.
- **Modüller arası bağlantı:** `PpeViolation.links` (`EntityRef`) ileride ihlal → düzeltici faaliyet iş kartı gibi bağlantılar için ayrılmıştır.

---

## Tamamlanmayanlar / sonraki aşamalar

- **Kimlik doğrulama ve yetkilendirme:** Henüz yok. Hem API hem arayüz için ayrıca geliştirilecek; httpOnly çerez ile oturum ve rol bazlı yetki önerilir.
- **YOLO tabanlı KKD tespiti ve model eğitimi:** HTTP modunda tespit kutuları gösterilmez; backend tespit kaydı tutmaz.
- **Kamera akışı:** RTSP IP kamera bağlantısı, WebRTC/HLS yayını ve kamera durumlarının gerçek telemetriden güncellenmesi henüz yok.
- **Gerçek zamanlı bildirimler (WebSocket/SSE):** Şu an API modunda 5 saniyelik yenileme kullanılıyor.
- **Kamera ekleme/düzenleme formu:** API hazır, arayüzü henüz yok.
- **Diğer modüller:** Drone ve İş Kartları modüllerinin işlevleri yok.
- **Altyapı:** Docker Compose ve production deployment yapılmadı.

---

## Lisans

[MIT](LICENSE) — şablonun orijinal lisansı korunmuştur.
