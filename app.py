import streamlit as st
import os
from crewai import Crew, Process, Task
from agents import get_crew_agents
from dotenv import load_dotenv

# 1. Setup & Environment
load_dotenv()
st.set_page_config(page_title="Entertainment AI", page_icon="🎬", layout="wide")

# 2. Memory Initialization
if "history" not in st.session_state:
    st.session_state.history = []

# 3. Sidebar (Left Corner)
with st.sidebar:
    st.title("⚙️ Controls")
    if st.button("🗑️ Clear Chat / New Plan", use_container_width=True):
        st.session_state.history = []
        st.success("History Cleared!") # Added visual feedback
        st.rerun()
    st.info("I remember our conversation! Ask me to 'plan' the choices we just discussed.")

st.title("🎬 Entertainment Planning Assistant")

# 4. Display Chat
# We use a container to keep the chat looking organized
chat_container = st.container()
with chat_container:
    for m in st.session_state.history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# 5. Intro Logic
if not st.session_state.history:
    intro = "Hello! I'm your Entertainment Assistant. What are we looking for? (e.g., 'Horror games for 2 hours' or 'Movies')"
    st.session_state.history.append({"role": "assistant", "content": intro})
    st.rerun()

# 6. The "Brain" (Multi-Agent Logic)
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to state and UI
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build context string so the agents have 'memory'
    context_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.history])

    with st.chat_message("assistant"):
        with st.spinner("🚀 Searching, verifying links, and planning..."):
            try:
                # Initialize our 3 agents from agents.py
                scout, logistics, planner = get_crew_agents()

                # Task 1: Search & Verify
                t1 = Task(
                    description=(
                        f"CONVERSATION HISTORY:\n{context_str}\n\n"
                        f"USER REQUEST: {prompt}\n"
                        "Find 3-5 options. If the user refers to a previous choice, focus on that. "
                        "If they want theaters, search for showtimes in their city."
                    ),
                    expected_output="Curated options with 'Why this fits' and city-specific theater info if applicable.",
                    agent=scout
                )

                # Task 2: Deep Link Extraction
                t2 = Task(
                    description="Find DIRECT URLs for the options. No homepages. Use 'BookMyShow' for theaters.",
                    expected_output="Direct deep-links (https://...) for every option mentioned.",
                    agent=logistics,
                    context=[t1]
                )

                # Task 3: Final Response & Itinerary
                t3 = Task(
                    description="Combine everything. If a time limit was mentioned, create a Markdown schedule table.",
                    expected_output="A friendly response with links and a schedule table.",
                    agent=planner,
                    context=[t1, t2]
                )

                # Assemble the Crew
                crew = Crew(
                    agents=[scout, logistics, planner],
                    tasks=[t1, t2, t3],
                    process=Process.sequential,
                    verbose=True # This shows the agent "thinking" in your terminal
                )

                # Run the process
                result = crew.kickoff()
                
                # Render the final result
                final_response = str(result)
                st.markdown(final_response)
                
                # Save to history
                st.session_state.history.append({"role": "assistant", "content": final_response})

            except Exception as e:
                # Better error reporting for the Pydantic/LLM issues
                st.error(f"⚠️ System Error: {e}")
                st.info("Tip: If you see a 'validation error', ensure agents.py is using the CrewAI LLM class.")