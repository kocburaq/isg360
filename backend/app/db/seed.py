"""Örnek (demo) veri yükleyici — tekrar çalıştırılabilir.

Kullanım (backend klasöründe):
    python -m app.db.seed           # eksik kayıtları ekler, mevcutlara dokunmaz
    python -m app.db.seed --reset   # örnek veriyi silip baştan yükler (edge node'lar dahil)

Veriler frontend'deki `src/mocks/` ile aynıdır ve SİMÜLASYONDUR:
kameralar `is_simulated=True`, ihlaller `source="simulation"` olarak işaretlenir.
Mevcut kayıtlar güncellenmez; böylece arayüzde yapılan değişiklikler (ör. "İncelendi")
seed tekrar çalıştırıldığında kaybolmaz.
"""

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.session import get_session_factory
from app.models import Camera, EdgeNode, Factory, FactoryZone, PpeViolation
from app.models.enums import (
    CameraStatus,
    DetectionSource,
    ViolationSeverity,
    ViolationStatus,
)

# (id, kod, ad, şehir) — "fac-default" migration'daki varsayılan fabrika ile aynıdır
FACTORIES = [
    ("fac-default", "F01", "Merkez Fabrika", "İstanbul"),
    ("fac-gebze", "F02", "Gebze Fabrikası", "Kocaeli"),
]

# (id, ad, alan, fabrika)
ZONES = [
    ("zone-entrance", "Giriş ve Güvenlik", "A Blok", "fac-default"),
    ("zone-assembly", "Montaj Holü", "B Blok", "fac-default"),
    ("zone-production", "Üretim Atölyesi", "B Blok", "fac-default"),
    ("zone-logistics", "Lojistik ve Depo", "C Blok", "fac-default"),
    ("zone-hazmat", "Tehlikeli Madde Alanı", "D Blok", "fac-default"),
    ("zone-press", "Pres Hattı", "P1 Hol", "fac-gebze"),
]

# (id, kod, ad, bölge, konum, durum, son sinyal [dk önce], çözünürlük, fps)
CAMERAS = [
    ("cam-01", "CAM-01", "Ana Giriş Kapısı", "zone-entrance",
     "Personel turnikeleri, kuzey cephe", "online", 0, "1920×1080", 25),
    ("cam-02", "CAM-02", "Montaj Hattı 1", "zone-assembly",
     "Hat başı, istasyon 1–4", "online", 0, "1920×1080", 25),
    ("cam-03", "CAM-03", "Kaynak Atölyesi", "zone-production",
     "Kaynak kabinleri önü", "online", 1, "2560×1440", 25),
    ("cam-04", "CAM-04", "Depo ve Sevkiyat", "zone-logistics",
     "Yükleme rampası 2", "online", 0, "1920×1080", 25),
    ("cam-05", "CAM-05", "Forklift Koridoru", "zone-logistics",
     "Raf blokları arası ana koridor", "offline", 134, "1280×720", 15),
    ("cam-06", "CAM-06", "Kimyasal Depolama", "zone-hazmat",
     "Depo kapısı iç taraf", "online", 2, "1920×1080", 25),
    ("cam-07", "CAM-07", "Pres 1 Önü", "zone-press",
     "Pres 1 operatör alanı", "online", 0, "1920×1080", 25),
    ("cam-08", "CAM-08", "Bobin Stok Alanı", "zone-press",
     "Vinç altı stok sahası", "online", 1, "1920×1080", 25),
]  # fmt: skip

# (kamera, eksik KKD, kaç dakika önce, durum, güven)
VIOLATIONS = [
    ("cam-01", ["vest"], 3, "open", 0.91),
    ("cam-02", ["helmet"], 6, "open", 0.88),
    ("cam-04", ["helmet", "vest"], 11, "open", 0.93),
    ("cam-02", ["vest"], 27, "acknowledged", 0.84),
    ("cam-01", ["helmet"], 48, "acknowledged", 0.79),
    ("cam-03", ["vest"], 75, "resolved", 0.86),
    ("cam-04", ["vest"], 96, "resolved", 0.90),
    ("cam-05", ["helmet"], 150, "resolved", 0.81),
    ("cam-02", ["helmet", "vest"], 190, "resolved", 0.95),
    ("cam-06", ["helmet"], 260, "resolved", 0.87),
    ("cam-01", ["vest"], 340, "resolved", 0.83),
    ("cam-04", ["helmet"], 420, "resolved", 0.89),
    ("cam-03", ["helmet"], 610, "resolved", 0.92),
    ("cam-02", ["vest"], 980, "resolved", 0.80),
    ("cam-05", ["helmet", "vest"], 1260, "resolved", 0.94),
    ("cam-01", ["helmet"], 1500, "resolved", 0.85),
    ("cam-06", ["vest"], 1720, "resolved", 0.82),
    ("cam-04", ["vest"], 2100, "resolved", 0.88),
    ("cam-02", ["helmet"], 2490, "resolved", 0.90),
    ("cam-03", ["helmet", "vest"], 2880, "resolved", 0.96),
    ("cam-01", ["vest"], 3300, "resolved", 0.78),
    ("cam-04", ["helmet"], 3720, "resolved", 0.87),
]

