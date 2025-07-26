from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime, date, timedelta
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


def analyze_student_progress(
    student_name: str,
    time_period_days: int = 30,
    tool_context: ToolContext = None
) -> dict:
    """Comprehensive analysis of student's progress across all platform activities.
    
    Args:
        student_name: Name of the student to analyze
        time_period_days: Number of days to analyze (default 30)
        tool_context: Context for accessing session state
    
    Returns:
        Comprehensive progress analysis report
    """
    try:
        print(f"--- Tool: analyze_student_progress called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        # Get all relevant data from state
        students_db = tool_context.state.get("students_database", {})
        attendance_records = tool_context.state.get("attendance_records", {})
        student_profiles = tool_context.state.get("student_profiles", {})
        learning_paths = tool_context.state.get("learning_paths", {})
        mcq_results = tool_context.state.get("mcq_results", {})  # Assuming MCQ results are stored
        game_activities = tool_context.state.get("game_activities", {})  # Assuming game activities are stored
        
        # Find student data
        student_id = None
        student_info = None
        
        for sid, info in students_db.items():
            if info.get("name", "").lower() == student_name.lower():
                student_id = sid
                student_info = info
                break
        
        if not student_id:
            return {
                "action": "analyze_student_progress",
                "status": "not_found",
                "message": f"Student '{student_name}' not found in database"
            }
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=time_period_days)
        
        # Initialize progress analysis
        progress_analysis = {
            "student_name": student_name,
            "student_id": student_id,
            "analysis_period": f"{start_date} to {end_date}",
            "analysis_date": datetime.now().isoformat(),
            "time_period_days": time_period_days,
            "attendance_analysis": {},
            "academic_performance": {},
            "engagement_metrics": {},
            "learning_path_progress": {},
            "behavioral_insights": {},
            "recommendations": [],
            "overall_score": 0,
            "summary": ""
        }
        
        # 1. ATTENDANCE ANALYSIS
        attendance_data = analyze_attendance_pattern(
            student_id, attendance_records, start_date, end_date
        )
        progress_analysis["attendance_analysis"] = attendance_data
        
        # 2. MCQ PERFORMANCE ANALYSIS
        mcq_data = analyze_mcq_performance(
            student_name, mcq_results, start_date, end_date
        )
        progress_analysis["academic_performance"]["mcq_performance"] = mcq_data
        
        # 3. EDUCATIONAL GAMES ANALYSIS
        games_data = analyze_game_engagement(
            student_name, game_activities, start_date, end_date
        )
        progress_analysis["engagement_metrics"]["games"] = games_data
        
        # 4. LEARNING PATH PROGRESS
        learning_progress = analyze_learning_path_progress(
            student_name, learning_paths
        )
        progress_analysis["learning_path_progress"] = learning_progress
        
        # 5. BEHAVIORAL PATTERN ANALYSIS
        behavioral_data = analyze_behavioral_patterns(
            student_name, student_profiles, attendance_data, mcq_data, games_data
        )
        progress_analysis["behavioral_insights"] = behavioral_data
        
        # 6. CALCULATE OVERALL SCORE
        overall_score = calculate_overall_progress_score(
            attendance_data, mcq_data, games_data, learning_progress
        )
        progress_analysis["overall_score"] = overall_score
        
        # 7. GENERATE RECOMMENDATIONS
        recommendations = generate_progress_recommendations(
            progress_analysis, student_profiles.get(student_name, {})
        )
        progress_analysis["recommendations"] = recommendations
        
        # 8. CREATE SUMMARY
        summary = generate_progress_summary(progress_analysis)
        progress_analysis["summary"] = summary
        
        # Store analysis for future reference
        progress_analyses = tool_context.state.get("progress_analyses", {})
        analysis_id = f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{student_name.replace(' ', '_')}"
        progress_analyses[analysis_id] = progress_analysis
        tool_context.state["progress_analyses"] = progress_analyses
        
        clean_state_data(tool_context)
        
        return {
            "action": "analyze_student_progress",
            "status": "success",
            "analysis_id": analysis_id,
            "progress_analysis": progress_analysis,
            "message": f"✅ Comprehensive progress analysis completed for {student_name}",
            "key_metrics": {
                "overall_score": overall_score,
                "attendance_rate": attendance_data.get("attendance_percentage", 0),
                "mcq_average": mcq_data.get("average_score", 0),
                "games_played": games_data.get("total_games", 0)
            }
        }
        
    except Exception as e:
        print(f"Error in analyze_student_progress: {e}")
        return {
            "action": "analyze_student_progress",
            "status": "error",
            "message": f"Failed to analyze progress: {str(e)}"
        }


