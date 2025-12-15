"""
Time Slot Finder

Finds available time slots in a calendar by analyzing existing events
and respecting preferred time windows.
"""

import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TimeWindow:
    """Represents a preferred time window for scheduling events."""
    start_hour: int  # 0-23
    end_hour: int  # 0-23
    start_minute: int = 0  # 0-59
    end_minute: int = 0  # 0-59


@dataclass
class TimeSlot:
    """Represents an available time slot."""
    start: datetime.datetime
    end: datetime.datetime
    duration_minutes: int
    
    def __post_init__(self):
        """Calculate duration after initialization."""
        delta = self.end - self.start
        self.duration_minutes = int(delta.total_seconds() / 60)


class TimeSlotFinder:
    """
    Finds free time slots in a calendar.
    
    Analyzes existing events and identifies gaps that can be used
    for scheduling new events.
    """
    
    def __init__(
        self,
        existing_events: List[dict],
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        preferred_time_windows: Optional[List[TimeWindow]] = None
    ):
        """
        Initialize the TimeSlotFinder.
        
        Args:
            existing_events: List of existing calendar events (from Google Calendar API)
            start_time: Start of the time window to search
            end_time: End of the time window to search
            preferred_time_windows: Optional list of preferred time windows
        """
        self.existing_events = existing_events
        self.start_time = start_time
        self.end_time = end_time
        self.preferred_time_windows = preferred_time_windows or []
    
    def find_free_slots(self, min_duration_minutes: int) -> List[TimeSlot]:
        """
        Find all free time slots that are at least min_duration_minutes long.
        
        Args:
            min_duration_minutes: Minimum duration required for a slot
            
        Returns:
            List of available TimeSlot objects, sorted by start time
        """
        # Parse existing events into time intervals
        busy_intervals = self._parse_events_to_intervals()
        
        # Sort by start time
        busy_intervals.sort(key=lambda x: x[0])
        
        # Find gaps between busy intervals
        free_slots = []
        current_time = self.start_time
        
        for busy_start, busy_end in busy_intervals:
            # If there's a gap before this busy period
            if current_time < busy_start:
                gap_duration = (busy_start - current_time).total_seconds() / 60
                if gap_duration >= min_duration_minutes:
                    free_slots.append(TimeSlot(
                        start=current_time,
                        end=busy_start,
                        duration_minutes=int(gap_duration)
                    ))
            
            # Move current_time to end of busy period
            if busy_end > current_time:
                current_time = busy_end
        
        # Check for gap after last busy period
        if current_time < self.end_time:
            gap_duration = (self.end_time - current_time).total_seconds() / 60
            if gap_duration >= min_duration_minutes:
                free_slots.append(TimeSlot(
                    start=current_time,
                    end=self.end_time,
                    duration_minutes=int(gap_duration)
                ))
        
        # Filter by preferred time windows if specified
        if self.preferred_time_windows:
            free_slots = self._filter_by_time_windows(free_slots)
        
        return free_slots
    
    def _parse_events_to_intervals(self) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """
        Parse calendar events into (start, end) datetime tuples.
        
        Returns:
            List of (start_datetime, end_datetime) tuples
        """
        intervals = []
        
        for event in self.existing_events:
            start = self._parse_event_time(event.get('start', {}))
            end = self._parse_event_time(event.get('end', {}))
            
            if start and end:
                # Only include events that overlap with our search window
                if start < self.end_time and end > self.start_time:
                    # Clip to search window
                    start = max(start, self.start_time)
                    end = min(end, self.end_time)
                    intervals.append((start, end))
        
        return intervals
    
    def _parse_event_time(self, time_dict: dict) -> Optional[datetime.datetime]:
        """
        Parse event time from Google Calendar API format.
        
        Args:
            time_dict: Event time dictionary with 'dateTime' or 'date' key
            
        Returns:
            Parsed datetime object, or None if invalid
        """
        if 'dateTime' in time_dict:
            # Full datetime
            return datetime.datetime.fromisoformat(time_dict['dateTime'].replace('Z', '+00:00'))
        elif 'date' in time_dict:
            # All-day event - treat as full day
            date_str = time_dict['date']
            # All-day events start at 00:00 and end at 23:59:59
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.replace(tzinfo=datetime.timezone.utc)
        return None
    
    def _filter_by_time_windows(self, slots: List[TimeSlot]) -> List[TimeSlot]:
        """
        Filter time slots to only include those within preferred time windows.
        
        Args:
            slots: List of time slots to filter
            
        Returns:
            Filtered list of time slots
        """
        filtered_slots = []
        
        for slot in slots:
            # Check if slot overlaps with any preferred time window
            for window in self.preferred_time_windows:
                if self._slot_in_window(slot, window):
                    filtered_slots.append(slot)
                    break
        
        return filtered_slots
    
    def _slot_in_window(self, slot: TimeSlot, window: TimeWindow) -> bool:
        """
        Check if a time slot overlaps with a preferred time window.
        
        Args:
            slot: Time slot to check
            window: Preferred time window
            
        Returns:
            True if slot overlaps with window, False otherwise
        """
        # Get the date of the slot
        slot_date = slot.start.date()
        
        # Create datetime objects for window boundaries on this date
        window_start = datetime.datetime.combine(
            slot_date,
            datetime.time(window.start_hour, window.start_minute)
        ).replace(tzinfo=slot.start.tzinfo)
        
        window_end = datetime.datetime.combine(
            slot_date,
            datetime.time(window.end_hour, window.end_minute)
        ).replace(tzinfo=slot.start.tzinfo)
        
        # Handle case where window spans midnight
        if window_end <= window_start:
            window_end += datetime.timedelta(days=1)
        
        # Check if slot overlaps with window
        return slot.start < window_end and slot.end > window_start

