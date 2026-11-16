# Factory Control System

Endüstriyel fabrikalar için yapay zekâ destekli, modüler yönetim sistemi.

- **1. aşama:** Web arayüzü (React)
- **2. aşama:** FastAPI backend, SQLite veritabanı ve Kamera Yönetimi'nin API ile çalışması
- **3.1 aşaması:** Çok fabrikalı yapı, saha sunucusu (edge) ↔ merkez API'si, ortak sözleşme paketi ve edge simülatörü

Akış: **Admin Girişi → Ana Kontrol Paneli → Modül Seçimi**

| Modül           | Durum                                                                            |
| --------------- | -------------------------------------------------------------------------------- |
| Kamera Yönetimi | Arayüz + REST API + kalıcı veritabanı + edge olayları (henüz simülatör kaynaklı) |
| İş Kartları     | "Yakında" sayfası                                                                |
| Drone Yönetimi  | "Yakında" sayfası                                                                |

> **Güvenlik ve prototip uyarısı**
>
> - Panel API'sinde (`/api/v1`) **henüz kullanıcı kimlik doğrulaması/yetkilendirme yoktur.** Yalnızca yerel
>   geliştirme içindir; `127.0.0.1` üzerinde çalıştırın, ağa veya internete açmayın.
> - Edge API'si (`/edge/v1`) edge node başına **API anahtarı** ister; anahtarlar yalnızca SHA-256 özeti olarak saklanır.
> - Arayüzdeki "Demo Modu" girişi **hiçbir güvenlik sağlamaz**.
> - Gerçek kamera, RTSP akışı veya YOLO modeli bağlı değildir. Seed kayıtları ve simülatör olayları
>   `isSimulated` / `source: "simulation"` olarak etiketlenir ve arayüzde öyle gösterilir.

