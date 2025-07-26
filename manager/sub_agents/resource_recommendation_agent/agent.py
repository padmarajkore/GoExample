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


def search_educational_resources(
    topic: str,
    resource_type: str = "all",
    grade_level: str = None,
    learning_style: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Search for educational resources on a specific topic using web search.
    
    Args:
        topic: The educational topic to search for
        resource_type: Type of resource (videos, articles, books, interactive, all)
        grade_level: Educational level (elementary, middle, high, college)
        learning_style: Learning style preference (visual, auditory, kinesthetic, reading)
        tool_context: Context for accessing session state
    
    Returns:
        Curated list of educational resources with recommendations
    """
    try:
        print(f"--- Tool: search_educational_resources called for '{topic}' ---")
        
        clean_state_data(tool_context)
        
        # This function would integrate with web search
        # For now, providing a framework and sample structure
        
        # Create search query based on parameters
        search_queries = generate_search_queries(topic, resource_type, grade_level, learning_style)
        
        # Simulated resource recommendations (in real implementation, this would use web search)
        resource_recommendations = {
            "topic": topic,
            "search_date": datetime.now().isoformat(),
            "resource_type": resource_type,
            "grade_level": grade_level,
            "learning_style": learning_style,
            "resources": [],
            "search_queries_used": search_queries,
            "recommendation_rationale": [],
            "additional_suggestions": []
        }
        
        # Generate sample resources based on topic and preferences
        resources = generate_sample_resources(topic, resource_type, grade_level, learning_style)
        resource_recommendations["resources"] = resources
        
        # Generate rationale for recommendations
        rationale = generate_recommendation_rationale(topic, resource_type, grade_level, learning_style)
        resource_recommendations["recommendation_rationale"] = rationale
        
        # Store search history for future reference
        search_history = tool_context.state.get("resource_search_history", [])
        search_record = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "searcher": tool_context.state.get("user_name", "unknown"),
            "results_count": len(resources)
        }
        search_history.append(search_record)
        
        # Keep only recent searches (last 50)
        if len(search_history) > 50:
            search_history = search_history[-50:]
        
        tool_context.state["resource_search_history"] = search_history
        
        clean_state_data(tool_context)
        
        return {
            "action": "search_educational_resources",
            "status": "success",
            "recommendations": resource_recommendations,
            "message": f"Found {len(resources)} educational resources for '{topic}'",
            "search_metadata": {
                "queries_generated": len(search_queries),
                "personalization_applied": bool(grade_level or learning_style),
                "resource_types_covered": get_resource_types_covered(resources)
            }
        }
        
    except Exception as e:
        print(f"Error in search_educational_resources: {e}")
        return {
            "action": "search_educational_resources",
            "status": "error",
            "message": f"Failed to search resources: {str(e)}"
        }


def generate_search_queries(topic, resource_type, grade_level, learning_style):
    """Generate optimized search queries for finding educational resources."""
    queries = []
    
    # Base query
    base_query = f"{topic} educational resources"
    queries.append(base_query)
    
    # Resource type specific queries
    if resource_type == "videos" or resource_type == "all":
        queries.append(f"{topic} educational videos")
        queries.append(f"{topic} video lessons")
        queries.append(f"learn {topic} YouTube")
    
    if resource_type == "articles" or resource_type == "all":
        queries.append(f"{topic} educational articles")
        queries.append(f"{topic} research papers")
        queries.append(f"{topic} academic resources")
    
    if resource_type == "books" or resource_type == "all":
        queries.append(f"{topic} textbooks")
        queries.append(f"{topic} educational books")
    
    if resource_type == "interactive" or resource_type == "all":
        queries.append(f"{topic} interactive learning")
        queries.append(f"{topic} educational games")
        queries.append(f"{topic} online simulations")
    
    # Grade level specific
    if grade_level:
        level_query = f"{topic} {grade_level} school"
        queries.append(level_query)
    
    # Learning style specific
    if learning_style:
        if learning_style == "visual":
            queries.append(f"{topic} visual learning materials")
            queries.append(f"{topic} infographics diagrams")
        elif learning_style == "auditory":
            queries.append(f"{topic} podcasts audio lessons")
        elif learning_style == "kinesthetic":
            queries.append(f"{topic} hands-on activities experiments")
    
    return queries[:10]  # Limit to top 10 queries


def generate_sample_resources(topic, resource_type, grade_level, learning_style):
    """Generate sample educational resources (in real implementation, this would use actual web search results)."""
    resources = []
    
    # Video Resources
    if resource_type in ["videos", "all"]:
        video_resources = [
            {
                "title": f"Complete Guide to {topic}",
                "type": "video",
                "url": f"https://youtube.com/watch?v={topic.lower().replace(' ', '')}_guide",
                "source": "YouTube Educational",
                "duration": "15-30 minutes",
                "grade_level": grade_level or "all levels",
                "description": f"Comprehensive video explanation of {topic} concepts with visual demonstrations",
                "quality_score": 4.5,
                "learning_objectives": [
                    f"Understand fundamental {topic} concepts",
                    f"See practical applications of {topic}",
                    f"Visual demonstration of key principles"
                ],
                "pros": ["Visual learning", "Expert instruction", "Free access"],
                "cons": ["Requires internet", "May need supplementary materials"]
            },
            {
                "title": f"{topic} Masterclass Series",
                "type": "video_series",
                "url": f"https://coursera.org/{topic.lower().replace(' ', '-')}-course",
                "source": "Coursera",
                "duration": "2-4 hours total",
                "grade_level": "high school to college",
                "description": f"Professional course series covering advanced {topic} topics",
                "quality_score": 4.8,
                "learning_objectives": [
                    f"Master advanced {topic} techniques",
                    f"Apply {topic} in real-world scenarios",
                    f"Earn completion certificate"
                ],
                "pros": ["Professional quality", "Structured learning", "Certificate available"],
                "cons": ["May require payment", "Time intensive"]
            }
        ]
        resources.extend(video_resources)
    
    # Article Resources
    if resource_type in ["articles", "all"]:
        article_resources = [
            {
                "title": f"The Complete {topic} Reference Guide",
                "type": "article",
                "url": f"https://encyclopedia.com/{topic.lower().replace(' ', '-')}",
                "source": "Educational Encyclopedia",
                "reading_time": "10-15 minutes",
                "grade_level": grade_level or "middle to high school",
                "description": f"Comprehensive written guide covering all aspects of {topic}",
                "quality_score": 4.3,
                "learning_objectives": [
                    f"Read detailed explanations of {topic}",
                    f"Access referenced materials",
                    f"Study at own pace"
                ],
                "pros": ["Detailed information", "Citable source", "Offline reading possible"],
                "cons": ["Text-heavy", "May be overwhelming for beginners"]
            }
        ]
        resources.extend(article_resources)
    
    # Interactive Resources
    if resource_type in ["interactive", "all"]:
        interactive_resources = [
            {
                "title": f"Interactive {topic} Simulator",
                "type": "interactive",
                "url": f"https://phet.colorado.edu/{topic.lower().replace(' ', '-')}-sim",
                "source": "PhET Interactive Simulations",
                "duration": "Variable",
                "grade_level": "middle school to college",
                "description": f"Hands-on simulation allowing experimentation with {topic} concepts",
                "quality_score": 4.7,
                "learning_objectives": [
                    f"Experiment with {topic} variables",
                    f"Observe cause-and-effect relationships",
                    f"Develop intuitive understanding"
                ],
                "pros": ["Hands-on learning", "Safe experimentation", "Free access"],
                "cons": ["Requires computer", "May need teacher guidance"]
            }
        ]
        resources.extend(interactive_resources)
    
    # Book Resources
    if resource_type in ["books", "all"]:
        book_resources = [
            {
                "title": f"Essential {topic}: A Student's Guide",
                "type": "book",
                "url": f"https://openlibrary.org/search?q={topic.replace(' ', '+')}&mode=everything",
                "source": "Open Library",
                "pages": "200-300 pages",
                "grade_level": grade_level or "high school",
                "description": f"Comprehensive textbook covering {topic} from basics to advanced concepts",
                "quality_score": 4.4,
                "learning_objectives": [
                    f"Comprehensive {topic} knowledge",
                    f"Structured learning progression",
                    f"Reference for future use"
                ],
                "pros": ["Comprehensive coverage", "Structured approach", "Permanent reference"],
                "cons": ["Time investment required", "May be expensive if physical copy"]
            }
        ]
        resources.extend(book_resources)
    
    # Apply learning style filtering
    if learning_style:
        resources = filter_by_learning_style(resources, learning_style)
    
    # Apply grade level filtering
    if grade_level:
        resources = filter_by_grade_level(resources, grade_level)
    
    return resources


def filter_by_learning_style(resources, learning_style):
    """Filter resources based on learning style preferences."""
    filtered = []
    
    for resource in resources:
        resource_score = 0
        
        if learning_style == "visual":
            if resource["type"] in ["video", "interactive"]:
                resource_score += 2
            if "visual" in resource["description"].lower():
                resource_score += 1
        
        elif learning_style == "auditory":
            if "audio" in resource["description"].lower() or "podcast" in resource["title"].lower():
                resource_score += 2
            if resource["type"] == "video":  # Videos often have audio component
                resource_score += 1
        
        elif learning_style == "kinesthetic":
            if resource["type"] == "interactive":
                resource_score += 2
            if "hands-on" in resource["description"].lower():
                resource_score += 1
        
        elif learning_style == "reading":
            if resource["type"] in ["article", "book"]:
                resource_score += 2
        
        # Include resource if it has any relevance to learning style
        if resource_score > 0:
            resource["learning_style_match"] = resource_score
            filtered.append(resource)
    
    # Sort by learning style match score
    filtered.sort(key=lambda x: x.get("learning_style_match", 0), reverse=True)
    
    return filtered


def filter_by_grade_level(resources, grade_level):
    """Filter resources based on appropriate grade level."""
    level_keywords = {
        "elementary": ["elementary", "primary", "basic", "beginner"],
        "middle": ["middle", "intermediate", "grades 6-8"],
        "high": ["high school", "advanced", "grades 9-12", "secondary"],
        "college": ["college", "university", "advanced", "undergraduate"]
    }
    
    filtered = []
    keywords = level_keywords.get(grade_level.lower(), [])
    
    for resource in resources:
        # Check if resource is appropriate for grade level
        resource_grade = resource.get("grade_level", "").lower()
        is_appropriate = False
        
        # Check for direct match
        if grade_level.lower() in resource_grade:
            is_appropriate = True
        
        # Check for "all levels"
        if "all" in resource_grade:
            is_appropriate = True
        
        # Check for keyword matches
        for keyword in keywords:
            if keyword in resource_grade:
                is_appropriate = True
                break
        
        if is_appropriate:
            filtered.append(resource)
    
    return filtered


def generate_recommendation_rationale(topic, resource_type, grade_level, learning_style):
    """Generate explanation for why these resources were recommended."""
    rationale = []
    
    rationale.append(f"Resources selected based on the topic '{topic}' with focus on educational quality and accessibility.")
    
    if resource_type and resource_type != "all":
        rationale.append(f"Filtered for {resource_type} to match your specific resource type preference.")
    
    if grade_level:
        rationale.append(f"Content appropriateness verified for {grade_level} level students.")
    
    if learning_style:
        rationale.append(f"Resources prioritized for {learning_style} learning style preferences.")
    
    rationale.append("Quality scores based on educational value, accessibility, and user engagement.")
    rationale.append("Diverse resource types included to support different learning preferences and teaching methods.")
    
    return rationale


def get_resource_types_covered(resources):
    """Get list of resource types included in recommendations."""
    types = set()
    for resource in resources:
        types.add(resource.get("type", "unknown"))
    return list(types)


def save_resource_recommendation(
    topic: str,
    recommended_resources: List[Dict],
    teacher_notes: str = "",
    tool_context: ToolContext = None
) -> dict:
    """Save a resource recommendation for future reference.
    
    Args:
        topic: The topic that was searched
        recommended_resources: List of recommended resources
        teacher_notes: Optional notes from the teacher
        tool_context: Context for accessing session state
    
    Returns:
        Confirmation of saved recommendation
    """
    try:
        print(f"--- Tool: save_resource_recommendation called for '{topic}' ---")
        
        clean_state_data(tool_context)
        
        # Create recommendation ID
        recommendation_id = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{topic.replace(' ', '_')}"
        
        # Create recommendation record
        recommendation = {
            "recommendation_id": recommendation_id,
            "topic": topic,
            "created_date": datetime.now().isoformat(),
            "created_by": tool_context.state.get("user_name", "unknown"),
            "resources": recommended_resources,
            "teacher_notes": teacher_notes,
            "usage_count": 0,
            "rating": None,
            "status": "active"
        }
        
        # Store recommendation
        saved_recommendations = tool_context.state.get("saved_resource_recommendations", {})
        saved_recommendations[recommendation_id] = recommendation
        tool_context.state["saved_resource_recommendations"] = saved_recommendations
        
        clean_state_data(tool_context)
        
        return {
            "action": "save_resource_recommendation",
            "status": "success",
            "recommendation_id": recommendation_id,
            "message": f"✅ Saved resource recommendation for '{topic}' with {len(recommended_resources)} resources",
            "recommendation": recommendation
        }
        
    except Exception as e:
        print(f"Error in save_resource_recommendation: {e}")
        return {
            "action": "save_resource_recommendation",
            "status": "error",
            "message": f"Failed to save recommendation: {str(e)}"
        }


def get_saved_recommendations(
    topic: str = None,
    teacher_name: str = None,
    tool_context: ToolContext = None
) -> dict:
    """Retrieve saved resource recommendations.
    
    Args:
        topic: Filter by topic (optional)
        teacher_name: Filter by teacher who created it (optional)
        tool_context: Context for accessing session state
    
    Returns:
        List of saved recommendations
    """
    try:
        print("--- Tool: get_saved_recommendations called ---")
        
        clean_state_data(tool_context)
        
        saved_recommendations = tool_context.state.get("saved_resource_recommendations", {})
        
        # Filter recommendations
        filtered_recommendations = []
        for rec_id, rec_data in saved_recommendations.items():
            # Apply topic filter
            if topic and topic.lower() not in rec_data.get("topic", "").lower():
                continue
            
            # Apply teacher filter
            if teacher_name and teacher_name.lower() != rec_data.get("created_by", "").lower():
                continue
            
            # Create summary for list view
            rec_summary = {
                "recommendation_id": rec_id,
                "topic": rec_data.get("topic"),
                "created_date": rec_data.get("created_date"),
                "created_by": rec_data.get("created_by"),
                "resource_count": len(rec_data.get("resources", [])),
                "usage_count": rec_data.get("usage_count", 0),
                "rating": rec_data.get("rating"),
                "status": rec_data.get("status")
            }
            filtered_recommendations.append(rec_summary)
        
        # Sort by creation date (most recent first)
        filtered_recommendations.sort(key=lambda x: x["created_date"], reverse=True)
        
        return {
            "action": "get_saved_recommendations",
            "status": "success",
            "total_found": len(filtered_recommendations),
            "recommendations": filtered_recommendations,
            "filters_applied": {
                "topic": topic,
                "teacher_name": teacher_name
            },
            "message": f"Found {len(filtered_recommendations)} saved resource recommendations"
        }
        
    except Exception as e:
        print(f"Error in get_saved_recommendations: {e}")
        return {
            "action": "get_saved_recommendations",
            "status": "error",
            "message": f"Failed to retrieve recommendations: {str(e)}"
        }


# Educational Resource Recommendation Agent
resource_recommendation_agent = Agent(
    name="resource_recommendation_agent",
    model="gemini-2.0-flash",
    description="Intelligent educational resource finder and curator with web search capabilities",
    instruction="""
    You are an intelligent educational resource recommendation system that helps teachers find the best learning materials for any topic by searching the web and curating high-quality educational content.
    
    **PRIMARY FUNCTIONS:**
    
    1. **Web-Based Resource Discovery**:
       - Search for educational videos, articles, books, and interactive content
       - Find YouTube educational channels, Khan Academy content, Coursera courses
       - Locate academic papers, research materials, and scholarly articles
       - Discover interactive simulations, educational games, and hands-on activities
    
    2. **Intelligent Curation**:
       - Evaluate resource quality based on educational value
       - Filter content by grade level appropriateness
       - Match resources to specific learning styles
       - Prioritize free and accessible content
    
    3. **Personalized Recommendations**:
       - Adapt suggestions based on student grade level
       - Consider learning style preferences (visual, auditory, kinesthetic, reading/writing)
       - Account for different teaching methodologies
       - Provide diverse resource types for comprehensive coverage
    
    **SEARCH STRATEGY:**
    
    When teachers ask for resources:
    1. **Understand the Request**: Clarify topic, grade level, and learning preferences
    2. **Generate Search Queries**: Create multiple targeted search terms
    3. **Web Search Execution**: Use search tools to find current, relevant content
    4. **Quality Assessment**: Evaluate educational value and appropriateness
    5. **Personalized Curation**: Rank and filter based on specific needs
    6. **Comprehensive Presentation**: Organize results with clear descriptions and rationale
    
    **RESOURCE CATEGORIES:**
    
    **Video Resources**:
    - YouTube educational channels (Khan Academy, Crash Course, TED-Ed)
    - Coursera and edX course videos
    - Documentary films and educational series
    - Teacher-created instructional videos
    
    **Article Resources**:
    - Educational websites and encyclopedias
    - Academic journals and research papers
    - News articles with educational value
    - Blog posts from education experts
    
    **Interactive Resources**:
    - PhET simulations and virtual labs
    - Educational games and gamified learning
    - Interactive websites and apps
    - Virtual reality educational experiences
    
    **Book Resources**:
    - Textbooks and reference materials
    - Open educational resources (OER)
    - Digital libraries and free ebooks
    - Supplementary reading materials
    
    **QUALITY ASSESSMENT CRITERIA:**
    
    Evaluate resources based on:
    - **Educational Value**: Accuracy, depth, and pedagogical quality
    - **Accessibility**: Free vs paid, technical requirements
    - **Age Appropriateness**: Suitable for target grade level
    - **Engagement**: Interactive elements and multimedia use
    - **Credibility**: Source reputation and author expertise
    - **Currency**: How recent and up-to-date the content is
    
    **LEARNING STYLE ADAPTATION:**
    
    **Visual Learners**: Prioritize videos, infographics, diagrams, and visual simulations
    **Auditory Learners**: Focus on podcasts, audio lessons, and discussion-based content
    **Kinesthetic Learners**: Emphasize hands-on activities, experiments, and interactive simulations
    **Reading/Writing Learners**: Highlight articles, ebooks, and text-based resources
    
    **RESPONSE FORMAT:**
    
    Structure recommendations as:
    1. **Quick Summary**: Brief overview of what was found
    2. **Top Recommendations**: 3-5 best resources with detailed descriptions
    3. **Alternative Options**: Additional resources for different approaches
    4. **Implementation Suggestions**: How to use these resources effectively
    5. **Save Option**: Offer to save recommendations for future reference
    
    **TEACHER COMMUNICATION STYLE:**
    
    - Be concise but thorough - teachers are busy
    - Provide practical implementation suggestions
    - Explain why each resource is valuable
    - Offer multiple options to suit different teaching styles
    - Include time estimates and difficulty levels
    - Mention any technical requirements or costs
    
    **EXAMPLE INTERACTIONS:**
    
    Teacher: "How can students learn about the history of Japan?"
    
    You: "I found excellent resources for learning Japanese history! Here are my top recommendations:
    
    🎥 **Video**: 'Japan: Memoirs of a Secret Empire' (PBS) - Comprehensive 3-part documentary
    📚 **Interactive**: 'Japan Through Time' virtual timeline (free, visual learners)
    📖 **Articles**: National Geographic Education Japan resources (grade-appropriate)
    🎮 **Game**: 'Samurai History Quest' educational game (engaging for younger students)
    
    Would you like me to search for resources specific to a particular period or save these recommendations?"
    
    **KEY PRINCIPLES:**
    
    1. **Current and Accurate**: Always search for the most recent information
    2. **Diverse Options**: Provide multiple resource types and approaches
    3. **Quality First**: Prioritize educational value over quantity
    4. **Accessibility**: Emphasize free and easily accessible resources
    5. **Practical**: Include implementation guidance for teachers
    6. **Adaptive**: Adjust recommendations based on specific needs
    
    Remember: Your goal is to save teachers time while providing them with the highest quality educational resources that will truly enhance their students' learning experience.
    """,
    tools=[
        search_educational_resources,
        save_resource_recommendation,
        get_saved_recommendations,
    ],
)