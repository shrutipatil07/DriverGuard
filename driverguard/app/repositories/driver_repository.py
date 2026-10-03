"""
SQLAlchemy Repository for Driver persistence.

Converts database access from raw SQL queries to SQLAlchemy 2.0 ORM operations.
Maintains exact interface compatibility with the existing service and route layers.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from driverguard.app.database import get_db_session, SessionLocal
from driverguard.app.models import User, Device, DrivingSession


class SQLAlchemyDriverRepository:
    """Repository implementation using SQLAlchemy ORM Sessions and Models."""

    def _get_session(self) -> Session:
        """Retrieve current HTTP request session or create standalone session."""
        try:
            return get_db_session()
        except RuntimeError:
            return SessionLocal()

    def _user_to_dict(self, user: User) -> Optional[Dict[str, Any]]:
        """Convert User model instance and relationships to dictionary format."""
        if user is None:
            return None

        device_id = "DEV-UNASSIGNED"
        if user.sessions:
            active_session = user.sessions[-1]
            if active_session.device:
                device_id = active_session.device.serial_number

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": user.role,
            "device_id": device_id,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all users using SQLAlchemy 2.0 select statement."""
        session = self._get_session()
        stmt = select(User)
        users = session.scalars(stmt).all()
        return [self._user_to_dict(user) for user in users]

    def get_by_id(self, driver_id: int) -> Optional[Dict[str, Any]]:
        """Find driver by primary key ID using SQLAlchemy session.get()."""
        session = self._get_session()
        user = session.get(User, driver_id)
        return self._user_to_dict(user)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find driver by email using select filter."""
        session = self._get_session()
        stmt = select(User).where(func.lower(User.email) == email.lower())
        user = session.scalar(stmt)
        return self._user_to_dict(user)

    def get_by_device_id(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Find driver by device serial number using ORM JOIN statement."""
        session = self._get_session()
        stmt = (
            select(User)
            .join(User.sessions)
            .join(DrivingSession.device)
            .where(Device.serial_number == device_id)
        )
        user = session.scalar(stmt)
        return self._user_to_dict(user)

    def add(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new User, Device, and Session using SQLAlchemy ORM objects.
        Demonstrates adding objects to session workspace and committing transaction.
        """
        session = self._get_session()
        now = datetime.now(timezone.utc).isoformat()

        # 1. Instantiate User model
        user = User(
            name=driver_data["name"],
            email=driver_data["email"],
            role="driver",
            created_at=now,
            updated_at=now,
        )

        # 2. Instantiate or find Device model
        device_serial = driver_data.get("device_id", f"DEV-{driver_data['name']}")
        device = session.scalar(select(Device).where(Device.serial_number == device_serial))
        if not device:
            device = Device(
                serial_number=device_serial,
                model="GuardVision-v1",
                status="active",
                created_at=now,
            )

        # 3. Instantiate DrivingSession connecting User and Device
        driving_session = DrivingSession(
            user=user,
            device=device,
            status="ongoing",
            start_time=now,
            created_at=now,
        )

        # Stage and commit via ORM Session
        session.add_all([user, device, driving_session])
        session.commit()

        return self._user_to_dict(user)

    def update(self, driver_id: int, updated_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update driver entity via ORM session change tracking."""
        session = self._get_session()
        user = session.get(User, driver_id)
        if not user:
            return None

        now = datetime.now(timezone.utc).isoformat()

        if "name" in updated_fields:
            user.name = updated_fields["name"]
        if "email" in updated_fields:
            user.email = updated_fields["email"]

        user.updated_at = now

        if "device_id" in updated_fields:
            new_device_serial = updated_fields["device_id"]
            device = session.scalar(select(Device).where(Device.serial_number == new_device_serial))
            if not device:
                device = Device(
                    serial_number=new_device_serial,
                    model="GuardVision-v1",
                    status="active",
                    created_at=now,
                )
                session.add(device)

            if user.sessions:
                user.sessions[-1].device = device
            else:
                driving_session = DrivingSession(
                    user=user,
                    device=device,
                    status="ongoing",
                    start_time=now,
                    created_at=now,
                )
                session.add(driving_session)

        session.commit()
        return self._user_to_dict(user)

    def delete(self, driver_id: int) -> bool:
        """Delete User entity via ORM session.delete()."""
        session = self._get_session()
        user = session.get(User, driver_id)
        if not user:
            return False

        session.delete(user)
        session.commit()
        return True


# Alias as driver_repository for service dependency injection
driver_repository = SQLAlchemyDriverRepository()
