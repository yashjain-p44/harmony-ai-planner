"""
Example demonstrating how to use GoogleAuthProvider with multiple repositories.

This shows how a single auth provider can be shared across multiple Google services,
allowing you to authenticate once and use the same credentials for Calendar, Tasks, etc.
"""

from .google_auth_provider import GoogleAuthProvider
from .calendar_repository import GoogleCalendarRepository
from .tasks_repository import GoogleTasksRepository


def example_shared_auth():
    """
    Example: Using a shared auth provider for multiple services.
    
    This approach allows you to:
    1. Authenticate once with all required scopes
    2. Share credentials across multiple repositories
    3. Avoid multiple authentication flows
    """
    # Define all scopes needed for your application
    all_scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/tasks"
    ]
    
    # Create a single auth provider with all scopes
    auth_provider = GoogleAuthProvider(scopes=all_scopes)
    
    # Use the same auth provider for multiple repositories
    calendar_repo = GoogleCalendarRepository(auth_provider=auth_provider)
    tasks_repo = GoogleTasksRepository(auth_provider=auth_provider)
    
    # Now you can use both repositories without re-authenticating
    events = calendar_repo.list_events()
    task_lists = tasks_repo.list_task_lists()
    
    print(f"Found {len(events)} calendar events")
    print(f"Found {len(task_lists)} task lists")


def example_separate_auth():
    """
    Example: Using separate auth providers for each service.
    
    This approach is useful when:
    1. You only need one service at a time
    2. You want to keep scopes minimal per service
    3. Services are used in different parts of your application
    """
    # Each repository creates its own auth provider
    calendar_repo = GoogleCalendarRepository()  # Uses calendar scopes only
    tasks_repo = GoogleTasksRepository()  # Uses tasks scopes only
    
    # Use repositories independently
    events = calendar_repo.list_events()
    task_lists = tasks_repo.list_task_lists()
    
    print(f"Found {len(events)} calendar events")
    print(f"Found {len(task_lists)} task lists")


if __name__ == "__main__":
    # Run the example
    print("=== Shared Auth Example ===")
    example_shared_auth()
    
    print("\n=== Separate Auth Example ===")
    example_separate_auth()

