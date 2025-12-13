"""
Test script for the scheduler application.

Creates a test plan and schedules events.
"""

import json
import os
from scheduler_app import schedule_plan
from models.plan_requirement import PlanRequirement

def test_scheduler():
    """Test the scheduler with example plan requirements."""
    
    # Create a test plan requirement
    requirement = PlanRequirement(
        plan_description="Reading books",
        total_minutes_per_week=120,
        min_event_duration=30,
        max_event_duration=60,
        min_break=15,
        scheduling_window_days=7
    )
    
    print("="*70)
    print("TESTING EVENT SCHEDULER")
    print("="*70)
    print(f"\nPlan: {requirement.plan_description}")
    print(f"Total minutes per week: {requirement.total_minutes_per_week}")
    print(f"Event duration: {requirement.min_event_duration}-{requirement.max_event_duration} minutes")
    print(f"Minimum break: {requirement.min_break} minutes")
    print(f"Scheduling window: {requirement.scheduling_window_days} days")
    print("\n" + "="*70)
    
    # Schedule the plan
    result = schedule_plan(requirement)
    
    # Print decision log
    print("\n" + "="*70)
    print("DECISION LOG")
    print("="*70)
    for i, decision in enumerate(result.decision_log, 1):
        print(f"\n[{i}] {decision.step.upper()}")
        print(f"    {decision.message}")
        if decision.details:
            for key, value in decision.details.items():
                print(f"    - {key}: {value}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
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
    
    return result.success


if __name__ == "__main__":
    success = test_scheduler()
    exit(0 if success else 1)

