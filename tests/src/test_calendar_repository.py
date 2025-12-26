"""
Test script for Google Calendar Repository

This script tests all methods of the GoogleCalendarRepository class.
Run this script to verify that the calendar repository is working correctly.
"""

import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.src.calendar_repository import GoogleCalendarRepository
from googleapiclient.errors import HttpError


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}TEST: {test_name}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")


def test_initialization():
    """Test repository initialization"""
    print_test_header("Repository Initialization")
    try:
        repo = GoogleCalendarRepository()
        print_success("Repository initialized successfully")
        return repo
    except FileNotFoundError as e:
        print_error(f"Initialization failed: {e}")
        print_info("Make sure credentials.json exists in app/creds/")
        return None
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        return None


def test_list_calendars(repo: GoogleCalendarRepository):
    """Test listing all calendars"""
    print_test_header("List Calendars")
    try:
        calendars = repo.list_calendars()
        print_success(f"Found {len(calendars)} calendar(s)")
        for calendar in calendars[:3]:  # Show first 3
            print(f"  - {calendar.get('summary', 'No name')} (ID: {calendar.get('id', 'N/A')})")
        if len(calendars) > 3:
            print(f"  ... and {len(calendars) - 3} more")
        return True
    except HttpError as e:
        print_error(f"Failed to list calendars: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_get_calendar(repo: GoogleCalendarRepository):
    """Test getting a specific calendar"""
    print_test_header("Get Calendar")
    try:
        calendar = repo.get_calendar("primary")
        print_success(f"Retrieved calendar: {calendar.get('summary', 'Primary')}")
        print(f"  Timezone: {calendar.get('timeZone', 'N/A')}")
        return True
    except HttpError as e:
        print_error(f"Failed to get calendar: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_list_events(repo: GoogleCalendarRepository):
    """Test listing events"""
    print_test_header("List Events")
    try:
        events = repo.list_events(max_results=5)
        print_success(f"Retrieved {len(events)} event(s)")
        if events:
            print("\nUpcoming events:")
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                summary = event.get("summary", "No title")
                print(f"  - {start}: {summary}")
        else:
            print_info("No upcoming events found")
        return True
    except HttpError as e:
        print_error(f"Failed to list events: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_create_event(repo: GoogleCalendarRepository):
    """Test creating an event"""
    print_test_header("Create Event")
    try:
        # Create an event 1 day from now
        start_time = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
        end_time = start_time + datetime.timedelta(hours=1)
        
        event = repo.create_event(
            summary="Test Event - Calendar Repository",
            start_time=start_time,
            end_time=end_time,
            description="This is a test event created by the calendar repository test script",
            location="Test Location"
        )
        
        event_id = event.get("id")
        print_success(f"Event created successfully")
        print(f"  Event ID: {event_id}")
        print(f"  Summary: {event.get('summary')}")
        print(f"  Start: {event['start'].get('dateTime', event['start'].get('date'))}")
        print(f"  End: {event['end'].get('dateTime', event['end'].get('date'))}")
        
        return event_id
    except HttpError as e:
        print_error(f"Failed to create event: {e}")
        return None
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return None


def test_get_event(repo: GoogleCalendarRepository, event_id: str):
    """Test getting a specific event"""
    print_test_header("Get Event")
    try:
        event = repo.get_event(event_id)
        print_success(f"Retrieved event: {event.get('summary')}")
        print(f"  Description: {event.get('description', 'No description')}")
        print(f"  Location: {event.get('location', 'No location')}")
        return True
    except HttpError as e:
        print_error(f"Failed to get event: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_update_event(repo: GoogleCalendarRepository, event_id: str):
    """Test updating an event"""
    print_test_header("Update Event")
    try:
        updated_event = repo.update_event(
            event_id=event_id,
            summary="Updated Test Event - Calendar Repository",
            description="This event has been updated by the test script",
            location="Updated Test Location"
        )
        print_success("Event updated successfully")
        print(f"  New Summary: {updated_event.get('summary')}")
        print(f"  New Description: {updated_event.get('description', 'No description')}")
        return True
    except HttpError as e:
        print_error(f"Failed to update event: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_list_events_with_filters(repo: GoogleCalendarRepository):
    """Test listing events with time filters"""
    print_test_header("List Events with Filters")
    try:
        # Get events for the next 7 days
        time_min = datetime.datetime.now(tz=datetime.timezone.utc)
        time_max = time_min + datetime.timedelta(days=7)
        
        events = repo.list_events(
            time_min=time_min,
            time_max=time_max,
            max_results=10
        )
        print_success(f"Found {len(events)} event(s) in the next 7 days")
        return True
    except HttpError as e:
        print_error(f"Failed to list events with filters: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_delete_event(repo: GoogleCalendarRepository, event_id: str, confirm: bool = False):
    """Test deleting an event"""
    print_test_header("Delete Event")
    if not confirm:
        print_info("Skipping delete test (set confirm=True to enable)")
        return True
    
    try:
        repo.delete_event(event_id)
        print_success(f"Event {event_id} deleted successfully")
        return True
    except HttpError as e:
        print_error(f"Failed to delete event: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def run_all_tests(cleanup: bool = False):
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("Google Calendar Repository Test Suite")
    print("="*60)
    print(f"{Colors.RESET}")
    
    # Initialize repository
    repo = test_initialization()
    if repo is None:
        print_error("Cannot proceed without repository initialization")
        return False
    
    test_results = []
    created_event_id = None
    
    try:
        # Test read operations
        test_results.append(("List Calendars", test_list_calendars(repo)))
        test_results.append(("Get Calendar", test_get_calendar(repo)))
        test_results.append(("List Events", test_list_events(repo)))
        test_results.append(("List Events with Filters", test_list_events_with_filters(repo)))
        
        # Test create operation
        created_event_id = test_create_event(repo)
        test_results.append(("Create Event", created_event_id is not None))
        
        if created_event_id:
            # Test operations on created event
            test_results.append(("Get Event", test_get_event(repo, created_event_id)))
            test_results.append(("Update Event", test_update_event(repo, created_event_id)))
            
            # Test delete (only if cleanup is enabled)
            if cleanup:
                test_results.append(("Delete Event", test_delete_event(repo, created_event_id, confirm=True)))
            else:
                test_results.append(("Delete Event", test_delete_event(repo, created_event_id, confirm=False)))
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print_error(f"Unexpected error during tests: {e}")
    
    # Print summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}Test Summary{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status}: {test_name}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.RESET}")
    
    if created_event_id and not cleanup:
        print(f"\n{Colors.YELLOW}Note: A test event was created (ID: {created_event_id})")
        print("Run with --cleanup flag to delete it automatically{Colors.RESET}")
    
    return passed == total


if __name__ == "__main__":
    # Check for cleanup flag
    cleanup = "--cleanup" in sys.argv or "-c" in sys.argv
    
    if cleanup:
        print(f"{Colors.YELLOW}Cleanup mode enabled - test events will be deleted{Colors.RESET}")
    
    success = run_all_tests(cleanup=cleanup)
    sys.exit(0 if success else 1)

