"""
Pydantic schemas for User validation.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreateSchema(BaseModel):
    """Schema for POST /api/v1/users."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(..., min_length=1, description="User's full name")
    email: EmailStr = Field(..., description="User's valid email address")
    role: Optional[str] = Field(default="driver", description="Role: driver, operator, or admin")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("'name' must be a non-empty string.")
        return value.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: Optional[str]) -> str:
        if value is None:
            return "driver"
        allowed = {"driver", "operator", "admin"}
        if value.lower() not in allowed:
            raise ValueError(f"'role' must be one of {allowed}")
        return value.lower()
