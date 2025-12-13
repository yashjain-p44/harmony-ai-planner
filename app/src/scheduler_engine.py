"""
Scheduler Engine

Main orchestrator for scheduling events based on plan requirements.
Coordinates time slot finding, event distribution, and calendar event creation.
"""

import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from calendar_repository import GoogleCalendarRepository
from models.plan_requirement import PlanRequirement
from time_slot_finder import TimeSlotFinder, TimeSlot
from event_distributor import EventDistributor, ScheduledEvent


@dataclass
class SchedulingDecision:
    """Represents a decision made during scheduling."""
    step: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class SchedulingResult:
    """Result of a scheduling operation."""
    success: bool
    events_created: List[Dict[str, Any]] = field(default_factory=list)
    event_ids: List[str] = field(default_factory=list)
    total_minutes_scheduled: int = 0
    remaining_minutes: int = 0
    decision_log: List[SchedulingDecision] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class SchedulerEngine:
    """
    Main scheduler engine that orchestrates event scheduling.
    
    Takes plan requirements, finds available time slots, distributes events,
    and creates calendar events.
    """
    
    def __init__(self, calendar_repository: GoogleCalendarRepository):
        """
        Initialize the SchedulerEngine.
        
        Args:
            calendar_repository: GoogleCalendarRepository instance for calendar operations
        """
        self.calendar_repository = calendar_repository
    
    def schedule_plan(self, requirement: PlanRequirement) -> SchedulingResult:
        """
        Schedule events based on plan requirements.
        
        Args:
            requirement: PlanRequirement object with scheduling requirements
            
        Returns:
            SchedulingResult with created events and decision log
        """
        result = SchedulingResult(success=False)
        
        try:
            # Step 1: Calculate scheduling window
            result.decision_log.append(SchedulingDecision(
                step="window_calculation",
                message=f"Calculating scheduling window: {requirement.scheduling_window_days} days",
                details={"window_days": requirement.scheduling_window_days}
            ))
            
            start_time, end_time = self._calculate_scheduling_window(
                requirement.scheduling_window_days
            )
            
            result.decision_log.append(SchedulingDecision(
                step="window_set",
                message=f"Scheduling window: {start_time.isoformat()} to {end_time.isoformat()}",
                details={
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            ))
            
            # Step 2: Fetch existing events
            result.decision_log.append(SchedulingDecision(
                step="fetch_events",
                message="Fetching existing calendar events",
                details={"calendar_id": requirement.calendar_id}
            ))
            
            existing_events = self.calendar_repository.list_events(
                calendar_id=requirement.calendar_id,
                time_min=start_time,
                time_max=end_time,
                max_results=2500,  # Large number to get all events
                single_events=True
            )
            
            result.decision_log.append(SchedulingDecision(
                step="events_fetched",
                message=f"Found {len(existing_events)} existing events in window",
                details={"event_count": len(existing_events)}
            ))
            
            # Step 3: Find free time slots
            result.decision_log.append(SchedulingDecision(
                step="find_slots",
                message=f"Finding free time slots (min duration: {requirement.min_event_duration} min)",
                details={"min_duration": requirement.min_event_duration}
            ))
            
            slot_finder = TimeSlotFinder(
                existing_events=existing_events,
                start_time=start_time,
                end_time=end_time,
                preferred_time_windows=requirement.preferred_time_windows
            )
            
            free_slots = slot_finder.find_free_slots(
                min_duration_minutes=requirement.min_event_duration
            )
            
            result.decision_log.append(SchedulingDecision(
                step="slots_found",
                message=f"Found {len(free_slots)} available time slots",
                details={
                    "slot_count": len(free_slots),
                    "total_available_minutes": sum(s.duration_minutes for s in free_slots)
                }
            ))
            
            if not free_slots:
                result.errors.append("No available time slots found in the scheduling window")
                result.decision_log.append(SchedulingDecision(
                    step="no_slots",
                    message="No available time slots found",
                    details={"error": "Cannot schedule events without available slots"}
                ))
                return result
            
            # Step 4: Distribute events across slots
            result.decision_log.append(SchedulingDecision(
                step="distribute_events",
                message=f"Distributing {requirement.total_minutes_per_week} minutes across events",
                details={
                    "total_minutes": requirement.total_minutes_per_week,
                    "min_duration": requirement.min_event_duration,
                    "max_duration": requirement.max_event_duration,
                    "min_break": requirement.min_break
                }
            ))
            
            distributor = EventDistributor(
                total_minutes=requirement.total_minutes_per_week,
                min_event_duration=requirement.min_event_duration,
                max_event_duration=requirement.max_event_duration,
                min_break=requirement.min_break
            )
            
            scheduled_events, remaining_minutes = distributor.distribute_events(free_slots)
            
            result.decision_log.append(SchedulingDecision(
                step="events_distributed",
                message=f"Planned {len(scheduled_events)} events ({requirement.total_minutes_per_week - remaining_minutes} minutes scheduled)",
                details={
                    "event_count": len(scheduled_events),
                    "minutes_scheduled": requirement.total_minutes_per_week - remaining_minutes,
                    "remaining_minutes": remaining_minutes
                }
            ))
            
            if remaining_minutes > 0:
                result.warnings.append(
                    f"Could not schedule all {requirement.total_minutes_per_week} minutes. "
                    f"Remaining: {remaining_minutes} minutes"
                )
            
            if not scheduled_events:
                result.errors.append("Could not schedule any events with the given constraints")
                return result
            
            # Step 5: Create calendar events
            result.decision_log.append(SchedulingDecision(
                step="create_events",
                message=f"Creating {len(scheduled_events)} calendar events",
                details={"event_count": len(scheduled_events)}
            ))
            
            created_events = []
            for i, scheduled_event in enumerate(scheduled_events):
                start_dt = datetime.datetime.fromisoformat(
                    scheduled_event.start_time.replace('Z', '+00:00')
                )
                end_dt = datetime.datetime.fromisoformat(
                    scheduled_event.end_time.replace('Z', '+00:00')
                )
                
                event_description = (
                    f"Part of plan: {requirement.plan_description}\n"
                    f"Duration: {scheduled_event.duration_minutes} minutes"
                )
                
                try:
                    created_event = self.calendar_repository.create_event(
                        summary=f"{requirement.plan_description} ({scheduled_event.duration_minutes} min)",
                        start_time=start_dt,
                        end_time=end_dt,
                        description=event_description,
                        calendar_id=requirement.calendar_id
                    )
                    
                    created_events.append(created_event)
                    result.event_ids.append(created_event.get('id'))
                    
                    result.decision_log.append(SchedulingDecision(
                        step="event_created",
                        message=f"Created event {i+1}/{len(scheduled_events)}: {start_dt.isoformat()}",
                        details={
                            "event_id": created_event.get('id'),
                            "start": start_dt.isoformat(),
                            "end": end_dt.isoformat(),
                            "duration": scheduled_event.duration_minutes
                        }
                    ))
                except Exception as e:
                    error_msg = f"Failed to create event {i+1}: {str(e)}"
                    result.errors.append(error_msg)
                    result.decision_log.append(SchedulingDecision(
                        step="event_creation_failed",
                        message=error_msg,
                        details={"error": str(e)}
                    ))
            
            result.events_created = created_events
            result.total_minutes_scheduled = requirement.total_minutes_per_week - remaining_minutes
            result.remaining_minutes = remaining_minutes
            result.success = len(created_events) > 0
            
            result.decision_log.append(SchedulingDecision(
                step="scheduling_complete",
                message=f"Scheduling complete: {len(created_events)} events created, {result.total_minutes_scheduled} minutes scheduled",
                details={
                    "events_created": len(created_events),
                    "minutes_scheduled": result.total_minutes_scheduled,
                    "remaining_minutes": remaining_minutes
                }
            ))
            
        except Exception as e:
            result.errors.append(f"Scheduling failed: {str(e)}")
            result.decision_log.append(SchedulingDecision(
                step="scheduling_error",
                message=f"Error during scheduling: {str(e)}",
                details={"error": str(e)}
            ))
        
        return result
    
    def _calculate_scheduling_window(
        self,
        window_days: int
    ) -> Tuple[datetime.datetime, datetime.datetime]:
        """
        Calculate the scheduling window from now.
        
        Args:
            window_days: Number of days to schedule ahead
            
        Returns:
            Tuple of (start_time, end_time)
        """
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        start_time = now
        end_time = now + datetime.timedelta(days=window_days)
        
        return start_time, end_time

