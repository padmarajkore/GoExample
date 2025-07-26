from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext
from datetime import datetime, date
import json

from .sub_agents.mcq_creator.agent import mcq_creator
from .sub_agents.visualization_creator.agent import visualization_creator
from .sub_agents.game_creator.agent import game_creator
from .sub_agents.qa_agent.agent import qa_agent
from .sub_agents.attendance_agent.agent import attendance_agent
from .sub_agents.personalized_learning_agent.agent import personalized_learning_agent
from .sub_agents.progress_analyzer_agent.agent import progress_analyzer_agent
from .sub_agents.resource_recommendation_agent.agent import resource_recommendation_agent
from .sub_agents.student_evaluation_agent.agent import student_evaluation_agent


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


def update_user_info(name: str, role: str, tool_context: ToolContext) -> dict:
    """Update user information in the session state.
    
    Args:
        name: User's name
        role: User's role (student, teacher, admin)
        tool_context: Context for accessing and updating session state
    
    Returns:
        Confirmation message
    """
    print(f"--- Tool: update_user_info called for {name} ({role}) ---")
    
    # Clean state data first
    clean_state_data(tool_context)
    
    # Get current user info for comparison
    old_name = tool_context.state.get("user_name", "")
    old_role = tool_context.state.get("user_role", "")
    
    # Update user information in state
    try:
        if hasattr(tool_context.state, '__setitem__'):
            tool_context.state["user_name"] = str(name)
            tool_context.state["user_role"] = str(role.lower())
        elif hasattr(tool_context.state, 'update'):
            tool_context.state.update({
                "user_name": str(name),
                "user_role": str(role.lower())
            })
    except Exception as e:
        print(f"Warning: Could not update user info: {e}")
    
    # Increment session count
    session_count = tool_context.state.get("session_count", 0) + 1
    try:
        if hasattr(tool_context.state, '__setitem__'):
            tool_context.state["session_count"] = session_count
        elif hasattr(tool_context.state, 'update'):
            tool_context.state.update({"session_count": session_count})
    except Exception as e:
        print(f"Warning: Could not update session count: {e}")
    
    # Log this interaction
    log_interaction(tool_context, "user_info_update", f"Updated to {name} ({role})")
    
    # Clean state after update
    clean_state_data(tool_context)
    
    return {
        "action": "update_user_info",
        "name": name,
        "role": role,
        "old_name": old_name,
        "old_role": old_role,
        "session_count": session_count,
        "message": f"Updated user info: {name} ({role}) - Session #{session_count}"
    }


def set_user_preferences(preferences: dict, tool_context: ToolContext) -> dict:
    """Set user preferences for personalized experience.
    
    Args:
        preferences: Dictionary with language, difficulty_level, subjects
        tool_context: Context for accessing and updating session state
    
    Returns:
        Confirmation message
    """
    print(f"--- Tool: set_user_preferences called ---")
    
    # Clean state data first
    clean_state_data(tool_context)
    
    current_prefs = tool_context.state.get("preferences", {})
    old_prefs = current_prefs.copy()
    
    # Update preferences while preserving existing ones
    current_prefs.update(preferences)
    
    try:
        if hasattr(tool_context.state, '__setitem__'):
            tool_context.state["preferences"] = current_prefs
        elif hasattr(tool_context.state, 'update'):
            tool_context.state.update({"preferences": current_prefs})
    except Exception as e:
        print(f"Warning: Could not update preferences: {e}")
    
    # Log this interaction
    log_interaction(tool_context, "preferences_update", f"Updated preferences: {preferences}")
    
    # Clean state after update
    clean_state_data(tool_context)
    
    return {
        "action": "set_user_preferences",
        "old_preferences": old_prefs,
        "new_preferences": current_prefs,
        "updated_fields": list(preferences.keys()),
        "message": f"Updated preferences: {', '.join(preferences.keys())}"
    }


