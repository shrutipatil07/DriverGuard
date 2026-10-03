"""
Pydantic schemas for Device validation.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeviceCreateSchema(BaseModel):
    """Schema for POST /api/v1/users/<id>/devices."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    serial_number: str = Field(..., min_length=1, description="Device unique serial number")
    model: str = Field(..., min_length=1, description="Hardware device model")

    @field_validator("serial_number", "model")
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"'{info.field_name}' must be a non-empty string.")
        return value.strip()
