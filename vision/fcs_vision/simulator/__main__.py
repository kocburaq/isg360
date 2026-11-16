"""Edge simülatörü — komut satırı.

Kullanım (vision klasöründe):
    python -m fcs_vision.simulator                       # sürekli çalışır (Ctrl+C ile durur)
    python -m fcs_vision.simulator --once                # tek tur (heartbeat + olay)
    python -m fcs_vision.simulator --event-probability 0.3 --seed 42
    python -m fcs_vision.simulator --offline cam-02      # cam-02'yi çevrimdışı bildir

Gerekli ayarlar: vision/.env içinde EDGE_API_URL ve EDGE_API_KEY.
"""

import argparse
import logging
import sys
import time
from datetime import UTC, datetime

from fcs_contracts import EdgeConfig, Heartbeat

from fcs_vision import __version__
from fcs_vision.config import get_settings
from fcs_vision.simulator.scenario import Scenario
from fcs_vision.sync.client import AuthError, CentralClient, CentralError, TransientError
from fcs_vision.sync.outbox import Outbox

log = logging.getLogger("fcs_vision.simulator")


def run_tick(
    client: CentralClient,
    outbox: Outbox,
    scenario: Scenario,
    config: EdgeConfig | None,
    etag: str | None,
) -> tuple[EdgeConfig | None, str | None]:
    """Bir tur: yapılandırmayı tazele → heartbeat → olay üret → kuyruğu boşalt."""
    new_config, etag = client.get_config(etag)
    if new_config is not None:
        if config is None or new_config.config_version != config.config_version:
            codes = ", ".join(c.code for c in new_config.cameras) or "yok"
            log.info(
                "Yapılandırma alındı: %s (%s) · kameralar: %s",
                new_config.node.name,
                new_config.node.factory_name,
                codes,
            )
        config = new_config
    assert config is not None
    if not config.cameras:
        log.warning("Bu edge node'a atanmış kamera yok; yalnızca heartbeat gönderiliyor.")

    now = datetime.now(UTC)
    result = client.send_heartbeat(
        Heartbeat(
            sent_at=now,
            software_version=f"sim-{__version__}",
            simulated=True,
            cameras=scenario.camera_heartbeats(config.cameras, now),
        )
    )
    if result.unknown_cameras:
        log.warning("Merkez bu kameraları tanımadı: %s", result.unknown_cameras)

    for event in scenario.tick(config.cameras, now):
        outbox.enqueue(event)
        state = "bitti" if event.ended_at else "yeni"
        log.info("Olay (%s): %s %s", state, event.camera_id, event.violation_type.value)

    sent, rejected = outbox.flush(client)
    if sent or rejected:
        log.info("Kuyruk: %d gönderildi, %d reddedildi", sent, rejected)
    return config, etag


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m fcs_vision.simulator")
    parser.add_argument("--once", action="store_true", help="Tek tur çalıştır ve çık")
    parser.add_argument("--interval", type=float, help="Tur aralığı (sn), varsayılan .env")
    parser.add_argument(
        "--event-probability",
        type=float,
        default=0.05,
        help="Her kamera için her turda yeni ihlal olasılığı (0-1)",
    )
    parser.add_argument("--seed", type=int, help="Tekrarlanabilir senaryo için rastgelelik tohumu")
    parser.add_argument(
        "--offline", default="", help="Çevrimdışı bildirilecek kameralar (virgülle ayrılmış)"
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # Her HTTP isteğini yazdırma; hatalar zaten ayrıca günlüğe yazılır
    logging.getLogger("httpx").setLevel(logging.WARNING)
    settings = get_settings()
    interval = args.interval or settings.heartbeat_interval_s
    scenario = Scenario(
        seed=args.seed,
        event_probability=args.event_probability,
        offline_cameras=frozenset(c.strip() for c in args.offline.split(",") if c.strip()),
    )

    try:
        client = CentralClient(
            settings.api_url,
            settings.api_key.get_secret_value(),
            timeout_s=settings.http_timeout_s,
        )
    except ValueError as exc:
        log.error("%s Bkz. vision/.env.example", exc)
        return 2

    log.info("Simülatör başladı → %s (tur aralığı %.0f sn)", settings.api_url, interval)
    config: EdgeConfig | None = None
    etag: str | None = None
    with client, Outbox(settings.resolved_outbox_path) as outbox:
        try:
            while True:
                try:
                    config, etag = run_tick(client, outbox, scenario, config, etag)
                except TransientError as exc:
                    # Ağ/merkez geçici olarak yok: olaylar kuyrukta bekler, sonraki turda denenir
                    log.warning("%s — kuyrukta bekleyen: %s", exc, outbox.counts().get("pending", 0))
                except AuthError as exc:
                    log.error("Kimlik doğrulama hatası: %s (EDGE_API_KEY'i kontrol edin)", exc.message)
                    return 1
                except CentralError as exc:
                    log.error("Merkez isteği reddetti: %s", exc)
                if args.once:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            log.info("Simülatör durduruldu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
