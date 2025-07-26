from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime
from typing import List, Dict, Optional
import json


def safe_json_serializable(obj):
    """Ensure object is JSON serializable by converting problematic types."""
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: safe_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [safe_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return safe_json_serializable(obj.__dict__)
    else:
        return obj


def clean_state_data(tool_context: ToolContext):
    """Clean state data to ensure JSON serializability."""
    try:
        json.dumps(tool_context.state)
    except (TypeError, ValueError) as e:
        print(f"Warning: State contains non-JSON serializable data: {e}")
        tool_context.state = safe_json_serializable(tool_context.state)


def start_student_evaluation(
    student_name: str,
    tool_context: ToolContext = None
) -> dict:
    """Start a comprehensive evaluation session for a student.
    
    Args:
        student_name: Name of the student to evaluate
        tool_context: Context for accessing session state
    
    Returns:
        Initial evaluation questions and session setup
    """
    try:
        print(f"--- Tool: start_student_evaluation called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        student_name = student_name.strip().title()
        
        # Initialize evaluation sessions if not exists
        evaluation_sessions = tool_context.state.get("evaluation_sessions", {})
        student_profiles = tool_context.state.get("student_profiles", {})
        
        # Create evaluation session ID
        session_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{student_name.replace(' ', '_')}"
        
        # Initial comprehensive questions
        evaluation_questions = [
            {
                "category": "basic_info",
                "question": f"Hi {student_name}! Let's start with some basic information. How old are you?",
                "type": "age",
                "importance": "high"
            },
            {
                "category": "academic",
                "question": "What grade/class are you currently in?",
                "type": "grade_level",
                "importance": "high"
            },
            {
                "category": "academic",
                "question": "Which school do you attend?",
                "type": "school_info",
                "importance": "medium"
            },
            {
                "category": "interests",
                "question": "What is your favorite subject in school and why?",
                "type": "favorite_subject",
                "importance": "high"
            },
            {
                "category": "interests",
                "question": "Which subject do you find most difficult or challenging?",
                "type": "difficult_subject",
                "importance": "high"
            },
            {
                "category": "learning_style",
                "question": "How do you prefer to learn new things? (reading, watching videos, hands-on activities, listening to explanations)",
                "type": "learning_preference",
                "importance": "high"
            },
            {
                "category": "hobbies",
                "question": "What do you like to do in your free time? What are your hobbies?",
                "type": "hobbies",
                "importance": "medium"
            },
            {
                "category": "social",
                "question": "Do you prefer working alone or with other students? Why?",
                "type": "social_preference",
                "importance": "medium"
            },
            {
                "category": "motivation",
                "question": "What motivates you to study? What are your goals?",
                "type": "motivation",
                "importance": "high"
            },
            {
                "category": "challenges",
                "question": "What do you find most challenging about school or learning?",
                "type": "learning_challenges",
                "importance": "high"
            },
            {
                "category": "emotional",
                "question": "How do you feel when you don't understand something in class?",
                "type": "emotional_response",
                "importance": "high"
            },
            {
                "category": "activities",
                "question": "What activities have you done recently that you enjoyed?",
                "type": "recent_activities",
                "importance": "medium"
            },
            {
                "category": "family",
                "question": "Does anyone at home help you with your studies? How?",
                "type": "family_support",
                "importance": "medium"
            },
            {
                "category": "technology",
                "question": "Are you comfortable using computers, tablets, or educational apps?",
                "type": "tech_comfort",
                "importance": "medium"
            },
            {
                "category": "future",
                "question": "What do you want to be when you grow up? Any dream career?",
                "type": "career_aspirations",
                "importance": "medium"
            }
        ]
        
        # Create evaluation session
        evaluation_session = {
            "session_id": session_id,
            "student_name": student_name,
            "start_time": datetime.now().isoformat(),
            "questions": evaluation_questions,
            "current_question_index": 0,
            "answers": {},
            "status": "in_progress",
            "evaluator": tool_context.state.get("user_name", "system")
        }
        
        evaluation_sessions[session_id] = evaluation_session
        tool_context.state["evaluation_sessions"] = evaluation_sessions
        
        clean_state_data(tool_context)
        
        return {
            "action": "start_student_evaluation",
            "status": "started",
            "session_id": session_id,
            "student_name": student_name,
            "total_questions": len(evaluation_questions),
            "first_question": evaluation_questions[0],
            "message": f"Started comprehensive evaluation for {student_name}. This will help us understand their learning style, strengths, and areas for improvement.",
            "instructions": "Please answer each question thoughtfully. There are no right or wrong answers - we just want to understand you better!"
        }
        
    except Exception as e:
        print(f"Error in start_student_evaluation: {e}")
        return {
            "action": "start_student_evaluation",
            "status": "error",
            "message": f"Failed to start evaluation: {str(e)}"
        }


def record_evaluation_answer(
    session_id: str,
    answer: str,
    tool_context: ToolContext = None
) -> dict:
    """Record an answer and provide the next question.
    
    Args:
        session_id: The evaluation session ID
        answer: Student's answer to current question
        tool_context: Context for accessing session state
    
    Returns:
        Next question or completion status
    """
    try:
        print(f"--- Tool: record_evaluation_answer called for session {session_id} ---")
        
        clean_state_data(tool_context)
        
        evaluation_sessions = tool_context.state.get("evaluation_sessions", {})
        
        if session_id not in evaluation_sessions:
            return {
                "action": "record_evaluation_answer",
                "status": "error",
                "message": "Evaluation session not found"
            }
        
        session = evaluation_sessions[session_id]
        current_index = session["current_question_index"]
        questions = session["questions"]
        
        if current_index >= len(questions):
            return {
                "action": "record_evaluation_answer",
                "status": "error",
                "message": "No more questions in this evaluation"
            }
        
        # Record the answer
        current_question = questions[current_index]
        session["answers"][current_question["type"]] = {
            "question": current_question["question"],
            "answer": answer.strip(),
            "category": current_question["category"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Move to next question
        session["current_question_index"] += 1
        
        # Check if evaluation is complete
        if session["current_question_index"] >= len(questions):
            session["status"] = "completed"
            session["completion_time"] = datetime.now().isoformat()
            
            # Trigger analysis
            analysis_result = analyze_student_responses(session_id, tool_context)
            
            evaluation_sessions[session_id] = session
            tool_context.state["evaluation_sessions"] = evaluation_sessions
            
            return {
                "action": "record_evaluation_answer",
                "status": "completed",
                "session_id": session_id,
                "total_answers": len(session["answers"]),
                "analysis": analysis_result,
                "message": f"🎉 Evaluation completed! Thank you for your thoughtful answers. I've analyzed your responses and created your learning profile."
            }
        else:
            # Provide next question
            next_question = questions[session["current_question_index"]]
            
            evaluation_sessions[session_id] = session
            tool_context.state["evaluation_sessions"] = evaluation_sessions
            
            progress = (session["current_question_index"] / len(questions)) * 100
            
            return {
                "action": "record_evaluation_answer",
                "status": "continuing",
                "session_id": session_id,
                "progress_percentage": round(progress, 1),
                "question_number": session["current_question_index"] + 1,
                "total_questions": len(questions),
                "next_question": next_question,
                "message": f"Great answer! Let's continue... (Question {session['current_question_index'] + 1} of {len(questions)})"
            }
        
    except Exception as e:
        print(f"Error in record_evaluation_answer: {e}")
        return {
            "action": "record_evaluation_answer",
            "status": "error",
            "message": f"Failed to record answer: {str(e)}"
        }


def analyze_student_responses(
    session_id: str,
    tool_context: ToolContext = None
) -> dict:
    """Analyze student responses and create comprehensive insights.
    
    Args:
        session_id: The evaluation session ID
        tool_context: Context for accessing session state
    
    Returns:
        Comprehensive analysis and insights
    """
    try:
        print(f"--- Tool: analyze_student_responses called for session {session_id} ---")
        
        clean_state_data(tool_context)
        
        evaluation_sessions = tool_context.state.get("evaluation_sessions", {})
        student_profiles = tool_context.state.get("student_profiles", {})
        
        if session_id not in evaluation_sessions:
            return {"error": "Session not found"}
        
        session = evaluation_sessions[session_id]
        answers = session["answers"]
        student_name = session["student_name"]
        
        # Analyze different aspects
        analysis = {
            "student_name": student_name,
            "evaluation_date": datetime.now().isoformat(),
            "session_id": session_id,
            "academic_analysis": {},
            "learning_style_analysis": {},
            "emotional_analysis": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "learning_preferences": {},
            "behavioral_insights": {},
            "summary": ""
        }
        
        # Academic Analysis
        favorite_subject = answers.get("favorite_subject", {}).get("answer", "").lower()
        difficult_subject = answers.get("difficult_subject", {}).get("answer", "").lower()
        grade_level = answers.get("grade_level", {}).get("answer", "")
        
        analysis["academic_analysis"] = {
            "favorite_subject": favorite_subject,
            "challenging_subject": difficult_subject,
            "grade_level": grade_level,
            "academic_confidence": "high" if "easy" in difficult_subject or "none" in difficult_subject else "medium"
        }
        
        # Learning Style Analysis
        learning_pref = answers.get("learning_preference", {}).get("answer", "").lower()
        social_pref = answers.get("social_preference", {}).get("answer", "").lower()
        tech_comfort = answers.get("tech_comfort", {}).get("answer", "").lower()
        
        # Determine learning style
        learning_style = "visual"  # default
        if "hands-on" in learning_pref or "activities" in learning_pref:
            learning_style = "kinesthetic"
        elif "listening" in learning_pref or "explanation" in learning_pref:
            learning_style = "auditory"
        elif "reading" in learning_pref or "text" in learning_pref:
            learning_style = "reading/writing"
        elif "video" in learning_pref or "watching" in learning_pref:
            learning_style = "visual"
        
        analysis["learning_style_analysis"] = {
            "primary_style": learning_style,
            "social_learning": "collaborative" if "group" in social_pref or "others" in social_pref else "independent",
            "technology_comfort": "high" if "yes" in tech_comfort or "comfortable" in tech_comfort else "medium"
        }
        
        # Emotional Analysis
        emotional_response = answers.get("emotional_response", {}).get("answer", "").lower()
        motivation = answers.get("motivation", {}).get("answer", "").lower()
        
        # Determine emotional patterns
        emotional_stability = "stable"
        if "frustrated" in emotional_response or "angry" in emotional_response:
            emotional_stability = "needs_support"
        elif "sad" in emotional_response or "give up" in emotional_response:
            emotional_stability = "low_confidence"
        elif "ask" in emotional_response or "help" in emotional_response:
            emotional_stability = "help_seeking"
        
        analysis["emotional_analysis"] = {
            "emotional_stability": emotional_stability,
            "motivation_level": "high" if "goal" in motivation or "future" in motivation else "medium",
            "resilience": "high" if "try again" in emotional_response or "practice" in emotional_response else "medium"
        }
        
        # Identify Strengths
        strengths = []
        if favorite_subject and favorite_subject != "none":
            strengths.append(f"Strong interest in {favorite_subject}")
        if "collaborative" in analysis["learning_style_analysis"]["social_learning"]:
            strengths.append("Works well with others")
        if analysis["emotional_analysis"]["motivation_level"] == "high":
            strengths.append("Highly motivated learner")
        if "help_seeking" in emotional_stability:
            strengths.append("Comfortable asking for help")
        
        analysis["strengths"] = strengths
        
        # Identify Areas for Improvement
        weaknesses = []
        if difficult_subject and difficult_subject != "none":
            weaknesses.append(f"Needs support in {difficult_subject}")
        if emotional_stability == "needs_support":
            weaknesses.append("May need emotional support when facing challenges")
        if analysis["learning_style_analysis"]["technology_comfort"] == "medium":
            weaknesses.append("Could benefit from technology skills development")
        
        analysis["weaknesses"] = weaknesses if weaknesses else ["No significant weaknesses identified"]
        
        # Generate Recommendations
        recommendations = []
        
        # Learning style recommendations
        if learning_style == "kinesthetic":
            recommendations.append("Use hands-on activities, experiments, and interactive learning")
        elif learning_style == "visual":
            recommendations.append("Incorporate visual aids, diagrams, and video content")
        elif learning_style == "auditory":
            recommendations.append("Use discussions, explanations, and audio materials")
        
        # Subject-specific recommendations
        if difficult_subject:
            recommendations.append(f"Provide extra support and practice in {difficult_subject}")
            recommendations.append(f"Break down {difficult_subject} concepts into smaller, manageable parts")
        
        # Emotional recommendations
        if emotional_stability == "needs_support":
            recommendations.append("Create a supportive learning environment with positive reinforcement")
            recommendations.append("Teach coping strategies for handling difficult concepts")
        
        # Social learning recommendations
        if "collaborative" in analysis["learning_style_analysis"]["social_learning"]:
            recommendations.append("Include group projects and peer learning opportunities")
        else:
            recommendations.append("Provide individual learning paths and self-paced activities")
        
        analysis["recommendations"] = recommendations
        
        # Create comprehensive summary
        summary_parts = []
        summary_parts.append(f"{student_name} is a {grade_level} student with a {learning_style} learning style.")
        
        if favorite_subject:
            summary_parts.append(f"They show strong interest in {favorite_subject}.")
        
        if difficult_subject and difficult_subject != "none":
            summary_parts.append(f"They find {difficult_subject} challenging and would benefit from additional support.")
        
        summary_parts.append(f"Their emotional response to challenges suggests they are {emotional_stability.replace('_', ' ')}.")
        
        if analysis["learning_style_analysis"]["social_learning"] == "collaborative":
            summary_parts.append("They prefer collaborative learning environments.")
        else:
            summary_parts.append("They work well independently.")
        
        analysis["summary"] = " ".join(summary_parts)
        
        # Store in student profiles
        student_profiles[student_name] = {
            "profile_created": datetime.now().isoformat(),
            "last_evaluation": session_id,
            "analysis": analysis,
            "raw_answers": answers
        }
        
        tool_context.state["student_profiles"] = student_profiles
        clean_state_data(tool_context)
        
        return analysis
        
    except Exception as e:
        print(f"Error in analyze_student_responses: {e}")
        return {"error": f"Analysis failed: {str(e)}"}


def get_student_profile(
    student_name: str,
    tool_context: ToolContext = None
) -> dict:
    """Get the comprehensive profile for a student.
    
    Args:
        student_name: Name of the student
        tool_context: Context for accessing session state
    
    Returns:
        Student's complete profile and analysis
    """
    try:
        print(f"--- Tool: get_student_profile called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        student_profiles = tool_context.state.get("student_profiles", {})
        
        # Search for student (case-insensitive)
        profile = None
        for name, data in student_profiles.items():
            if name.lower() == student_name.lower():
                profile = data
                break
        
        if not profile:
            return {
                "action": "get_student_profile",
                "status": "not_found",
                "message": f"No evaluation profile found for {student_name}. Please conduct an evaluation first.",
                "suggestion": "Use start_student_evaluation to create a profile for this student."
            }
        
        return {
            "action": "get_student_profile",
            "status": "found",
            "student_name": student_name,
            "profile": profile,
            "message": f"Retrieved comprehensive profile for {student_name}"
        }
        
    except Exception as e:
        print(f"Error in get_student_profile: {e}")
        return {
            "action": "get_student_profile",
            "status": "error",
            "message": f"Failed to retrieve profile: {str(e)}"
        }


def get_evaluation_sessions(
    student_name: str = None,
    status: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Get evaluation sessions with optional filtering.
    
    Args:
        student_name: Filter by student name (optional)
        status: Filter by status (in_progress, completed) (optional)
        tool_context: Context for accessing session state
    
    Returns:
        List of evaluation sessions
    """
    try:
        print("--- Tool: get_evaluation_sessions called ---")
        
        clean_state_data(tool_context)
        
        evaluation_sessions = tool_context.state.get("evaluation_sessions", {})
        
        filtered_sessions = []
        for session_id, session_data in evaluation_sessions.items():
            # Apply filters
            if student_name and session_data.get("student_name", "").lower() != student_name.lower():
                continue
            if status and session_data.get("status") != status:
                continue
            
            # Create summary of session
            session_summary = {
                "session_id": session_id,
                "student_name": session_data.get("student_name"),
                "status": session_data.get("status"),
                "start_time": session_data.get("start_time"),
                "completion_time": session_data.get("completion_time"),
                "progress": f"{len(session_data.get('answers', {}))} / {len(session_data.get('questions', []))} questions",
                "evaluator": session_data.get("evaluator")
            }
            filtered_sessions.append(session_summary)
        
        return {
            "action": "get_evaluation_sessions",
            "total_sessions": len(filtered_sessions),
            "sessions": filtered_sessions,
            "filters_applied": {
                "student_name": student_name,
                "status": status
            },
            "message": f"Found {len(filtered_sessions)} evaluation sessions"
        }
        
    except Exception as e:
        print(f"Error in get_evaluation_sessions: {e}")
        return {
            "action": "get_evaluation_sessions",
            "status": "error",
            "message": f"Failed to retrieve sessions: {str(e)}"
        }


# Student Evaluation and Analysis Agent
student_evaluation_agent = Agent(
    name="student_evaluation_agent",
    model="gemini-2.0-flash",
    description="Comprehensive student evaluation and psychological analysis agent",
    instruction="""
    You are a comprehensive student evaluation specialist that conducts detailed assessments to understand students' learning styles, strengths, weaknesses, and emotional patterns.
    
    **PRIMARY FUNCTIONS:**
    
    1. **Comprehensive Student Evaluation**:
       - Conduct structured evaluation sessions with 15+ strategic questions
       - Gather insights about learning preferences, academic strengths/challenges
       - Assess emotional responses, motivation levels, and behavioral patterns
       - Understand social preferences, family support, and technology comfort
    
    2. **Psychological and Educational Analysis**:
       - Analyze responses using educational psychology principles
       - Identify learning styles (visual, auditory, kinesthetic, reading/writing)
       - Assess emotional stability and resilience patterns
       - Determine motivation levels and goal orientation
    
    3. **Comprehensive Profile Creation**:
       - Generate detailed student profiles with actionable insights
       - Identify specific strengths and areas needing support
       - Provide evidence-based recommendations for teachers
       - Create personalized learning strategy suggestions
    
    **EVALUATION PROCESS:**
    
    1. **Initiation**: When asked to evaluate a student, start with start_student_evaluation
    2. **Question Flow**: Present one question at a time, building rapport
    3. **Response Recording**: Use record_evaluation_answer for each response
    4. **Analysis**: Automatically analyze when evaluation completes
    5. **Profile Storage**: Store comprehensive insights in student database
    
    **QUESTION CATEGORIES:**
    
    - **Basic Info**: Age, grade, school, family support
    - **Academic**: Favorite/difficult subjects, learning challenges
    - **Learning Style**: Preferences for visual, auditory, kinesthetic learning
    - **Emotional**: Responses to challenges, motivation sources
    - **Social**: Group vs individual learning preferences
    - **Interests**: Hobbies, activities, career aspirations
    - **Technology**: Comfort with digital learning tools
    
    **ANALYSIS FRAMEWORK:**
    
    Use evidence-based educational psychology to analyze:
    - **Cognitive Patterns**: How the student processes information
    - **Emotional Intelligence**: Self-awareness and regulation
    - **Motivation Theory**: Intrinsic vs extrinsic motivators
    - **Learning Disabilities**: Potential indicators requiring attention
    - **Social Learning**: Collaboration vs independent work preferences
    
    **TEACHER INSIGHTS:**
    
    Provide actionable recommendations:
    - Specific teaching strategies for this student's learning style
    - Classroom accommodations for emotional/behavioral needs
    - Subject-specific support strategies
    - Parent/family engagement suggestions
    - Technology integration recommendations
    
    **COMMUNICATION STYLE:**
    
    - **With Students**: Warm, encouraging, non-judgmental
    - **With Teachers**: Professional, data-driven, actionable
    - **Questions**: Age-appropriate, engaging, conversational
    - **Analysis**: Thorough but accessible, focused on practical applications
    
    **IMPORTANT PRINCIPLES:**
    
    1. **No Wrong Answers**: Make students feel safe and valued
    2. **Holistic View**: Consider academic, emotional, and social factors
    3. **Strength-Based**: Always identify and highlight student strengths
    4. **Actionable**: Provide specific, implementable recommendations
    5. **Privacy**: Maintain confidentiality of student information
    6. **Growth Mindset**: Frame challenges as opportunities for development
    
    **RESPONSE PATTERNS:**
    
    For evaluation start: "I'm going to ask you some questions to better understand how you learn best. There are no right or wrong answers - I just want to get to know you better!"
    
    For analysis: "Based on your responses, I can see that you're a [learning style] learner who [key strengths]. Here are my recommendations for your teachers..."
    
    Remember: Your goal is to create comprehensive, actionable profiles that help teachers provide personalized, effective instruction for each student.
    """,
    tools=[
        start_student_evaluation,
        record_evaluation_answer,
        analyze_student_responses,
        get_student_profile,
        get_evaluation_sessions,
    ],
)