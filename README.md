# Sahayak Agent with Persistent Database and Attendance Management

This enhanced version of your Sahayak educational agent system now includes:

1. **Persistent Database Storage** - All sessions are stored in SQLite database
2. **Attendance Management Agent** - Complete student attendance tracking system
3. **Enhanced Session Management** - User profiles, preferences, and history

## Project Structure

```
sahayakagent/
├── main.py                           # Updated with database persistence
├── session_utils.py                  # Session management utilities  
├── test_attendance.py                # Comprehensive test script
├── sahayak_agent_data.db             # SQLite database (created automatically)
├── manager/
│   ├── agent.py                      # Updated manager with attendance agent
│   └── sub_agents/
│       ├── mcq_creator/
│       ├── visualization_creator/
│       ├── game_creator/
│       ├── qa_agent/
│       └── attendance_agent/         # NEW: Attendance management
│           ├── __init__.py
│           └── agent.py
└── README.md                         # This file
```

## Key Features

### 1. Persistent Database Storage

- **SQLite Database**: All session data persists across application restarts
- **User Profiles**: Remembers user names, roles, and preferences
- **Session History**: Tracks interaction count and session data
- **Automatic Session Management**: Creates new sessions or continues existing ones

### 2. Attendance Management System

The attendance agent provides comprehensive student attendance tracking:

#### Core Features:
- **Individual Attendance Marking**: Mark students as present, absent, late, or excused
- **Bulk Attendance Operations**: Mark multiple students at once
- **Attendance Queries**: View attendance by date, student, or class
- **Statistical Reports**: Calculate attendance rates and generate summaries
- **Historical Data**: Access complete attendance history for any student

#### Supported Operations:
- `mark_attendance()` - Mark individual student attendance
- `get_attendance_by_date()` - Get all attendance for a specific date
- `get_student_attendance()` - Get attendance history for a student
- `get_class_attendance_summary()` - Get class attendance statistics
- `bulk_mark_attendance()` - Mark attendance for multiple students

### 3. Enhanced User Management

- **Role-based Access**: Different features for students, teachers, and administrators
- **Personalized Experience**: Customizable preferences and difficulty levels
- **Session Continuity**: Users can continue where they left off
- **Multi-user Support**: Separate data for different users

## Setup Instructions

### 1. File Placement

Place the new files in your existing structure:

```bash
# Copy the new attendance agent
mkdir -p sahayakagent/manager/sub_agents/attendance_agent/
# Place attendance_agent/__init__.py and agent.py files

# Update existing files
# Replace sahayakagent/main.py with the updated version
# Replace sahayakagent/manager/agent.py with the updated manager
# Add session_utils.py to sahayakagent/
# Add test_attendance.py to sahayakagent/
```

### 2. Dependencies

Ensure you have the required dependencies:

```bash
pip install google-adk sqlite3 uvicorn fastapi
```

### 3. Environment Setup

Make sure your `.env` file contains:

```env
GOOGLE_API_KEY=your_api_key_here
```

## Usage Examples

### 1. Starting the System

```bash
cd sahayakagent
python main.py
```

The system will:
- Create/connect to the SQLite database
- Set up persistent session management
- Start the FastAPI server with all agents

### 2. Basic Attendance Operations

#### For Teachers:

```
"Hi, I'm Ms. Johnson, a mathematics teacher."
"Mark John Smith (ID: STU001) as present for Mathematics today."
"Mark Sarah Wilson (ID: STU002) as late for Mathematics today."  
"Show me today's attendance for Mathematics class."
"Give me an attendance summary for Mathematics class today."
```

#### For Administrators:

```
"I need to mark bulk attendance for English class."
"Show me attendance statistics for the whole school."
"Generate an attendance report for this week."
```

### 3. Student Queries

```
"Show me John Smith's attendance history."
"What's John's attendance rate for Mathematics?"
"Which students were absent yesterday?"
```

### 4. Advanced Operations

```
"Show attendance for Mathematics between 2024-01-01 and 2024-01-31."
"Calculate the overall attendance rate for Science class."
"Export attendance data for reporting."
```

## Testing the System

Run the comprehensive test script to verify everything works:

```bash
cd sahayakagent
python test_attendance.py
```

This will:
- Create test sessions with sample data
- Test all attendance operations
- Demonstrate bulk operations
- Show database persistence
- Generate sample reports

## API Endpoints

The system now includes additional REST endpoints:

- `GET /api/sessions/{user_id}` - Get all sessions for a user
- `POST /api/sessions/{user_id}` - Create a new session for a user

## Database Schema

The SQLite database automatically creates tables for:
- **Sessions**: User session metadata
- **Session States**: Complete session state data including attendance records
- **Timestamps**: Creation and modification dates

## Attendance Data Structure

Each attendance record contains:

```json
{
  "student_id": "STU001",
  "student_name": "John Smith", 
  "subject": "Mathematics",
  "date": "2024-01-15",
  "status": "present",
  "timestamp": "2024-01-15T10:30:00",
  "marked_by": "Ms. Johnson"
}
```

## Role-Based Features

### Students
- View their own attendance history
- Check attendance statistics
- Access learning materials based on attendance

### Teachers  
- Mark attendance for their classes
- View class attendance summaries
- Generate attendance reports
- Track individual student progress

### Administrators
- Access all attendance data
- Generate school-wide reports
- Manage bulk operations
- View system statistics

## Advanced Configuration

### Database Configuration

You can use different databases by changing the connection string:

```python
# PostgreSQL
db_url = "postgresql://user:password@localhost/sahayak_db"

# MySQL  
db_url = "mysql://user:password@localhost/sahayak_db"

# SQLite (default)
db_url = "sqlite:///./sahayak_agent_data.db"
```

### Session Management

Customize session behavior in `main.py`:

```python
def initialize_default_state():
    return {
        "user_name": "",
        "user_role": "",
        "custom_field": "value",
        # Add your custom fields
    }
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check if the database file has proper permissions
   - Verify SQLite is installed

2. **Session Not Persisting**
   - Ensure `DatabaseSessionService` is used instead of `InMemorySessionService`
   - Check database write permissions

3. **Attendance Data Not Saving**
   - Verify the attendance agent is properly included in sub_agents
   - Check tool_context.state updates

### Debug Mode

Enable detailed logging by adding to your session queries:

```python
# In session_utils.py, set debug mode
DEBUG_MODE = True
```

## Production Deployment

For production use:

1. **Use PostgreSQL or MySQL** instead of SQLite
2. **Configure Connection Pooling** for better performance  
3. **Set up Database Backups** for attendance data
4. **Implement User Authentication** for security
5. **Add Input Validation** for attendance data
6. **Configure CORS** properly for your frontend

## Next Steps

Consider adding:

- **Email/SMS Notifications** for absences
- **Parent Portal Integration** for attendance viewing
- **Calendar Integration** for attendance scheduling
- **Automated Reports** sent to administrators
- **Attendance Analytics** and trend analysis
- **Mobile App Support** for quick attendance marking

## Support

The system includes comprehensive error handling and logging. Check:

1. Console output for detailed error messages
2. Database state using the session utilities
3. Test scripts for functionality verification

For issues, refer to the test scripts and session utilities for debugging assistance.# GoExample
