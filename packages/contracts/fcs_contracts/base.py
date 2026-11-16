from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ContractModel(BaseModel):
    """Tüm sözleşme modelleri: camelCase JSON, bilinmeyen alan reddi, değişmez nesneler."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )


def _require_tz(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Zaman damgası zaman dilimi içermelidir (ör. 2026-11-15T10:00:00Z).")
    return value


# Edge ile merkez arasında yalnızca zaman dilimi bilgili zamanlar taşınır.
AwareDatetime = Annotated[datetime, AfterValidator(_require_tz)]
