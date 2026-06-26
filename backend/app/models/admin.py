"""Modèles SQLAlchemy du module Administration."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.auth import User
from backend.app.models.base import TimestampMixin


class ApplicationSetting(TimestampMixin, Base):
    """Paramètre global de l'application."""

    __tablename__ = "application_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(30), default="string", nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="global", index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AiProvider(TimestampMixin, Base):
    """Fournisseur IA configurable."""

    __tablename__ = "ai_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    website_url: Mapped[str | None] = mapped_column(String(255))
    documentation_url: Mapped[str | None] = mapped_column(String(255))
    default_model: Mapped[str | None] = mapped_column(String(120))
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    max_concurrent_requests: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    models: Mapped[list["AiModel"]] = relationship(
        back_populates="provider",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="provider")


class AiModel(TimestampMixin, Base):
    """Modèle IA rattaché à un fournisseur."""

    __tablename__ = "ai_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    api_identifier: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    input_cost: Mapped[float | None] = mapped_column(Float)
    output_cost: Mapped[float | None] = mapped_column(Float)
    max_context_tokens: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    provider: Mapped[AiProvider] = relationship(back_populates="models")


class ApiKey(TimestampMixin, Base):
    """Clé API chiffrée."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    provider_id: Mapped[int | None] = mapped_column(ForeignKey("ai_providers.id", ondelete="SET NULL"))
    provider_name: Mapped[str | None] = mapped_column(String(120), index=True)
    encrypted_value: Mapped[str] = mapped_column(Text, nullable=False)
    value_fingerprint: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    provider: Mapped[AiProvider | None] = relationship(back_populates="api_keys")
    created_by_user: Mapped[User | None] = relationship(
        back_populates="api_keys_created",
        foreign_keys=[created_by_id],
    )
    updated_by_user: Mapped[User | None] = relationship(
        back_populates="api_keys_updated",
        foreign_keys=[updated_by_id],
    )


class AuditLog(TimestampMixin, Base):
    """Journal d'audit des actions applicatives."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    module: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(30), default="info", index=True, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(80))
    user_agent: Mapped[str | None] = mapped_column(String(255))
    result: Mapped[str] = mapped_column(String(50), default="success", nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[dict | None] = mapped_column(JSON)


class ErrorLog(TimestampMixin, Base):
    """Journal des erreurs applicatives."""

    __tablename__ = "error_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exception: Mapped[str] = mapped_column(String(255), nullable=False)
    traceback: Mapped[str | None] = mapped_column(Text)
    endpoint: Mapped[str | None] = mapped_column(String(255), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    environment: Mapped[str] = mapped_column(String(50), default="development", nullable=False)
    level: Mapped[str] = mapped_column(String(30), default="error", index=True, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)


class SystemParameter(TimestampMixin, Base):
    """Paramètre spécialisé SEO, GEO ou IA."""

    __tablename__ = "system_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    key: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
    value_type: Mapped[str] = mapped_column(String(30), default="string", nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
