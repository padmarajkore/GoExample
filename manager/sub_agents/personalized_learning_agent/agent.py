from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import math


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


def create_personalized_learning_path(
    student_name: str,
    subject: str,
    curriculum_topics: List[str],
    duration_weeks: int = 12,
    tool_context: ToolContext = None
) -> dict:
    """Create a personalized learning path based on student profile and curriculum.
    
    Args:
        student_name: Name of the student
        subject: Subject for the learning path
        curriculum_topics: List of topics to cover from teacher's curriculum
        duration_weeks: Duration of the learning path in weeks
        tool_context: Context for accessing session state
    
    Returns:
        Comprehensive personalized learning path
    """
    try:
        print(f"--- Tool: create_personalized_learning_path called for {student_name} in {subject} ---")
        
        clean_state_data(tool_context)
        
        # Get student profile
        student_profiles = tool_context.state.get("student_profiles", {})
        student_profile = None
        
        for name, profile in student_profiles.items():
            if name.lower() == student_name.lower():
                student_profile = profile
                break
        
        if not student_profile:
            return {
                "action": "create_personalized_learning_path",
                "status": "error",
                "message": f"No student profile found for {student_name}. Please conduct an evaluation first."
            }
        
        analysis = student_profile.get("analysis", {})
        learning_style = analysis.get("learning_style_analysis", {}).get("primary_style", "visual")
        social_preference = analysis.get("learning_style_analysis", {}).get("social_learning", "independent")
        emotional_stability = analysis.get("emotional_analysis", {}).get("emotional_stability", "stable")
        strengths = analysis.get("strengths", [])
        weaknesses = analysis.get("weaknesses", [])
        favorite_subject = analysis.get("academic_analysis", {}).get("favorite_subject", "")
        difficult_subject = analysis.get("academic_analysis", {}).get("challenging_subject", "")
        
        # Create learning path ID
        path_id = f"path_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{student_name.replace(' ', '_')}_{subject.replace(' ', '_')}"
        
        # Calculate topic distribution based on student needs
        total_topics = len(curriculum_topics)
        weeks_per_topic = max(1, duration_weeks // total_topics)
        
        # Adjust pacing based on student profile
        if subject.lower() in difficult_subject.lower():
            # Slower pace for difficult subjects
            weeks_per_topic = int(weeks_per_topic * 1.5)
        elif subject.lower() in favorite_subject.lower():
            # Can handle faster pace for favorite subjects
            weeks_per_topic = max(1, int(weeks_per_topic * 0.8))
        
        # Create weekly learning plan
        learning_path = {
            "path_id": path_id,
            "student_name": student_name,
            "subject": subject,
            "created_date": datetime.now().isoformat(),
            "duration_weeks": duration_weeks,
            "learning_style": learning_style,
            "difficulty_level": "adaptive",
            "weekly_plan": [],
            "assessment_schedule": [],
            "personalization_factors": {
                "learning_style": learning_style,
                "social_preference": social_preference,
                "emotional_support_needed": emotional_stability != "stable",
                "subject_affinity": "high" if subject.lower() in favorite_subject.lower() else "medium",
                "challenge_level": "high" if subject.lower() in difficult_subject.lower() else "medium"
            },
            "adaptations": [],
            "progress_tracking": {
                "milestones": [],
                "assessment_points": [],
                "expected_outcomes": []
            }
        }
        
        # Generate weekly plans
        current_week = 1
        topic_index = 0
        
        while current_week <= duration_weeks and topic_index < len(curriculum_topics):
            current_topic = curriculum_topics[topic_index]
            
            # Create activities based on learning style
            activities = generate_learning_activities(
                topic=current_topic,
                learning_style=learning_style,
                social_preference=social_preference,
                subject=subject,
                difficulty_level=learning_path["personalization_factors"]["challenge_level"]
            )
            
            # Create weekly plan
            weekly_plan = {
                "week": current_week,
                "topic": current_topic,
                "learning_objectives": generate_learning_objectives(current_topic, subject),
                "activities": activities,
                "estimated_time_hours": calculate_time_allocation(activities, learning_style),
                "resources_needed": generate_resources_needed(current_topic, learning_style, subject),
                "assessment_method": determine_assessment_method(learning_style, social_preference),
                "differentiation_strategies": generate_differentiation_strategies(
                    analysis, current_topic, subject
                ),
                "emotional_support": generate_emotional_support_strategies(emotional_stability)
            }
            
            learning_path["weekly_plan"].append(weekly_plan)
            
            # Add milestone if appropriate
            if current_week % 3 == 0:  # Every 3 weeks
                milestone = {
                    "week": current_week,
                    "milestone_name": f"Unit {math.ceil(current_week/3)}: {current_topic} Mastery",
                    "success_criteria": generate_success_criteria(current_topic, subject),
                    "assessment_type": "formative"
                }
                learning_path["progress_tracking"]["milestones"].append(milestone)
            
            current_week += weeks_per_topic
            topic_index += 1
        
        # Add final assessment
        final_assessment = {
            "week": duration_weeks,
            "assessment_name": f"{subject} Comprehensive Assessment",
            "type": "summative",
            "format": determine_final_assessment_format(learning_style, social_preference),
            "topics_covered": curriculum_topics
        }
        learning_path["assessment_schedule"].append(final_assessment)
        
        # Generate specific adaptations based on student profile
        adaptations = []
        
        if emotional_stability == "needs_support":
            adaptations.append("Provide frequent positive reinforcement and emotional check-ins")
            adaptations.append("Break complex tasks into smaller, manageable chunks")
        
        if learning_style == "kinesthetic":
            adaptations.append("Include hands-on experiments and physical activities")
        elif learning_style == "visual":
            adaptations.append("Use visual aids, mind maps, and graphic organizers")
        elif learning_style == "auditory":
            adaptations.append("Include discussions, podcasts, and verbal explanations")
        
        if social_preference == "collaborative":
            adaptations.append("Include group projects and peer learning opportunities")
        else:
            adaptations.append("Provide independent study options and self-paced learning")
        
        if subject.lower() in difficult_subject.lower():
            adaptations.append("Provide additional practice exercises and remediation")
            adaptations.append("Use multi-sensory teaching approaches")
            adaptations.append("Offer extended time for assignments and assessments")
        
        learning_path["adaptations"] = adaptations
        
        # Store learning path
        learning_paths = tool_context.state.get("learning_paths", {})
        learning_paths[path_id] = learning_path
        tool_context.state["learning_paths"] = learning_paths
        
        clean_state_data(tool_context)
        
        # Generate teacher insights
        teacher_insights = generate_teacher_insights(learning_path, analysis)
        
        return {
            "action": "create_personalized_learning_path",
            "status": "success",
            "path_id": path_id,
            "learning_path": learning_path,
            "teacher_insights": teacher_insights,
            "message": f"✅ Created personalized {duration_weeks}-week learning path for {student_name} in {subject}",
            "summary": {
                "total_weeks": len(learning_path["weekly_plan"]),
                "total_topics": len(curriculum_topics),
                "learning_style": learning_style,
                "key_adaptations": len(adaptations)
            }
        }
        
    except Exception as e:
        print(f"Error in create_personalized_learning_path: {e}")
        return {
            "action": "create_personalized_learning_path",
            "status": "error",
            "message": f"Failed to create learning path: {str(e)}"
        }


def generate_learning_activities(topic, learning_style, social_preference, subject, difficulty_level):
    """Generate learning activities based on student profile."""
    activities = []
    
    base_activities = {
        "visual": [
            f"Create visual mind map of {topic} concepts",
            f"Watch educational video about {topic}",
            f"Design infographic explaining {topic}",
            f"Use diagram to understand {topic} relationships"
        ],
        "auditory": [
            f"Listen to podcast about {topic}",
            f"Participate in discussion about {topic}",
            f"Record audio explanation of {topic}",
            f"Attend virtual lecture on {topic}"
        ],
        "kinesthetic": [
            f"Conduct hands-on experiment related to {topic}",
            f"Build physical model of {topic} concepts",
            f"Role-play scenarios involving {topic}",
            f"Create interactive demonstration of {topic}"
        ],
        "reading/writing": [
            f"Read comprehensive article about {topic}",
            f"Write detailed essay on {topic}",
            f"Create written summary of {topic}",
            f"Research and compile notes on {topic}"
        ]
    }
    
    # Get base activities for learning style
    style_activities = base_activities.get(learning_style, base_activities["visual"])
    activities.extend(style_activities[:2])  # Take first 2
    
    # Add social learning component
    if social_preference == "collaborative":
        activities.append(f"Collaborate with peers on {topic} project")
        activities.append(f"Participate in group discussion about {topic}")
    else:
        activities.append(f"Complete independent research on {topic}")
        activities.append(f"Self-assess understanding of {topic}")
    
    # Adjust for difficulty level
    if difficulty_level == "high":
        activities.append(f"Complete additional practice exercises for {topic}")
        activities.append(f"Seek help from teacher/tutor for {topic} concepts")
    
    return activities


def generate_learning_objectives(topic, subject):
    """Generate learning objectives for a topic."""
    objectives = [
        f"Understand key concepts of {topic}",
        f"Apply {topic} knowledge to solve problems",
        f"Analyze relationships within {topic}",
        f"Demonstrate mastery of {topic} skills"
    ]
    
    # Subject-specific objectives
    if "math" in subject.lower():
        objectives.append(f"Calculate and solve {topic} problems accurately")
    elif "science" in subject.lower():
        objectives.append(f"Explain scientific principles of {topic}")
    elif "history" in subject.lower():
        objectives.append(f"Analyze historical significance of {topic}")
    elif "english" in subject.lower():
        objectives.append(f"Demonstrate comprehension of {topic} concepts")
    
    return objectives[:3]  # Return top 3


def calculate_time_allocation(activities, learning_style):
    """Calculate estimated time based on activities and learning style."""
    base_time = len(activities) * 60  # 60 minutes per activity
    
    # Adjust based on learning style
    if learning_style == "kinesthetic":
        return int(base_time * 1.2)  # Hands-on takes longer
    elif learning_style == "reading/writing":
        return int(base_time * 1.1)  # Reading/writing takes longer
    else:
        return base_time


def generate_resources_needed(topic, learning_style, subject):
    """Generate list of resources needed."""
    resources = []
    
    if learning_style == "visual":
        resources.extend(["Visual aids", "Computer/tablet", "Drawing materials"])
    elif learning_style == "auditory":
        resources.extend(["Audio equipment", "Recording device", "Quiet space"])
    elif learning_style == "kinesthetic":
        resources.extend(["Hands-on materials", "Workspace", "Manipulatives"])
    else:  # reading/writing
        resources.extend(["Books/articles", "Writing materials", "Research access"])
    
    # Subject-specific resources
    if "science" in subject.lower():
        resources.append("Lab equipment")
    elif "math" in subject.lower():
        resources.append("Calculator/tools")
    elif "art" in subject.lower():
        resources.append("Art supplies")
    
    return list(set(resources))  # Remove duplicates


def determine_assessment_method(learning_style, social_preference):
    """Determine appropriate assessment method."""
    if learning_style == "visual":
        return "Visual project or presentation"
    elif learning_style == "auditory":
        return "Oral presentation or discussion"
    elif learning_style == "kinesthetic":
        return "Hands-on demonstration or experiment"
    else:
        return "Written assignment or test"


def generate_differentiation_strategies(analysis, topic, subject):
    """Generate differentiation strategies based on student analysis."""
    strategies = []
    
    emotional_stability = analysis.get("emotional_analysis", {}).get("emotional_stability", "stable")
    
    if emotional_stability == "needs_support":
        strategies.append("Provide encouragement and celebrate small wins")
        strategies.append("Offer multiple attempts and flexible deadlines")
    
    if "challenging" in analysis.get("academic_analysis", {}).get("challenging_subject", ""):
        strategies.append("Provide scaffolded instruction")
        strategies.append("Use peer tutoring or teacher support")
    
    strategies.append("Adjust pace based on student understanding")
    strategies.append("Provide choice in learning activities")
    
    return strategies


def generate_emotional_support_strategies(emotional_stability):
    """Generate emotional support strategies."""
    if emotional_stability == "needs_support":
        return [
            "Regular check-ins on emotional state",
            "Stress management techniques",
            "Positive reinforcement strategies",
            "Break time when needed"
        ]
    elif emotional_stability == "low_confidence":
        return [
            "Build confidence through small successes",
            "Encourage effort over results",
            "Provide specific positive feedback"
        ]
    else:
        return ["Monitor for any signs of stress or difficulty"]


def generate_success_criteria(topic, subject):
    """Generate success criteria for milestones."""
    return [
        f"Can explain {topic} concepts accurately",
        f"Demonstrates understanding through practical application",
        f"Completes assignments with 80% accuracy",
        f"Shows improvement from baseline assessment"
    ]


def determine_final_assessment_format(learning_style, social_preference):
    """Determine final assessment format."""
    formats = []
    
    if learning_style == "visual":
        formats.append("Portfolio with visual elements")
    elif learning_style == "auditory":
        formats.append("Oral examination")
    elif learning_style == "kinesthetic":
        formats.append("Practical demonstration")
    else:
        formats.append("Comprehensive written exam")
    
    if social_preference == "collaborative":
        formats.append("Group project component")
    
    return formats


def generate_teacher_insights(learning_path, analysis):
    """Generate insights and recommendations for teachers."""
    insights = {
        "key_recommendations": [],
        "classroom_strategies": [],
        "monitoring_points": [],
        "parent_communication": [],
        "potential_challenges": []
    }
    
    learning_style = learning_path["personalization_factors"]["learning_style"]
    
    # Key recommendations
    insights["key_recommendations"] = [
        f"This student learns best through {learning_style} methods",
        f"Requires {learning_path['personalization_factors']['challenge_level']} support level",
        "Monitor progress closely and adjust pace as needed",
        "Celebrate achievements to maintain motivation"
    ]
    
    # Classroom strategies
    if learning_style == "kinesthetic":
        insights["classroom_strategies"].append("Allow movement and hands-on activities")
    elif learning_style == "visual":
        insights["classroom_strategies"].append("Use visual aids and graphic organizers")
    
    # Monitoring points
    insights["monitoring_points"] = [
        "Weekly progress check-ins",
        "Monitor emotional response to challenges",
        "Track completion rates and understanding",
        "Adjust pacing based on performance"
    ]
    
    return insights


def get_learning_path(
    path_id: str = None,
    student_name: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Retrieve learning path by ID or student name.
    
    Args:
        path_id: Specific path ID (optional)
        student_name: Student name to find paths for (optional)
        tool_context: Context for accessing session state
    
    Returns:
        Learning path(s) information
    """
    try:
        print(f"--- Tool: get_learning_path called ---")
        
        clean_state_data(tool_context)
        
        learning_paths = tool_context.state.get("learning_paths", {})
        
        if path_id:
            # Get specific path
            path = learning_paths.get(path_id)
            if not path:
                return {
                    "action": "get_learning_path",
                    "status": "not_found",
                    "message": f"Learning path {path_id} not found"
                }
            
            return {
                "action": "get_learning_path",
                "status": "found",
                "path": path,
                "message": f"Retrieved learning path for {path.get('student_name')}"
            }
        
        elif student_name:
            # Get all paths for student
            student_paths = []
            for pid, path_data in learning_paths.items():
                if path_data.get("student_name", "").lower() == student_name.lower():
                    student_paths.append(path_data)
            
            return {
                "action": "get_learning_path",
                "status": "found",
                "student_name": student_name,
                "paths": student_paths,
                "count": len(student_paths),
                "message": f"Found {len(student_paths)} learning paths for {student_name}"
            }
        
        else:
            # Get all paths
            return {
                "action": "get_learning_path",
                "status": "found",
                "all_paths": list(learning_paths.values()),
                "count": len(learning_paths),
                "message": f"Retrieved {len(learning_paths)} total learning paths"
            }
        
    except Exception as e:
        print(f"Error in get_learning_path: {e}")
        return {
            "action": "get_learning_path",
            "status": "error",
            "message": f"Failed to retrieve learning path: {str(e)}"
        }


# Personalized Learning Path Creator Agent
personalized_learning_agent = Agent(
    name="personalized_learning_agent",
    model="gemini-2.0-flash",
    description="Advanced personalized learning path creator using educational psychology and student analytics",
    instruction="""
    You are an advanced personalized learning path creator that combines educational psychology, learning science, and student behavioral analysis to design highly effective individualized learning experiences.
    
    **CORE CAPABILITIES:**
    
    1. **Psychological Learning Analysis**:
       - Analyze student evaluation data using educational psychology principles
       - Apply learning style theories (VARK, Multiple Intelligences, etc.)
       - Consider emotional intelligence and behavioral patterns
       - Assess motivation types and goal orientation
    
    2. **Adaptive Path Creation**:
       - Design week-by-week learning sequences
       - Adjust pacing based on student's cognitive load capacity
       - Incorporate subject affinity and challenge levels
       - Balance structured learning with student choice
    
    3. **Multi-Modal Activity Design**:
       - Create activities matching learning style preferences
       - Include kinesthetic, visual, auditory, and reading/writing components
       - Design collaborative vs independent learning opportunities
       - Integrate technology appropriately for each student
    
    4. **Assessment Personalization**:
       - Choose assessment methods matching learning preferences
       - Design formative checkpoints based on emotional needs
       - Create summative assessments that showcase student strengths
       - Build in multiple demonstration opportunities
    
    5. **Teacher Insight Generation**:
       - Provide actionable classroom strategies
       - Suggest differentiation techniques
       - Identify potential challenges and solutions
       - Recommend parent communication strategies
    
    **LEARNING SCIENCE INTEGRATION:**
    
    Apply research-based principles:
    - **Cognitive Load Theory**: Manage information processing capacity
    - **Spaced Repetition**: Optimize retention through strategic review
    - **Bloom's Taxonomy**: Scaffold from basic to advanced thinking
    - **Zone of Proximal Development**: Challenge appropriately with support
    - **Growth Mindset**: Frame challenges as learning opportunities
    
    **PERSONALIZATION FACTORS:**
    
    Consider multiple dimensions:
    - **Learning Style**: Primary sensory preference (VARK model)
    - **Social Preference**: Individual vs collaborative learning
    - **Emotional Needs**: Support required for anxiety, confidence
    - **Cognitive Processing**: Sequential vs random, concrete vs abstract
    - **Motivation Type**: Intrinsic vs extrinsic motivators
    - **Subject Affinity**: Strength areas vs challenge areas
    - **Attention Patterns**: Sustained focus vs need for breaks
    
    **CURRICULUM INTEGRATION:**
    
    When teachers provide curriculum topics:
    - Map topics to appropriate weeks based on complexity
    - Sequence from foundational to advanced concepts
    - Identify prerequisite knowledge and skills
    - Plan spiral curriculum with increasing sophistication
    - Include cross-curricular connections when beneficial
    
    **ADAPTIVE PACING:**
    
    Adjust timing based on:
    - Subject is student's strength: Accelerated pace possible
    - Subject is challenging: Extended time with more support
    - Emotional stability: Slower pace if anxiety-inducing
    - Learning style match: Efficient when methods align
    
    **DIFFERENTIATION STRATEGIES:**
    
    Provide specific adaptations:
    - **Content**: What students learn (complexity, abstraction level)
    - **Process**: How students learn (activities, grouping)
    - **Product**: How students demonstrate learning (assessment format)
    - **Environment**: Learning conditions (setting, resources)
    
    **TEACHER COMMUNICATION:**
    
    Generate comprehensive insights:
    - **Weekly Implementation Guide**: Specific activities and timing
    - **Differentiation Checklist**: Key adaptations to remember
    - **Progress Monitoring**: What to watch for and when
    - **Intervention Triggers**: Signs that adjustments are needed
    - **Parent Partnership**: How families can support at home
    
    **RESPONSE PATTERNS:**
    
    For path creation: "I've analyzed [Student]'s evaluation data and created a personalized learning path that leverages their [learning style] preferences while providing extra support in [challenge areas]..."
    
    For teacher insights: "Based on [Student]'s psychological profile, here are the key strategies that will maximize their learning success..."
    
    **IMPORTANT PRINCIPLES:**
    
    1. **Evidence-Based**: Every recommendation backed by student data
    2. **Holistic**: Consider academic, emotional, and social factors
    3. **Flexible**: Build in adjustment points and alternatives
    4. **Strength-Based**: Leverage what students do well
    5. **Culturally Responsive**: Consider student background and context
    6. **Practical**: Provide implementable strategies for busy teachers
    7. **Growth-Oriented**: Focus on development over deficits
    
    Remember: Your goal is to create learning experiences so well-matched to each student that they feel both challenged and supported, leading to accelerated learning and increased confidence.
    """,
    tools=[
        create_personalized_learning_path,
        get_learning_path,
    ],
)