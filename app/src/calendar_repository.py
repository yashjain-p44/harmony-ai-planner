"""
Google Calendar API Repository

This module provides a repository class for interacting with the Google Calendar API.
It handles authentication and provides methods to get and set calendar information.
"""

import datetime
import os
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarRepository:
    """
    Repository class for Google Calendar API operations.
    
    Provides methods to:
    - Get calendar events (list, get by ID)
    - Create calendar events
    - Update calendar events
    - Delete calendar events
    - List calendars
    """
    
    # Scopes for read and write access to calendar
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    
    def __init__(
        self,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """
        Initialize the Google Calendar Repository.
        
        Args:
            credentials_file: Path to the OAuth2 credentials JSON file.
                            If None, uses default path: app/creds/credentials.json
            token_file: Path to store/load the token JSON file.
                       If None, uses default path: app/src/token.json
        """
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths if not provided
        if credentials_file is None:
            credentials_file = os.path.join(script_dir, "..", "creds", "credentials.json")
        if token_file is None:
            token_file = os.path.join(script_dir, "token.json")
        
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Calendar API and build the service.
        Handles OAuth2 flow and token refresh.
        """
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If there are no (valid) credentials available, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth flow
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download your OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        
        # Build the service
        self.service = build("calendar", "v3", credentials=creds)
    
    def list_events(
        self,
        calendar_id: str = "primary",
        time_min: Optional[datetime.datetime] = None,
        time_max: Optional[datetime.datetime] = None,
        max_results: int = 10,
        single_events: bool = True,
        order_by: str = "startTime"
    ) -> List[Dict[str, Any]]:
        """
        List events from a calendar.
        
        Args:
            calendar_id: Calendar identifier. Defaults to "primary".
            time_min: Lower bound (exclusive) for an event's start time.
                     If None, uses current time.
            time_max: Upper bound (exclusive) for an event's end time.
                     If None, no upper bound.
            max_results: Maximum number of events to return. Defaults to 10.
            single_events: Whether to expand recurring events into instances.
                          Defaults to True.
            order_by: The order of the events returned. Defaults to "startTime".
        
        Returns:
            List of event dictionaries.
        
        Raises:
            HttpError: If the API request fails.
        """
        if time_min is None:
            time_min = datetime.datetime.now(tz=datetime.timezone.utc)
        
        time_min_str = time_min.isoformat()
        time_max_str = time_max.isoformat() if time_max else None
        
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min_str,
                    timeMax=time_max_str,
                    maxResults=max_results,
                    singleEvents=single_events,
                    orderBy=order_by,
                )
                .execute()
            )
            return events_result.get("items", [])
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to list events: {error}".encode()
            )
    
    def get_event(
        self,
        event_id: str,
        calendar_id: str = "primary"
    ) -> Dict[str, Any]:
        """
        Get a specific event by ID.
        
        Args:
            event_id: The ID of the event to retrieve.
            calendar_id: Calendar identifier. Defaults to "primary".
        
        Returns:
            Event dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            return event
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to get event {event_id}: {error}".encode()
            )
    
    def create_event(
        self,
        summary: str,
        start_time: datetime.datetime,
        end_time: Optional[datetime.datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = "primary",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            summary: Title/summary of the event.
            start_time: Start time of the event (datetime object).
            end_time: End time of the event (datetime object).
                      If None, defaults to 1 hour after start_time.
            description: Description of the event.
            location: Location of the event.
            attendees: List of attendee email addresses.
            calendar_id: Calendar identifier. Defaults to "primary".
            **kwargs: Additional event properties (e.g., colorId, reminders, etc.).
        
        Returns:
            Created event dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        if end_time is None:
            end_time = start_time + datetime.timedelta(hours=1)
        
        # Format datetime to RFC3339 format
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": str(start_time.tzinfo) if start_time.tzinfo else "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": str(end_time.tzinfo) if end_time.tzinfo else "UTC",
            },
        }
        
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]
        
        # Add any additional properties
        event.update(kwargs)
        
        try:
            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )
            return created_event
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to create event: {error}".encode()
            )
    
    def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing calendar event.
        
        Args:
            event_id: The ID of the event to update.
            calendar_id: Calendar identifier. Defaults to "primary".
            summary: New title/summary of the event.
            start_time: New start time of the event.
            end_time: New end time of the event.
            description: New description of the event.
            location: New location of the event.
            attendees: New list of attendee email addresses.
            **kwargs: Additional event properties to update.
        
        Returns:
            Updated event dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        # First, get the existing event
        event = self.get_event(event_id, calendar_id)
        
        # Update fields if provided
        if summary is not None:
            event["summary"] = summary
        if start_time is not None:
            event["start"] = {
                "dateTime": start_time.isoformat(),
                "timeZone": str(start_time.tzinfo) if start_time.tzinfo else "UTC",
            }
        if end_time is not None:
            event["end"] = {
                "dateTime": end_time.isoformat(),
                "timeZone": str(end_time.tzinfo) if end_time.tzinfo else "UTC",
            }
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location
        if attendees is not None:
            event["attendees"] = [{"email": email} for email in attendees]
        
        # Update any additional properties
        event.update(kwargs)
        
        try:
            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )
            return updated_event
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to update event {event_id}: {error}".encode()
            )
    
    def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary"
    ) -> None:
        """
        Delete a calendar event.
        
        Args:
            event_id: The ID of the event to delete.
            calendar_id: Calendar identifier. Defaults to "primary".
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to delete event {event_id}: {error}".encode()
            )
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List all calendars accessible by the user.
        
        Returns:
            List of calendar dictionaries.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            calendars_result = self.service.calendarList().list().execute()
            return calendars_result.get("items", [])
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to list calendars: {error}".encode()
            )
    
    def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """
        Get a specific calendar by ID.
        
        Args:
            calendar_id: The ID of the calendar to retrieve.
        
        Returns:
            Calendar dictionary.
        
        Raises:
            HttpError: If the API request fails.
        """
        try:
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            return calendar
        except HttpError as error:
            raise HttpError(
                resp=error.resp,
                content=f"Failed to get calendar {calendar_id}: {error}".encode()
            )