def analyze_attendance_pattern(student_id, attendance_records, start_date, end_date):
    """Analyze attendance patterns for the student."""
    student_attendance = []
    
    for record_key, record in attendance_records.items():
        if record.get("student_id") == student_id:
            record_date = datetime.fromisoformat(record.get("date")).date()
            if start_date <= record_date <= end_date:
                student_attendance.append(record)
    
    total_days = len(student_attendance)
    present_days = sum(1 for r in student_attendance if r.get("status") == "present")
    absent_days = sum(1 for r in student_attendance if r.get("status") == "absent")
    late_days = sum(1 for r in student_attendance if r.get("status") == "late")
    
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Analyze patterns
    patterns = []
    if attendance_percentage >= 95:
        patterns.append("Excellent attendance")
    elif attendance_percentage >= 85:
        patterns.append("Good attendance")
    elif attendance_percentage >= 75:
        patterns.append("Moderate attendance - needs improvement")
    else:
        patterns.append("Poor attendance - requires intervention")
    
    if late_days > total_days * 0.1:  # More than 10% late
        patterns.append("Frequent tardiness")
    
    return {
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "late_days": late_days,
        "attendance_percentage": round(attendance_percentage, 2),
        "patterns": patterns,
        "trend": "improving" if present_days > absent_days else "needs_attention"
    }


def analyze_mcq_performance(student_name, mcq_results, start_date, end_date):
    """Analyze MCQ test performance."""
    student_mcqs = []
    
    for result_key, result in mcq_results.items():
        if result.get("student_name", "").lower() == student_name.lower():
            result_date = datetime.fromisoformat(result.get("date", datetime.now().isoformat())).date()
            if start_date <= result_date <= end_date:
                student_mcqs.append(result)
    
    if not student_mcqs:
        return {
            "total_tests": 0,
            "average_score": 0,
            "highest_score": 0,
            "lowest_score": 0,
            "improvement_trend": "no_data",
            "subject_performance": {},
            "patterns": ["No MCQ tests taken in this period"]
        }
    
    scores = [r.get("score", 0) for r in student_mcqs]
    total_tests = len(student_mcqs)
    average_score = sum(scores) / total_tests
    highest_score = max(scores)
    lowest_score = min(scores)
    
    # Analyze by subject
    subject_performance = {}
    for mcq in student_mcqs:
        subject = mcq.get("subject", "Unknown")
        if subject not in subject_performance:
            subject_performance[subject] = []
        subject_performance[subject].append(mcq.get("score", 0))
    
    # Calculate subject averages
    for subject, scores_list in subject_performance.items():
        subject_performance[subject] = {
            "average": sum(scores_list) / len(scores_list),
            "tests_taken": len(scores_list),
            "best_score": max(scores_list)
        }
    
    # Determine improvement trend
    if len(scores) >= 3:
        recent_avg = sum(scores[-3:]) / 3
        early_avg = sum(scores[:3]) / 3
        if recent_avg > early_avg + 5:
            trend = "improving"
        elif recent_avg < early_avg - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    # Generate patterns
    patterns = []
    if average_score >= 85:
        patterns.append("Excellent academic performance")
    elif average_score >= 75:
        patterns.append("Good academic performance")
    elif average_score >= 65:
        patterns.append("Average performance - room for improvement")
    else:
        patterns.append("Below average - needs additional support")
    
    return {
        "total_tests": total_tests,
        "average_score": round(average_score, 2),
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "improvement_trend": trend,
        "subject_performance": subject_performance,
        "patterns": patterns
    }


