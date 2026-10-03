"""
SQLAlchemy Repository for User entity operations.
"""

from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from driverguard.app.database import get_db_session, SessionLocal
from driverguard.app.models import User


class UserRepository:
    """Handles database persistence for User objects."""

    def _get_session(self) -> Session:
        try:
            return get_db_session()
        except RuntimeError:
            return SessionLocal()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch user by primary key ID."""
        session = self._get_session()
        return session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch user by unique email address."""
        session = self._get_session()
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return session.scalar(stmt)

    def get_all(self) -> List[User]:
        """Fetch all users."""
        session = self._get_session()
        return list(session.scalars(select(User)).all())

    def add(self, name: str, email: str, role: str = "driver") -> User:
        """Create and persist a new user entity."""
        session = self._get_session()
        now = datetime.now(timezone.utc).isoformat()
        user = User(
            name=name,
            email=email,
            role=role,
            created_at=now,
            updated_at=now,
        )
        session.add(user)
        session.commit()
        return user


user_repository = UserRepository()
