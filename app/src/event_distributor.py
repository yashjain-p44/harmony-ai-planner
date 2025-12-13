"""
Event Distributor

Distributes required minutes across multiple events while respecting
constraints like min/max duration and minimum breaks between events.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

from time_slot_finder import TimeSlot


@dataclass
class ScheduledEvent:
    """Represents a scheduled event with timing and duration."""
    start_time: str  # ISO format datetime string
    end_time: str  # ISO format datetime string
    duration_minutes: int
    slot_index: int  # Index of the slot used
    slot_start: str  # Original slot start time


class EventDistributor:
    """
    Distributes required minutes across multiple events.
    
    Takes available time slots and distributes the required total minutes
    across them while respecting min/max duration and break constraints.
    """
    
    def __init__(
        self,
        total_minutes: int,
        min_event_duration: int,
        max_event_duration: int,
        min_break: int
    ):
        """
        Initialize the EventDistributor.
        
        Args:
            total_minutes: Total minutes to distribute across events
            min_event_duration: Minimum duration for each event (minutes)
            max_event_duration: Maximum duration for each event (minutes)
            min_break: Minimum break between events (minutes)
        """
        self.total_minutes = total_minutes
        self.min_event_duration = min_event_duration
        self.max_event_duration = max_event_duration
        self.min_break = min_break
    
    def distribute_events(
        self,
        available_slots: List[TimeSlot]
    ) -> Tuple[List[ScheduledEvent], int]:
        """
        Distribute required minutes across available time slots.
        
        Args:
            available_slots: List of available time slots
            
        Returns:
            Tuple of (list of scheduled events, remaining minutes not scheduled)
        """
        if not available_slots:
            return [], self.total_minutes
        
        scheduled_events = []
        remaining_minutes = self.total_minutes
        
        # Sort slots by start time
        sorted_slots = sorted(available_slots, key=lambda s: s.start)
        
        # Try to distribute events across slots
        for i, slot in enumerate(sorted_slots):
            if remaining_minutes <= 0:
                break
            
            # Check if we need a break from previous event
            if scheduled_events:
                last_event = scheduled_events[-1]
                # Calculate break needed
                break_needed = self._calculate_break_needed(
                    last_event.end_time,
                    slot.start.isoformat()
                )
                
                if break_needed < self.min_break:
                    # Not enough break time, skip this slot
                    continue
            
            # Determine how many minutes to use from this slot
            event_duration = self._calculate_event_duration(
                slot.duration_minutes,
                remaining_minutes
            )
            
            if event_duration >= self.min_event_duration:
                # Create event in this slot
                import datetime
                start_dt = slot.start
                end_dt = start_dt + datetime.timedelta(minutes=event_duration)
                
                scheduled_events.append(ScheduledEvent(
                    start_time=start_dt.isoformat(),
                    end_time=end_dt.isoformat(),
                    duration_minutes=event_duration,
                    slot_index=i,
                    slot_start=slot.start.isoformat()
                ))
                
                remaining_minutes -= event_duration
        
        return scheduled_events, remaining_minutes
    
    def _calculate_event_duration(
        self,
        slot_duration: int,
        remaining_minutes: int
    ) -> int:
        """
        Calculate optimal event duration for a slot.
        
        Args:
            slot_duration: Available duration in the slot (minutes)
            remaining_minutes: Minutes still needed to schedule
            
        Returns:
            Event duration in minutes
        """
        # Try to use max duration if possible
        if remaining_minutes >= self.max_event_duration:
            # Use max duration, but not more than slot allows
            return min(self.max_event_duration, slot_duration)
        else:
            # Use remaining minutes, but respect min/max constraints
            event_duration = min(remaining_minutes, slot_duration)
            
            # Ensure it's at least min_event_duration
            if event_duration < self.min_event_duration:
                # Can't fit minimum duration in this slot
                return 0
            
            # Don't exceed max_event_duration
            return min(event_duration, self.max_event_duration)
    
    def _calculate_break_needed(self, last_event_end: str, next_slot_start: str) -> int:
        """
        Calculate break time between last event and next slot.
        
        Args:
            last_event_end: ISO format datetime string of last event end
            next_slot_start: ISO format datetime string of next slot start
            
        Returns:
            Break duration in minutes
        """
        import datetime
        
        end_dt = datetime.datetime.fromisoformat(last_event_end.replace('Z', '+00:00'))
        start_dt = datetime.datetime.fromisoformat(next_slot_start.replace('Z', '+00:00'))
        
        if start_dt <= end_dt:
            return 0
        
        delta = start_dt - end_dt
        return int(delta.total_seconds() / 60)
    
    def get_optimal_event_count(self) -> Tuple[int, int]:
        """
        Calculate optimal number of events and minutes per event.
        
        Returns:
            Tuple of (number of events, minutes per event)
        """
        # Try to maximize number of events with max duration
        if self.total_minutes <= self.max_event_duration:
            return 1, self.total_minutes
        
        # Calculate how many max-duration events we can fit
        num_max_events = self.total_minutes // self.max_event_duration
        remaining = self.total_minutes % self.max_event_duration
        
        if remaining >= self.min_event_duration:
            # Can fit one more event with remaining minutes
            return num_max_events + 1, self.max_event_duration
        else:
            # Distribute remaining minutes across existing events
            if num_max_events > 0:
                # Add remaining to last event (if it doesn't exceed max)
                return num_max_events, self.max_event_duration
            else:
                # Can't even fit one event
                return 0, 0

