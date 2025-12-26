"""
Test script for Google Tasks Repository

This script tests all methods of the GoogleTasksRepository to ensure
they work correctly with the Google Tasks API.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.src.tasks_repository import GoogleTasksRepository


def test_list_task_lists(repo: GoogleTasksRepository):
    """Test listing all task lists."""
    print("\n=== Testing list_task_lists() ===")
    try:
        task_lists = repo.list_task_lists()
        print(f"✓ Successfully retrieved {len(task_lists)} task list(s)")
        for task_list in task_lists:
            print(f"  - {task_list.get('title', 'Untitled')} (ID: {task_list.get('id')})")
        return task_lists
    except Exception as e:
        error_str = str(e)
        print(f"✗ Error: {error_str}")
        if "accessNotConfigured" in error_str or "API has not been used" in error_str:
            print("\n  ⚠️  Google Tasks API is not enabled in your Google Cloud project.")
            print("  Please enable it at: https://console.developers.google.com/apis/api/tasks.googleapis.com/overview")
        elif "insufficientPermissions" in error_str or "Insufficient Permission" in error_str:
            print("\n  ⚠️  Token was created with insufficient scopes.")
            print("  Please delete token.json and re-authenticate to get the tasks scope.")
        return []


def test_get_task_list(repo: GoogleTasksRepository, task_list_id: str = "@default"):
    """Test getting a specific task list."""
    print(f"\n=== Testing get_task_list('{task_list_id}') ===")
    try:
        task_list = repo.get_task_list(task_list_id)
        print(f"✓ Successfully retrieved task list: {task_list.get('title', 'Untitled')}")
        print(f"  ID: {task_list.get('id')}")
        print(f"  Updated: {task_list.get('updated')}")
        return task_list
    except Exception as e:
        error_str = str(e)
        print(f"✗ Error: {error_str}")
        if "accessNotConfigured" in error_str or "API has not been used" in error_str:
            print("\n  ⚠️  Google Tasks API is not enabled.")
        return None


def test_list_tasks(repo: GoogleTasksRepository, task_list_id: str = "@default"):
    """Test listing tasks from a task list."""
    print(f"\n=== Testing list_tasks('{task_list_id}') ===")
    try:
        tasks = repo.list_tasks(task_list_id=task_list_id, show_completed=False)
        print(f"✓ Successfully retrieved {len(tasks)} task(s)")
        for task in tasks[:5]:  # Show first 5 tasks
            title = task.get('title', 'Untitled')
            status = task.get('status', 'unknown')
            due = task.get('due', 'No due date')
            print(f"  - {title} (Status: {status}, Due: {due})")
        if len(tasks) > 5:
            print(f"  ... and {len(tasks) - 5} more task(s)")
        return tasks
    except Exception as e:
        error_str = str(e)
        print(f"✗ Error: {error_str}")
        if "accessNotConfigured" in error_str or "API has not been used" in error_str:
            print("\n  ⚠️  Google Tasks API is not enabled.")
        return []


def test_create_task(repo: GoogleTasksRepository, task_list_id: str = "@default"):
    """Test creating a new task."""
    print(f"\n=== Testing create_task() ===")
    try:
        test_task = repo.create_task(
            title="Test Task - Created by test script",
            task_list_id=task_list_id,
            notes="This is a test task created to verify the repository works correctly."
        )
        print(f"✓ Successfully created task: {test_task.get('title')}")
        print(f"  ID: {test_task.get('id')}")
        return test_task
    except Exception as e:
        error_str = str(e)
        print(f"✗ Error: {error_str}")
        if "accessNotConfigured" in error_str or "API has not been used" in error_str:
            print("\n  ⚠️  Google Tasks API is not enabled.")
        return None


def test_get_task(repo: GoogleTasksRepository, task_id: str, task_list_id: str = "@default"):
    """Test getting a specific task."""
    print(f"\n=== Testing get_task('{task_id}') ===")
    try:
        task = repo.get_task(task_id, task_list_id=task_list_id)
        print(f"✓ Successfully retrieved task: {task.get('title')}")
        print(f"  Status: {task.get('status')}")
        print(f"  Notes: {task.get('notes', 'No notes')}")
        return task
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_update_task(repo: GoogleTasksRepository, task_id: str, task_list_id: str = "@default"):
    """Test updating a task."""
    print(f"\n=== Testing update_task('{task_id}') ===")
    try:
        updated_task = repo.update_task(
            task_id=task_id,
            task_list_id=task_list_id,
            notes="Updated notes - This task was updated by the test script."
        )
        print(f"✓ Successfully updated task: {updated_task.get('title')}")
        print(f"  Updated notes: {updated_task.get('notes')}")
        return updated_task
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def test_delete_task(repo: GoogleTasksRepository, task_id: str, task_list_id: str = "@default"):
    """Test deleting a task."""
    print(f"\n=== Testing delete_task('{task_id}') ===")
    try:
        repo.delete_task(task_id, task_list_id=task_list_id)
        print(f"✓ Successfully deleted task with ID: {task_id}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Tasks Repository Test Suite")
    print("=" * 60)
    print("\nNOTE: Make sure Google Tasks API is enabled in your Google Cloud Console:")
    print("      https://console.developers.google.com/apis/api/tasks.googleapis.com/overview")
    print("=" * 60)
    
    # Initialize repository
    print("\nInitializing GoogleTasksRepository...")
    try:
        repo = GoogleTasksRepository()
        print("✓ Repository initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize repository: {e}")
        if "credentials file not found" in str(e).lower():
            print("\n  ⚠️  Make sure credentials.json exists in app/creds/")
        return
    
    # Test 1: List task lists
    task_lists = test_list_task_lists(repo)
    
    # Use default task list for testing
    task_list_id = "@default"
    if task_lists:
        # Try to use the first task list if available
        first_list_id = task_lists[0].get('id')
        if first_list_id:
            task_list_id = first_list_id
            print(f"\nUsing task list: {task_lists[0].get('title')} (ID: {task_list_id})")
    
    # Test 2: Get specific task list
    test_get_task_list(repo, task_list_id)
    
    # Test 3: List tasks
    existing_tasks = test_list_tasks(repo, task_list_id)
    
    # Test 4: Create a new task
    created_task = test_create_task(repo, task_list_id)
    
    if created_task:
        task_id = created_task.get('id')
        
        # Test 5: Get the created task
        test_get_task(repo, task_id, task_list_id)
        
        # Test 6: Update the task
        test_update_task(repo, task_id, task_list_id)
        
        # Test 7: Delete the task (cleanup)
        print("\n--- Cleaning up test task ---")
        test_delete_task(repo, task_id, task_list_id)
    
    print("\n" + "=" * 60)
    print("Test Suite Completed")
    print("=" * 60)


if __name__ == "__main__":
    main()

