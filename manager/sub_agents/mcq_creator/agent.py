from google.adk.agents import Agent
import random
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class MCQQuestion:
    """Data class for MCQ questions"""
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"
    tags: List[str] = None

class MCQGenerator:
    """Enhanced MCQ generation with topic-specific templates and difficulty levels"""
    
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.question_templates = {
            "definition": "What is {concept}?",
            "application": "How would you apply {concept} in {context}?",
            "comparison": "What is the main difference between {concept1} and {concept2}?",
            "cause_effect": "What is the primary cause of {phenomenon}?",
            "process": "What is the first step in {process}?",
            "fact": "Which of the following is true about {topic}?"
        }
        
        # Topic-specific knowledge base (expandable)
        self.knowledge_base = {
            "python": {
                "concepts": ["variables", "functions", "classes", "loops", "dictionaries"],
                "contexts": ["data analysis", "web development", "automation"],
                "facts": ["Python is interpreted", "Python uses indentation", "Python is dynamically typed"]
            },
            "mathematics": {
                "concepts": ["algebra", "geometry", "calculus", "statistics"],
                "contexts": ["real-world problems", "engineering", "finance"],
                "facts": ["Pi is approximately 3.14159", "A triangle has 180 degrees"]
            },
            "history": {
                "concepts": ["democracy", "revolution", "empire", "civilization"],
                "contexts": ["ancient times", "modern era", "war", "peace"],
                "facts": ["World War II ended in 1945", "The Renaissance began in Italy"]
            }
        }

def create_mcqs(topic: str, num_questions: int = 3, difficulty: str = "medium") -> Dict:
    """
    Generate MCQ questions for a given topic with enhanced features.
    
    Args:
        topic: The educational topic for question generation
        num_questions: Number of questions to generate (default: 3)
        difficulty: Difficulty level - easy, medium, or hard (default: medium)
    
    Returns:
        Dictionary containing status, metadata, and generated questions
    """
    try:
        # Input validation
        if not topic or not isinstance(topic, str):
            return {
                "status": "error",
                "message": "Topic must be a non-empty string",
                "questions": []
            }
        
        if num_questions < 1 or num_questions > 10:
            num_questions = min(max(1, num_questions), 10)  # Clamp between 1-10
        
        if difficulty not in ["easy", "medium", "hard"]:
            difficulty = "medium"
        
        generator = MCQGenerator()
        topic_lower = topic.lower()
        
        # Generate questions
        questions = []
        for i in range(num_questions):
            question_data = generator._generate_single_question(topic, topic_lower, difficulty, i)
            questions.append(question_data)
        
        return {
            "status": "success",
            "metadata": {
                "topic": topic,
                "num_questions": len(questions),
                "difficulty": difficulty,
                "generated_at": "2024-current-timestamp"  # In real implementation, use datetime
            },
            "questions": questions,
            "instructions": "Select the best answer for each question. Explanations are provided for learning."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating questions: {str(e)}",
            "questions": []
        }

