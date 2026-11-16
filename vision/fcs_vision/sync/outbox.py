"""Kalıcı olay kuyruğu (outbox).

Olaylar önce yerel SQLite dosyasına yazılır, sonra merkeze gönderilir. Ağ kopar
veya edge yeniden başlarsa bekleyen olaylar kaybolmaz; merkez `eventId` ile
idempotent olduğundan tekrar gönderim çift kayıt oluşturmaz.

Durumlar:
    pending   gönderilmeyi bekliyor
    sent      merkez kabul etti (created / duplicate / updated)
    rejected  merkez kalıcı olarak reddetti; yeniden denenmez
"""

import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fcs_contracts import EventResultStatus, ViolationEvent

from fcs_vision.sync.client import CentralClient, TransientError

MAX_BATCH = 100

_SCHEMA = """
CREATE TABLE IF NOT EXISTS outbox (
    event_id   TEXT PRIMARY KEY,
    payload    TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'pending'
               CHECK (status IN ('pending', 'sent', 'rejected')),
    attempts   INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_outbox_status ON outbox (status, updated_at);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


class Outbox:
    def __init__(self, path: Path | str) -> None:
        self._db = sqlite3.connect(str(path))
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "Outbox":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def enqueue(self, event: ViolationEvent) -> None:
        """Olayı kuyruğa ekler. Aynı olay (ör. bitiş zamanıyla) tekrar eklenirse güncellenir."""
        with self._db:
            self._db.execute(
                """
                INSERT INTO outbox (event_id, payload, status, updated_at)
                VALUES (?, ?, 'pending', ?)
                ON CONFLICT (event_id) DO UPDATE SET
                    payload = excluded.payload,
                    status = 'pending',
                    updated_at = excluded.updated_at
                """,
                (str(event.event_id), event.model_dump_json(), _now()),
            )

    def pending(self, limit: int = MAX_BATCH) -> list[ViolationEvent]:
        rows = self._db.execute(
            "SELECT payload FROM outbox WHERE status = 'pending' ORDER BY updated_at LIMIT ?",
            (limit,),
        ).fetchall()
        return [ViolationEvent.model_validate_json(payload) for (payload,) in rows]

    def counts(self) -> dict[str, int]:
        rows = self._db.execute("SELECT status, COUNT(*) FROM outbox GROUP BY status")
        return {status: count for status, count in rows}

    def _mark(self, event_ids: Sequence[str], status: str, error: str | None = None) -> None:
        with self._db:
            self._db.executemany(
                "UPDATE outbox SET status = ?, last_error = ?, attempts = attempts + 1, "
                "updated_at = ? WHERE event_id = ?",
                [(status, error, _now(), eid) for eid in event_ids],
            )

    def flush(self, client: CentralClient) -> tuple[int, int]:
        """Bekleyen olayları gönderir. (gönderilen, reddedilen) döner.

        Ağ hatasında olaylar kuyrukta kalır ve TransientError yukarı iletilir.
        """
        sent = rejected = 0
        while batch := self.pending(MAX_BATCH):
            try:
                result = client.send_events(batch)
            except TransientError as exc:
                with self._db:
                    self._db.executemany(
                        "UPDATE outbox SET attempts = attempts + 1, last_error = ? "
                        "WHERE event_id = ?",
                        [(str(exc), str(e.event_id)) for e in batch],
                    )
                raise
            accepted = [
                str(r.event_id) for r in result.results if r.status != EventResultStatus.REJECTED
            ]
            refused = [r for r in result.results if r.status == EventResultStatus.REJECTED]
            self._mark(accepted, "sent")
            for r in refused:
                self._mark([str(r.event_id)], "rejected", r.reason)
            sent += len(accepted)
            rejected += len(refused)
            if len(result.results) < len(batch):  # beklenmedik yanıt; sonsuz döngüye girme
                break
        return sent, rejected

    def prune(self, older_than: timedelta = timedelta(days=7)) -> int:
        """Gönderilmiş eski kayıtları siler (reddedilenler inceleme için tutulur)."""
        cutoff = (datetime.now(UTC) - older_than).isoformat()
        with self._db:
            cur = self._db.execute(
                "DELETE FROM outbox WHERE status = 'sent' AND updated_at < ?", (cutoff,)
            )
        return cur.rowcount
