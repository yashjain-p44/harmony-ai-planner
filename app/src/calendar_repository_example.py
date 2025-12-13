"""
Example usage of the Google Calendar Repository

This file demonstrates how to use the GoogleCalendarRepository class
to interact with the Google Calendar API.
"""

import datetime
from calendar_repository import GoogleCalendarRepository


def example_usage():
    """Example demonstrating various repository operations."""
    
    # Initialize the repository
    # It will handle authentication automatically
    calendar_repo = GoogleCalendarRepository()
    
    # Example 1: List upcoming events
    print("=== Listing upcoming events ===")
    events = calendar_repo.list_events(max_results=5)
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{start}: {event.get('summary', 'No title')}")
    
    # Example 2: Create a new event
    print("\n=== Creating a new event ===")
    start_time = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
    end_time = start_time + datetime.timedelta(hours=1)
    
    new_event = calendar_repo.create_event(
        summary="Meeting with Team",
        start_time=start_time,
        end_time=end_time,
        description="Discuss project progress",
        location="Conference Room A",
        attendees=["team@example.com"]
    )
    print(f"Created event: {new_event.get('summary')} (ID: {new_event.get('id')})")
    
    # Example 3: Get a specific event
    print("\n=== Getting a specific event ===")
    event_id = new_event.get("id")
    event = calendar_repo.get_event(event_id)
    print(f"Event: {event.get('summary')}")
    
    # Example 4: Update an event
    print("\n=== Updating an event ===")
    updated_event = calendar_repo.update_event(
        event_id=event_id,
        summary="Updated Meeting with Team",
        description="Updated description"
    )
    print(f"Updated event: {updated_event.get('summary')}")
    
    # Example 5: List all calendars
    print("\n=== Listing all calendars ===")
    calendars = calendar_repo.list_calendars()
    for calendar in calendars:
        print(f"Calendar: {calendar.get('summary')} (ID: {calendar.get('id')})")
    
    # Example 6: Delete an event (commented out to avoid accidental deletion)
    # print("\n=== Deleting an event ===")
    # calendar_repo.delete_event(event_id)
    # print(f"Deleted event: {event_id}")


if __name__ == "__main__":
    example_usage()

