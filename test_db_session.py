import asyncio
from google.adk.sessions import DatabaseSessionService
import os

db_url = "sqlite:///./sahayak_agent_data.db"
print(f"[TEST] Using database at: {os.path.abspath('./sahayak_agent_data.db')}")
session_service = DatabaseSessionService(db_url=db_url)

APP_NAME = "Sahayak Educational Agent"
USER_ID = "testuser"

async def main():
    # Try to create a new session
    initial_state = {"user_name": "Test User", "test": True}
    new_session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        state=initial_state,
    )
    print(f"[TEST] Created session: {new_session.id}")

    # List all sessions for this user
    sessions = await session_service.list_sessions(app_name=APP_NAME, user_id=USER_ID)
    print(f"[TEST] Sessions for user {USER_ID}:")
    for s in sessions.sessions:
        print(f"  - id: {s.id}, state: {s.state}")

if __name__ == "__main__":
    asyncio.run(main()) 