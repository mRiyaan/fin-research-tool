# 💰 AI-Powered Earnings Call Analyst
A specialized research tool designed to transform unstructured, scanned financial transcripts into structured, analyst-ready strategic summaries. Built for the Tech Intern (L2) Assessment.

## 🚀 Live Demo
Link: [https://fin-research-tool-mriyaan.streamlit.app](https://fin-research-tool-mriyaan.streamlit.app)

## 📖 Overview
Financial research often involves parsing through 20+ page transcripts. A major pain point is that these documents are frequently uploaded as scanned image PDFs, making standard text-scraping libraries (like PyPDF2 or pdfplumber) fail.

This tool solves that by using a Multimodal Vision approach. Instead of traditional OCR, it leverages the Gemini 1.5 Flash "Vision" engine to interpret the document pages as visual data, ensuring it remains "unbreakable" regardless of document quality.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **AI Engine:** Google Gemini 1.5 Flash (Multimodal)
- **Backend:** Python
- **Deployment:** Streamlit Community Cloud

## ✨ Key Features
- **Native PDF OCR:** Handles both digital and scanned image PDFs with high accuracy.
- **Deep Financial Extraction:** Automatically identifies Order Books, EBITDA margins, and Revenue guidance.
- **Sentiment Analysis:** Analyzes management's tone vs. analyst skepticism in the Q&A section.
- **Institutional Guardrails:** 
  - **No Hallucination:** Forced to return "N/A" if data is missing.
  - **Safety Bypass:** Custom configurations to prevent "Defense/Industrial" keywords from being flagged.

## 🧠 Judgment Calls & Logic
### 1. Tone Assessment
The tool evaluates tone based on management's responsiveness. Direct, data-backed answers to adversarial analyst questions yield a Bullish rating, while vague or boilerplate responses are flagged as Cautious.

### 2. Handling Vague Guidance
If management provides qualitative guidance (e.g., "we expect strong growth"), the tool reports it literally. It is explicitly programmed not to invent numerical percentages that aren't in the source text.

### 3. Hallucination Mitigation
By using a "Closed-World" System Prompt and 0.0 Temperature, the model is restricted to the uploaded document only. It cannot use external market data to "fill in the blanks."

## ⚙️ Local Setup
Clone the repo:
```bash
git clone https://github.com/mRiyaan/fin-research-tool
```

Install dependencies:
```bash
pip install -r requirements.txt
```

4.  **API Key Setup**:
    - You need a Google Gemini API Key. Get one here: [Google AI Studio](https://aistudio.google.com/app/apikey)
    - You can either:
        - Create a `.env` file in the root directory and add: `GOOGLE_API_KEY=your_key_here`
        - OR enter it directly in the app's sidebar.

## Running the App

Run the following command in your terminal:

```bash
streamlit run app.py
```

The application should open automatically in your default web browser.

## Usage

1.  Enter your Google API Key in the sidebar (if not set in `.env`).
2.  Upload a PDF file containing an earnings call transcript.
3.  Click "Analyze Transcript".
4.  View the strategic summary, sentiment analysis, and key takeaways.