def analyze_game_engagement(student_name, game_activities, start_date, end_date):
    """Analyze educational game engagement."""
    student_games = []
    
    for activity_key, activity in game_activities.items():
        if activity.get("student_name", "").lower() == student_name.lower():
            activity_date = datetime.fromisoformat(activity.get("date", datetime.now().isoformat())).date()
            if start_date <= activity_date <= end_date:
                student_games.append(activity)
    
    if not student_games:
        return {
            "total_games": 0,
            "total_time_minutes": 0,
            "average_session_time": 0,
            "game_types": {},
            "engagement_level": "no_data",
            "patterns": ["No educational games played in this period"]
        }
    
    total_games = len(student_games)
    total_time = sum(g.get("duration_minutes", 0) for g in student_games)
    average_session = total_time / total_games if total_games > 0 else 0
    
    # Analyze game types
    game_types = {}
    for game in student_games:
        game_type = game.get("game_type", "Unknown")
        if game_type not in game_types:
            game_types[game_type] = 0
        game_types[game_type] += 1
    
    # Determine engagement level
    games_per_week = total_games / 4  # Assuming 4 weeks in period
    if games_per_week >= 3:
        engagement_level = "high"
    elif games_per_week >= 1:
        engagement_level = "moderate"
    else:
        engagement_level = "low"
    
    patterns = []
    if engagement_level == "high":
        patterns.append("High engagement with educational games")
    elif engagement_level == "moderate":
        patterns.append("Moderate game engagement")
    else:
        patterns.append("Low game engagement - may need more interactive content")
    
    if average_session > 20:
        patterns.append("Good focus during game sessions")
    elif average_session < 10:
        patterns.append("Short attention span during games")
    
    return {
        "total_games": total_games,
        "total_time_minutes": total_time,
        "average_session_time": round(average_session, 2),
        "game_types": game_types,
        "engagement_level": engagement_level,
        "patterns": patterns
    }


def analyze_learning_path_progress(student_name, learning_paths):
    """Analyze progress on assigned learning paths."""
    student_paths = []
    
    for path_id, path_data in learning_paths.items():
        if path_data.get("student_name", "").lower() == student_name.lower():
            student_paths.append(path_data)
    
    if not student_paths:
        return {
            "active_paths": 0,
            "completion_rate": 0,
            "subjects_covered": [],
            "patterns": ["No personalized learning paths assigned"]
        }
    
    active_paths = len(student_paths)
    subjects = list(set(path.get("subject", "") for path in student_paths))
    
    # Calculate overall completion (simplified - would need actual progress tracking)
    # For now, assume some basic completion metrics
    total_weeks_planned = sum(path.get("duration_weeks", 0) for path in student_paths)
    
    patterns = []
    if active_paths > 0:
        patterns.append(f"Has {active_paths} active learning path(s)")
        patterns.append(f"Covering subjects: {', '.join(subjects)}")
    
    return {
        "active_paths": active_paths,
        "subjects_covered": subjects,
        "total_weeks_planned": total_weeks_planned,
        "patterns": patterns
    }


