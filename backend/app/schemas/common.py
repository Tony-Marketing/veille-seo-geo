"""Schémas Pydantic communs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    """Base schema configured for SQLAlchemy objects."""

    model_config = ConfigDict(from_attributes=True)


class TimestampRead(OrmModel):
    """Timestamp fields exposed in read schemas."""

    created_at: datetime
    updated_at: datetime
