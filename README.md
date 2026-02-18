# Financial Research Tool

A Streamlit application that uses Google's Gemini 2.5 Flash model to analyze earnings call transcripts (PDF) and provide a strategic summary.

## Setup

1.  **Clone or Download this repository** to your local machine.

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
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
