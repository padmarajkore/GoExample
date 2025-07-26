from google.adk.agents import Agent

def answer_question(question: str) -> dict:
    """Answer any query from the teacher (placeholder logic)."""
    return {"status": "success", "question": question, "answer": f"This is a placeholder answer for: {question}"}

qa_agent = Agent(
    name="qa_agent",
    model="gemini-2.0-flash",
    description="Agent that answers any query from the teacher.",
    instruction="""
    You are an agent that answers any educational or administrative query from a teacher. Provide clear, concise, and helpful answers.
    """,
    tools=[answer_question],
) 