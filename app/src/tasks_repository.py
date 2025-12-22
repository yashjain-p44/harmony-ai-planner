"""
Google Tasks API Repository

This module provides a repository class for interacting with the Google Tasks API.
It uses GoogleAuthProvider for authentication and provides methods to manage tasks.
"""

from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Handle both relative and absolute imports
try:
    from .google_auth_provider import GoogleAuthProvider
except ImportError:
    from google_auth_provider import GoogleAuthProvider


class GoogleTasksRepository:
    """
    Repository class for Google Tasks API operations.
    
    Provides methods to:
    - List tasks
    - Get task by ID
    - Create tasks
    - Update tasks
    - Delete tasks
    - List task lists
    """
    
    # Scopes for read and write access to tasks
    TASKS_SCOPES = ["https://www.googleapis.com/auth/tasks"]
    
    def __init__(
        self,
        auth_provider: Optional[GoogleAuthProvider] = None,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """
        Initialize the Google Tasks Repository.
        
        Args:
            auth_provider: Optional GoogleAuthProvider instance. If provided, will use
                         this provider for authentication. If None, creates a new provider
                         with tasks scopes.
            credentials_file: Path to the OAuth2 credentials JSON file.
                            Only used if auth_provider is None.
                            If None, uses default path: app/creds/credentials.json
            token_file: Path to store/load the token JSON file.
                       Only used if auth_provider is None.
                       If None, uses default path: app/src/token.json
        """
        # Use provided auth provider or create a new one
        if auth_provider is None:
            self.auth_provider = GoogleAuthProvider(
                scopes=self.TASKS_SCOPES,
                credentials_file=credentials_file,
                token_file=token_file
            )
        else:
            self.auth_provider = auth_provider
        
        # Build the service using credentials from auth provider
        credentials = self.auth_provider.get_credentials()
        self.service = build("tasks", "v1", credentials=credentials)
    
    def list_task_lists(self) -> List[Dict[str, Any]]:
        """
        List all task lists accessible by the user.
        
        Returns:
            List of task list dictionaries.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            task_lists_result = self.service.tasklists().list().execute()
            return task_lists_result.get("items", [])
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to list task lists: {error}".encode()
            )
    
    def get_task_list(self, task_list_id: str) -> Dict[str, Any]:
        """
        Get a specific task list by ID.
        
        Args:
            task_list_id: The ID of the task list to retrieve.
        
        Returns:
            Task list dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            task_list = self.service.tasklists().get(tasklist=task_list_id).execute()
            return task_list
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to get task list {task_list_id}: {error}".encode()
            )
    
    def list_tasks(
        self,
        task_list_id: str = "@default",
        show_completed: bool = False,
        show_deleted: bool = False,
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks from a task list.
        
        Args:
            task_list_id: Task list identifier. Defaults to "@default".
            show_completed: Whether to show completed tasks. Defaults to False.
            show_deleted: Whether to show deleted tasks. Defaults to False.
            max_results: Maximum number of tasks to return. If None, returns all.
        
        Returns:
            List of task dictionaries.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            params = {
                "tasklist": task_list_id,
                "showCompleted": show_completed,
                "showDeleted": show_deleted,
            }
            if max_results:
                params["maxResults"] = max_results
            
            tasks_result = self.service.tasks().list(**params).execute()
            return tasks_result.get("items", [])
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to list tasks: {error}".encode()
            )
    
    def get_task(self, task_id: str, task_list_id: str = "@default") -> Dict[str, Any]:
        """
        Get a specific task by ID.
        
        Args:
            task_id: The ID of the task to retrieve.
            task_list_id: Task list identifier. Defaults to "@default".
        
        Returns:
            Task dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            task = self.service.tasks().get(
                tasklist=task_list_id, task=task_id
            ).execute()
            return task
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to get task {task_id}: {error}".encode()
            )
    
    def create_task(
        self,
        title: str,
        task_list_id: str = "@default",
        notes: Optional[str] = None,
        due: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new task.
        
        Args:
            title: Title of the task (required).
            task_list_id: Task list identifier. Defaults to "@default".
            notes: Notes/description for the task.
            due: Due date in RFC3339 format (e.g., "2025-12-31T23:59:59Z").
            **kwargs: Additional task properties.
        
        Returns:
            Created task dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        task = {
            "title": title,
        }
        
        if notes:
            task["notes"] = notes
        if due:
            task["due"] = due
        
        # Add any additional properties
        task.update(kwargs)
        
        try:
            created_task = self.service.tasks().insert(
                tasklist=task_list_id, body=task
            ).execute()
            return created_task
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to create task: {error}".encode()
            )
    
    def update_task(
        self,
        task_id: str,
        task_list_id: str = "@default",
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing task.
        
        Args:
            task_id: The ID of the task to update.
            task_list_id: Task list identifier. Defaults to "@default".
            title: New title of the task.
            notes: New notes/description for the task.
            due: New due date in RFC3339 format.
            status: Task status ("needsAction" or "completed").
            **kwargs: Additional task properties to update.
        
        Returns:
            Updated task dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        # First, get the existing task
        task = self.get_task(task_id, task_list_id)
        
        # Update fields if provided
        if title is not None:
            task["title"] = title
        if notes is not None:
            task["notes"] = notes
        if due is not None:
            task["due"] = due
        if status is not None:
            task["status"] = status
        
        # Update any additional properties
        task.update(kwargs)
        
        try:
            updated_task = self.service.tasks().update(
                tasklist=task_list_id, task=task_id, body=task
            ).execute()
            return updated_task
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to update task {task_id}: {error}".encode()
            )
    
    def delete_task(self, task_id: str, task_list_id: str = "@default") -> None:
        """
        Delete a task.
        
        Args:
            task_id: The ID of the task to delete.
            task_list_id: Task list identifier. Defaults to "@default".
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            self.service.tasks().delete(
                tasklist=task_list_id, task=task_id
            ).execute()
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to delete task {task_id}: {error}".encode()
            )

