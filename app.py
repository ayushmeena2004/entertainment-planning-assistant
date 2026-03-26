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
        st.rerun()
    st.info("I remember our conversation! Ask me to 'plan' the choices we just discussed.")

st.title("🎬 Entertainment Planning Assistant")

# 4. Display Chat
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# 5. Intro
if not st.session_state.history:
    intro = "Hello! I'm your Entertainment Assistant. What are we looking for? (e.g., 'Horror games for 2 hours' or 'Movies in Betma')"
    st.session_state.history.append({"role": "assistant", "content": intro})
    st.rerun()

# 6. The "Brain" (Multi-Agent Logic)
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build history context so the agent 'remembers'
    context_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.history])

    with st.chat_message("assistant"):
        with st.spinner("Searching and verifying links..."):
            try:
                scout, logistics, planner = get_crew_agents()

                # Task 1: Search & Verify (Using context to remember previous choices)
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

                crew = Crew(
                    agents=[scout, logistics, planner],
                    tasks=[t1, t2, t3],
                    process=Process.sequential,
                    verbose=True
                )

                result = crew.kickoff()
                
                final_response = str(result)
                st.markdown(final_response)
                st.session_state.history.append({"role": "assistant", "content": final_response})

            except Exception as e:
                st.error(f"Error: {e}")