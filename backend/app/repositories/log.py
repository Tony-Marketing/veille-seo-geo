"""Compatibility repositories for logs."""

from backend.app.repositories.admin import AuditLogRepository, ErrorLogRepository

__all__ = ["AuditLogRepository", "ErrorLogRepository"]