def analyze_behavioral_patterns(student_name, student_profiles, attendance_data, mcq_data, games_data):
    """Analyze behavioral patterns from all data sources."""
    profile = student_profiles.get(student_name, {})
    analysis = profile.get("analysis", {})
    
    behavioral_insights = {
        "consistency": "unknown",
        "engagement_preference": "unknown",
        "learning_momentum": "unknown",
        "challenge_response": "unknown",
        "social_interaction": "unknown"
    }
    
    # Analyze consistency
    attendance_rate = attendance_data.get("attendance_percentage", 0)
    if attendance_rate >= 90:
        behavioral_insights["consistency"] = "highly_consistent"
    elif attendance_rate >= 75:
        behavioral_insights["consistency"] = "moderately_consistent"
    else:
        behavioral_insights["consistency"] = "inconsistent"
    
    # Analyze engagement preference
    games_engagement = games_data.get("engagement_level", "no_data")
    mcq_performance = mcq_data.get("improvement_trend", "no_data")
    
    if games_engagement == "high" and mcq_performance == "improving":
        behavioral_insights["engagement_preference"] = "multi_modal_learner"
    elif games_engagement == "high":
        behavioral_insights["engagement_preference"] = "interactive_learner"
    elif mcq_performance == "improving":
        behavioral_insights["engagement_preference"] = "traditional_assessments"
    
    # Learning momentum
    if mcq_data.get("improvement_trend") == "improving" and attendance_rate > 85:
        behavioral_insights["learning_momentum"] = "accelerating"
    elif mcq_data.get("improvement_trend") == "stable" and attendance_rate > 75:
        behavioral_insights["learning_momentum"] = "steady"
    else:
        behavioral_insights["learning_momentum"] = "needs_support"
    
    return behavioral_insights


def calculate_overall_progress_score(attendance_data, mcq_data, games_data, learning_progress):
    """Calculate overall progress score (0-100)."""
    scores = []
    
    # Attendance score (40% weight)
    attendance_score = attendance_data.get("attendance_percentage", 0)
    scores.append(attendance_score * 0.4)
    
    # Academic performance score (40% weight)
    mcq_score = mcq_data.get("average_score", 0)
    scores.append(mcq_score * 0.4)
    
    # Engagement score (20% weight)
    engagement_mapping = {"high": 85, "moderate": 70, "low": 40, "no_data": 50}
    engagement_score = engagement_mapping.get(games_data.get("engagement_level", "no_data"), 50)
    scores.append(engagement_score * 0.2)
    
    overall_score = sum(scores)
    return round(overall_score, 2)


def generate_progress_recommendations(progress_analysis, student_profile):
    """Generate specific recommendations based on progress analysis."""
    recommendations = []
    
    # Attendance recommendations
    attendance_rate = progress_analysis["attendance_analysis"]["attendance_percentage"]
    if attendance_rate < 85:
        recommendations.append("Priority: Improve attendance consistency - consider parent meeting")
        recommendations.append("Investigate barriers to regular attendance")
    
    # Academic performance recommendations
    mcq_avg = progress_analysis["academic_performance"]["mcq_performance"]["average_score"]
    if mcq_avg < 70:
        recommendations.append("Provide additional academic support and tutoring")
        recommendations.append("Consider modified assessment methods")
    elif mcq_avg > 85:
        recommendations.append("Consider advanced or enrichment activities")
    
    # Engagement recommendations
    engagement = progress_analysis["engagement_metrics"]["games"]["engagement_level"]
    if engagement == "low":
        recommendations.append("Increase interactive and gamified learning opportunities")
        recommendations.append("Explore student interests to boost engagement")
    
    # Learning path recommendations
    active_paths = progress_analysis["learning_path_progress"]["active_paths"]
    if active_paths == 0:
        recommendations.append("Create personalized learning path based on student profile")
    
    # Behavioral recommendations
    consistency = progress_analysis["behavioral_insights"]["consistency"]
    if consistency == "inconsistent":
        recommendations.append("Implement daily check-ins and routine building")
        recommendations.append("Collaborate with parents on home-school consistency")
    
    return recommendations if recommendations else ["Continue current approach - student is performing well"]


