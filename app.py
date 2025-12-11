import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # We'll handle this in the UI
    pass
else:
    genai.configure(api_key=api_key)

# Page Config
st.set_page_config(
    page_title="Idea Validator",
    page_icon="🔥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Mode & Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stTextArea textarea {
        background-color: #262730;
        color: #FAFAFA;
        border: 1px solid #4B4B4B;
    }
    .stButton > button {
        width: 100%;
        background-color: #FF4B4B; 
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    .report-box {
        background-color: #262730;
        border: 1px solid #4B4B4B;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Mock Data Functions ---

def get_mock_response(idea):
    """Fallback mock response for the roast."""
    import random
    responses = [
        {
            "roast": "This idea is so derivative it makes a photocopier look original. You're building a feature, not a product.",
            "score": 15,
            "action": "Pivot to something that solves a real problem for people with money."
        },
        {
            "roast": "The only thing 'revolutionary' about this is how quickly you'll burn through your savings. No one needs this.",
            "score": 5,
            "action": "Don't quit your day job. Seriously."
        }
    ]
    return random.choice(responses)

def get_mock_plan(idea):
    """Fallback mock response for the detailed plan."""
    return """
    **Mock Execution Plan (API Unavailable):**
    
    1.  **Validation**: Go to Reddit r/SaaS and ask if anyone would pay for this. (Spoiler: No).
    2.  **MVP**: Build a landing page in 1 hour using Carrd. Do not write code.
    3.  **Outreach**: Cold email 50 potential users. If 0 reply, kill the idea.
    4.  **Pivot**: Realize the market is too small. Switch to selling shovels to other AI startups.
    5.  **Scale**: If by miracle you get users, automate the backend with Python.
    """

# --- API Functions ---

def get_ai_response(idea):
    """
    Sends the idea to Gemini for a roast (JSON).
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = f"""
        You are a brutal VC investor. Analyze this SaaS idea:
        "{idea}"
        Return a pure JSON response with exactly three keys: 
        "roast" (a 2-sentence harsh critique), 
        "score" (an integer 0-100), 
        and "action" (one specific next step). 
        Do not wrap in markdown code blocks. Output raw JSON only.
        """
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        text_response = response.text.strip()
        # Cleanup
        if text_response.startswith("```json"): text_response = text_response[7:]
        if text_response.endswith("```"): text_response = text_response[:-3]
        return json.loads(text_response)
    except Exception as e:
        print(f"API Error (Roast): {e}")
        result = get_mock_response(idea)
        result["error"] = f"⚠️ API Quota/Error (Using Mock Data): {str(e)}"
        return result

def get_execution_plan(idea):
    """
    Sends the idea to Gemini for a detailed 5-step plan (Text).
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        prompt = f"""
        Write a detailed 5-step execution plan for this SaaS idea:
        "{idea}"
        Be specific, actionable, and ruthless. Format it as markdown.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API Error (Plan): {e}")
        return get_mock_plan(idea) + f"\n\n*(System Note: Generated via Mock due to API Error: {str(e)})*"

# --- UI Layout ---

# Sidebar: Tip Jar
with st.sidebar:
    st.header("About")
    st.markdown("This AI will crush your dreams so the market doesn't have to.")
    st.markdown("---")
    st.link_button("☕ Support the Developer", "https://www.buymeacoffee.com/")

# Main Content
st.title("🔥 Roast My SaaS Idea")
st.markdown("### Validate your startup idea before you lose your life savings.")

# User Input
idea_input = st.text_area("What's your \"billion dollar\" idea?", height=150, placeholder="e.g., Uber for dog walkers who also know how to code...")

# Session State to hold data between interactions
if 'roast_result' not in st.session_state:
    st.session_state.roast_result = None

# Action Button
if st.button("Roast My Idea 🔥"):
    if not idea_input.strip():
        st.warning("Please enter an idea first. We can't roast thin air.")
    elif not api_key:
        st.error("Please configure your GEMINI_API_KEY in the .env file first.")
    else:
        with st.spinner("Analyzing market saturation... Judging your life choices..."):
            st.session_state.roast_result = get_ai_response(idea_input)

# Display Results
if st.session_state.roast_result:
    result = st.session_state.roast_result
    
    # Error Warning
    if "error" in result:
        st.warning(result['error'])

    # 1. Roast
    st.subheader("💀 The Brutal Reality")
    st.error(result.get("roast", "Roast unavailable."))
    
    # 2. Score
    st.subheader("Viability Score")
    score = result.get("score", 0)
    st.progress(score)
    st.caption(f"Score: {score}/100")
    
    # 3. Action
    st.subheader("🚀 First Concrete Step")
    st.success(result.get("action", "No action provided."))
    
    st.markdown("---")
    
    # --- Feature: Report Generator ---
    st.subheader("📄 One More Thing...")
    st.markdown("Need a roadmap to fix this mess?")
    
    if st.button("Generate Detailed Execution Plan 🧠"):
        with st.spinner("Drafting your escape plan..."):
            plan_text = get_execution_plan(idea_input)
            
            # Show in expander
            with st.expander("View Execution Plan", expanded=True):
                st.markdown(plan_text)
                
            # Download Button for the Plan
            st.download_button(
                label="📥 Download Execution Plan",
                data=plan_text,
                file_name="execution_plan.txt",
                mime="text/plain"
            )
