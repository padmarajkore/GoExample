from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime, date
from typing import List, Dict, Optional
import json

def safe_json_serializable(obj):
    """Ensure object is JSON serializable by converting problematic types."""
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Skip objects that are likely framework objects
        if obj.__class__.__module__.startswith('google.adk'):
            return f"<{obj.__class__.__name__} object>"
        return safe_json_serializable(obj.__dict__)
    else:
        return obj

def clean_state_data(tool_context: ToolContext):
    """Clean state data to ensure JSON serializability by modifying existing state in-place."""
    try:
        # Test if current state is JSON serializable
        json.dumps(tool_context.state)
    except (TypeError, ValueError) as e:
        print(f"Warning: State contains non-JSON serializable data: {e}")
        
        # Instead of replacing the entire state, clean individual keys
        state_dict = dict(tool_context.state)  # Create a copy
        
        for key, value in state_dict.items():
            try:
                json.dumps(value)  # Test if this value is serializable
            except (TypeError, ValueError):
                # Clean this specific value and update it in the original state
                cleaned_value = safe_json_serializable(value)
                # Update the state dictionary directly
                try:
                    if hasattr(tool_context.state, '__setitem__'):
                        tool_context.state[key] = cleaned_value
                    elif hasattr(tool_context.state, 'update'):
                        tool_context.state.update({key: cleaned_value})
                except Exception as update_error:
                    print(f"Warning: Could not update state key {key}: {update_error}")