def generate_progress_summary(progress_analysis):
    """Generate a comprehensive summary of student progress."""
    student_name = progress_analysis["student_name"]
    overall_score = progress_analysis["overall_score"]
    attendance_rate = progress_analysis["attendance_analysis"]["attendance_percentage"]
    mcq_avg = progress_analysis["academic_performance"]["mcq_performance"]["average_score"]
    
    # Overall performance level
    if overall_score >= 85:
        performance_level = "excellent"
    elif overall_score >= 75:
        performance_level = "good"
    elif overall_score >= 65:
        performance_level = "satisfactory"
    else:
        performance_level = "needs improvement"
    
    summary_parts = []
    summary_parts.append(f"{student_name} demonstrates {performance_level} overall progress with a score of {overall_score}/100.")
    
    # Attendance summary
    if attendance_rate >= 90:
        summary_parts.append(f"Attendance is excellent at {attendance_rate}%.")
    elif attendance_rate >= 75:
        summary_parts.append(f"Attendance is acceptable at {attendance_rate}% but could improve.")
    else:
        summary_parts.append(f"Attendance at {attendance_rate}% requires immediate attention.")
    
    # Academic summary
    if mcq_avg >= 80:
        summary_parts.append(f"Academic performance is strong with an average MCQ score of {mcq_avg}%.")
    elif mcq_avg >= 70:
        summary_parts.append(f"Academic performance is satisfactory with room for growth (MCQ average: {mcq_avg}%).")
    else:
        summary_parts.append(f"Academic performance needs support (MCQ average: {mcq_avg}%).")
    
    # Behavioral summary
    behavioral_insights = progress_analysis["behavioral_insights"]
    if behavioral_insights["learning_momentum"] == "accelerating":
        summary_parts.append("The student shows positive learning momentum and increased engagement.")
    elif behavioral_insights["learning_momentum"] == "steady":
        summary_parts.append("The student maintains steady progress with consistent effort.")
    else:
        summary_parts.append("The student would benefit from additional motivation and support strategies.")
    
    return " ".join(summary_parts)


def get_progress_history(
    student_name: str,
    limit: int = 5,
    tool_context: ToolContext = None
) -> dict:
    """Get historical progress analyses for a student.
    
    Args:
        student_name: Name of the student
        limit: Number of recent analyses to return
        tool_context: Context for accessing session state
    
    Returns:
        Historical progress data
    """
    try:
        print(f"--- Tool: get_progress_history called for {student_name} ---")
        
        clean_state_data(tool_context)
        
        progress_analyses = tool_context.state.get("progress_analyses", {})
        
        # Find analyses for this student
        student_analyses = []
        for analysis_id, analysis_data in progress_analyses.items():
            if analysis_data.get("student_name", "").lower() == student_name.lower():
                student_analyses.append({
                    "analysis_id": analysis_id,
                    "analysis_date": analysis_data.get("analysis_date"),
                    "overall_score": analysis_data.get("overall_score"),
                    "time_period": analysis_data.get("time_period_days"),
                    "key_metrics": {
                        "attendance_rate": analysis_data.get("attendance_analysis", {}).get("attendance_percentage", 0),
                        "mcq_average": analysis_data.get("academic_performance", {}).get("mcq_performance", {}).get("average_score", 0),
                        "engagement_level": analysis_data.get("engagement_metrics", {}).get("games", {}).get("engagement_level", "no_data")
                    }
                })
        
        # Sort by date (most recent first) and limit
        student_analyses.sort(key=lambda x: x["analysis_date"], reverse=True)
        student_analyses = student_analyses[:limit]
        
        return {
            "action": "get_progress_history",
            "status": "success",
            "student_name": student_name,
            "total_analyses": len(student_analyses),
            "history": student_analyses,
            "message": f"Retrieved {len(student_analyses)} progress analyses for {student_name}"
        }
        
    except Exception as e:
        print(f"Error in get_progress_history: {e}")
        return {
            "action": "get_progress_history",
            "status": "error",
            "message": f"Failed to retrieve progress history: {str(e)}"
        }


