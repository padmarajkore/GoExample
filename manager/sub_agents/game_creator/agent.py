from google.adk.agents import Agent

def create_game_html(topic: str) -> dict:
    """Generate a simple educational game as a single HTML file (placeholder logic)."""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>{topic} Game</title></head>
    <body>
    <h1>Game for {topic}</h1>
    <p>This is a placeholder for a simple educational game about {topic}.</p>
    <!-- Insert game code here -->
    </body>
    </html>
    """
    return {"status": "success", "topic": topic, "html": html_content}

game_creator = Agent(
    name="game_creator",
    model="gemini-2.5-pro",
    description="Agent that generates a simple educational game as a single HTML file for a given topic.",
    instruction="""
    You are an agent that creates a single working HTML file for a simple educational game to help students learn a topic interactively. The HTML should be ready to use and playable. provide the single html file output.
    """,
    # tools=[create_game_html],
) 


