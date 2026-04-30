from crewai import Agent
from crewai.tools import tool
from dotenv import load_dotenv
import os
import requests
from tavily import TavilyClient
import json

# ------------------ LOAD ENV ------------------ #
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")
RAWG_API_KEY = os.getenv("RAWG_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ------------------ LLM (⚡ OPTIMIZED) ------------------ #
from crewai import LLM

llm = LLM(
    model="groq/llama-3.3-70b-Versatile",   # ✅ lighter model (fixes rate limit)
    api_key=GROQ_API_KEY,
    temperature=0.5,
    max_tokens=800                 # ✅ limit output
)

# ------------------ TOOLS ------------------ #

def get_movie_data(query):
    try:
        # ✅ FIX: use 's=' for search instead of exact title
        url = f"http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5).json()

        if response.get("Search"):
            movie = response["Search"][0]
            return {
                "type": "movie",
                "title": movie["Title"],
                "year": movie["Year"],
                "link": f"https://www.imdb.com/title/{movie['imdbID']}/"
            }

        return {"error": "Movie not found", "query": query}

    except Exception as e:
        return {"error": str(e)}


def get_game_data(query):
    try:
        url = f"https://api.rawg.io/api/games?search={query}&key={RAWG_API_KEY}"
        response = requests.get(url, timeout=5).json()

        if response.get("results"):
            game = response["results"][0]
            return {
                "type": "game",
                "name": game["name"],
                "rating": game["rating"],
                "link": f"https://rawg.io/games/{game['slug']}"
            }

        return {"error": "Game not found", "query": query}

    except Exception as e:
        return {"error": str(e)}


tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

def search_web(query):
    try:
        result = tavily_client.search(query=query)
        return {
            "type": "web",
            "results": result.get("results", [])[:3]  # ✅ limit results
        }
    except Exception as e:
        return {"error": str(e)}


# ------------------ SMART ROUTER ------------------ #

@tool("smart_search")
def smart_search(query: str) -> str:
    """
Fetch REAL-TIME data smartly.
"""

    query_lower = query.lower()

    try:
        # 🎬 Movies
        if any(word in query_lower for word in [
            "movie", "film", "horror", "bollywood", "hollywood"
        ]):
            result = get_movie_data(query)

        # 🎮 Games
        elif any(word in query_lower for word in [
            "game", "gaming", "steam", "ps5", "xbox"
        ]):
            result = get_game_data(query)

        # 🔥 Trending
        elif "trending" in query_lower or "latest" in query_lower:
            result = search_web(query + " trending movies 2025")

        # 🌐 Default
        else:
            result = search_web(query)

        # ✅ IMPORTANT: stop retry loop
        if "error" in result:
            return json.dumps({
                "type": "fallback",
                "message": "No exact result found, suggest popular items instead"
            })

        return json.dumps(result)

    except Exception as e:
        return json.dumps({"error": str(e)})


# ------------------ AGENTS ------------------ #

def get_crew_agents():

    scout = Agent(
        role="Entertainment Scout",
        goal="""
Find 3 best recommendations.
Rules:
- Use smart_search ONLY ONCE
- Do NOT retry tool
- Keep answers short
""",
        backstory="You rely on tools but avoid loops.",
        llm=llm,
        tools=[smart_search],
        verbose=False
    )

    logistics = Agent(
        role="Access Specialist",
        goal="""
Provide valid links only.
Rules:
- Use smart_search ONLY ONCE
- Do NOT retry
""",
        backstory="You validate links efficiently.",
        llm=llm,
        tools=[smart_search],
        verbose=False
    )

    # UPDATED PLANNER AGENT
    planner = Agent(
        role="Master Planner",
        goal="""
Synthesize recommendations into a detailed, chronological schedule. 
Ensure the output is a step-by-step timeline with specific time slots.
""",
        backstory="""
You are a precision-focused logistics coordinator. 
You excel at organizing events into a linear, easy-to-read timeline, 
ensuring that time is allocated logically for travel, enjoyment, and breaks.
""",
        llm=llm,
        verbose=False
    )

    return scout, logistics, planner