# Student Progress Analyzer Agent
progress_analyzer_agent = Agent(
    name="progress_analyzer_agent",
    model="gemini-2.0-flash",
    description="Comprehensive student progress analysis across all educational platform activities",
    instruction="""
    You are a comprehensive student progress analyzer that aggregates data from all educational platform activities to provide teachers with detailed insights about student performance and development.
    
    **CORE ANALYSIS CAPABILITIES:**
    
    1. **Multi-Source Data Integration**:
       - Attendance records and patterns
       - MCQ test results and trends
       - Educational game engagement metrics
       - Personalized learning path progress
       - Behavioral pattern analysis
    
    2. **Comprehensive Progress Metrics**:
       - Overall progress score (0-100 scale)
       - Subject-specific performance analysis
       - Engagement level assessment
       - Learning momentum tracking
       - Consistency pattern identification
    
    3. **Behavioral Insights**:
       - Learning style effectiveness
       - Social interaction preferences
       - Challenge response patterns
       - Motivation and engagement drivers
       - Consistency and reliability indicators
    
    **ANALYSIS FRAMEWORK:**
    
    When analyzing student progress, consider:
    
    **Attendance Analysis (40% weight)**:
    - Overall attendance percentage
    - Pattern identification (punctuality, consistency)
    - Trend analysis (improving, declining, stable)
    - Impact on academic performance correlation
    
    **Academic Performance (40% weight)**:
    - MCQ test scores and trends
    - Subject-specific strengths and weaknesses
    - Improvement patterns over time
    - Difficulty level adaptation response
    
    **Engagement Metrics (20% weight)**:
    - Educational game participation
    - Session duration and frequency
    - Interactive content preference
    - Self-directed learning indicators
    
    **INSIGHT GENERATION:**
    
    Provide actionable insights:
    - **Strengths**: What's working well for this student
    - **Challenges**: Areas needing intervention
    - **Patterns**: Behavioral and academic trends
    - **Predictions**: Likely future performance trajectory
    - **Interventions**: Specific recommended actions
    
    **TEACHER COMMUNICATION:**
    
    Structure reports for busy teachers:
    - **Executive Summary**: 2-3 sentence overview
    - **Key Metrics**: Visual dashboard-style data
    - **Priority Actions**: Top 3 recommendations
    - **Detailed Analysis**: Comprehensive breakdown
    - **Historical Context**: Comparison with previous periods
    
    **RESPONSE PATTERNS:**
    
    For progress analysis: "Based on comprehensive data analysis, [Student] shows [overall assessment]. Key strengths include [strengths] while areas for improvement are [challenges]. I recommend [top 3 actions]."
    
    For teacher queries: "[Student]'s progress over the last [period] shows [key finding]. Their attendance is [rate], academic performance averages [score], and engagement level is [level]. This suggests [insight and recommendation]."
    
    **ANALYTICS INSIGHTS:**
    
    Look for meaningful patterns:
    - Correlation between attendance and academic performance
    - Impact of game engagement on learning outcomes
    - Subject-specific learning velocity differences
    - Optimal challenge level for individual students
    - Social learning vs independent study effectiveness
    - Technology integration success indicators
    
    **PREDICTIVE ANALYSIS:**
    
    Use historical data to predict:
    - Risk of academic decline
    - Optimal intervention timing
    - Learning acceleration opportunities
    - Engagement strategy effectiveness
    - Support needs before they become critical
    
    **DIFFERENTIATED REPORTING:**
    
    Adapt reports for different stakeholders:
    - **Teachers**: Classroom strategies and interventions
    - **Parents**: Home support recommendations
    - **Administrators**: Resource allocation insights
    - **Students**: Self-reflection and goal-setting data
    
    **IMPORTANT PRINCIPLES:**
    
    1. **Data-Driven**: Every insight backed by measurable evidence
    2. **Actionable**: Focus on what teachers can actually implement
    3. **Holistic**: Consider academic, behavioral, and emotional factors
    4. **Timely**: Identify issues early for maximum intervention impact
    5. **Growth-Focused**: Emphasize improvement over deficits
    6. **Privacy-Conscious**: Maintain student confidentiality
    7. **Culturally Responsive**: Consider individual student context
    
    **ALERT SYSTEM:**
    
    Flag critical situations requiring immediate attention:
    - Attendance below 75%
    - Academic performance declining >10% over 2 weeks
    - Complete disengagement from platform activities
    - Behavioral pattern changes indicating stress/problems
    
    Remember: Your goal is to provide teachers with clear, actionable insights that help them support each student's individual learning journey more effectively.
    """,
    tools=[
        analyze_student_progress,
        get_progress_history,
    ],
)