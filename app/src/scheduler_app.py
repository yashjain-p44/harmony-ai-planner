"""
Scheduler Application

Main application interface for scheduling events based on plan requirements.
Provides both function and CLI interfaces.
"""

import sys
import json
from typing import Optional

from calendar_repository import GoogleCalendarRepository
from models.plan_requirement import PlanRequirement
from scheduler_engine import SchedulerEngine, SchedulingResult


def schedule_plan(
    requirement: PlanRequirement,
    calendar_repository: Optional[GoogleCalendarRepository] = None
) -> SchedulingResult:
    """
    Schedule events based on plan requirements.
    
    Args:
        requirement: PlanRequirement object with scheduling requirements
        calendar_repository: Optional GoogleCalendarRepository instance.
                          If None, creates a new one.
    
    Returns:
        SchedulingResult with created events and decision log
    """
    if calendar_repository is None:
        calendar_repository = GoogleCalendarRepository()
    
    engine = SchedulerEngine(calendar_repository)
    return engine.schedule_plan(requirement)


def print_decision_log(result: SchedulingResult):
    """
    Print the decision log in a readable format.
    
    Args:
        result: SchedulingResult to print
    """
    print("\n" + "="*70)
    print("SCHEDULING DECISION LOG")
    print("="*70)
    
    for i, decision in enumerate(result.decision_log, 1):
        print(f"\n[{i}] {decision.step.upper()}")
        print(f"    {decision.message}")
        if decision.details:
            for key, value in decision.details.items():
                print(f"    - {key}: {value}")
    
    print("\n" + "="*70)


def print_summary(result: SchedulingResult):
    """
    Print a summary of the scheduling result.
    
    Args:
        result: SchedulingResult to summarize
    """
    print("\n" + "="*70)
    print("SCHEDULING SUMMARY")
    print("="*70)
    
    if result.success:
        print(f"✓ Success: {len(result.events_created)} events created")
        print(f"  Total minutes scheduled: {result.total_minutes_scheduled}")
        if result.remaining_minutes > 0:
            print(f"  ⚠ Remaining minutes: {result.remaining_minutes}")
    else:
        print("✗ Scheduling failed")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  ✗ {error}")
    
    if result.events_created:
        print("\nCreated Events:")
        for i, event in enumerate(result.events_created, 1):
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'N/A'))
            summary = event.get('summary', 'N/A')
            event_id = event.get('id', 'N/A')
            print(f"  {i}. {start} - {summary} (ID: {event_id})")
    
    print("="*70 + "\n")


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scheduler_app.py <plan_json_file>")
        print("\nExample plan JSON:")
        print(json.dumps({
            "plan_description": "Reading books",
            "total_minutes_per_week": 120,
            "min_event_duration": 30,
            "max_event_duration": 60,
            "min_break": 15,
            "scheduling_window_days": 7
        }, indent=2))
        sys.exit(1)
    
    plan_file = sys.argv[1]
    
    try:
        # Load plan from JSON file
        with open(plan_file, 'r') as f:
            plan_data = json.load(f)
        
        # Create PlanRequirement from JSON
        requirement = PlanRequirement(**plan_data)
        
        print(f"Scheduling plan: {requirement.plan_description}")
        print(f"Total minutes per week: {requirement.total_minutes_per_week}")
        print(f"Event duration: {requirement.min_event_duration}-{requirement.max_event_duration} minutes")
        print(f"Scheduling window: {requirement.scheduling_window_days} days")
        
        # Schedule the plan
        result = schedule_plan(requirement)
        
        # Print results
        print_decision_log(result)
        print_summary(result)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except FileNotFoundError:
        print(f"Error: Plan file not found: {plan_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in plan file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

