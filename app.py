import streamlit as st
import os
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv
import json
import re


load_dotenv()

# --- Configuration ---
st.set_page_config(
    page_title="Earnings Call AI Analyst",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar: API Key ---
with st.sidebar:
    st.header("🔑 API Configuration")
    user_api_key = st.text_input("Enter your Google API Key", type="password")
    
    # Prioritize user input, fallback to environment variable
    api_key = user_api_key if user_api_key else os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.warning("⚠️ Please enter a Google API Key to proceed.")
        st.caption("Don't have one? Get it [here](https://aistudio.google.com/app/apikey).")

    # --- Debug Option ---
    st.divider()
    if st.checkbox("Show Available Models (Debug)"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                st.write("Available Gemini Models:")
                for m in models:
                    if 'generateContent' in m.supported_generation_methods:
                        st.code(m.name)
            except Exception as e:
                st.error(f"Error fetching models: {e}")
        else:
            st.warning("Enter API Key first.")

# --- Helper Functions ---

def extract_text_from_pdf(uploaded_file):
    """Extracts text from a PDF file using pypdf."""
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def analyze_transcript(text, api_key):
    """Analyzes the transcript using Gemini 2.5 Flash."""
    try:
        genai.configure(api_key=api_key)
        # using gemini-2.5-flash 
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Using f-string for cleaner variable injection
        prompt = f"""
        You are an expert financial analyst. Your task is to analyze the following Earnings Call Transcript and provide a structured strategic summary.
        
        Strictly output the result as a valid JSON object with the following keys:
        - "sentiment": String (one of: "Bullish", "Neutral", "Bearish")
        - "confidence_score": Integer (1-100)
        - "summary": String (A concise 2-sentence executive summary)
        - "positives": List of strings (Top 3 tailwinds/strengths)
        - "negatives": List of strings (Top 3 headwinds/risks)
        - "outlook": String (Management's guidance)

        Do not include markdown formatting (like ```json). Just return the raw JSON string.

        Transcript:
        {text} 
        """
        
        response = model.generate_content(prompt)
        
        if response.text:
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response.text).strip()
            return json.loads(cleaned_text)
        else:
            return None

    except Exception as e:
        # If 2.5 fails, this error will show up in the UI
        st.error(f"Error during analysis: {e}")
        return None

# --- Main UI ---
st.title("💰 Earnings Call AI Analyst")
st.markdown("Upload an earnings call transcript (PDF) to get an AI-powered strategic summary.")

uploaded_file = st.file_uploader("Upload Transcript (PDF)", type="pdf")

if uploaded_file is not None:
    if st.button("Analyze Transcript"):
        if not api_key:
            st.error("Please provide an API Key to proceed.")
        else:
            with st.spinner("Extracting text and analyzing with Gemini... This may take a moment."):
                # 1. Extract Text
                transcript_text = extract_text_from_pdf(uploaded_file)
                
                if transcript_text:
                    # 2. Analyze with LLM
                    analysis_result = analyze_transcript(transcript_text, api_key)
                    
                    if analysis_result:
                        # 3. Display Results
                        st.success("Analysis Complete!")
                        st.divider()
                        
                        # Sentiment & Score
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Sentiment", analysis_result.get("sentiment", "N/A"))
                        with col2:
                            st.metric("Confidence Score", f"{analysis_result.get('confidence_score', 0)}/100")
                        
                        st.subheader("Executive Summary")
                        st.write(analysis_result.get("summary", "No summary available."))
                        
                        st.divider()
                        
                        # Positives & Negatives
                        p_col, n_col = st.columns(2)
                        
                        with p_col:
                            st.subheader("✅ Positives")
                            for item in analysis_result.get("positives", []):
                                st.write(f"- {item}")
                                
                        with n_col:
                            st.subheader("🔻 Negatives")
                            for item in analysis_result.get("negatives", []):
                                st.write(f"- {item}")
                        
                        st.divider()

                        # Outlook
                        st.subheader("🔮 Management Outlook")
                        st.info(analysis_result.get("outlook", "No specific outlook provided."))
                        
                        # Raw Data Expander (Optional, good for debugging/transparency)
                        with st.expander("View Full Extracted JSON Analysis"):
                            st.json(analysis_result)

    
else:
    st.info("Please upload a PDF file to begin.")