def get_user_session_summary(tool_context: ToolContext) -> dict:
    """Get a summary of the current user's session data.
    
    Args:
        tool_context: Context for accessing session state
    
    Returns:
        Summary of session data
    """
    print("--- Tool: get_user_session_summary called ---")
    
    # Clean state data first
    clean_state_data(tool_context)
    
    state = tool_context.state
    
    # Calculate summary statistics
    attendance_records = state.get("attendance_records", {})
    interaction_history = state.get("interaction_history", [])
    preferences = state.get("preferences", {})
    
    # Get recent activity
    recent_interactions = interaction_history[-5:] if len(interaction_history) > 5 else interaction_history
    recent_attendance = sorted(
        attendance_records.values(), 
        key=lambda x: x.get("timestamp", ""), 
        reverse=True
    )[:5] if attendance_records else []
    
    summary = {
        "user_info": {
            "name": state.get("user_name", "Not set"),
            "role": state.get("user_role", "Not set"),
            "session_count": state.get("session_count", 0)
        },
        "preferences": preferences,
        "statistics": {
            "total_attendance_records": len(attendance_records),
            "total_interactions": len(interaction_history),
            "preferences_set": len(preferences)
        },
        "recent_activity": {
            "recent_interactions": recent_interactions,
            "recent_attendance": recent_attendance
        }
    }
    
    return {
        "action": "get_user_session_summary",
        "summary": summary,
        "message": f"Session summary for {state.get('user_name', 'user')} - Session #{state.get('session_count', 0)}"
    }


def log_interaction(tool_context: ToolContext, interaction_type: str, details: str) -> dict:
    """Log a user interaction for tracking and analytics.
    
    Args:
        tool_context: Context for accessing session state
        interaction_type: Type of interaction (e.g., 'query', 'attendance', 'mcq_request')
        details: Details about the interaction
    
    Returns:
        Confirmation of logging
    """
    # Clean state data first
    clean_state_data(tool_context)
    
    interaction_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": str(interaction_type),
        "details": str(details)[:500],  # Limit details length
        "session_count": tool_context.state.get("session_count", 0),
        "user_role": tool_context.state.get("user_role", "unknown")
    }
    
    # Add to interaction history
    interaction_history = tool_context.state.get("interaction_history", [])
    interaction_history.append(interaction_entry)
    
    # Keep only last 100 interactions to prevent excessive growth
    if len(interaction_history) > 100:
        interaction_history = interaction_history[-100:]
    
    try:
        if hasattr(tool_context.state, '__setitem__'):
            tool_context.state["interaction_history"] = interaction_history
        elif hasattr(tool_context.state, 'update'):
            tool_context.state.update({"interaction_history": interaction_history})
    except Exception as e:
        print(f"Warning: Could not update interaction history: {e}")
    
    # Clean state after update
    clean_state_data(tool_context)
    
    return {
        "action": "log_interaction",
        "type": interaction_type,
        "timestamp": interaction_entry["timestamp"],
        "total_interactions": len(interaction_history)
    }


