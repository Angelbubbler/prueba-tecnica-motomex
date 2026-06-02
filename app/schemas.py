from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    marca: str
    modelo: str
    categoria: str
    precio: float = Field(gt=0)
    moneda: str = "MXN"
    ciudad: str
    estado: str
    stock: int = Field(ge=0)
    compatibilidad_general: list[str]
    especificaciones: dict[str, Any] = Field(default_factory=dict)

    @field_validator("moneda")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if value != "MXN":
            raise ValueError("La moneda soportada para esta prueba es MXN.")
        return value


class Product(ProductBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LeadCreate(BaseModel):
    session_id: str | None = None
    nombre: str | None = None
    ciudad: str | None = None
    estado: str | None = None
    producto_interes: str | None = None
    vehiculo: str | None = None
    anio_vehiculo: str | None = None
    direccion_envio: str | None = None
    desea_comprar: bool | None = None

    @field_validator(
        "session_id",
        "nombre",
        "ciudad",
        "estado",
        "producto_interes",
        "vehiculo",
        "anio_vehiculo",
        "direccion_envio",
        mode="before",
    )
    @classmethod
    def coerce_optional_text(cls, value):
        if value is None:
            return None
        return str(value)


class Lead(BaseModel):
    id: int
    session_id: str | None = None
    nombre: str | None
    ciudad: str | None
    estado: str | None
    producto_interes: str | None
    vehiculo: str | None
    anio_vehiculo: str | None
    direccion_envio: str | None
    lead_completo: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatMessage(BaseModel):
    message: str
    history: list[dict[str, str]] = []
    session_id: str | None = None