Proje, [satnaing/shadcn-admin](https://github.com/satnaing/shadcn-admin) şablonu (MIT) temel alınarak geliştirilmiştir.

---

## Mimari (hedef)

Her fabrikada bir **saha sunucusu (edge)** kameraları okur, modeli çalıştırır ve kuralları uygular; merkeze
yalnızca **olaylar, kamera durumu (heartbeat) ve kanıt görüntüsü** gider. Canlı video FastAPI'den geçmez.

```
 FABRİKA                                      MERKEZ
┌──────────────────────────────┐   HTTPS   ┌───────────────────────────────┐
│ vision/ (edge servisi)        │──────────►│ backend/  /edge/v1 (API anahtarı)│
│  sync/: yapılandırma, heartbeat│◄──────────│   config · heartbeat · events  │
│         kalıcı olay kuyruğu    │           │ backend/  /api/v1  (panel)      │
│  (3.2+) rules · ingest ·       │           │ SQLite → PostgreSQL            │
│         inference · tracking   │           └──────────────┬────────────────┘
└──────────────────────────────┘                          │ REST
        ▲ packages/contracts: iki tarafın ortak şeması      ▼
                                                  Web paneli (src/)
```

**3.1'de çalışan:** sözleşme paketi, edge API'si, edge node yönetimi (CLI), heartbeat ile kamera durumu,
heartbeat kesilince kameraların çevrimdışı olması, idempotent olay alma ve gerçek kamera yerine **simülatör**.

---

## Teknolojiler

**Frontend:** React 19 · Vite · TypeScript · TanStack Router / Query / Table · Tailwind CSS 4 · shadcn/ui · Zustand · Zod

**Backend:** Python 3.11+ · FastAPI · Pydantic v2 · SQLAlchemy 2.0 · Alembic · SQLite (PostgreSQL'e hazır) · pytest

**Edge (vision):** Python 3.11+ · httpx · Pydantic · SQLite (yerel olay kuyruğu)

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
2. Bağımlılıkları ve ortak sözleşme paketini (`packages/contracts`) kurar.
3. Ayar dosyasını oluşturur.
4. Veritabanı tablolarını migration ile kurar (`backend\data\fcs_dev.db`).
5. Örnek fabrika, bölge, kamera ve ihlal verilerini yükler.

Seed komutu tekrar çalıştırılabilir: eksik kayıtları ekler, mevcutları (ör. "İncelendi" yapılmış ihlalleri)
değiştirmez. Her şeyi sıfırlamak için `.\.venv\Scripts\python.exe -m app.db.seed --reset` kullanılır
(**edge node'lar ve API anahtarları da silinir**).

> **2. aşamadan güncelliyorsanız:** `backend` klasöründe
> `.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt`, ardından `alembic upgrade head` ve
> `app.db.seed` komutlarını çalıştırın. Migration mevcut verileri korur ve bölgeleri "Merkez Fabrika"ya bağlar.

### 4. Edge simülatörü kurulumu (isteğe bağlı)

Gerçek kamera ve model olmadan edge ↔ merkez akışını denemek içindir.

```powershell
# 1) Edge node oluştur ve kamera ata (API anahtarı yalnızca bir kez gösterilir)
cd C:\Projeler\isg360\backend
.\.venv\Scripts\python.exe -m app.cli.edge_nodes create --factory fac-default --name "Merkez Simülatör" --cameras cam-01,cam-02,cam-03

# 2) Vision ortamını kur
cd C:\Projeler\isg360\vision
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
# .env dosyasında EDGE_API_KEY= satırına 1. adımda verilen anahtarı yazın
```

Diğer edge node komutları: `list`, `assign --node <id> --cameras ...`, `unassign --cameras ...`,
`rotate-key --node <id>`, `deactivate --node <id>`. Node ve anahtar yönetimi, panel API'sinde kullanıcı kimlik
doğrulaması olmadığı için bilinçli olarak yalnızca bu yerel komutla yapılır.

### 5. Çalıştırma

Ayrı PowerShell pencereleri açın.

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

**Pencere 3 — Edge simülatörü (isteğe bağlı):**

```powershell
cd C:\Projeler\isg360\vision
.\.venv\Scripts\python.exe -m fcs_vision.simulator --event-probability 0.3
```

Seçenekler: `--once` (tek tur), `--seed 42` (tekrarlanabilir senaryo), `--offline cam-02` (kamerayı çevrimdışı bildir),
`--interval 5`. Simülatör çalışırken atanmış kameralar "Çevrimiçi" olur ve panelde "Saha sunucusu" etiketli ihlaller
belirir. Simülatör durdurulduğunda kameralar heartbeat zaman aşımından (varsayılan 60 sn) sonra "Çevrimdışı" olur.

**Backend olmadan (mock modu):** `npm run dev` yeterlidir. Arayüz tarayıcı içindeki örnek veriyle çalışır.
Bu modda yapılan değişiklikler sayfa yenilenince sıfırlanır.

### 6. Testler ve kontroller

```powershell
# Frontend
npm run typecheck
npm run lint
npm run test:browser:install   # yalnızca ilk sefer (Playwright Chromium)
npm test
npm run build

# Backend (sözleşme paketi testleri de bu ortamda çalışır)
cd backend
.\.venv\Scripts\python.exe -m pytest
cd ..\packages\contracts
..\..\backend\.venv\Scripts\python.exe -m pytest

# Edge (vision)
cd ..\..\vision
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

| Değişken                         | Varsayılan                    | Açıklama                                                       |
| -------------------------------- | ----------------------------- | -------------------------------------------------------------- |
| `APP_ENV`                        | `development`                 | Yalnızca `development`/`test`; başka değerle uygulama başlamaz |
| `DATABASE_URL`                   | `sqlite:///./data/fcs_dev.db` | SQLAlchemy adresi (göreli yol `backend\` klasörüne göre)       |
| `CORS_ORIGINS`                   | localhost:5173 / 4173         | İzin verilen frontend origin'leri (`*` reddedilir)             |
| `ALLOWED_HOSTS`                  | `localhost,127.0.0.1`         | Kabul edilen Host başlıkları (LAN/IP erişimini engeller)       |
| `APP_TIMEZONE`                   | `Europe/Istanbul`             | "Bugünkü ihlaller" hesabı için saat dilimi                     |
| `DB_ECHO`                        | `false`                       | SQL sorgularını konsola yazdır                                 |
| `EDGE_HEARTBEAT_TIMEOUT_S`       | `60`                          | Bu süre heartbeat gelmeyen edge kameraları çevrimdışı olur     |
| `EDGE_LIVENESS_CHECK_INTERVAL_S` | `15`                          | Canlılık kontrolü aralığı (`0` = kapalı)                       |
| `EDGE_MAX_CLOCK_SKEW_S`          | `300`                         | Edge saatinin ileride olabileceği en fazla süre                |

### Edge (`vision\.env`)

| Değişken                    | Varsayılan                      | Açıklama                               |
| --------------------------- | ------------------------------- | -------------------------------------- |
| `EDGE_API_URL`              | `http://127.0.0.1:8000/edge/v1` | Merkez edge API adresi                 |
| `EDGE_API_KEY`              | —                               | `app.cli.edge_nodes create` çıktısı    |
| `EDGE_OUTBOX_PATH`          | `./data/outbox.db`              | Gönderilemeyen olayların yerel kuyruğu |
| `EDGE_HEARTBEAT_INTERVAL_S` | `10`                            | Tur (heartbeat) aralığı                |
| `EDGE_HTTP_TIMEOUT_S`       | `10`                            | HTTP zaman aşımı                       |

`.env` dosyaları, veritabanı/kuyruk dosyaları ve `.venv` klasörleri Git'e eklenmez (`.gitignore`).

---

## REST API

### Panel API (`/api/v1`) — kimlik doğrulama yok, yalnızca yerel

| Yöntem   | Yol                  | Açıklama                                                                                                         |
| -------- | -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `GET`    | `/health`            | Servis durumları (API, veritabanı, edge node'lar; YOLO ve RTSP "simülasyon")                                     |
| `GET`    | `/factories`         | Fabrikalar                                                                                                       |
| `GET`    | `/zones`             | Bölgeler · `factory_id`                                                                                          |
| `GET`    | `/cameras`           | Sayfalı liste · `factory_id`, `status` (tekrarlanabilir), `zone_id`, `q`, `page`, `page_size`                    |
| `GET`    | `/cameras/{id}`      | Kamera ayrıntısı                                                                                                 |
| `POST`   | `/cameras`           | Kamera ekle (`201`, yeni kamera durumu `unknown`)                                                                |
| `PATCH`  | `/cameras/{id}`      | Kısmi güncelleme                                                                                                 |
| `DELETE` | `/cameras/{id}`      | Sil (`204`); ihlal kaydı olan kamera İSG geçmişi için silinemez (`409`)                                          |
| `GET`    | `/violations`        | Sayfalı liste · `factory_id`, `camera_id`, `zone_id`, `type`, `status`, `severity`, `ppe`, `from`, `to`, `order` |
| `GET`    | `/violations/{id}`   | İhlal ayrıntısı                                                                                                  |
| `PATCH`  | `/violations/{id}`   | `{ "status": "acknowledged" }` ve/veya `{ "description": "..." }`                                                |
| `GET`    | `/dashboard/summary` | Kamera ve ihlal sayıları · `factory_id`                                                                          |

### Edge API (`/edge/v1`) — `Authorization: Bearer <edge API anahtarı>`

| Yöntem | Yol          | Açıklama                                                                                                 |
| ------ | ------------ | -------------------------------------------------------------------------------------------------------- |
| `GET`  | `/config`    | Node bilgisi ve atanmış kameralar. `ETag` döner; `If-None-Match` ile değişmediyse `304`                  |
| `POST` | `/heartbeat` | Kamera durumları (`online`/`offline`), yazılım sürümü, `simulated` bayrağı                               |
| `POST` | `/events`    | Toplu ihlal olayları (en fazla 100). Olay başına sonuç: `created` / `duplicate` / `updated` / `rejected` |

- **Idempotency:** Her olay edge'de üretilen `eventId` taşır; aynı olay tekrar gelirse `duplicate`, bitiş zamanı
  eklenmişse `updated` döner. Başka bir node'un `eventId`'si `rejected (event_id_conflict)` olur.
- **Reddedilen olaylar** (`camera_not_assigned`, `future_timestamp`) yeniden denenmez; edge bunları yerel kuyrukta
  inceleme için saklar.
- **Sözleşme sürümü:** İstemci `X-FCS-Contract-Version: 1` gönderir; uyumsuz sürüm `400 unsupported_contract` alır.
- **Hata kodları:** `401` anahtar yok/geçersiz · `403` node devre dışı · `422` doğrulama hatası.

Ortak kurallar: liste yanıtı `{ "items": [...], "total", "page", "pageSize" }`; JSON alanları camelCase; hata yanıtı
her zaman `{ "error": { "code", "message", "details" } }`.

---

## Klasör mimarisi

```
isg360/
├── src/                         Frontend (React)
│   ├── config/ modules/ types/  Ortam değişkenleri, modül kaydı, ortak tipler (Factory, FactoryZone, EntityRef…)
│   ├── services/ mocks/         axios istemcisi, auth sözleşmesi, mock modu verisi
│   ├── features/cameras/        Kamera Yönetimi
│   │   ├── api/                 CameraService arayüzü · mock ve HTTP uygulamaları · query key'ler
│   │   ├── hooks/               React Query hook'ları (bileşenlerin tek veri erişim noktası)
│   │   ├── components/          Grid, detay paneli, fabrika seçici, ihlal bildirimleri/geçmişi…
│   │   ├── config/ lib/         KKD sınıfları, ihlal türleri, durum etiketleri, saf yardımcılar
│   │   └── types.ts             Kamera, ihlal, özet modelleri (backend şemalarıyla aynı)
│   └── features/work-orders/ drones/   "Yakında" modülleri
│
├── backend/                     Merkez (FastAPI)
│   ├── app/
│   │   ├── main.py              Uygulama fabrikası, CORS, TrustedHost, canlılık kontrol döngüsü
│   │   ├── core/                config.py · errors.py · security.py (edge API anahtarları)
│   │   ├── db/                  base.py · session.py · seed.py
│   │   ├── models/              Factory, FactoryZone, Camera, EdgeNode, PpeViolation, enum'lar
│   │   ├── repositories/        Veritabanı erişimi (yalnızca sorgular)
│   │   ├── services/            İş mantığı (kameralar, ihlaller, edge, sistem)
│   │   ├── schemas/             Pydantic istek/yanıt modelleri (camelCase JSON)
│   │   ├── api/v1/              Panel API'si
│   │   ├── api/edge/            Edge API'si (API anahtarıyla)
│   │   └── cli/edge_nodes.py    Edge node oluşturma, kamera atama, anahtar yenileme
│   ├── alembic/versions/        Migration'lar
│   └── tests/                   pytest (her test geçici SQLite + migration + seed)
│
├── packages/contracts/          Edge ↔ merkez ortak sözleşmesi (Pydantic): olay, heartbeat, yapılandırma, enum'lar
│
└── vision/                      Saha (edge) servisi
    ├── fcs_vision/
    │   ├── sync/                client.py (merkez istemcisi) · outbox.py (kalıcı olay kuyruğu)
    │   ├── simulator/           Seed'li senaryo üreteci + komut satırı
    │   └── (3.2+) rules/ ingest/ inference/ tracking/ evidence/
    └── tests/                   Sahte merkez (httpx MockTransport) ile testler
```

**Backend katmanları:** `api` → `services` → `repositories` → `models`. HTTP katmanı iş kuralı içermez; servisler HTTP'den
bağımsızdır ve hata durumlarında `AppError` fırlatır; repository'ler yalnızca parametreli SQLAlchemy sorguları çalıştırır.

### Veri modeli

- `factories`: id, kod, ad, şehir, saat dilimi.
- `factory_zones`: fabrikaya bağlı bölgeler (kamera, drone ve iş kartları aynı bölgeyi kullanır).
- `edge_nodes`: fabrikaya bağlı saha sunucusu, API anahtarı özeti (SHA-256), etkinlik, son görülme, yazılım sürümü.
- `cameras`: kod, ad, bölge, konum, durum, son sinyal, akış bilgisi, KKD sınıfları, `is_simulated`, `edge_node_id`.
- `ppe_violations`: kamera, bölge, ihlal türü (`missing_ppe` / `restricted_area` / `missing_harness`), eksik KKD
  listesi, tespit ve bitiş zamanı, güven, önem, inceleme durumu, kaynak, açıklama; edge olaylarında ayrıca
  `event_id` (benzersiz), `edge_node_id`, `rule_id`, `track_id`, `model_ref`.

Fabrika bilgisi kamera ve ihlalde tekrar saklanmaz; bölge üzerinden türetilir (tutarsızlık riski olmaz).

Taşınabilirlik: enum'lar VARCHAR + CHECK kısıtı, sabit kısıt adları, UTC zamanlar, SQLite/PostgreSQL'de aynı çalışan JSON alanları.
SQLite migration'ları FK kontrolü kapalıyken çalışır ve sonunda `PRAGMA foreign_key_check` ile bütünlük doğrulanır.

### PostgreSQL'e geçiş

1. `requirements.txt` içindeki `psycopg[binary]` satırını açıp yükleyin.
2. `.env` → `DATABASE_URL=postgresql+psycopg://kullanici:sifre@localhost:5432/fcs`
3. `.\.venv\Scripts\python.exe -m alembic upgrade head` ve ardından `.\.venv\Scripts\python.exe -m app.db.seed`

### Yeni migration oluşturma

```powershell
cd backend
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "aciklama"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Not: Alembic, enum değer kümesi (CHECK kısıtı) değişikliklerini algılamaz; bu değişiklikler migration'a elle yazılır
(örnek: `20261115_..._factories_edge_nodes_and_edge_events.py`).

---

## Genişletme rehberi

- **Yeni ihlal türü:** `packages/contracts/fcs_contracts/enums.py` → `ViolationType`; migration'da CHECK kısıtını güncelleyin;
  frontend `features/cameras/types.ts` → `ViolationType` ve `config/violation-types.ts`.
- **Yeni KKD sınıfı:** `packages/contracts/fcs_contracts/enums.py` → `PpeClass`; frontend `PpeClassId` ve `config/ppe-classes.ts`.
- **Yeni backend modülü (ör. drones):** `models/` → `repositories/` → `services/` → `schemas/` → `api/v1/endpoints/` ve router kaydı, ardından migration.
- **Yeni frontend modülü:** `modules/registry.ts` kaydı + `features/<modül>/` (kamera modülüyle aynı yapı) + rota.
- **Gerçek kamera görüntüsü:** `SimulatedFeed` yer tutucudur; RTSP'nin WebRTC/HLS'e dönüştürülmesi gerekir (MediaMTX önerilir).

---

## Tamamlanmayanlar / sonraki aşamalar

| Aşama | İçerik                                                                                                           |
| ----- | ---------------------------------------------------------------------------------------------------------------- |
| 3.2   | Kural motoru (KKD, yasaklı bölge, yüksekte çalışma, süre ve tekrar bildirim kuralları) — video/model gerektirmez |
| 3.3   | Akış okuma: dosya/RTSP, yeniden bağlanma, kare örnekleme, gerçek heartbeat                                       |
| 3.4   | Çalıştırma ortamı, kişi dedektörü, takip, GPU/Docker kurulumu (YOLO lisans kararı gerekli)                       |
| 3.5   | KKD eklentisi, model kaydı, uçtan uca video → olay → panel                                                       |
| 3.6   | Panel: poligon/kural düzenleyici, kanıt görüntüleri, SSE ile anlık olaylar                                       |
| 3.7   | Emniyet kemeri tespiti (veri toplama, etiketleme, ince ayar)                                                     |
| 3.8   | Kullanıcı kimlik doğrulama ve roller, PostgreSQL, Docker Compose, pilot fabrika                                  |

Bilinen sınırlamalar:

- **Panel kimlik doğrulaması:** Panel API'sinde ve arayüzde gerçek kullanıcı doğrulaması yok (3.8). Edge API'si anahtarla korunur.
- **Kamera ekleme ve edge atama:** Kamera ekleme/düzenleme formu yok, API hazır. Edge'e kamera atama yalnızca CLI ile yapılır.
- **Anlık bildirim:** Panel 5 saniyede bir yeniler; SSE henüz yok.
- **Edge kameralarında tespit kutuları:** Edge kameralarında tespit kutusu gösterilmez; merkez tespit karesi tutmaz.

---

## Lisans

[MIT](LICENSE) — şablonun orijinal lisansı korunmuştur.
