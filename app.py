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
    intro = "Hello! I'm your Entertainment Assistant. What are we looking for? (e.g., 'Horror games for 2 hours' or 'Movies')"
    st.session_state.history.append({"role": "assistant", "content": intro})
    st.rerun()

# 6. The "Brain" (Multi-Agent Logic)
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Limit history (better performance)
    recent_history = st.session_state.history[-6:]
    context_str = "\n".join([f"{m['role']}: {m['content']}" for m in recent_history])

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching and verifying links..."):
            try:
                scout, logistics, planner = get_crew_agents()

                # =============================
                # Task 1: Discovery
                # =============================
                t1 = Task(
                    description=(
                        f"CONTEXT:\n{context_str}\n\n"
                        f"USER REQUEST: {prompt}\n\n"
                        "Find 3-5 best options.\n"
                        "- Understand user intent (mood, time, platform)\n"
                        "- Include WHY it fits\n"
                        "- If location-based → include city relevance"
                    ),
                    expected_output="Structured recommendations with reasons",
                    agent=scout
                )

                # =============================
                # Task 2: Links
                # =============================
                t2 = Task(
                    description="""
                    Find DIRECT working links:
                    - BookMyShow for movies
                    - Netflix / Prime / YouTube links
                    - No homepages
                    """,
                    expected_output="Clean deep links only",
                    agent=logistics,
                    context=[t1]
                )

                # =============================
                # Task 3: JSON Output
                # =============================
                t3 = Task(
                    description="""
                    Convert everything into STRICT JSON.

                    Format:
                    {
                        "recommendations": [
                            {
                                "title": "",
                                "description": "",
                                "why": ""
                            }
                        ],
                        "links": [
                            {
                                "title": "",
                                "url": ""
                            }
                        ],
                        "schedule": [
                            {
                                "time": "",
                                "activity": ""
                            }
                        ]
                    }

                    Rules:
                    - No extra text
                    - No explanation
                    - Only valid JSON
                    """,
                    expected_output="Valid JSON only",
                    agent=planner,
                    context=[t1, t2]
                )

                crew = Crew(
                    agents=[scout, logistics, planner],
                    tasks=[t1, t2, t3],
                    process=Process.sequential,
                    verbose=False
                )

                result = crew.kickoff()

                # =============================
                # JSON Parsing
                # =============================
                import json

                try:
                    data = json.loads(str(result))
                except Exception:
                    st.warning("⚠️ Could not parse structured data. Showing raw output.")
                    st.markdown(str(result))
                    st.session_state.history.append({
                        "role": "assistant",
                        "content": str(result)
                    })
                    st.stop()

                # =============================
                # 🎬 UI: Recommendations
                # =============================
                st.markdown("## 🎬 Top Picks for You")

                for item in data.get("recommendations", []):
                    with st.container(border=True):
                        st.subheader(item.get("title", ""))
                        st.write(item.get("description", ""))
                        st.caption(f"✨ {item.get('why', '')}")

                # =============================
                # 🔗 UI: Links
                # =============================
                if data.get("links"):
                    st.markdown("## 🔗 Watch / Play")

                    for link in data["links"]:
                        st.link_button(
                            link.get("title", "Open"),
                            link.get("url", "#")
                        )

                # =============================
                # 📅 UI: Schedule
                # =============================
                if data.get("schedule"):
                    st.markdown("## 📅 Your Plan")

                    for s in data["schedule"]:
                        st.write(f"**{s.get('time','')}** → {s.get('activity','')}")

                # Save response
                st.session_state.history.append({
                    "role": "assistant",
                    "content": str(data)
                })

            except Exception as e:
                st.error(f"❌ Error: {e}")