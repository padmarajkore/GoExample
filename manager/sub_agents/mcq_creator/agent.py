from google.adk.agents import Agent

def create_mcqs(topic: str) -> dict:
    """Generate MCQ questions for a given topic (placeholder logic)."""
    return {
        "status": "success",
        "topic": topic,
        "questions": [
            {
                "question": f"What is a key concept in {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
        ]
    }

mcq_creator = Agent(
    name="mcq_creator",
    model="gemini-2.0-flash",
    description="Agent that generates MCQ questions for a given topic.",
    instruction="""
    You are an agent that creates multiple-choice questions (MCQs) for any educational topic provided by the user. Each question should have 4 options and indicate the correct answer.
    """,
    tools=[create_mcqs],
) 