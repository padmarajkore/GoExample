import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from manager.agent import root_agent
# from google.adk.services.exceptions import SessionNotFoundError
from google.adk.cli.fast_api import get_fast_api_app


# Database configuration
db_url = "sqlite:///./sahayak_agent_data.db"
# Print the absolute path for debugging
print(f"[DEBUG] Using database at: {os.path.abspath('./sahayak_agent_data.db')}")
session_service = DatabaseSessionService(db_url=db_url)


# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))


# Updated CORS origins - removed "*" to avoid conflicts
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000", 
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]


# Set web=True if you want to serve a web interface
SERVE_WEB_INTERFACE = True


# Application constants
APP_NAME = "Sahayak Educational Agent"


def initialize_default_state():
    """Initialize default state for new sessions."""
    return {
        "user_name": "",
        "user_role": "",  # student, teacher, admin
        "session_count": 0,
        "preferences": {
            "language": "english",
            "difficulty_level": "medium",
            "subjects": []
        },
        "interaction_history": [],
        "attendance_records": {},
    }


def get_or_create_session(user_id: str, session_id: str = None) -> str:
    """Get existing session or create a new one for the user."""
    
    # 1. If a specific session ID is provided, try to fetch it
    if session_id:
        try:
            existing_session = session_service.get_session(
                app_name=APP_NAME, 
                user_id=user_id, 
                session_id=session_id
            )
            print(f"Retrieved existing session: {session_id}")
            return session_id
        # except SessionNotFoundError:
        #     print(f"Session {session_id} not found. Will check for other sessions or create new one.")
        except Exception as e:
            print(f"Unexpected error fetching session {session_id}: {e}. Will check for other sessions or create new one.")

    # 2. Try to find the most recent session for the user
    try:
        existing_sessions = session_service.list_sessions(
            app_name=APP_NAME, 
            user_id=user_id
        )
        
        if existing_sessions and len(existing_sessions.sessions) > 0:
            # Use the most recent session (first in the list)
            most_recent_session_id = existing_sessions.sessions[0].id
            print(f"Continuing with most recent session: {most_recent_session_id}")
            return most_recent_session_id
            
    except Exception as e:
        print(f"Could not list existing sessions for user {user_id}: {e}. Creating new session.")

    # 3. Create a new session with initial state
    try:
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            state=initialize_default_state(),
        )
        print(f"Created new session: {new_session.id}")
        return new_session.id
        
    except Exception as e:
        print(f"CRITICAL: Failed to create a new session for user {user_id}: {e}")
        raise RuntimeError(f"Failed to create session for user {user_id}") from e


def display_session_info(user_id: str, session_id: str):
    """Display session information for debugging."""
    try:
        session = session_service.get_session(
            app_name=APP_NAME, 
            user_id=user_id, 
            session_id=session_id
        )
        
        print(f"\n{'='*50}")
        print(f"SESSION INFO")
        print(f"{'='*50}")
        print(f"App Name: {APP_NAME}")
        print(f"User ID: {user_id}")
        print(f"Session ID: {session_id}")
        print(f"User Name: {session.state.get('user_name', 'Not set')}")
        print(f"User Role: {session.state.get('user_role', 'Not set')}")
        print(f"Session Count: {session.state.get('session_count', 0)}")
        print(f"Preferences: {session.state.get('preferences', {})}")
        print(f"Attendance Records: {len(session.state.get('attendance_records', {}))} records")
        print(f"Interaction History: {len(session.state.get('interaction_history', []))} entries")
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"Error displaying session info: {e}")


# Create the runner with database session service
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


# Call the function to get the FastAPI app instance
app = get_fast_api_app(
    agent_dir=AGENT_DIR,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)


# Add explicit CORS middleware to ensure it works properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Health check endpoint for frontend connection testing
@app.get("/health")
async def health_check():
    """Simple health check endpoint for frontend to test connection."""
    return {
        "status": "ok", 
        "message": "Sahayak Educational Agent server is running",
        "app_name": APP_NAME,
        "cors_enabled": True,
        "allowed_origins": ALLOWED_ORIGINS
    }


# CORS preflight endpoint (sometimes needed for complex requests)
@app.options("/run_sse")
async def options_run_sse():
    """Handle preflight requests for /run_sse endpoint."""
    return {"message": "OK"}


