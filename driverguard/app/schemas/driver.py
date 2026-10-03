"""
Pydantic schemas for DriverGuard request validation.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class DriverCreateSchema(BaseModel):
    """
    Schema for POST /api/v1/drivers (Driver Creation).

    Validates that:
    - name is a non-empty string
    - email is a valid email format
    - device_id is a non-empty string
    - unknown fields are strictly forbidden
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(..., min_length=1, description="Driver's full name")
    email: EmailStr = Field(..., description="Driver's valid email address")
    device_id: str = Field(..., min_length=1, description="Unique telemetry device ID")

    @field_validator("name", "device_id")
    @classmethod
    def validate_non_empty(cls, value: str, info) -> str:
        if not value or not value.strip():
            raise ValueError(f"'{info.field_name}' must be a non-empty string.")
        return value.strip()


class DriverUpdateSchema(BaseModel):
    """
    Schema for PATCH /api/v1/drivers/<id> (Partial Update).

    Validates that:
    - sent fields match valid data types and constraints
    - unknown fields are strictly forbidden
    - at least one field must be supplied
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = Field(default=None)
    device_id: Optional[str] = Field(default=None, min_length=1)

    @field_validator("name", "device_id")
    @classmethod
    def validate_non_empty_if_present(cls, value: Optional[str], info) -> Optional[str]:
        if value is not None:
            if not value or not value.strip():
                raise ValueError(f"'{info.field_name}' must be a non-empty string if provided.")
            return value.strip()
        return value