# Kimliği sabit ek kayıtlar (yukarıdaki listenin numaralandırması değişmesin diye ayrı)
# (id, kamera, eksik KKD, kaç dakika önce, durum, güven)
EXTRA_VIOLATIONS = [
    ("vio-0023", "cam-07", ["helmet"], 400, "resolved", 0.86),
    ("vio-0024", "cam-08", ["vest"], 2600, "resolved", 0.84),
]

PPE_LABELS = {"helmet": "baret", "vest": "reflektörlü yelek"}


def severity_for(missing: list[str]) -> ViolationSeverity:
    if len(missing) > 1 or missing[0] == "helmet":
        return ViolationSeverity.HIGH
    return ViolationSeverity.MEDIUM


@dataclass
class SeedResult:
    factories: int = 0
    zones: int = 0
    cameras: int = 0
    violations: int = 0


def seed_demo_data(session: Session, *, now: datetime | None = None) -> SeedResult:
    """Eksik örnek kayıtları ekler. Var olan kayıtlar değiştirilmez."""
    now = now or datetime.now(UTC)
    result = SeedResult()
    factory_ids = set(session.scalars(select(Factory.id)))
    for factory_id, code, name, city in FACTORIES:
        if factory_id not in factory_ids:
            session.add(Factory(id=factory_id, code=code, name=name, city=city))
            result.factories += 1
    session.flush()

    zone_by_id = {z.id: z for z in session.scalars(select(FactoryZone))}
    for zone_id, name, area, factory_id in ZONES:
        if zone_id not in zone_by_id:
            session.add(FactoryZone(id=zone_id, name=name, area=area, factory_id=factory_id))
            result.zones += 1
    session.flush()

    cameras = {c.id: c for c in session.scalars(select(Camera))}
    for cid, code, name, zone_id, location, status, seen_ago, res, fps in CAMERAS:
        if cid in cameras:
            continue
        camera = Camera(
            id=cid,
            code=code,
            name=name,
            zone_id=zone_id,
            location=location,
            status=CameraStatus(status),
            last_seen_at=now - timedelta(minutes=seen_ago),
            stream_protocol="rtsp",
            stream_configured=False,
            resolution=res,
            fps=fps,
            ppe_classes=["helmet", "vest"],
            is_simulated=True,
        )
        session.add(camera)
        cameras[cid] = camera
        result.cameras += 1
    session.flush()

    existing = set(session.scalars(select(PpeViolation.id)))
    total = len(VIOLATIONS)
    specs = [
        (f"vio-{total - index:04d}", *spec) for index, spec in enumerate(VIOLATIONS)
    ] + EXTRA_VIOLATIONS
    for vid, camera_id, missing, ago, status, confidence in specs:
        if vid in existing:
            continue
        labels = ", ".join(PPE_LABELS[m] for m in missing)
        detected_at = now - timedelta(minutes=ago)
        session.add(
            PpeViolation(
                id=vid,
                camera_id=camera_id,
                zone_id=cameras[camera_id].zone_id,
                missing_ppe=missing,
                detected_at=detected_at,
                confidence=confidence,
                severity=severity_for(missing),
                status=ViolationStatus(status),
                source=DetectionSource.SIMULATION,
                description=f"Simüle edilmiş tespit: {labels} eksik.",
                reviewed_at=None if status == "open" else detected_at + timedelta(minutes=2),
            )
        )
        result.violations += 1

    session.commit()
    return result


def reset_demo_data(session: Session) -> None:
    """Tüm verileri siler: ihlaller → kameralar → edge node'lar → bölgeler → fabrikalar.

    Edge node'lar ve API anahtarları da silinir; yeniden oluşturulmaları gerekir.
    """
    session.execute(delete(PpeViolation))
    session.execute(delete(Camera))
    session.execute(delete(EdgeNode))
    session.execute(delete(FactoryZone))
    session.execute(delete(Factory))
    session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Örnek kamera ve ihlal verilerini yükler.")
    parser.add_argument(
        "--reset", action="store_true", help="Mevcut verileri silip örnek veriyi baştan yükler."
    )
    args = parser.parse_args()

    with get_session_factory()() as session:
        if args.reset:
            reset_demo_data(session)
            print("Mevcut veriler (edge node'lar dahil) silindi.")
        result = seed_demo_data(session)

    print(
        f"Eklenen kayıtlar: fabrika: {result.factories}, bölge: {result.zones}, "
        f"kamera: {result.cameras}, ihlal: {result.violations}"
    )
    if result.factories == result.zones == result.cameras == result.violations == 0:
        print("Örnek veriler zaten yüklü; mevcut kayıtlar değiştirilmedi.")


if __name__ == "__main__":
    main()