def clear_user_data(data_type: str, tool_context: ToolContext) -> dict:
    """Clear specific types of user data (for privacy/cleanup).
    
    Args:
        data_type: Type of data to clear ('interactions', 'attendance', 'preferences', 'all')
        tool_context: Context for accessing session state
    
    Returns:
        Confirmation of data clearing
    """
    print(f"--- Tool: clear_user_data called for {data_type} ---")
    
    # Clean state data first
    clean_state_data(tool_context)
    
    cleared_items = {}
    
    try:
        if data_type.lower() in ['interactions', 'all']:
            interactions_count = len(tool_context.state.get("interaction_history", []))
            if hasattr(tool_context.state, '__setitem__'):
                tool_context.state["interaction_history"] = []
            elif hasattr(tool_context.state, 'update'):
                tool_context.state.update({"interaction_history": []})
            cleared_items["interactions"] = interactions_count
        
        if data_type.lower() in ['attendance', 'all']:
            attendance_count = len(tool_context.state.get("attendance_records", {}))
            if hasattr(tool_context.state, '__setitem__'):
                tool_context.state["attendance_records"] = {}
            elif hasattr(tool_context.state, 'update'):
                tool_context.state.update({"attendance_records": {}})
            cleared_items["attendance_records"] = attendance_count
        
        if data_type.lower() in ['preferences', 'all']:
            default_prefs = {
                "language": "english",
                "difficulty_level": "medium",
                "subjects": []
            }
            if hasattr(tool_context.state, '__setitem__'):
                tool_context.state["preferences"] = default_prefs
            elif hasattr(tool_context.state, 'update'):
                tool_context.state.update({"preferences": default_prefs})
            cleared_items["preferences"] = "reset to defaults"
        
        if data_type.lower() == 'all':
            # Reset to initial state but keep user info and session count
            user_name = tool_context.state.get("user_name", "")
            user_role = tool_context.state.get("user_role", "")
            session_count = tool_context.state.get("session_count", 0)
            
            # Clear all keys first
            keys_to_remove = list(tool_context.state.keys())
            for key in keys_to_remove:
                try:
                    if hasattr(tool_context.state, '__delitem__'):
                        del tool_context.state[key]
                except Exception as e:
                    print(f"Warning: Could not remove key {key}: {e}")
            
            # Set the essential data back
            initial_state = {
                "user_name": user_name,
                "user_role": user_role,
                "session_count": session_count,
                "preferences": {
                    "language": "english",
                    "difficulty_level": "medium",
                    "subjects": []
                },
                "interaction_history": [],
                "attendance_records": {},
            }
            
            for key, value in initial_state.items():
                try:
                    if hasattr(tool_context.state, '__setitem__'):
                        tool_context.state[key] = value
                    elif hasattr(tool_context.state, 'update'):
                        tool_context.state.update({key: value})
                except Exception as e:
                    print(f"Warning: Could not set {key}: {e}")
    
    except Exception as e:
        print(f"Error during data clearing: {e}")
    
    # Log this action
    log_interaction(tool_context, "data_cleanup", f"Cleared {data_type} data")
    
    # Clean state after update
    clean_state_data(tool_context)
    
    return {
        "action": "clear_user_data",
        "data_type": data_type,
        "cleared_items": cleared_items,
        "message": f"Successfully cleared {data_type} data: {cleared_items}"
    }


def get_session_analytics(tool_context: ToolContext) -> dict:
    """Get analytics about the user's session and usage patterns.
    
    Args:
        tool_context: Context for accessing session state
    
    Returns:
        Analytics data
    """
    print("--- Tool: get_session_analytics called ---")
    
    # Clean state data first
    clean_state_data(tool_context)
    
    state = tool_context.state
    interactions = state.get("interaction_history", [])
    attendance_records = state.get("attendance_records", {})
    
    # Analyze interaction patterns
    interaction_types = {}
    for interaction in interactions:
        itype = interaction.get("type", "unknown")
        interaction_types[itype] = interaction_types.get(itype, 0) + 1
    
    # Analyze attendance patterns if user is teacher/admin
    attendance_stats = {}
    if state.get("user_role") in ["teacher", "admin"] and attendance_records:
        # Count by status
        status_count = {}
        subject_count = {}
        for record in attendance_records.values():
            status = record.get("status", "unknown")
            subject = record.get("subject", "unknown")
            status_count[status] = status_count.get(status, 0) + 1
            subject_count[subject] = subject_count.get(subject, 0) + 1
        
        attendance_stats = {
            "by_status": status_count,
            "by_subject": subject_count,
            "total_records": len(attendance_records)
        }
    
    # Recent activity summary
    recent_interactions = interactions[-10:] if len(interactions) > 10 else interactions
    
    analytics = {
        "user_info": {
            "name": state.get("user_name", "Not set"),
            "role": state.get("user_role", "Not set"),
            "session_count": state.get("session_count", 0)
        },
        "interaction_analytics": {
            "total_interactions": len(interactions),
            "interaction_types": interaction_types,
            "recent_interactions": len(recent_interactions)
        },
        "attendance_analytics": attendance_stats,
        "preferences": state.get("preferences", {}),
        "data_health": {
            "state_keys": list(state.keys()),
            "largest_data_structure": max(
                [(k, len(v)) for k, v in state.items() if isinstance(v, (list, dict))],
                key=lambda x: x[1],
                default=("none", 0)
            )
        }
    }
    
    return {
        "action": "get_session_analytics",
        "analytics": analytics,
        "message": f"Analytics for {state.get('user_name', 'user')} - {len(interactions)} total interactions"
    }


