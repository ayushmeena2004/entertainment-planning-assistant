import streamlit as st
import os
import json
import ast  # ✅ Added for bulletproof parsing of Python-style dictionaries
from crewai import Crew, Process, Task
from agents import get_crew_agents
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

# ------------------ SETUP ------------------ #
load_dotenv()

# Define the structured output schema
class TimelineItem(BaseModel):
    time: str
    event: str
    details: str

class Recommendation(BaseModel):
    title: str
    description: str
    why: str

class Link(BaseModel):
    title: str
    url: str

class PlanOutput(BaseModel):
    timeline: List[TimelineItem]
    recommendations: List[Recommendation]
    links: List[Link]

st.set_page_config(page_title="Entertainment AI", page_icon="🎬", layout="wide")

# ------------------ MEMORY ------------------ #
if "history" not in st.session_state:
    st.session_state.history = []

# ------------------ SIDEBAR ------------------ #
with st.sidebar:
    st.title("⚙️ Controls")
    if st.button("🗑️ Clear Chat / New Plan", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    st.info("Ask normally → then say 'plan it' to generate schedule")

# ------------------ TITLE ------------------ #
st.title("🎬 Entertainment Planning Assistant")

# ------------------ DISPLAY CHAT ------------------ #
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ------------------ INTRO ------------------ #
if not st.session_state.history:
    intro = "Hello! I'm your Entertainment Assistant. What are we looking for?"
    st.session_state.history.append({"role": "assistant", "content": intro})
    st.rerun()

# ------------------ USER INPUT ------------------ #
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ------------------ AI RESPONSE ------------------ #
    with st.chat_message("assistant"):
        with st.spinner("🔍 Finding best content for you..."):
            try:
                scout, logistics, planner = get_crew_agents()

                # --- TASK 1: Discovery ---
                t1 = Task(
                    description=(
                        f"USER REQUEST: {prompt}\n\n"
                        "Find 3 BEST recommendations based on the user's request."
                    ),
                    expected_output="Short list of 3 items",
                    agent=scout
                )

                # --- TASK 2: Sourcing ---
                t2 = Task(
                    description="Get 3 valid direct links for the recommendations found.",
                    expected_output="3 valid URLs",
                    agent=logistics,
                    context=[t1]
                )

                # --- TASK 3: Planning ---
                t3 = Task(
                    description=(
                        "Synthesize the recommendations and links into a detailed, "
                        "chronological timeline. Ensure every activity is assigned a "
                        "specific time slot. Use the PlanOutput structure."
                    ),
                    expected_output="A structured plan with timeline, recommendations, and links.",
                    agent=planner,
                    context=[t1, t2],
                    output_json=PlanOutput 
                )

                # ------------------ CREW ------------------ #
                crew = Crew(
                    agents=[scout, logistics, planner],
                    tasks=[t1, t2, t3],
                    process=Process.sequential,
                    verbose=False
                )

                result = crew.kickoff()

                # ------------------ BULLETPROOF DATA EXTRACTION ------------------ #
                data = None
                try:
                    # 1. Try Pydantic object first
                    data = result.pydantic.model_dump()
                except Exception:
                    try:
                        # 2. Try standard JSON parsing
                        clean = str(result).strip()
                        if "```json" in clean:
                            clean = clean.split("```json")[-1].split("```")[0]
                        data = json.loads(clean)
                    except Exception:
                        try:
                            # 3. Handle Python-style output (fix for image_2b385d.png)
                            data = ast.literal_eval(str(result).strip())
                        except Exception as final_e:
                            st.error("Failed to parse output format.")
                            st.stop()

                # ------------------ UI RENDERING ------------------ #
                
                # 1. TIMELINE SECTION
                if data and data.get("timeline"):
                    st.markdown("## 📅 Your Schedule")
                    for slot in data["timeline"]:
                        with st.container(border=True):
                            col1, col2 = st.columns([1, 4])
                            col1.markdown(f"**{slot.get('time')}**")
                            col2.markdown(f"**{slot.get('event')}**")
                            if slot.get('details'):
                                col2.caption(slot.get('details'))

                # 2. RECOMMENDATIONS SECTION
                st.markdown("## 🎬 Top Picks")
                for item in data.get("recommendations", []):
                    with st.container(border=True):
                        st.subheader(item.get("title", ""))
                        st.write(item.get("description", ""))
                        st.caption(f"✨ {item.get('why', '')}")

                # 3. LINKS SECTION
                if data.get("links"):
                    st.markdown("## 🔗 Resources & Links")
                    links_list = data["links"]
                    cols = st.columns(len(links_list))
                    for idx, link in enumerate(links_list):
                        with cols[idx]:
                            st.link_button(
                                link.get("title", "Visit"),
                                link.get("url", "#"),
                                use_container_width=True
                            )

                # Save to history
                st.session_state.history.append({
                    "role": "assistant",
                    "content": "Plan generated successfully! See the details above."
                })

            except Exception as e:
                st.error(f"❌ Error: {e}")
                with st.expander("Show Raw Error Output"):
                    st.write(str(result) if 'result' in locals() else "No result generated")