# Extended MCQGenerator class with enhanced methods
class MCQGenerator:
    """Enhanced MCQ generation with topic-specific templates and difficulty levels"""
    
    def __init__(self):
        self.difficulty_levels = ["easy", "medium", "hard"]
        self.question_templates = {
            "definition": "What is {concept}?",
            "application": "How would you apply {concept} in {context}?",
            "comparison": "What is the main difference between {concept1} and {concept2}?",
            "cause_effect": "What is the primary cause of {phenomenon}?",
            "process": "What is the first step in {process}?",
            "fact": "Which of the following is true about {topic}?"
        }
        
        # Expanded knowledge base
        self.knowledge_base = {
            "python": {
                "concepts": ["variables", "functions", "classes", "loops", "dictionaries", "modules"],
                "contexts": ["data analysis", "web development", "automation", "machine learning"],
                "facts": ["Python is interpreted", "Python uses indentation", "Python is dynamically typed"],
                "processes": ["debugging", "testing", "deployment"]
            },
            "mathematics": {
                "concepts": ["algebra", "geometry", "calculus", "statistics", "probability"],
                "contexts": ["real-world problems", "engineering", "finance", "research"],
                "facts": ["Pi is approximately 3.14159", "A triangle has 180 degrees"],
                "processes": ["problem solving", "proof writing", "calculation"]
            },
            "biology": {
                "concepts": ["cell", "DNA", "evolution", "photosynthesis", "metabolism"],
                "contexts": ["medicine", "ecology", "genetics", "research"],
                "facts": ["DNA contains genetic information", "Mitochondria produce energy"],
                "processes": ["cellular respiration", "protein synthesis", "cell division"]
            }
        }
    
    def _generate_single_question(self, topic: str, topic_lower: str, difficulty: str, question_num: int) -> Dict:
        """Generate a single MCQ question"""
        
        # Get topic-specific data or use generic approach
        topic_data = self.knowledge_base.get(topic_lower, {
            "concepts": [f"{topic} fundamentals", f"{topic} principles", f"{topic} applications"],
            "contexts": ["practical scenarios", "theoretical frameworks", "real-world applications"],
            "facts": [f"{topic} is an important subject", f"{topic} has various applications"],
            "processes": [f"{topic} methodology", f"{topic} implementation"]
        })
        
        # Select question type based on difficulty and variety
        question_types = list(self.question_templates.keys())
        question_type = question_types[question_num % len(question_types)]
        
        # Generate question based on type
        if question_type == "definition":
            concept = random.choice(topic_data["concepts"])
            question_text = f"What is {concept} in the context of {topic}?"
            correct_answer = f"A fundamental concept in {topic} related to {concept}"
            
        elif question_type == "application":
            concept = random.choice(topic_data["concepts"])
            context = random.choice(topic_data["contexts"])
            question_text = f"How would you apply {concept} in {context}?"
            correct_answer = f"By implementing {concept} principles in {context}"
            
        elif question_type == "fact":
            fact = random.choice(topic_data["facts"])
            question_text = f"Which statement is true about {topic}?"
            correct_answer = fact
            
        else:  # Default case
            question_text = f"What is a key principle of {topic}?"
            correct_answer = f"Understanding the core concepts of {topic}"
        
        # Generate distractors (incorrect options)
        distractors = self._generate_distractors(topic, correct_answer, difficulty)
        
        # Combine and shuffle options
        all_options = [correct_answer] + distractors
        random.shuffle(all_options)
        correct_index = all_options.index(correct_answer)
        option_labels = ["A", "B", "C", "D"]
        
        return {
            "id": f"q_{question_num + 1}",
            "question": question_text,
            "options": {
                option_labels[i]: option 
                for i, option in enumerate(all_options)
            },
            "correct_answer": option_labels[correct_index],
            "explanation": f"The correct answer is {correct_answer} because it directly relates to the core principles of {topic}.",
            "difficulty": difficulty,
            "topic": topic,
            "question_type": question_type
        }
    
    def _generate_distractors(self, topic: str, correct_answer: str, difficulty: str) -> List[str]:
        """Generate plausible but incorrect answer options"""
        
        base_distractors = [
            f"An unrelated concept in {topic}",
            f"A common misconception about {topic}",
            f"An outdated approach to {topic}"
        ]
        
        # Adjust distractors based on difficulty
        if difficulty == "easy":
            distractors = [
                f"Not related to {topic}",
                f"Opposite of what {topic} represents",
                f"Incorrect interpretation of {topic}"
            ]
        elif difficulty == "hard":
            distractors = [
                f"A subtle variation that doesn't apply to {topic}",
                f"A closely related but distinct concept from {topic}",
                f"A partial understanding of {topic} principles"
            ]
        else:  # medium
            distractors = base_distractors
        
        return distractors[:3]  # Return 3 distractors

# Create the enhanced agent
mcq_creator = Agent(
    name="mcq_creator",
    model="gemini-2.0-flash",
    description="Advanced agent that generates educational MCQ questions with multiple difficulty levels, explanations, and topic-specific content.",
    instruction="""
    You are an advanced educational MCQ generator agent. Your capabilities include:
    
    1. **Question Generation**: Create multiple-choice questions for any educational topic
    2. **Difficulty Levels**: Generate questions at easy, medium, or hard difficulty levels
    3. **Question Variety**: Use different question types (definition, application, comparison, etc.)
    4. **Quality Assurance**: Ensure questions are educational, clear, and have one correct answer
    5. **Explanations**: Provide explanations for correct answers to enhance learning
    
    **Guidelines**:
    - Each question must have exactly 4 options (A, B, C, D)
    - Only one option should be correct
    - Questions should be clear and unambiguous
    - Avoid trick questions unless specifically requested
    - Tailor content to the specified difficulty level
    - Include educational explanations for better learning outcomes
    
    **Parameters**:
    - topic (required): The subject matter for questions
    - num_questions (optional): Number of questions (1-10, default: 3)
    - difficulty (optional): easy/medium/hard (default: medium)
    
    Always validate inputs and provide helpful error messages for invalid requests.
    """,
    tools=[create_mcqs],
)