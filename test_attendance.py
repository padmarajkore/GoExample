import asyncio
import sys
import os
from datetime import datetime, date, timedelta

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from session_utils import call_agent_async, display_session_state, get_user_sessions_summary
from manager.sub_agents.attendance_agent.agent import attendance_agent

# Database configuration
db_url = "sqlite:///./test_attendance_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# Application constants
APP_NAME = "Attendance Test System"
TEACHER_USER_ID = "teacher_001"
ADMIN_USER_ID = "admin_001"

def initialize_test_state():
    """Initialize test state for attendance system."""
    return {
        "user_name": "Test Teacher",
        "user_role": "teacher",
        "session_count": 1,
        "preferences": {
            "language": "english",
            "difficulty_level": "medium",
            "subjects": ["Mathematics", "Science", "English"]
        },
        "attendance_records": {},
        "interaction_history": []
    }

async def run_attendance_tests():
    """Run comprehensive tests for the attendance system."""
    
    print("=" * 60)
    print("ATTENDANCE MANAGEMENT SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Create session for teacher
    try:
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=TEACHER_USER_ID,
            state=initialize_test_state(),
        )
        session_id = new_session.id
        print(f"Created test session: {session_id}")
    except Exception as e:
        print(f"Error creating session: {e}")
        return
    
    # Create runner with attendance agent
    runner = Runner(
        agent=attendance_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    # Test scenarios
    test_queries = [
        # Initial setup and single attendance marking
        "Hi, I'm Ms. Johnson, a mathematics teacher. Please mark John Smith (ID: STU001) as present for Mathematics today.",
        
        # Mark more students
        "Mark Sarah Wilson (ID: STU002) as late for Mathematics today.",
        "Mark Mike Brown (ID: STU003) as absent for Mathematics today.",
        "Mark Lisa Davis (ID: STU004) as present for Mathematics today.",
        "Mark Tom Johnson (ID: STU005) as excused for Mathematics today.",
        
        # View today's attendance
        "Show me today's attendance for Mathematics class.",
        
        # Get class summary
        "Give me an attendance summary for Mathematics class today.",
        
        # Check individual student attendance
        "Show me John Smith's (STU001) attendance history.",
        
        # Mark attendance for different subject
        "Mark John Smith (STU001) as present for Science today.",
        "Mark Sarah Wilson (STU002) as present for Science today.",
        "Mark Mike Brown (STU003) as late for Science today.",
        
        # Get attendance for different date (yesterday)
        f"Show me attendance records for {(date.today() - timedelta(days=1)).isoformat()}.",
        
        # Bulk attendance test (this would be more complex in real implementation)
        "Show me attendance summary for Science class today.",
        
        # Error handling tests
        "Mark student XYZ123 as 'maybe' for Mathematics today.",  # Invalid status
        "Show attendance for student INVALID_ID.",  # Non-existent student
        
        # Statistics and reporting
        "What's the overall attendance rate for Mathematics?",
        "Show me all attendance records for today.",
    ]
    
    # Run each test query
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*20} TEST {i:02d} {'='*20}")
        print(f"Query: {query}")
        print("-" * 50)
        
        try:
            response = await call_agent_async(runner, TEACHER_USER_ID, session_id, query)
            if response:
                print(f"Success: Query processed")
            else:
                print("Warning: No response received")
        except Exception as e:
            print(f"Error: {e}")
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Final state display
    print(f"\n{'='*20} FINAL SESSION STATE {'='*20}")
    display_session_state(session_service, APP_NAME, TEACHER_USER_ID, session_id, "Final State")
    
    # Session summary
    print(f"\n{'='*20} SESSION SUMMARY {'='*20}")
    summary = get_user_sessions_summary(session_service, APP_NAME, TEACHER_USER_ID)
    print(f"Sessions Summary: {summary}")
    
    print("\n" + "="*60)
    print("ATTENDANCE SYSTEM TEST COMPLETED")
    print("="*60)

async def demo_bulk_attendance():
    """Demonstrate bulk attendance marking functionality."""
    print("\n" + "="*40)
    print("BULK ATTENDANCE DEMO")
    print("="*40)
    
    # Create a separate session for bulk demo
    bulk_state = initialize_test_state()
    bulk_state["user_name"] = "Principal Smith"
    bulk_state["user_role"] = "admin"
    
    try:
        bulk_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=ADMIN_USER_ID,
            state=bulk_state,
        )
        bulk_session_id = bulk_session.id
    except Exception as e:
        print(f"Error creating bulk session: {e}")
        return
    
    runner = Runner(
        agent=attendance_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )
    
    # Simulate bulk attendance marking
    bulk_queries = [
        "I need to mark attendance for English class. Here are the students: John Smith (STU001) is present, Sarah Wilson (STU002) is present, Mike Brown (STU003) is absent, Lisa Davis (STU004) is late, and Tom Johnson (STU005) is excused.",
        "Show me the attendance summary for English class today.",
        "What's the attendance rate for English class?",
    ]
    
    for query in bulk_queries:
        print(f"\nBulk Query: {query}")
        print("-" * 30)
        try:
            await call_agent_async(runner, ADMIN_USER_ID, bulk_session_id, query)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(1)

async def main():
    print("Starting Attendance Management System Tests...")

    # Run the main tests
    await run_attendance_tests()

    # Run bulk attendance demo
    await demo_bulk_attendance()

    print("\nAll tests completed! Check the database file 'test_attendance_data.db' for persistent data.")

if __name__ == "__main__":
    asyncio.run(main())