# Enhanced session management endpoints
@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user_id: str):
    """Get all sessions for a user with detailed information."""
    try:
        sessions_response = session_service.list_sessions(
            app_name=APP_NAME,
            user_id=user_id,
        )
        
        detailed_sessions = []
        for session_info in sessions_response.sessions:
            try:
                # Get full session details
                full_session = session_service.get_session(
                    app_name=APP_NAME,
                    user_id=user_id,
                    session_id=session_info.id
                )
                
                session_details = {
                    "id": session_info.id,
                    "created_at": session_info.created_at,
                    "user_name": full_session.state.get("user_name", ""),
                    "user_role": full_session.state.get("user_role", ""),
                    "session_count": full_session.state.get("session_count", 0),
                    "attendance_records_count": len(full_session.state.get("attendance_records", {})),
                    "interaction_count": len(full_session.state.get("interaction_history", [])),
                    "preferences": full_session.state.get("preferences", {})
                }
                detailed_sessions.append(session_details)
                
            except Exception as e:
                print(f"Error getting details for session {session_info.id}: {e}")
                # Add basic info even if details fail
                detailed_sessions.append({
                    "id": session_info.id,
                    "created_at": session_info.created_at,
                    "error": f"Could not load session details: {str(e)}"
                })
        
        return {
            "user_id": user_id,
            "total_sessions": len(detailed_sessions),
            "sessions": detailed_sessions
        }
        
    except Exception as e:
        return {"error": f"Failed to retrieve sessions: {str(e)}"}


@app.post("/api/sessions/{user_id}")
async def create_user_session(user_id: str, force_new: bool = False):
    """Create a new session for a user or get existing one."""
    try:
        if force_new:
            # Force create a new session
            new_session = session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                state=initialize_default_state(),
            )
            session_id = new_session.id
            print(f"Force created new session: {session_id}")
        else:
            # Use existing logic to get or create session
            session_id = get_or_create_session(user_id)
        
        # Display session info for debugging
        display_session_info(user_id, session_id)
        
        return {
            "user_id": user_id,
            "session_id": session_id,
            "message": "Session ready"
        }
        
    except Exception as e:
        return {"error": f"Failed to create/get session: {str(e)}"}


@app.get("/api/sessions/{user_id}/{session_id}")
async def get_session_details(user_id: str, session_id: str):
    """Get detailed information about a specific session."""
    try:
        session = session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "app_name": APP_NAME,
            "user_id": user_id,
            "session_id": session_id,
            "state": session.state,
            "created_at": getattr(session, 'created_at', None),
            "message": "Session details retrieved successfully"
        }
        
    # except SessionNotFoundError:
    #     return {"error": f"Session {session_id} not found for user {user_id}"}
    except Exception as e:
        return {"error": f"Failed to retrieve session details: {str(e)}"}


@app.delete("/api/sessions/{user_id}/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """Delete a specific session."""
    try:
        # Note: DatabaseSessionService might not have a delete method
        # This is a placeholder - check ADK documentation for actual delete method
        return {"message": "Session deletion not implemented in current ADK version"}
    except Exception as e:
        return {"error": f"Failed to delete session: {str(e)}"}


@app.get("/api/database/health")
async def check_database_health():
    """Check database health and connectivity."""
    try:
        # Try a simple operation to test database connectivity
        test_sessions = session_service.list_sessions(
            app_name="health_check", 
            user_id="test_user"
        )
        
        return {
            "status": "healthy",
            "message": "Database connection is working properly",
            "database_url": db_url,
            "timestamp": "2025-01-01T00:00:00"  # Placeholder timestamp
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database health check failed: {str(e)}",
            "database_url": db_url,
            "timestamp": "2025-01-01T00:00:00"  # Placeholder timestamp
        }


if __name__ == "__main__":
    print(f"Starting Sahayak Educational Agent with database: {db_url}")
    print("Features:")
    print("- Persistent session storage with SQLite")
    print("- Automatic session management")
    print("- User information persistence")
    print("- Attendance records storage")
    print("- Cross-session memory")
    print("- CORS enabled for frontend integration")
    print(f"- Allowed origins: {ALLOWED_ORIGINS}")
    print("\nDatabase sessions will be automatically managed")
    print("Access the API at: http://localhost:8000")
    print("API Documentation at: http://localhost:8000/docs")
    print("Health check at: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)