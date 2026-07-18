# AI-based COVID-19 Information Chatbot

An AI-powered chatbot that answers COVID-19 related questions in natural language. Built with Python and Streamlit, it combines TF-IDF/FAQ-based retrieval with Google's Gemini API to generate accurate, context-grounded responses.

### 🚀 Live Demo
👉 **[Try the chatbot here](https://covidbot-f4ylrlgk8kcavgxwqwlwzf.streamlit.app/)**

> ⚠️ **Disclaimer:** This chatbot is intended for educational awareness only. It is not a replacement for professional medical advice, diagnosis, or emergency services.

## Features

- 💬 Conversational chat interface built with Streamlit
- 🔍 Hybrid retrieval using TF-IDF and cosine similarity over a curated FAQ knowledge base
- 🧠 Response generation powered by Google's Gemini API (`gemini-2.5-flash`)
- 🩺 Intent detection for topics like symptoms, prevention, testing, vaccines, isolation, and recovery
- ✍️ Fuzzy matching for informal or misspelled COVID-related terms (e.g., "cov-19", "corona")
- 🗂️ Session-based chat history with a "Clear Conversation" option

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| NLP / ML | scikit-learn (TF-IDF, cosine similarity) |
| LLM | Google Gemini API |
| Data | JSON-based FAQ knowledge base |

## Project Structure

```
ai_covid_chatbot_project/
├── app.py                     # Streamlit app entry point
├── requirements.txt
├── data/
│   └── covid_faq.json         # FAQ knowledge base
├── src/
│   ├── chatbot.py             # Core chatbot logic (retrieval + Gemini)
│   ├── data_loader.py         # Loads and validates FAQ data
│   ├── text_preprocessor.py   # Text cleaning and tokenization
│   └── utils.py
└── assets/
    └── chatbot_banner.txt
```

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd ai_covid_chatbot_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your Gemini API key**

   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## Example Questions

- What is COVID-19?
- Tell me about coronavirus
- Is corona dangerous?
- What are the symptoms of COVID-19?
- My antigen test is positive, what should I do?
- How does corona spread?
- Is the COVID vaccine safe?
- What should I do during isolation?
- What is post-COVID recovery?

## Notes

- Make sure `.env` is listed in `.gitignore` and never committed to version control.
- If you're missing a Gemini API key, get one from [Google AI Studio](https://aistudio.google.com/).

## License

This project is for educational purposes.
