#!/usr/bin/env python3
"""
CLI interface for testing Sahayak Agent with persistent storage.
This allows you to interact with the agent directly from the command line
and see how data persists across sessions.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from manager.agent import root_agent
from session_utils import call_agent_async, display_session_state, get_user_sessions_summary
from main import get_or_create_session, initialize_default_state, APP_NAME

# Load environment variables
load_dotenv()

# Database configuration (same as main.py)
db_url = "sqlite:///./sahayak_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# Create the runner
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


def print_banner():
    """Print the CLI banner."""
    print("\n" + "="*60)
    print("🎓 SAHAYAK EDUCATIONAL AGENT - CLI INTERFACE")
    print("="*60)
    print("Features:")
    print("- Persistent memory across sessions")
    print("- User profile management")
    print("- Attendance tracking")
    print("- Educational content creation")
    print("- Cross-session data retention")
    print("="*60)


def print_help():
    """Print available commands."""
    print("\n📋 Available Commands:")
    print("  help          - Show this help message")
    print("  sessions      - List all sessions for current user")
    print("  switch <id>   - Switch to a specific session")
    print("  new           - Force create a new session")
    print("  state         - Show current session state")
    print("  backup        - Backup current session")
    print("  clear         - Clear screen")
    print("  exit/quit     - Exit the CLI")
    print("\n💬 Or just type your question/request directly!")
    print("="*60)


def print_session_info(user_id, session_id):
    """Print current session information."""
    try:
        session = session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        
        print(f"\n🔗 Current Session Info:")
        print(f"   User ID: {user_id}")
        print(f"   Session ID: {session_id[:8]}...")
        print(f"   User: {session.state.get('user_name', 'Not set')} ({session.state.get('user_role', 'Not set')})")
        print(f"   Session #: {session.state.get('session_count', 0)}")
        print(f"   Records: {len(session.state.get('attendance_records', {}))} attendance, {len(session.state.get('interaction_history', []))} interactions")
        
    except Exception as e:
        print(f"❌ Error getting session info: {e}")


async def handle_command(command, user_id, session_id):
    """Handle special CLI commands."""
    parts = command.strip().split()
    cmd = parts[0].lower()
    
    if cmd == "help":
        print_help()
        return session_id
    
    elif cmd == "sessions":
        print("\n📂 Your Sessions:")
        summary = get_user_sessions_summary(session_service, APP_NAME, user_id)
        if summary.get("sessions"):
            for i, session in enumerate(summary["sessions"], 1):
                current = "👉 " if session["session_id"] == session_id else "   "
                print(f"{current}{i}. {session['session_id'][:8]}... - {session['user_name']} ({session['user_role']})")
                print(f"      Session #{session['session_count']}, {session['attendance_records_count']} attendance records")
        else:
            print("   No sessions found.")
        return session_id
    
    elif cmd == "switch" and len(parts) > 1:
        new_session_id = parts[1]
        try:
            session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=new_session_id)
            print(f"✅ Switched to session: {new_session_id[:8]}...")
            print_session_info(user_id, new_session_id)
            return new_session_id
        except Exception as e:
            print(f"❌ Failed to switch to session {new_session_id}: {e}")
            return session_id
    
    elif cmd == "new":
        try:
            new_session = session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                state=initialize_default_state(),
            )
            print(f"✅ Created new session: {new_session.id[:8]}...")
            print_session_info(user_id, new_session.id)
            return new_session.id
        except Exception as e:
            print(f"❌ Failed to create new session: {e}")
            return session_id
    
    elif cmd == "state":
        display_session_state(session_service, APP_NAME, user_id, session_id, "Current Session State")
        return session_id
    
    elif cmd == "backup":
        from session_utils import backup_session_data
        backup_file = f"backup_{user_id}_{session_id[:8]}_{asyncio.get_event_loop().time():.0f}.json"
        result = backup_session_data(session_service, APP_NAME, user_id, session_id, backup_file)
        if result["status"] == "success":
            print(f"✅ {result['message']}")
            print(f"   Backup size: {result['backup_size']} bytes")
            print(f"   Records: {result['records_count']}")
        else:
            print(f"❌ {result['message']}")
        return session_id
    
    elif cmd == "clear":
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        print_session_info(user_id, session_id)
        return session_id
    
    else:
        print(f"❌ Unknown command: {cmd}")
        print("   Type 'help' for available commands")
        return session_id


async def main_async():
    """Main async function for the CLI interface."""
    print_banner()
    
    # Get user ID (in a real app, this might come from authentication)
    print("\n🔐 User Authentication:")
    user_id = input("Enter your user ID (or press Enter for 'demo_user'): ").strip()
    if not user_id:
        user_id = "demo_user"
    
    # Get or create session
    print(f"\n🔍 Setting up session for user: {user_id}")
    session_id = get_or_create_session(user_id)
    
    # Display initial session info
    print_session_info(user_id, session_id)
    print_help()
    
    print(f"\n🚀 Ready! You can now interact with Sahayak Agent.")
    print("   Your data will persist across sessions.")
    print("   Type 'exit' or 'quit' to end the conversation.\n")
    
    # Main interaction loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{user_id}> ").strip()
            
            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n👋 Goodbye! Your data has been saved to the database.")
                print(f"   Database: {db_url}")
                print(f"   Session ID: {session_id}")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Handle special commands
            if user_input.startswith(("help", "sessions", "switch", "new", "state", "backup", "clear")):
                session_id = await handle_command(user_input, user_id, session_id)
                continue
            
            # Process regular queries through the agent
            print(f"\n🤖 Processing your request...")
            response = await call_agent_async(runner, user_id, session_id, user_input)
            
            if not response:
                print("⚠️  No response received from agent")
            
        except KeyboardInterrupt:
            print(f"\n\n🛑 Interrupted by user. Your data has been saved.")
            break
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            print("   Continuing with the session...")


def main():
    """Main entry point."""
    try:
        # Check if we have the required environment variables
        if not os.getenv("GOOGLE_API_KEY"):
            print("❌ Error: GOOGLE_API_KEY environment variable not set")
            print("   Please set your Google API key in the .env file")
            return
        
        # Run the async main function
        asyncio.run(main_async())
        
    except Exception as e:
        print(f"❌ Failed to start CLI: {e}")
        return


if __name__ == "__main__":
    main()