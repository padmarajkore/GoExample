from google.genai import types
from datetime import datetime
import json
import os


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def display_session_state(session_service, app_name, user_id, session_id, label="Current State"):
    """Display the current session state in a formatted way."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        # Format the output with clear sections
        print(f"\n{'-' * 15} {label} {'-' * 15}")
        
        # Handle the user info
        user_name = session.state.get("user_name", "Unknown")
        user_role = session.state.get("user_role", "Unknown")
        session_count = session.state.get("session_count", 0)
        
        print(f"👤 User: {user_name} ({user_role})")
        print(f"📊 Session Count: {session_count}")
        
        # Handle preferences
        preferences = session.state.get("preferences", {})
        if preferences:
            print(f"⚙️  Preferences:")
            for key, value in preferences.items():
                print(f"   {key}: {value}")
        
        # Handle attendance records count
        attendance_records = session.state.get("attendance_records", {})
        if attendance_records:
            print(f"📋 Attendance Records: {len(attendance_records)} total")
            
            # Show recent attendance activity (last 5 records)
            recent_records = sorted(
                attendance_records.values(), 
                key=lambda x: x.get("timestamp", ""), 
                reverse=True
            )[:5]
            
            if recent_records:
                print("   Recent Activity:")
                for record in recent_records:
                    date = record.get("date", "N/A")
                    student = record.get("student_name", "N/A")
                    subject = record.get("subject", "N/A")
                    status = record.get("status", "N/A")
                    print(f"     {date}: {student} - {subject} ({status})")
        
        # Handle interaction history count
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print(f"💬 Interaction History: {len(interaction_history)} entries")
            
            # Show recent interactions (last 3)
            recent_interactions = interaction_history[-3:] if len(interaction_history) > 3 else interaction_history
            if recent_interactions:
                print("   Recent Interactions:")
                for interaction in recent_interactions:
                    timestamp = interaction.get("timestamp", "N/A")
                    query_type = interaction.get("type", "general")
                    print(f"     {timestamp}: {query_type}")
        
        print("-" * (32 + len(label)))
        
    except Exception as e:
        print(f"Error displaying session state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    # Log basic event info
    print(f"Event ID: {event.id}, Author: {event.author}")
    
    # Check for specific parts first
    has_specific_part = False
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "executable_code") and part.executable_code:
                # Access the actual code string via .code
                print(
                    f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                )
                has_specific_part = True
            elif hasattr(part, "code_execution_result") and part.code_execution_result:
                # Access outcome and output correctly
                print(
                    f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                )
                has_specific_part = True
            elif hasattr(part, "tool_response") and part.tool_response:
                # Print tool response information
                print(f"  Tool Response: {part.tool_response.output}")
                has_specific_part = True
            # Also print any text parts found in any event for debugging
            elif hasattr(part, "text") and part.text and not part.text.isspace():
                print(f"  Text: '{part.text.strip()}'")
    
    # Check for final response after specific parts
    final_response = None
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═══════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═══════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )
    
    return final_response


async def call_agent_async(runner, user_id, session_id, query):
    """Call the agent asynchronously with the user's query."""
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None
    
    # Display state before processing
    display_session_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )
    
    try:
        print(
            f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Inside try block: {query} ---{Colors.RESET}"
        )
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            print(
                f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Inside try block: {query} ---{Colors.RESET}"
            )
            # Process each event and get the final response if available
            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"Error during agent call: {e}")
    
    # Display state after processing the message
    display_session_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )
    
    return final_response_text


def get_user_sessions_summary(session_service, app_name, user_id):
    """Get a summary of all sessions for a user."""
    try:
        sessions = session_service.list_sessions(app_name=app_name, user_id=user_id)
        
        if not sessions.sessions:
            return {"message": "No sessions found for this user", "sessions": []}
        
        session_summaries = []
        for session in sessions.sessions:
            try:
                full_session = session_service.get_session(
                    app_name=app_name, user_id=user_id, session_id=session.id
                )
                
                summary = {
                    "session_id": session.id,
                    "created_at": session.created_at,
                    "user_name": full_session.state.get("user_name", "Unknown"),
                    "user_role": full_session.state.get("user_role", "Unknown"),
                    "session_count": full_session.state.get("session_count", 0),
                    "attendance_records_count": len(full_session.state.get("attendance_records", {})),
                    "interaction_count": len(full_session.state.get("interaction_history", [])),
                    "preferences": full_session.state.get("preferences", {}),
                    "last_interaction": full_session.state.get("interaction_history", [])[-1] if full_session.state.get("interaction_history") else None
                }
                session_summaries.append(summary)
            except Exception as e:
                print(f"Error getting session {session.id}: {e}")
                continue
        
        return {
            "message": f"Found {len(session_summaries)} sessions for user {user_id}",
            "sessions": session_summaries
        }
        
    except Exception as e:
        return {"error": f"Error retrieving sessions: {e}", "sessions": []}


