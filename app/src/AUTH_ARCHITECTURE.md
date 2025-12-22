# Google Authentication Architecture

This document describes the authentication architecture for Google API repositories.

## Overview

The authentication layer has been decoupled from individual repositories using a `GoogleAuthProvider` class. This allows:

1. **Shared Authentication**: Use a single auth provider across multiple Google services (Calendar, Tasks, etc.)
2. **Reusability**: Create new repositories without duplicating authentication code
3. **Flexibility**: Choose between shared or separate authentication per service

## Architecture

```
GoogleAuthProvider (handles OAuth2 flow, credentials, token refresh)
    ↓
    ├── GoogleCalendarRepository (uses auth provider)
    ├── GoogleTasksRepository (uses auth provider)
    └── [Future repositories can use the same provider]
```

## Components

### GoogleAuthProvider

Centralized authentication provider that handles:
- OAuth2 authentication flow
- Credential loading and saving
- Token refresh
- Scope management

**Location**: `app/src/google_auth_provider.py`

### GoogleCalendarRepository

Calendar API repository that uses `GoogleAuthProvider` for authentication.

**Location**: `app/src/calendar_repository.py`

### GoogleTasksRepository

Tasks API repository that uses `GoogleAuthProvider` for authentication.

**Location**: `app/src/tasks_repository.py`

## Usage Examples

### Example 1: Shared Authentication (Recommended)

Use a single auth provider for multiple services:

```python
from app.src import GoogleAuthProvider, GoogleCalendarRepository, GoogleTasksRepository

# Create auth provider with all required scopes
auth_provider = GoogleAuthProvider(
    scopes=[
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks"
    ]
)

# Share the same auth provider across repositories
calendar_repo = GoogleCalendarRepository(auth_provider=auth_provider)
tasks_repo = GoogleTasksRepository(auth_provider=auth_provider)

# Use both repositories (only authenticated once)
events = calendar_repo.list_events()
task_lists = tasks_repo.list_task_lists()
```

### Example 2: Separate Authentication

Each repository creates its own auth provider:

```python
from app.src import GoogleCalendarRepository, GoogleTasksRepository

# Each repository manages its own authentication
calendar_repo = GoogleCalendarRepository()  # Uses calendar scopes only
tasks_repo = GoogleTasksRepository()  # Uses tasks scopes only

# Use repositories independently
events = calendar_repo.list_events()
task_lists = tasks_repo.list_task_lists()
```

### Example 3: Backward Compatibility

The old API still works (for backward compatibility):

```python
from app.src import GoogleCalendarRepository

# Old way still works - uses default paths
calendar_repo = GoogleCalendarRepository()

# Or with custom paths
calendar_repo = GoogleCalendarRepository(
    credentials_file="/path/to/credentials.json",
    token_file="/path/to/token.json"
)
```

## Creating New Repositories

To create a new Google service repository:

1. **Define scopes** for your service
2. **Accept optional auth_provider** in constructor
3. **Create auth provider if not provided**
4. **Use credentials from auth provider** to build service

Example template:

```python
from typing import Optional
from googleapiclient.discovery import build
from .google_auth_provider import GoogleAuthProvider

class GoogleNewServiceRepository:
    SERVICE_SCOPES = ["https://www.googleapis.com/auth/newservice"]
    
    def __init__(
        self,
        auth_provider: Optional[GoogleAuthProvider] = None,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        if auth_provider is None:
            self.auth_provider = GoogleAuthProvider(
                scopes=self.SERVICE_SCOPES,
                credentials_file=credentials_file,
                token_file=token_file
            )
        else:
            self.auth_provider = auth_provider
        
        credentials = self.auth_provider.get_credentials()
        self.service = build("newservice", "v1", credentials=credentials)
    
    # Add your service methods here...
```

## Benefits

1. **DRY Principle**: Authentication logic is written once and reused
2. **Single Sign-On**: Authenticate once for multiple services
3. **Easier Testing**: Mock the auth provider instead of each repository
4. **Future-Proof**: Easy to add new Google services
5. **Backward Compatible**: Existing code continues to work

## File Structure

```
app/src/
├── google_auth_provider.py      # Centralized authentication
├── calendar_repository.py       # Calendar API repository
├── tasks_repository.py          # Tasks API repository
├── auth_example.py              # Usage examples
└── AUTH_ARCHITECTURE.md         # This file
```

## Migration Guide

If you have existing code using `GoogleCalendarRepository`:

**No changes required!** The old API is still supported:

```python
# This still works
repo = GoogleCalendarRepository()
```

To take advantage of shared authentication:

```python
# Create shared auth provider
auth = GoogleAuthProvider(scopes=[...])

# Use it with multiple repositories
calendar = GoogleCalendarRepository(auth_provider=auth)
tasks = GoogleTasksRepository(auth_provider=auth)
```

