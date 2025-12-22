"""
Google API Repository Package

This package provides repositories for Google services (Calendar, Tasks, etc.)
with a shared authentication provider.
"""

from .google_auth_provider import GoogleAuthProvider
from .calendar_repository import GoogleCalendarRepository
from .tasks_repository import GoogleTasksRepository

__all__ = [
    "GoogleAuthProvider",
    "GoogleCalendarRepository",
    "GoogleTasksRepository",
]

