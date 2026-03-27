from crewai import Agent
from langchain_groq import ChatGroq
import os

def get_crew_agents():
    # Initialize the LLM (ensure your .env has GROQ_API_KEY)
    llm_string = "groq/llama-3.3-70b-versatile"

    # 1. The Scout: Finds the 'Vibe'
    scout = Agent(
        role="Entertainment Scout",
        goal="Find the top 3 trending movies or games based on the user's mood.",
        backstory="You are an expert at tracking viral trends on Netflix, Steam, and BookMyShow.",
        llm=llm_string,
        verbose=True
    )

    # 2. The Logistics Expert: Finds the 'Access'
    logistics = Agent(
        role="Access Specialist",
        goal="Find direct, non-broken URLs for the Scout's suggestions.",
        backstory="You are a master of deep-linking. You find direct 'Play' or 'Ticket' pages.",
        llm=llm_string,
        verbose=True
    )

    # 3. The Planner: Creates the 'Timeline'
    planner = Agent(
        role="Master Planner",
        goal="Create a minute-by-minute schedule in a Markdown table.",
        backstory="You are a productivity guru who knows how to pack maximum fun into any time budget.",
        llm=llm_string,
        verbose=True
    )

    return scout, logistics, planner