import os
import re
import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data_loader import load_faq_data
from src.text_preprocessor import preprocess_text, tokenize_text


@dataclass
class RetrievalResult:
    question: str
    answer: str
    category: str
    score: float


class CovidChatbot:
    def __init__(self):
        load_dotenv()
        print("✅ GEMINI-ONLY COVID CHATBOT LOADED")
        self.faq_data = load_faq_data()
        self.chat_history: List[Dict[str, str]] = []
        self.covid_keywords = self._build_covid_keywords()
        self.intent_keywords = self._build_intent_keywords()
        self.covid_patterns = self._build_covid_patterns()
        self.vectorizer, self.faq_matrix = self._build_retriever()
        self.client = self._build_genai_client()
        self.model_name = "gemini-2.5-flash"

    def _build_genai_client(self):
        api_key = os.getenv("GEMINI_API_KEY", "").strip()

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Add it to your .env file before running the app."
            )

        print("✅ API KEY LOADED SUCCESSFULLY")
        return genai.Client(api_key=api_key)

    def _build_covid_keywords(self) -> set:
        return {
            "covid", "covid19", "covid-19", "covid 19",
            "cov19", "cov-19", "cov 19",
            "corona", "coronavirus", "corona virus",
            "sars-cov-2", "sars cov 2", "sars", "virus", "viral",
            "pandemic", "infection", "infected", "contagious", "spread",
            "transmission", "exposure", "variant", "variants",
            "omicron", "delta", "symptom", "symptoms", "fever", "cough",
            "cold", "flu", "throat", "sore", "breathing", "breath",
            "oxygen", "smell", "taste", "fatigue", "bodyache",
            "headache", "pneumonia", "chest", "positive", "negative",
            "rtpcr", "rt-pcr", "antigen", "test", "testing", "swab",
            "quarantine", "isolation", "mask", "sanitizer", "sanitize",
            "disinfect", "distance", "vaccination", "vaccine", "vaccines",
            "booster", "dose", "immunity", "hospital", "hospitalization",
            "recover", "recovery", "postcovid", "longcovid", "long"
        }

    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        return {
            "symptoms": [
                "symptom", "symptoms", "fever", "cough", "breath",
                "oxygen", "taste", "smell", "fatigue", "cold", "throat"
            ],
            "prevention": [
                "prevent", "prevention", "mask", "sanitize",
                "sanitizer", "distance", "avoid", "protection"
            ],
            "testing": [
                "test", "testing", "rtpcr", "rt-pcr", "antigen",
                "positive", "negative", "report", "swab"
            ],
            "vaccination": [
                "vaccine", "vaccination", "booster", "dose", "immunity"
            ],
            "treatment": [
                "medicine", "treat", "treatment", "doctor",
                "hospital", "care", "recover", "recovery"
            ],
            "transmission": [
                "spread", "transmission", "infect", "infection",
                "contagious", "exposure"
            ],
            "long_covid": [
                "long covid", "brain fog", "after effects",
                "post covid", "fatigue"
            ],
        }

    def _build_covid_patterns(self) -> List[str]:
        return [
            r"\bcov[\s\-]*19\b",
            r"\bcovid[\s\-]*19\b",
            r"\bcovid\b",
            r"\bcorona\b",
            r"\bcorona[\s\-]*virus\b",
            r"\bcoronavirus\b",
            r"\bsars[\s\-]*cov[\s\-]*2\b",
            r"\brt[\s\-]*pcr\b",
            r"\blong[\s\-]*covid\b",
            r"\bpost[\s\-]*covid\b",
        ]

    def _build_retriever(self) -> Tuple[TfidfVectorizer, object]:
        corpus = []
        for item in self.faq_data:
            combined = f"{item['question']} {item['answer']} {item['category']}"
            corpus.append(preprocess_text(combined))

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            min_df=1
        )
        faq_matrix = vectorizer.fit_transform(corpus)
        return vectorizer, faq_matrix

    def reset_history(self):
        self.chat_history = []

    def preprocess(self, text: str) -> str:
        return preprocess_text(text)

    def _normalize_for_detection(self, text: str) -> str:
        text = self.preprocess(text)

        replacements = {
            "cov 19": "covid 19",
            "cov-19": "covid-19",
            "cov19": "covid19",
            "corona virus": "coronavirus",
            "post covid": "postcovid",
            "long covid": "longcovid",
            "rt pcr": "rtpcr",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _similar_words(self, a: str, b: str, threshold: float = 0.78) -> bool:
        return SequenceMatcher(None, a, b).ratio() >= threshold

    def _has_fuzzy_covid_match(self, tokens: set) -> bool:
        core_terms = [
            "covid", "covid19", "corona", "coronavirus",
            "omicron", "delta", "rtpcr", "antigen",
            "quarantine", "isolation", "vaccination", "booster"
        ]

        for token in tokens:
            if len(token) < 4:
                continue
            for term in core_terms:
                if self._similar_words(token, term):
                    return True
        return False

    def detect_intent(self, user_input: str) -> str:
        text = self._normalize_for_detection(user_input)

        best_intent = "general"
        best_score = 0

        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent

    def is_covid_related(self, user_input: str) -> bool:
        normalized_text = self._normalize_for_detection(user_input)
        tokens = set(tokenize_text(normalized_text))

        if any(keyword in normalized_text for keyword in self.covid_keywords):
            return True

        if any(re.search(pattern, normalized_text) for pattern in self.covid_patterns):
            return True

        if self._has_fuzzy_covid_match(tokens):
            return True

        symptom_words = {
            "fever", "cough", "cold", "breath", "breathing",
            "oxygen", "taste", "smell", "fatigue", "headache",
            "throat", "viral", "infection", "bodyache", "chest"
        }

        testing_words = {
            "test", "testing", "positive", "negative",
            "rtpcr", "antigen", "report", "swab"
        }

        prevention_words = {
            "mask", "sanitize", "sanitizer", "distance",
            "quarantine", "isolation", "spread", "prevent",
            "prevention", "protection", "contagious", "exposure"
        }

        vaccine_words = {
            "vaccine", "vaccination", "booster",
            "dose", "immunity"
        }

        treatment_words = {
            "doctor", "hospital", "medicine",
            "recovery", "recover", "care", "oxygen"
        }

        if len(tokens.intersection(symptom_words)) >= 2:
            return True

        if len(tokens.intersection(testing_words)) >= 1 and len(tokens.intersection(symptom_words)) >= 1:
            return True

        if len(tokens.intersection(prevention_words)) >= 2:
            return True

        if len(tokens.intersection(vaccine_words)) >= 1:
            return True

        if len(tokens.intersection(treatment_words)) >= 2 and (
            len(tokens.intersection(symptom_words)) >= 1 or
            len(tokens.intersection(testing_words)) >= 1
        ):
            return True

        faq_results = self.retrieve_relevant_faqs(user_input, top_k=3)
        if faq_results and faq_results[0].score >= 0.12:
            return True

        return False

    def retrieve_relevant_faqs(self, user_input: str, top_k: int = 5) -> List[RetrievalResult]:
        cleaned_query = self._normalize_for_detection(user_input)
        query_vector = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vector, self.faq_matrix).flatten()
        ranked_indices = similarities.argsort()[::-1][:top_k]

        results: List[RetrievalResult] = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            item = self.faq_data[idx]
            results.append(
                RetrievalResult(
                    question=item["question"],
                    answer=item["answer"],
                    category=item.get("category", "general"),
                    score=score,
                )
            )
        return results

    def _format_context_for_prompt(self, results: List[RetrievalResult]) -> str:
        lines = []
        for i, item in enumerate(results, start=1):
            lines.append(
                f"FAQ {i}\n"
                f"Category: {item.category}\n"
                f"Question: {item.question}\n"
                f"Answer: {item.answer}\n"
                f"Similarity Score: {item.score:.3f}"
            )
        return "\n\n".join(lines)

    def _format_chat_history(self, max_turns: int = 6) -> str:
        if not self.chat_history:
            return "No previous conversation."

        recent_turns = self.chat_history[-max_turns:]
        lines = []
        for turn in recent_turns:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Assistant: {turn['assistant']}")
        return "\n".join(lines)

    def build_prompt(self, user_input: str) -> str:
        intent = self.detect_intent(user_input)
        faq_results = self.retrieve_relevant_faqs(user_input, top_k=5)
        faq_context = self._format_context_for_prompt(faq_results)
        history_context = self._format_chat_history()

        return f"""
You are an advanced AI-based COVID-19 Information Chatbot.

Your task is to answer ONLY COVID-19 related questions in a natural, proper, human-readable way.

Rules:
1. Understand wording variations like cov-19, covid19, corona, coronavirus, post-covid, long covid, and informal user phrasing.
2. Use the FAQ context only for support and grounding. Do not mention FAQ in your answer.
3. Do not say "Here is the FAQ backup answer" or anything similar.
4. Give a direct answer first.
5. Then provide a **Key Points** section with 4 to 6 bullet points.
6. Add **When to seek help** only if medically relevant.
7. Use simple, clear, beginner-friendly language.
8. If the question is not related to COVID-19, politely refuse.
9. End with: This is general educational information, not a medical diagnosis.

Detected intent: {intent}

Recent conversation:
{history_context}

Supporting context:
{faq_context}

User question:
{user_input}
""".strip()

    def _ask_gemini(self, prompt: str) -> str:
        retries = 1
        delay = 2

        for attempt in range(retries):
            try:
                print("📡 Sending request to Gemini API...")

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )

                print("✅ API RESPONSE RECEIVED")

                text = getattr(response, "text", "")
                if not text:
                    return ""

                return text.strip()

            except Exception as e:
                error_text = str(e)
                print("❌ API ERROR:", error_text)

                if "503" in error_text or "UNAVAILABLE" in error_text:
                    if attempt < retries - 1:
                        print(f"⏳ Retrying in {delay} seconds...")
                        time.sleep(delay)
                        delay *= 2
                        continue
                    raise Exception("503 UNAVAILABLE: Gemini server is busy right now. Please try again later.")

                if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                    raise Exception("429 RESOURCE_EXHAUSTED: API quota or rate limit reached. Please try again later.")

                raise Exception(error_text)

        return ""

    def get_response(self, user_input: str) -> str:
        user_input = (user_input or "").strip()

        if not user_input:
            return "Please type a COVID-19 related question."

        if not self.is_covid_related(user_input):
            return (
                "I am mainly designed for COVID-19 related questions. "
                "You can ask me about corona symptoms, testing, spread, vaccine, prevention, isolation, or recovery."
            )

        prompt = self.build_prompt(user_input)

        try:
            response_text = self._ask_gemini(prompt)

            if not response_text or len(response_text.strip()) < 20:
                return (
                    "I understood your question as COVID-19 related, but I could not generate a proper answer from Gemini right now. "
                    "Please try again in a moment."
                )

        except Exception as e:
            error_text = str(e)

            if "503" in error_text or "UNAVAILABLE" in error_text:
                return (
                    "I understood your question as COVID-19 related, but Gemini API is busy right now due to high demand. "
                    "Please try again after a few seconds."
                )

            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                return (
                    "I understood your question as COVID-19 related, but the Gemini API usage limit has been reached right now. "
                    "Please try again later."
                )

            return (
                "I understood your question as COVID-19 related, but Gemini API is not responding properly right now. "
                f"Error: {error_text}"
            )

        self.chat_history.append({
            "user": user_input,
            "assistant": response_text
        })

        return response_text