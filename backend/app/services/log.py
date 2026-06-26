"""Compatibility services for logs."""

from backend.app.services.admin import AuditLogService, ErrorLogService

__all__ = ["AuditLogService", "ErrorLogService"]
