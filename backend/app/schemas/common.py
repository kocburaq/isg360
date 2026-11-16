from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel


class ApiModel(BaseModel):
    """Yanıt modelleri: JSON alan adları camelCase (frontend TypeScript tipleriyle aynı)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        from_attributes=True,
    )


class RequestModel(ApiModel):
    """İstek gövdeleri: bilinmeyen alanlar reddedilir, metinlerin boşlukları kırpılır."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PatchModel(RequestModel):
    """Kısmi güncelleme: en az bir alan gerekir; zorunlu alanlara `null` gönderilemez."""

    _nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _check_fields(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("Güncellenecek en az bir alan gönderilmelidir.")
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in self._nullable_fields:
                raise ValueError(f"'{to_camel(name)}' alanı null olamaz.")
        return self

    def changes(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True, by_alias=False)


class Page[T](ApiModel):
    items: list[T]
    total: int = Field(description="Filtreye uyan toplam kayıt sayısı")
    page: int
    page_size: int