def save_attendance(
    student_name: str,
    grade: str = None,
    date_str: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Save attendance for a student by name. Creates new student if doesn't exist.
    
    Args:
        student_name: Name of the student
        grade: Student's grade/class (optional, will ask if not provided)
        date_str: Date in YYYY-MM-DD format (defaults to today)
        tool_context: Context for accessing and updating session state
    
    Returns:
        Confirmation message with attendance record
    """
    try:
        print(f"--- Tool: save_attendance called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        # Use today's date if not provided
        if not date_str:
            date_str = date.today().isoformat()
        
        # Validate student name
        if not student_name or not student_name.strip():
            return {
                "action": "save_attendance",
                "status": "error",
                "message": "Student name is required"
            }
        
        student_name = student_name.strip().title()
        
        # Get student database
        students_db = tool_context.state.get("students_database", {})
        attendance_records = tool_context.state.get("attendance_records", {})
        
        # Check if student exists
        student_id = None
        for sid, student_info in students_db.items():
            if student_info.get("name", "").lower() == student_name.lower():
                student_id = sid
                break
        
        # Create new student if doesn't exist
        if not student_id:
            student_id = f"student_{len(students_db) + 1:04d}"
            new_student = {
                "name": student_name,
                "grade": grade or "Not specified",
                "created_date": datetime.now().isoformat(),
                "total_attendance_days": 0,
                "created_by": tool_context.state.get("user_name", "system")
            }
            students_db[student_id] = new_student
            
            # Update the state
            try:
                if hasattr(tool_context.state, '__setitem__'):
                    tool_context.state["students_database"] = students_db
                elif hasattr(tool_context.state, 'update'):
                    tool_context.state.update({"students_database": students_db})
            except Exception as e:
                print(f"Warning: Could not update students_database: {e}")
            
            print(f"Created new student: {student_name} with ID: {student_id}")
        else:
            # Update grade if provided and different
            if grade and students_db[student_id].get("grade") != grade:
                students_db[student_id]["grade"] = grade
                try:
                    if hasattr(tool_context.state, '__setitem__'):
                        tool_context.state["students_database"] = students_db
                    elif hasattr(tool_context.state, 'update'):
                        tool_context.state.update({"students_database": students_db})
                except Exception as e:
                    print(f"Warning: Could not update student grade: {e}")
        
        # Create attendance record
        record_key = f"{date_str}_{student_id}"
        attendance_record = {
            "student_id": student_id,
            "student_name": student_name,
            "grade": students_db[student_id]["grade"],
            "date": date_str,
            "status": "present",
            "timestamp": datetime.now().isoformat(),
            "marked_by": tool_context.state.get("user_name", "system")
        }
        
        # Check if attendance already marked for today
        if record_key in attendance_records:
            return {
                "action": "save_attendance",
                "status": "info",
                "message": f"Attendance already marked for {student_name} on {date_str}",
                "existing_record": attendance_records[record_key]
            }
        
        # Save attendance record
        attendance_records[record_key] = attendance_record
        
        # Update student's total attendance count
        students_db[student_id]["total_attendance_days"] = students_db[student_id].get("total_attendance_days", 0) + 1
        students_db[student_id]["last_attendance"] = date_str
        
        # Update state with both changes
        try:
            updates = {
                "students_database": students_db,
                "attendance_records": attendance_records
            }
            
            for key, value in updates.items():
                if hasattr(tool_context.state, '__setitem__'):
                    tool_context.state[key] = value
                elif hasattr(tool_context.state, 'update'):
                    tool_context.state.update({key: value})
        except Exception as e:
            print(f"Warning: Could not update state: {e}")
        
        clean_state_data(tool_context)
        
        return {
            "action": "save_attendance",
            "status": "success",
            "record": attendance_record,
            "student_info": students_db[student_id],
            "message": f"✅ Attendance saved for {student_name} (Grade: {students_db[student_id]['grade']}) on {date_str}",
            "is_new_student": student_id not in [r.get("student_id") for r in attendance_records.values() if r.get("student_id") != student_id]
        }
        
    except Exception as e:
        print(f"Error in save_attendance: {e}")
        return {
            "action": "save_attendance",
            "status": "error",
            "message": f"Failed to save attendance: {str(e)}"
        }

def get_student_by_name(
    student_name: str,
    tool_context: ToolContext = None
) -> dict:
    """Search for a student by name in the database.
    
    Args:
        student_name: Name of the student to search
        tool_context: Context for accessing session state
    
    Returns:
        Student information if found
    """
    try:
        print(f"--- Tool: get_student_by_name called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        students_db = tool_context.state.get("students_database", {})
        
        # Search for student (case-insensitive)
        found_students = []
        for student_id, student_info in students_db.items():
            if student_name.lower() in student_info.get("name", "").lower():
                student_data = student_info.copy()
                student_data["student_id"] = student_id
                found_students.append(student_data)
        
        if not found_students:
            return {
                "action": "get_student_by_name",
                "status": "not_found",
                "message": f"No student found with name '{student_name}'",
                "suggestions": "Would you like to create a new student record?"
            }
        
        return {
            "action": "get_student_by_name",
            "status": "found",
            "students": found_students,
            "count": len(found_students),
            "message": f"Found {len(found_students)} student(s) matching '{student_name}'"
        }
        
    except Exception as e:
        print(f"Error in get_student_by_name: {e}")
        return {
            "action": "get_student_by_name",
            "status": "error",
            "message": f"Failed to search student: {str(e)}"
        }

def get_attendance_summary(
    student_name: str = None,
    date_range_days: int = 30,
    tool_context: ToolContext = None
) -> dict:
    """Get attendance summary for a student or all students.
    
    Args:
        student_name: Name of specific student (optional)
        date_range_days: Number of days to look back (default 30)
        tool_context: Context for accessing session state
    
    Returns:
        Attendance summary
    """
    try:
        print(f"--- Tool: get_attendance_summary called ---")
        
        clean_state_data(tool_context)
        
        students_db = tool_context.state.get("students_database", {})
        attendance_records = tool_context.state.get("attendance_records", {})
        
        # Calculate date range
        end_date = date.today()
        start_date = date.fromordinal(end_date.toordinal() - date_range_days)
        
        if student_name:
            # Get summary for specific student
            student_id = None
            for sid, student_info in students_db.items():
                if student_info.get("name", "").lower() == student_name.lower():
                    student_id = sid
                    break
            
            if not student_id:
                return {
                    "action": "get_attendance_summary",
                    "status": "error",
                    "message": f"Student '{student_name}' not found"
                }
            
            # Get attendance records for this student
            student_records = []
            for record_key, record in attendance_records.items():
                if record.get("student_id") == student_id:
                    record_date = datetime.fromisoformat(record.get("date")).date()
                    if start_date <= record_date <= end_date:
                        student_records.append(record)
            
            total_days = len(student_records)
            present_days = sum(1 for r in student_records if r.get("status") == "present")
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            return {
                "action": "get_attendance_summary",
                "student_name": student_name,
                "student_id": student_id,
                "date_range": f"{start_date} to {end_date}",
                "summary": {
                    "total_days": total_days,
                    "present_days": present_days,
                    "attendance_percentage": round(attendance_percentage, 2)
                },
                "records": student_records,
                "message": f"Attendance summary for {student_name}: {present_days}/{total_days} days ({attendance_percentage:.1f}%)"
            }
        else:
            # Get summary for all students
            all_summaries = []
            for student_id, student_info in students_db.items():
                student_records = []
                for record_key, record in attendance_records.items():
                    if record.get("student_id") == student_id:
                        record_date = datetime.fromisoformat(record.get("date")).date()
                        if start_date <= record_date <= end_date:
                            student_records.append(record)
                
                total_days = len(student_records)
                present_days = sum(1 for r in student_records if r.get("status") == "present")
                attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
                
                all_summaries.append({
                    "student_id": student_id,
                    "student_name": student_info.get("name"),
                    "grade": student_info.get("grade"),
                    "total_days": total_days,
                    "present_days": present_days,
                    "attendance_percentage": round(attendance_percentage, 2)
                })
            
            return {
                "action": "get_attendance_summary",
                "date_range": f"{start_date} to {end_date}",
                "total_students": len(all_summaries),
                "summaries": all_summaries,
                "message": f"Attendance summary for {len(all_summaries)} students over last {date_range_days} days"
            }
        
    except Exception as e:
        print(f"Error in get_attendance_summary: {e}")
        return {
            "action": "get_attendance_summary",
            "status": "error",
            "message": f"Failed to get attendance summary: {str(e)}"
        }

# Enhanced attendance management agent
attendance_agent = Agent(
    name="attendance_agent",
    model="gemini-2.0-flash",
    description="Enhanced student attendance management with automatic student creation",
    instruction="""
    You are an enhanced attendance management assistant that helps teachers manage student attendance with intelligent student database management.
    
    **KEY FEATURES:**
    
    1. **Smart Attendance Saving**: 
       - When a teacher asks to "save attendance" for a student, ask only for the student's name
       - Automatically search the database for existing students
       - If student exists, mark attendance with current date
       - If student doesn't exist, create new student record with minimal info (name, grade)
       - Store attendance with date, status (present by default)
    
    2. **Automatic Student Management**:
       - Maintain students_database with unique student IDs
       - Track total attendance days for each student
       - Store basic info: name, grade, creation date, attendance count
    
    3. **Simple Attendance Workflow**:
       - Teacher: "Save attendance for John Smith"
       - You: Ask for grade if new student, otherwise just confirm attendance saved
       - Auto-assign student ID and mark as present for today
    
    **RESPONSE PATTERNS:**
    
    For attendance requests:
    - "I'll save attendance for [Name]. Let me check if they're in our database..."
    - If new: "This appears to be a new student. What grade/class is [Name] in?"
    - If existing: "✅ Attendance saved for [Name] (Grade X) for today's date"
    
    For queries:
    - Provide clear summaries with attendance percentages
    - Show recent attendance patterns
    - Highlight students with low attendance
    
    **IMPORTANT GUIDELINES:**
    
    1. **Minimal Information Required**: Only ask for name initially, grade only if new student
    2. **Smart Defaults**: Use current date, mark as "present" by default
    3. **Database Growth**: Automatically expand student database as needed
    4. **User-Friendly**: Make attendance marking as quick as possible for teachers
    5. **Data Integrity**: Prevent duplicate attendance for same student on same day
    
    Always be efficient and helpful - teachers need quick attendance marking during class time!
    """,
    tools=[
        save_attendance,
        get_student_by_name,
        get_attendance_summary,
    ],
)