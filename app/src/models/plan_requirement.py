"""
Plan Requirement Model

Pydantic models for validating plan requirements for event scheduling.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator


class TimeWindow(BaseModel):
    """Represents a preferred time window for scheduling events."""
    
    start_hour: int = Field(ge=0, le=23, description="Start hour (0-23)")
    start_minute: int = Field(ge=0, le=59, default=0, description="Start minute (0-59)")
    end_hour: int = Field(ge=0, le=23, description="End hour (0-23)")
    end_minute: int = Field(ge=0, le=59, default=0, description="End minute (0-59)")
    
    @model_validator(mode='after')
    def validate_time_window(self):
        """Ensure end time is after start time."""
        if self.end_hour < self.start_hour:
            raise ValueError("End hour must be after or equal to start hour")
        if self.end_hour == self.start_hour and self.end_minute <= self.start_minute:
            raise ValueError("End time must be after start time")
        return self


class PlanRequirement(BaseModel):
    """
    Plan requirement model for event scheduling.
    
    Defines the requirements for scheduling events based on a plan.
    """
    
    plan_description: str = Field(..., description="Description of the plan (e.g., 'Reading books')")
    total_minutes_per_week: int = Field(..., gt=0, description="Total minutes required per week")
    min_event_duration: int = Field(..., gt=0, description="Minimum event duration in minutes")
    max_event_duration: int = Field(..., gt=0, description="Maximum event duration in minutes")
    min_break: int = Field(..., ge=0, description="Minimum break between events in minutes")
    scheduling_window_days: int = Field(default=7, ge=1, le=365, description="Number of days to schedule ahead (default: 7)")
    preferred_time_windows: Optional[List[TimeWindow]] = Field(
        default=None,
        description="Preferred time windows for scheduling (optional)"
    )
    calendar_id: str = Field(default="primary", description="Calendar ID to use")
    
    @field_validator('max_event_duration')
    @classmethod
    def validate_max_duration(cls, v, info):
        """Ensure max_event_duration is >= min_event_duration."""
        if 'min_event_duration' in info.data:
            min_duration = info.data['min_event_duration']
            if v < min_duration:
                raise ValueError("max_event_duration must be >= min_event_duration")
        return v
    
    @field_validator('total_minutes_per_week')
    @classmethod
    def validate_total_minutes(cls, v, info):
        """Ensure total_minutes_per_week is reasonable."""
        if 'min_event_duration' in info.data:
            min_duration = info.data['min_event_duration']
            if v < min_duration:
                raise ValueError("total_minutes_per_week must be >= min_event_duration")
        return v

