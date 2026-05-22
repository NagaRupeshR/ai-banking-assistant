# complaint/analyzer.py

from .classifier import classify_complaint
from .llm import generate_analysis
from .filter_rag import filtered_rag_content

def prettify(text):
    if not isinstance(text, str):
        return text
    return text.replace('_', ' ').strip().title()


def normalize_list(value):
    if isinstance(value, list):
        return [prettify(v) if isinstance(v, str) else v for v in value]
    if isinstance(value, str):
        return [prettify(value)]
    return []


def normalize_timeline(value):
    if isinstance(value, list):
        output = []

        for item in value:
            if isinstance(item, dict):
                date = item.get("date", "Timeline")
                event = prettify(item.get("event", ""))
                output.append(f"{date}: {event}")
            else:
                output.append(prettify(str(item)))

        return output

    return []


def normalize_mermaid(category):
    safe_category = prettify(category)

    return f"""flowchart TD
A[Complaint Submitted] --> B[Category: {safe_category}]
B --> C[Contact Bank or App Support]
C --> D{{Resolved Within 5 Days?}}
D -->|Yes| E[Issue Closed]
D -->|No| F[Escalate to Bank Nodal Officer]
F --> G{{Resolved Within 30 Days?}}
G -->|Yes| E
G -->|No| H[File Complaint on RBI CMS]
H --> I[RBI Ombudsman Review]
I --> J[Final Resolution]
"""

def analyze_complaint(text):

    # 1. Classifier
    category, clf_confidence, top_predictions = classify_complaint(text)
    print(category, clf_confidence, top_predictions)

    # 2. Obtain filtered RAG content
    rag_content = filtered_rag_content(text)

    print("\n rag_content",rag_content)

    # rag_content format:
    # {
    #     "filtered_context": "...",
    #     "sources": [
    #         {
    #             "content": "...",
    #             "source": "faiss"
    #         },
    #         {
    #             "content": "...",
    #             "source": "https://..."
    #         }
    #     ]
    # }

    filtered_context = rag_content.get("filtered_context", "")
    rag_sources = rag_content.get("sources", [])

    # 3. LLM Prompt
    prompt = f"""
You are an expert AI Banking Complaint Resolution Assistant for India.

IMPORTANT RULES:
1. Return ONLY valid JSON.
2. Use plain English, not snake_case.
3. resolution_steps must be a list of short sentences.
4. preventive_advice must be a list of short sentences.
5. timeline must be a list of strings like "Day 0: File complaint with bank".
6. success_probability should be like "92%".
7. confidence_score must be a number between 0 and 1.
8. If a UPI transaction is only a few hours old, advise waiting up to 24 hours before escalation.
9. Do not return dictionaries inside timeline.
10. Keep the answer concise and professional.
11. Use the provided filtered context as the primary evidence.
12. If the filtered context includes web content, treat it as supportive only.

Complaint:
{text}

Classifier Prediction:
{category}

Classifier Confidence:
{clf_confidence}

Top Predictions:
{top_predictions}

Filtered Relevant Context:
{filtered_context}

Return JSON with keys:
category
urgency
priority
eligibility
resolution_steps
estimated_time
success_probability
confidence_score
preventive_advice
timeline
mermaid_code
official_links
similar_cases
"""

    # 4. LLM Call
    result = generate_analysis(prompt)
    print("\n",result)

    if not isinstance(result, dict):
        result = {}

    # 5. Normalize output
    result["category"] = prettify(result.get("category", category))
    result["urgency"] = prettify(result.get("urgency", "High"))
    result["priority"] = prettify(result.get("priority", "Action Required"))

    result["eligibility"] = prettify(
        result.get(
            "eligibility",
            "Eligible if unresolved by the bank after 30 days."
        )
    )

    result["estimated_time"] = result.get(
        "estimated_time",
        "2–5 working days"
    )

    result["success_probability"] = str(
        result.get("success_probability", "90%")
    ).replace("%", "")

    try:
        result["confidence_score"] = float(
            result.get("confidence_score", clf_confidence)
        )
    except Exception:
        result["confidence_score"] = clf_confidence

    result["resolution_steps"] = normalize_list(
        result.get("resolution_steps", [])
    )

    result["preventive_advice"] = normalize_list(
        result.get("preventive_advice", [])
    )

    result["timeline"] = normalize_timeline(
        result.get("timeline", [])
    )

    result["similar_cases"] = normalize_list(
        result.get("similar_cases", [])
    )

    # 6. Mermaid
    result["mermaid_code"] = normalize_mermaid(
        result["category"]
    )

    # 7. Attach explainability metadata
    result["top_predictions"] = top_predictions

    # Replaces old retrieved_chunks + api_sources
    result["rag_context"] = filtered_context
    result["rag_sources"] = rag_sources

    # Optional backward compatibility
    result["retrieved_chunks"] = [
        item["content"]
        for item in rag_sources
        if item.get("source") == "faiss"
    ]

    result["api_sources"] = [
        {
            "url": item["source"],
            "content": item["content"]
        }
        for item in rag_sources
        if item.get("source") != "faiss"
    ]

    # 8. Warning system
    if result["confidence_score"] < 0.6:
        result["warning"] = (
            "This recommendation is uncertain. "
            "Please verify using official RBI sources below."
        )

    return result