root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Educational Manager Agent with comprehensive persistent memory and session management",
    instruction="""
    You are a comprehensive educational manager agent with advanced persistent storage capabilities.
    You manage user sessions, delegate tasks to specialized subagents, and maintain detailed
    user data across multiple sessions.
    
    **PERSISTENT SESSION STATE:**
    
    The session state contains:
    - user_name: Current user's name
    - user_role: User's role (student, teacher, admin)  
    - session_count: Number of sessions for this user
    - preferences: User preferences (language, difficulty_level, subjects)
    - interaction_history: Detailed history of all user interactions
    - attendance_records: Complete attendance data (managed by attendance_agent)
    - student_profiles: Detailed student psychological and academic profiles
    - learning_paths: Personalized learning paths for students
    - progress_analyses: Comprehensive progress tracking and analytics
    - resource_search_history: History of educational resource searches
    - saved_resource_recommendations: Curated educational resources by teachers
    - evaluation_sessions: Comprehensive student evaluation data and analysis
    
    **SESSION MANAGEMENT TOOLS:**
    
    You have powerful tools for managing persistent data:
    1. **update_user_info**: Update user name and role, increment session count
    2. **set_user_preferences**: Update user preferences for personalized experience
    3. **get_user_session_summary**: Get comprehensive overview of user's data
    4. **log_interaction**: Track specific user interactions for analytics
    5. **clear_user_data**: Clean up user data for privacy/maintenance
    6. **get_session_analytics**: Get detailed analytics about usage patterns
    
    **SPECIALIZED SUB-AGENTS:**
    
    Delegate tasks to appropriate subagents based on their expertise:
    
    **📝 MCQ Creator (mcq_creator)**:
    - Creates multiple choice questions for any subject and difficulty level
    - Generates answer explanations and educational feedback
    - Supports various question types and formats
    - Ideal for: "Create MCQ questions", "Generate quiz", "Test creation"
    
    **🎨 Visualization Creator (visualization_creator)**:
    - Creates 3D HTML visualizations, interactive diagrams, and educational graphics
    - Builds immersive learning experiences with WebGL and Three.js
    - Generates charts, graphs, and data visualizations
    - Ideal for: "Create 3D model", "Visualize concept", "Interactive diagram"
    
    **🎮 Game Creator (game_creator)**:
    - Develops educational games and interactive learning activities
    - Creates gamified assessments and skill-building exercises
    - Builds engaging educational experiences with game mechanics
    - Ideal for: "Create learning game", "Educational activity", "Interactive exercise"
    
    **🤔 Q&A Agent (qa_agent)**:
    - Handles general educational questions and explanations
    - Provides detailed subject matter expertise across all academic areas
    - Offers step-by-step problem solving and concept clarification
    - Ideal for: "Explain concept", "Help with homework", "Answer questions"
    
    **📊 Attendance Agent (attendance_agent)**:
    - **Enhanced student attendance management with intelligent database features**
    - **Smart Attendance Saving**: Automatically searches existing student database, creates new students if needed
    - **Minimal Information Required**: Only asks for student name initially, grade only for new students
    - **Database Growth**: Automatically expands student database with unique IDs and tracking
    - **Quick Workflow**: Optimized for fast attendance marking during class time
    - **Comprehensive Reporting**: Attendance summaries, patterns, and analytics
    - **Duplicate Prevention**: Prevents duplicate attendance for same student/date
    - Ideal for: "Save attendance for [student]", "Attendance report", "Student lookup"
    
    **🎯 Personalized Learning Agent (personalized_learning_agent)**:
    - **Advanced personalized learning path creator using educational psychology**
    - **Psychological Analysis**: Applies VARK learning styles, Multiple Intelligences, emotional intelligence
    - **Adaptive Path Creation**: Week-by-week learning sequences with personalized pacing
    - **Multi-Modal Activities**: Creates activities matching individual learning preferences
    - **Assessment Personalization**: Chooses assessment methods based on student profiles
    - **Teacher Insights**: Provides classroom strategies and differentiation techniques
    - **Curriculum Integration**: Maps teacher's curriculum topics to personalized timelines
    - Ideal for: "Create learning path for [student]", "Personalize curriculum", "Student-specific planning"
    
    **📈 Progress Analyzer Agent (progress_analyzer_agent)**:
    - **Comprehensive student progress analysis across all platform activities**
    - **Multi-Source Integration**: Combines attendance, MCQ results, game engagement, learning paths
    - **Progress Metrics**: Overall scores (0-100), subject-specific analysis, engagement levels
    - **Behavioral Insights**: Learning patterns, consistency, motivation drivers
    - **Predictive Analysis**: Risk identification and intervention recommendations
    - **Teacher Reports**: Executive summaries, key metrics, priority actions
    - **Historical Tracking**: Progress over time with trend analysis
    - Ideal for: "Analyze [student] progress", "Student performance report", "Progress tracking"
    
    **🔍 Resource Recommendation Agent (resource_recommendation_agent)**:
    - **Intelligent educational resource finder with web search capabilities**
    - **Web-Based Discovery**: Searches for videos, articles, books, interactive content across the internet
    - **Quality Curation**: Evaluates educational value, accessibility, and age-appropriateness
    - **Personalized Matching**: Adapts to grade levels and learning style preferences
    - **Multi-Source Integration**: YouTube, Khan Academy, Coursera, academic papers, simulations
    - **Save & Organize**: Teachers can save and categorize resource recommendations
    - **Implementation Guidance**: Provides practical suggestions for classroom use
    - Ideal for: "Find resources for [topic]", "Educational videos about [subject]", "Interactive learning materials"
    
    **🧠 Student Evaluation Agent (student_evaluation_agent)**:
    - **Comprehensive student evaluation and psychological analysis specialist**
    - **Structured Assessments**: Conducts detailed 15+ question evaluations to understand learning styles
    - **Psychological Insights**: Analyzes emotional patterns, motivation levels, and behavioral tendencies
    - **Learning Style Analysis**: Identifies visual, auditory, kinesthetic, and reading/writing preferences
    - **Profile Creation**: Generates detailed student profiles with strengths, weaknesses, and recommendations
    - **Evidence-Based Analysis**: Uses educational psychology principles for actionable insights
    - **Teacher Guidance**: Provides specific strategies for personalized instruction
    - **Ongoing Tracking**: Maintains evaluation sessions and profile updates over time
    - Ideal for: "Evaluate [student]", "Create student profile", "Understanding learning styles", "Student assessment"
    
    **DELEGATION GUIDELINES:**
    
    Choose the right agent based on the request:
    - **Content Creation**: mcq_creator, visualization_creator, game_creator
    - **Student Management**: attendance_agent, personalized_learning_agent, progress_analyzer_agent, student_evaluation_agent
    - **Educational Support**: qa_agent for general questions and explanations
    - **Resource Discovery**: resource_recommendation_agent for finding educational materials
    - **Data Analysis**: progress_analyzer_agent for comprehensive insights
    - **Personalization**: personalized_learning_agent for individualized learning experiences
    - **Student Assessment**: student_evaluation_agent for comprehensive evaluations and profiles
    
    **USER ONBOARDING & MANAGEMENT:**
    
    1. **New Users (empty user_name)**:
       - Warmly welcome them to Sahayak Educational Agent
       - Explain that the system remembers them across sessions
       - Ask for their name and role (student/teacher/admin)
       - Use update_user_info to store their information
       - Explain features available based on their role
       - Optionally ask about preferences (language, difficulty, subjects)
    
    2. **Returning Users (has user_name)**:
       - Welcome them back by name with session number
       - Acknowledge their role and mention persistent features
       - Offer to continue from where they left off
       - Suggest activities based on their interaction history
       - Show awareness of their preferences and past activity
    
    3. **Role-Based Personalization**:
       - **Students**: Focus on learning, practice, games, progress tracking, resource discovery
       - **Teachers**: Emphasize content creation, attendance, student management, personalized learning paths, resource curation, student evaluation
       - **Admins**: Highlight reporting, analytics, bulk operations, system management, resource oversight, comprehensive student assessments
    
    **ADVANCED EDUCATIONAL FEATURES:**
    
    For teachers and admins, provide comprehensive educational management:
    - **Student Database**: Automatic student creation and management via attendance_agent
    - **Learning Analytics**: Deep insights into student progress and behavior patterns
    - **Personalized Education**: Individual learning paths based on psychological profiles
    - **Resource Discovery**: Web-based search and curation of educational materials
    - **Data-Driven Decisions**: Comprehensive analytics for educational interventions
    - **Curriculum Mapping**: Alignment of personalized paths with curriculum requirements
    - **Student Evaluation**: Comprehensive psychological and educational assessments
    
    **SMART PERSONALIZATION:**
    
    Use persistent data intelligently:
    - Reference previous interactions naturally in conversation
    - Adapt content difficulty based on stored preferences
    - Suggest follow-up activities based on interaction history
    - Remember user's favorite subjects and teaching methods
    - Track progress over time and celebrate milestones
    - Connect related activities across different agents (e.g., MCQ performance → learning path adjustments)
    - Use student evaluation data to inform all other educational activities
    
    **RESPONSE PATTERNS:**
    
    1. **First Session**: "Welcome to Sahayak Educational Agent! I'm designed to remember our conversations and help you build on previous learning. To get started, could you tell me your name and whether you're a student, teacher, or administrator?"
    
    2. **Returning Users**: "Welcome back, [Name]! Great to see you again - this is your session #[X]. I remember you're a [role] and we've worked together on [reference to past activity]. How can I help you today?"
    
    3. **Session Continuity**: "Building on our previous conversation about [topic]..." or "Following up on the [content type] we created last time..."
    
    4. **Analytics Integration**: When appropriate, reference usage patterns: "I notice you often ask about [subject], so I've prepared some advanced material..."
    
    **PRIVACY & DATA MANAGEMENT:**
    
    - Respect user privacy while maintaining helpful persistence
    - Offer users control over their data with clear_user_data tool
    - Provide transparency about what data is stored
    - Use analytics responsibly to improve user experience
    
    **CONVERSATION FLOW:**
    
    Always maintain context awareness:
    - Reference session count naturally in conversation
    - Build on previous interactions when relevant
    - Adapt your communication style based on user's demonstrated preferences
    - Proactively suggest relevant features based on role and history
    - Connect insights across different agent interactions for holistic support
    - Leverage student evaluation data to enhance all educational recommendations
    
    Remember: Every interaction is an opportunity to demonstrate the value of persistent
    memory while providing excellent educational support. Make users feel that their
    data is working for them to create a better, more personalized learning experience
    across all educational activities, including comprehensive student evaluation and analysis.
    """,
    sub_agents=[
        mcq_creator, 
        visualization_creator, 
        game_creator, 
        qa_agent, 
        attendance_agent,
        personalized_learning_agent,
        progress_analyzer_agent,
        resource_recommendation_agent,
        student_evaluation_agent
    ],
    tools=[
        update_user_info, 
        set_user_preferences, 
        get_user_session_summary,
        log_interaction,
        clear_user_data,
        get_session_analytics
    ],
)