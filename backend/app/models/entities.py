"""Modèles SQLAlchemy principaux."""

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin


class Entity(TimestampMixin, Base):
    """Entité suivie par la plateforme."""

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    websites: Mapped[list["Website"]] = relationship(back_populates="entity")


class Website(TimestampMixin, Base):
    """Site web suivi."""

    __tablename__ = "websites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    url: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    cms: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    entity: Mapped[Entity | None] = relationship(back_populates="websites")


class Competitor(TimestampMixin, Base):
    """Concurrent d'une entité ou d'un site."""

    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    website_url: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Keyword(TimestampMixin, Base):
    """Mot-clé suivi."""

    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"))
    term: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[str | None] = mapped_column(String(50))


class Url(TimestampMixin, Base):
    """URL auditée ou suivie."""

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int | None] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer)
    is_indexable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Report(TimestampMixin, Base):
    """Rapport généré."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    report_type: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)


class ProjectTask(TimestampMixin, Base):
    """Tâche projet."""

    __tablename__ = "project_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_id: Mapped[int | None] = mapped_column(ForeignKey("entities.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="todo", nullable=False)
    priority: Mapped[str | None] = mapped_column(String(50))
