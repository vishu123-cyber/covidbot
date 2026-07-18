import json
import os
from typing import List, Dict


FAQ_FILENAME = "covid_faq.json"


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_faq_path() -> str:
    return os.path.join(get_project_root(), "data", FAQ_FILENAME)


def load_faq_data() -> List[Dict[str, str]]:
    """Load FAQ records from the JSON file and keep only valid entries."""
    file_path = get_faq_path()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{FAQ_FILENAME} not found at: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("covid_faq.json must contain a list of FAQ objects.")

    cleaned_records: List[Dict[str, str]] = []

    for item in data:
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        category = str(item.get("category", "general")).strip() or "general"

        if question and answer:
            cleaned_records.append(
                {
                    "question": question,
                    "answer": answer,
                    "category": category,
                }
            )

    if not cleaned_records:
        raise ValueError("No valid FAQ question-answer pairs found in covid_faq.json.")

    return cleaned_records