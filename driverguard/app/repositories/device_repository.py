"""
SQLAlchemy Repository for Device entity operations.
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from driverguard.app.database import get_db_session, SessionLocal
from driverguard.app.models import Device, DrivingSession, User


class DeviceRepository:
    """Handles database persistence for Device objects."""

    def _get_session(self) -> Session:
        try:
            return get_db_session()
        except RuntimeError:
            return SessionLocal()

    def get_by_id(self, device_id: int) -> Optional[Device]:
        """Fetch device by primary key ID."""
        session = self._get_session()
        return session.get(Device, device_id)

    def get_by_serial_number(self, serial_number: str) -> Optional[Device]:
        """Fetch device by serial number."""
        session = self._get_session()
        stmt = select(Device).where(Device.serial_number == serial_number)
        return session.scalar(stmt)

    def get_devices_by_user_id(self, user_id: int) -> List[Device]:
        """Fetch all devices attached to a user via sessions."""
        session = self._get_session()
        stmt = (
            select(Device)
            .join(DrivingSession, Device.id == DrivingSession.device_id)
            .where(DrivingSession.user_id == user_id)
            .distinct()
        )
        return list(session.scalars(stmt).all())

    def attach_device_to_user(self, user: User, serial_number: str, model: str) -> Device:
        """Create a device and link it to a user via a new driving session."""
        session = self._get_session()
        now = datetime.now(timezone.utc).isoformat()

        # Check or create device
        device = session.scalar(select(Device).where(Device.serial_number == serial_number))
        if not device:
            device = Device(
                serial_number=serial_number,
                model=model,
                status="active",
                created_at=now,
            )
            session.add(device)

        # Create session mapping
        driving_session = DrivingSession(
            user=user,
            device=device,
            status="ongoing",
            start_time=now,
            created_at=now,
        )

        session.add(driving_session)
        session.commit()
        return device


device_repository = DeviceRepository()
