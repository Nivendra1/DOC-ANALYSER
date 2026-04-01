import os
import json
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def analyse_document(text: str) -> dict:
    # Truncate to avoid token limits but keep enough for good analysis
    truncated = text[:6000] if len(text) > 6000 else text

    prompt = f"""You are an expert document analyst. Analyse the following document text and return a JSON response only — no explanation, no markdown, no extra text.

Document Text:
\"\"\"{truncated}\"\"\"

Return this exact JSON structure:
{{
  "document_type": "one of: Invoice, Resume, Contract, Report, Article, Letter, Form, Research Paper, Email, Other",
  "summary": "A concise 2-4 sentence summary of the document content",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "entities": {{
    "names": ["list of person names found"],
    "organizations": ["list of organization/company names found"],
    "locations": ["list of locations/places found"],
    "dates": ["list of dates found"],
    "monetary_amounts": ["list of monetary values found"],
    "other": ["any other important entities"]
  }},
  "sentiment": "positive or negative or neutral",
  "sentiment_confidence": 0.0
}}

Rules:
- sentiment_confidence must be a float between 0.0 and 1.0
- If no entities found in a category, return empty array []
- keywords must be exactly 5 most relevant terms
- Be accurate and specific, never fabricate information not in the text
- Return ONLY valid JSON, nothing else"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up if model wraps in markdown
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        result = fallback_response()

    # Validate and sanitize
    result = sanitize_result(result)
    return result


def sanitize_result(result: dict) -> dict:
    valid_sentiments = {"positive", "negative", "neutral"}
    valid_doc_types = {
        "Invoice", "Resume", "Contract", "Report", "Article",
        "Letter", "Form", "Research Paper", "Email", "Other"
    }

    if result.get("sentiment") not in valid_sentiments:
        result["sentiment"] = "neutral"

    if result.get("document_type") not in valid_doc_types:
        result["document_type"] = "Other"

    conf = result.get("sentiment_confidence", 0.75)
    try:
        conf = float(conf)
        conf = max(0.0, min(1.0, conf))
    except (ValueError, TypeError):
        conf = 0.75
    result["sentiment_confidence"] = conf

    if not isinstance(result.get("keywords"), list):
        result["keywords"] = []

    entities = result.get("entities", {})
    for key in ["names", "organizations", "locations", "dates", "monetary_amounts", "other"]:
        if not isinstance(entities.get(key), list):
            entities[key] = []
    result["entities"] = entities

    if not result.get("summary"):
        result["summary"] = "Summary could not be generated."

    return result


def fallback_response() -> dict:
    return {
        "document_type": "Other",
        "summary": "Document was processed but detailed analysis could not be completed.",
        "keywords": [],
        "entities": {
            "names": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "monetary_amounts": [],
            "other": []
        },
        "sentiment": "neutral",
        "sentiment_confidence": 0.5
    }
