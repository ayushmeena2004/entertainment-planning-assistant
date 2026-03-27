import os
from crewai import Agent, LLM
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# 1. The Wrapper for Search (Fixed for CrewAI 2026)
@tool('DuckDuckGoSearch')
def search_tool(search_query: str):
    """Search the web for real-time information on movies, games, or showtimes."""
    return DuckDuckGoSearchRun().run(search_query)

def get_crew_agents():
    # 2. Optimized LLM
    my_llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.5 # Slightly lower temperature for more factual results
    )

    # 3. The Scout (Improved: Trend Intelligence)
    scout = Agent(
        role="Entertainment Trend Analyst",
        goal="Discover 3-5 high-quality entertainment options that match the user's specific mood and location.",
        backstory=(
            "You are a elite digital scout with access to real-time data from IMDb, Rotten Tomatoes, and Steam. "
            "You don't just find random items; you look for critically acclaimed and trending content. "
            "If a user mentions a location like Betma, you prioritize local theater showtimes."
        ),
        llm=my_llm,
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

    # 4. The Logistics Expert (Improved: Deep Link Verification)
    logistics = Agent(
        role="Digital Access Specialist",
        goal="Provide direct, verified deep-links for streaming or ticket booking for the Scout's suggestions.",
        backstory=(
            "You are a master of navigation. You hate broken links and generic homepages. "
            "Your job is to find the exact URL for the 'Book Tickets' button on BookMyShow or the "
            "'Watch Now' button on Netflix/Prime. You verify the technical requirements for games too."
        ),
        llm=my_llm,
        tools=[search_tool],
        verbose=True,
        allow_delegation=False
    )

    # 5. The Planner (Improved: Itinerary Architect)
    planner = Agent(
        role="Chief Experience Architect",
        goal="Synthesize suggestions into a professional, actionable entertainment itinerary.",
        backstory=(
            "You are a world-class event planner. You understand that fun requires timing. "
            "You calculate setup times, intermission breaks, and travel logic. "
            "Your output is always a clean, aesthetic Markdown table that a user can follow easily."
        ),
        llm=my_llm,
        verbose=True,
        allow_delegation=False
    )

    return scout, logistics, planner