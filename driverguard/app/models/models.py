"""
SQLAlchemy 2.0 ORM Models for DriverGuard.

Defines declarative mappings for:
- User
- Device
- CalibrationProfile
- DrivingSession
- FatigueEvent
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import String, Float, ForeignKey, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy models."""
    pass


class User(Base):
    """Maps to 'users' table."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String, default="driver", nullable=False)
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    calibration_profile: Mapped[Optional["CalibrationProfile"]] = relationship(
        "CalibrationProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    sessions: Mapped[List["DrivingSession"]] = relationship(
        "DrivingSession", back_populates="user", cascade="all, delete-orphan"
    )


class Device(Base):
    """Maps to 'devices' table."""
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    serial_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    sessions: Mapped[List["DrivingSession"]] = relationship(
        "DrivingSession", back_populates="device"
    )


class CalibrationProfile(Base):
    """Maps to 'calibration_profiles' table (1:1 with User)."""
    __tablename__ = "calibration_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    ear_threshold: Mapped[float] = mapped_column(Float, default=0.20, nullable=False)
    mar_threshold: Mapped[float] = mapped_column(Float, default=0.50, nullable=False)
    head_pitch_threshold: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="calibration_profile")


class DrivingSession(Base):
    """Maps to 'sessions' table (1:N with User and Device)."""
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[int] = mapped_column(
        ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False
    )
    start_time: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )
    end_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="ongoing", nullable=False)
    created_at: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    device: Mapped["Device"] = relationship("Device", back_populates="sessions")
    fatigue_events: Mapped[List["FatigueEvent"]] = relationship(
        "FatigueEvent", back_populates="session", cascade="all, delete-orphan"
    )


class FatigueEvent(Base):
    """Maps to 'fatigue_events' table (1:N with DrivingSession)."""
    __tablename__ = "fatigue_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[str] = mapped_column(
        String, default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    session: Mapped["DrivingSession"] = relationship("DrivingSession", back_populates="fatigue_events")
