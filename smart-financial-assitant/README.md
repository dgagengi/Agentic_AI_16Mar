# Smart Financial Assistant

An agentic AI web application for financial management using LangChain and LangGraph.

## Features

- Track expenses
- Budget summary
- Financial tips
- Human in the loop (HITL)

## Architecture

User → Streamlit UI → LangGraph (orchestration) → LangChain (tools) → Groq (fast LLM) → Llama (detailed LLM) → Observability

## Setup

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your actual Groq API key:
     ```
     GROQ_API_KEY=your_actual_api_key_here
     ```

5. **Run the application**:
   ```bash
   streamlit run main.py
   ```

   The app will be available at `http://localhost:8501`

## Usage

- Enter your User ID in the sidebar
- Use tabs to manage expenses, budgets, view summaries, and chat with the AI assistant