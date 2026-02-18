import streamlit as st
import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import json
import re
import tempfile
import time

# Load environment variables
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

    st.divider()
    st.markdown("### 🛠️ System Status")
    st.info("Mode: **Professional Analyst**")
    st.caption("Model: `gemini-2.5-flash`")
    st.caption("Safety: `Disabled`")
    st.caption("Input: `Native PDF Upload`")

# --- Helper Functions ---

def analyze_transcript_multimodal(file_path, api_key):
    """Analyzes the PDF directly using Gemini 2.5 Flash Multimodal capabilities with Professional Persona."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Safety Settings
        # Safety settings to prevent blocking of financial risks
        safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}
        ]

        # 1. Upload file to Gemini
        gemini_file = genai.upload_file(file_path, mime_type="application/pdf")
        
        # 2. Wait for processing (usually instant for PDFs)
        while gemini_file.state.name == "PROCESSING":
            time.sleep(1)
            gemini_file = genai.get_file(gemini_file.name)

        if gemini_file.state.name == "FAILED":
             raise ValueError("Gemini failed to process the PDF file.")

        # 3. Prompt
        prompt = """
        You are a Senior Equity Research Analyst. Perform a deep-dive analysis of this scanned earnings call.
        
        STEP 1: OCR the document and identify the Key Financial Metrics (Revenue, EBITDA, Net Profit, Order Book/Backlog).
        STEP 2: Analyze the 'Tone' of the Management vs. the 'Tone' of the Analysts in the Q&A.
        STEP 3: Extract any specific 'Guidance' or 'Outlook' numbers provided for the next fiscal year.
        
        Provide the final analysis ONLY as a valid JSON object:
        {
          "sentiment": "Strong Bullish / Bullish / Neutral / Bearish / Strong Bearish",
          "confidence_score": 1-100,
          "summary": "A high-level 3-sentence summary of the business trajectory.",
          "positives": ["At least 3 specific tailwinds with data points if available"],
          "negatives": ["At least 3 specific risks or headwinds mentioned"],
          "outlook": "Detail the management's numerical or strategic guidance for the future",
          "key_metrics": {
              "revenue": "Value if found",
              "ebitda": "Value if found",
              "net_profit": "Value if found",
              "order_book": "Value if found",
              "margin_guidance": "Percentage if found"
          }
        }
        Do not use markdown. Return raw JSON.
        """
        
        # 4. Generate Content (Prompt + File)
        response = model.generate_content([prompt, gemini_file], safety_settings=safety_settings)
        
        # 5. Cleanup (Delete file from Gemini)
        try:
            gemini_file.delete()
        except:
            pass

        if response.text:
            cleaned_text = re.sub(r'```json\s*|\s*```', '', response.text).strip()
            return json.loads(cleaned_text)
        else:
            return None

    except Exception as e:
        # Pass the error up
        raise e

# --- Main UI ---
st.title("💰 Earnings Call AI Analyst")
st.markdown("Upload an earnings call transcript (PDF) to get an AI-powered strategic summary.")

uploaded_file = st.file_uploader("Upload Transcript (PDF)", type="pdf")

if uploaded_file is not None:
    if st.button("Analyze Transcript"):
        if not api_key:
            st.error("Please provide an API Key to proceed.")
        else:
            # --- Checkpoint System ---
            status_container = st.status("🚀 Processing...", expanded=True)
            progress_bar = status_container.progress(0, text="Initializing...")
            temp_path = None
            
            try:
                # Checkpoint 1: Uploading
                status_container.write("📤 Uploading PDF to Gemini (Vision Mode)...")
                progress_bar.progress(10, text="Uploading PDF...")
                
                # Create a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_path = tmp.name

                if temp_path:
                    progress_bar.progress(30, text="PDF Uploaded. Waiting for processing...")
                    status_container.write("✅ Upload success. Model is 'reading' the file...")
                    
                    # Checkpoint 2: AI Analysis
                    progress_bar.progress(50, text="Analyzing financial data with Gemini 2.5 Flash...")
                    status_container.write("🧠 Analyzing with **Gemini 2.5 Flash**...")
                    
                    result = analyze_transcript_multimodal(temp_path, api_key) # Using 'result' to match new UI logic
                    
                    if result:
                        progress_bar.progress(100, text="Analysis Complete!")
                        status_container.update(label="Analysis Complete!", state="complete", expanded=False)
                        st.balloons()
                        
                        # --- Professional UI ---
                        st.divider()

                        # 1. Top Level Metrics
                        col1, col2, col3 = st.columns([1, 1, 2])
                        col1.metric("Market Sentiment", result.get("sentiment", "N/A"))
                        col2.metric("AI Confidence", f"{result.get('confidence_score', 0)}%")
                        
                        # Extract order book/metrics
                        metrics = result.get("key_metrics", {})
                        order_book = metrics.get("order_book", "N/A")
                        
                        with col3:
                            st.markdown("### Order Book")
                            st.markdown(f"<h1 style='font-size: 3rem; color: #4CAF50;'>{order_book}</h1>", unsafe_allow_html=True)

                        # 2. Executive Summary
                        st.subheader("📋 Strategic Executive Summary")
                        st.info(result.get("summary", "No summary available."))

                        # 3. Pros and Cons
                        p_col, n_col = st.columns(2)
                        with p_col:
                            st.subheader("✅ Key Tailwinds")
                            for p in result.get("positives", []):
                                st.success(f"{p}")
                                
                        with n_col:
                            st.subheader("⚠️ Critical Risks")
                            for n in result.get("negatives", []):
                                st.error(f"{n}")

                        st.divider()

                        # 4. Management Guidance
                        st.subheader("🔮 Forward-Looking Guidance")
                        st.warning(result.get("outlook", "No specific guidance provided."))

                        # 5. Key Metrics Table (Extra Professional Touch)
                        st.subheader("📊 Key Financial Metrics")
                        st.json(metrics)
                        
                        # Raw Data Expander
                        with st.expander("View Full Raw Analysis"):
                            st.json(result)
                    else:
                        status_container.update(label="Analysis Failed", state="error")
                else:
                    status_container.update(label="File Error", state="error")
            except Exception as e:
                status_container.update(label="Error Occurred", state="error")
                st.error(f"An error occurred: {e}")
            finally:
                # Local cleanup
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)

    
else:
    st.info("Please upload a PDF file to begin.")
