
# 🎬 Entertainment Planning Assistant (AI Powered)

An intelligent AI-based entertainment recommendation and planning system built using **CrewAI** and **Streamlit**. This assistant suggests movies, games, and trending content while creating a personalized schedule for users.

## 🚀 Features
*   🎯 **Smart recommendations** (Movies / Games / Trending)
*   🔍 **Real-time data fetching** using external APIs
*   🤖 **Multi-agent system** using CrewAI:
    *   **Scout Agent** → Finds the best content.
    *   **Logistics Agent** → Fetches valid links.
    *   **Planner Agent** → Creates a structured plan.
*   📅 **Auto-generated** entertainment schedules.
*   🔗 **Direct watch/play links**.
*   💬 **Chat-based UI** using Streamlit.
*   🧠 **Context-aware** responses.

## 🏗️ Tech Stack
*   **Frontend:** Streamlit
*   **Backend / AI Orchestration:** CrewAI
*   **LLM Provider:** Groq
*   **APIs Used:**
    *   🎬 OMDb API (Movies)
    *   🎮 RAWG API (Games)
    *   🌐 Tavily API (Web search)

## 🧠 How It Works
1.  User enters a query (e.g., “Horror movies for 2 hours”).
2.  **CrewAI agents collaborate:**
    *   **Scout** finds the best recommendations.
    *   **Logistics** fetches valid links.
    *   **Planner** structures the final output.
3.  **Streamlit UI displays:**
    *   🎬 Recommendations
    *   🔗 Links
    *   📅 Detailed Schedule

## 📂 Project Structure
```text
Entertainment-Assistant/
│
├── app.py              # Streamlit UI
├── agents.py           # CrewAI agents + tools
├── requirements.txt    # Dependencies
├── .env                # API keys (not included)
└── README.md           # Documentation