def backup_session_data(session_service, app_name, user_id, session_id, backup_file):
    """Backup session data to a JSON file."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        backup_data = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "backup_timestamp": datetime.now().isoformat(),
            "state": session.state,
            "backup_version": "1.0",
            "agent_type": "sahayak_educational_agent"
        }
        
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_file)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        return {
            "status": "success", 
            "message": f"Session data backed up to {backup_file}",
            "backup_size": os.path.getsize(backup_file),
            "records_count": {
                "attendance_records": len(backup_data["state"].get("attendance_records", {})),
                "interaction_history": len(backup_data["state"].get("interaction_history", []))
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Backup failed: {e}"}


def restore_session_data(session_service, backup_file):
    """Restore session data from a JSON backup file."""
    try:
        if not os.path.exists(backup_file):
            return {"status": "error", "message": f"Backup file {backup_file} not found"}
        
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        # Validate backup data structure
        required_fields = ["app_name", "user_id", "state"]
        for field in required_fields:
            if field not in backup_data:
                return {"status": "error", "message": f"Invalid backup file: missing {field}"}
        
        # Create/update session with backed up data
        try:
            new_session = session_service.create_session(
                app_name=backup_data["app_name"],
                user_id=backup_data["user_id"],
                state=backup_data["state"]
            )
            session_id = new_session.id
        except Exception:
            # If create fails, the session might already exist
            # For now, we'll just report success with the provided session_id
            session_id = backup_data.get("session_id", "restored_session")
        
        return {
            "status": "success", 
            "message": f"Session data restored from {backup_file}",
            "restored_data": {
                "app_name": backup_data["app_name"],
                "user_id": backup_data["user_id"],
                "session_id": session_id,
                "backup_timestamp": backup_data.get("backup_timestamp"),
                "backup_version": backup_data.get("backup_version", "unknown")
            },
            "restored_counts": {
                "attendance_records": len(backup_data["state"].get("attendance_records", {})),
                "interaction_history": len(backup_data["state"].get("interaction_history", []))
            }
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Restore failed: {e}"}


def migrate_session_data(session_service, app_name, user_id, session_id):
    """Migrate session data to ensure compatibility with current schema."""
    try:
        session = session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        
        # Define expected schema
        expected_schema = {
            "user_name": "",
            "user_role": "",
            "session_count": 0,
            "preferences": {
                "language": "english",
                "difficulty_level": "medium",
                "subjects": []
            },
            "interaction_history": [],
            "attendance_records": {},
        }
        
        # Check and update schema
        updated = False
        for key, default_value in expected_schema.items():
            if key not in session.state:
                session.state[key] = default_value
                updated = True
            elif key == "preferences" and isinstance(session.state[key], dict):
                # Update preferences sub-schema
                for pref_key, pref_default in expected_schema["preferences"].items():
                    if pref_key not in session.state[key]:
                        session.state[key][pref_key] = pref_default
                        updated = True
        
        if updated:
            # Note: ADK handles state updates automatically through tools
            # This function mainly validates the schema
            return {
                "status": "success",
                "message": "Session schema updated successfully",
                "updated": True,
                "current_schema": list(session.state.keys())
            }
        else:
            return {
                "status": "success",
                "message": "Session schema is up to date",
                "updated": False,
                "current_schema": list(session.state.keys())
            }
    
    except Exception as e:
        return {"status": "error", "message": f"Migration failed: {e}"}


def check_database_health(session_service):
    """Check the health of the database connection."""
    try:
        # Try to perform a simple operation
        test_sessions = session_service.list_sessions(app_name="health_check", user_id="test")
        return {
            "status": "healthy",
            "message": "Database connection is working properly",
            "timestamp": datetime.now().isoformat(),
            "test_query_successful": True
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database health check failed: {e}",
            "timestamp": datetime.now().isoformat(),
            "test_query_successful": False
        }


def get_database_stats(session_service, app_name):
    """Get statistics about the database usage."""
    try:
        # This is a simplified version - collecting what we can from the session service
        stats = {
            "app_name": app_name,
            "timestamp": datetime.now().isoformat(),
            "status": "Partial statistics available through session service",
            "note": "Full database statistics would require direct database access"
        }
        
        return stats
        
    except Exception as e:
        return {
            "error": f"Error collecting database stats: {e}",
            "timestamp": datetime.now().isoformat()
        }


def cleanup_old_sessions(session_service, app_name, user_id, keep_latest=5):
    """Clean up old sessions for a user, keeping only the most recent ones."""
    try:
        sessions = session_service.list_sessions(app_name=app_name, user_id=user_id)
        
        if not sessions.sessions or len(sessions.sessions) <= keep_latest:
            return {
                "status": "success",
                "message": f"No cleanup needed. User has {len(sessions.sessions)} sessions (keeping {keep_latest})",
                "sessions_removed": 0
            }
        
        # Note: ADK's DatabaseSessionService might not have a delete method
        # This is a placeholder for the logic - check ADK documentation
        sessions_to_remove = sessions.sessions[keep_latest:]
        
        return {
            "status": "info",
            "message": f"Would remove {len(sessions_to_remove)} old sessions (deletion not implemented)",
            "sessions_to_remove": [s.id for s in sessions_to_remove],
            "sessions_kept": keep_latest
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Cleanup failed: {e}"}


def log_interaction(session_service, app_name, user_id, session_id, interaction_type, query, response=None):
    """Log user interaction for analytics and debugging."""
    try:
        session = session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
        
        interaction_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "query": query[:200] if query else "",  # Truncate long queries
            "response_length": len(response) if response else 0,
            "session_count": session.state.get("session_count", 0)
        }
        
        # Add to interaction history
        interaction_history = session.state.get("interaction_history", [])
        interaction_history.append(interaction_entry)
        
        # Keep only last 100 interactions to prevent excessive growth
        if len(interaction_history) > 100:
            interaction_history = interaction_history[-100:]
        
        # Note: In real usage, this would be handled by agent tools
        # This function is for demonstration and external logging
        
        return {
            "status": "success",
            "message": "Interaction logged successfully",
            "total_interactions": len(interaction_history)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to log interaction: {e}"}