"""
Driver Service Layer.

Encapsulates all driver domain logic and business rules.
Completely decoupled from HTTP frameworks (Flask) and data access engines (SQLAlchemy).
"""

from datetime import datetime, timezone
from typing import List, Dict, Any

from driverguard.app.exceptions import DriverNotFoundError, DuplicateDriverError
from driverguard.app.repositories.driver_repository import SQLAlchemyDriverRepository, driver_repository
from driverguard.app.schemas.driver import DriverCreateSchema, DriverUpdateSchema


class DriverService:
    """Service orchestrating Driver business operations and enforcing business rules."""

    def __init__(self, repo: SQLAlchemyDriverRepository = None):
        self.repo = repo or driver_repository

    def list_drivers(self) -> List[Dict[str, Any]]:
        """Retrieve list of all drivers."""
        return self.repo.get_all()

    def get_driver(self, driver_id: int) -> Dict[str, Any]:
        """
        Retrieve driver by ID.
        Raises DriverNotFoundError if driver does not exist.
        """
        driver = self.repo.get_by_id(driver_id)
        if not driver:
            raise DriverNotFoundError(driver_id)
        return driver

    def create_driver(self, data: DriverCreateSchema) -> Dict[str, Any]:
        """
        Enforce business rules for creating a driver:
        - Check unique email constraint
        - Check unique device_id constraint
        - Attach status and timestamps
        - Delegate saving to Repository
        """
        if self.repo.get_by_email(data.email):
            raise DuplicateDriverError("email", data.email)

        if self.repo.get_by_device_id(data.device_id):
            raise DuplicateDriverError("device_id", data.device_id)

        now = datetime.now(timezone.utc).isoformat()
        driver_payload = {
            "name": data.name,
            "email": data.email,
            "device_id": data.device_id,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }

        return self.repo.add(driver_payload)

    def update_driver(self, driver_id: int, data: DriverUpdateSchema) -> Dict[str, Any]:
        """
        Enforce business rules for updating a driver:
        - Verify driver existence
        - Check unique email constraint if email changed
        - Check unique device_id constraint if device_id changed
        - Apply update timestamps and delegate to Repository
        """
        existing = self.repo.get_by_id(driver_id)
        if not existing:
            raise DriverNotFoundError(driver_id)

        update_fields = data.model_dump(exclude_unset=True)

        if "email" in update_fields:
            email_owner = self.repo.get_by_email(update_fields["email"])
            if email_owner and email_owner["id"] != driver_id:
                raise DuplicateDriverError("email", update_fields["email"])

        if "device_id" in update_fields:
            device_owner = self.repo.get_by_device_id(update_fields["device_id"])
            if device_owner and device_owner["id"] != driver_id:
                raise DuplicateDriverError("device_id", update_fields["device_id"])

        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        updated_driver = self.repo.update(driver_id, update_fields)
        return updated_driver

    def delete_driver(self, driver_id: int) -> None:
        """
        Verify existence and delete driver.
        Raises DriverNotFoundError if driver does not exist.
        """
        existing = self.repo.get_by_id(driver_id)
        if not existing:
            raise DriverNotFoundError(driver_id)

        self.repo.delete(driver_id)


# Singleton instance for route dependency injection
driver_service = DriverService()
