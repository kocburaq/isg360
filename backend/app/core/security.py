"""Edge node API anahtarları.

- Anahtar yalnızca oluşturulurken bir kez gösterilir; veritabanında SHA-256 özeti saklanır.
- Anahtarlar 256 bit rastgele değer içerdiğinden (kaba kuvvetle tahmin edilemez),
  parola için gereken yavaş hash (bcrypt/argon2) yerine SHA-256 yeterlidir ve
  özet üzerinden doğrudan indeksli arama yapılabilir.
"""

import hashlib
import hmac
import secrets
from dataclasses import dataclass

API_KEY_PREFIX = "fcs_edge_"
# Anahtarı tanımak için saklanan ilk karakter sayısı (gizli kısmın yalnızca 4 karakteri)
VISIBLE_PREFIX_LENGTH = len(API_KEY_PREFIX) + 4


@dataclass(frozen=True)
class GeneratedApiKey:
    key: str
    hash: str
    prefix: str


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def generate_api_key() -> GeneratedApiKey:
    key = API_KEY_PREFIX + secrets.token_urlsafe(32)
    return GeneratedApiKey(key=key, hash=hash_api_key(key), prefix=key[:VISIBLE_PREFIX_LENGTH])


def looks_like_api_key(value: str) -> bool:
    return value.startswith(API_KEY_PREFIX) and 20 <= len(value) <= 128


def constant_time_equals(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
