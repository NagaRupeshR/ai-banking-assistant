from .rag import get_retriever
from .rag_api import api_web_rag
from .llm import generate_analysis

"""
Returns:
{
    "filtered_context": "...",
    "sources": [
        {
            "content": "Relevant extracted text chunk 1",
            "source": "faiss"
        },
        {
            "content": "Relevant extracted text chunk 2",
            "source": "https://example.com/page"
        }
    ]
}
"""



def filtered_rag_content(text):

    retriever=get_retriever()
    # 1. Retrieve FAISS documents (trusted RBI content)
    docs = retriever.search(text, k=3)

    faiss_docs = []
    for doc in docs:
        faiss_docs.append({
            "source": "faiss",
            "content": doc
        })

    # 2. Retrieve API documents (web content)
    api_results = api_web_rag(text)

    api_docs = []
    for r in api_results[:3]:
        api_docs.append({
            "source": r.get("url", ""),
            "content": r.get("content", ""),
            "title": r.get("title", "")
        })

    print("\n rag_api:",api_results)
    # 3. Build numbered context for LLM
    numbered_context = []

    all_docs = []

    # FAISS docs
    for item in faiss_docs:
        all_docs.append({
            "source": "faiss",
            "content": item["content"]
        })

    # API docs
    for item in api_docs:
        all_docs.append({
            "source": item["source"],
            "content": item["content"]
        })

    for idx, item in enumerate(all_docs, start=1):
        numbered_context.append(
            f"""
            DOCUMENT {idx}
            SOURCE: {item['source']}
            CONTENT:
            {item['content']}
            """
        )

    combined_context = "\n\n".join(numbered_context)

    # 4. Prompt
    prompt = prompt = f"""
You are an expert context filtering system for Indian banking complaints.

Your task is to extract ONLY the minimal document fragments that are directly and explicitly useful for resolving the complaint.

USER COMPLAINT:
{text}

RETRIEVED DOCUMENTS:
{combined_context}

STRICT FILTERING RULES:
1. Extract ONLY information that directly helps answer, resolve, verify, or investigate the complaint.
2. DO NOT include background information, introductions, summaries, generic banking explanations, policy overviews, disclaimers, examples, advertisements, navigation text, greetings, or unrelated legal text.
3. DO NOT include partially relevant content.
4. DO NOT infer, assume, summarize, reinterpret, or generate new information.
5. DO NOT merge multiple sections unless all parts are directly relevant.
6. DO NOT include duplicate or near-duplicate content.
7. DO NOT include content that is merely topically related.
8. Include content ONLY if it directly answers:
   - what happened,
   - why it happened,
   - applicable banking rule/process,
   - required action,
   - escalation path,
   - timelines,
   - charges/fees,
   - refund/reversal conditions,
   - RBI/bank compliance obligations,
   - transaction failure handling,
   - KYC/account/block/fraud procedures,
   - complaint resolution process.
9. If relevance is uncertain, EXCLUDE the content.
10. Prefer shorter precise excerpts over long passages.
11. Preserve the original wording exactly as it appears in the source.
12. Never fabricate or hallucinate missing details.
13. Output must contain ONLY evidence grounded in the retrieved documents.
14. If no directly useful evidence exists, return an empty sources list.

SOURCE RULES:
1. Preserve the exact source for every extracted part.
2. If the source is from FAISS, set source as "faiss".
3. If the source is from API, set source as the exact URL.

OUTPUT RULES:
1. Return ONLY valid JSON.
2. Do not include markdown.
3. Do not include explanations.
4. Do not include reasoning.
5. Do not include notes or comments.
6. The JSON must strictly follow the schema below.

JSON FORMAT:
{{
  "sources": [
    {{
      "content": "Relevant extracted text.",
      "source": "faiss"
    }},
    {{
      "content": "Relevant extracted text.",
      "source": "https://example.com/page"
    }}
  ]
}}

If nothing relevant is found:
{{
  "sources": []
}}
"""

    # 5. LLM Call
    result = generate_analysis(prompt)

    if not isinstance(result, dict):
        result = {"sources": []}

    sources = result.get("sources", [])

    # 6. Normalize Output
    normalized_sources = []

    for item in sources:
        if not isinstance(item, dict):
            continue

        content = str(item.get("content", "")).strip()
        source = str(item.get("source", "")).strip()

        if not content:
            continue

        if not source:
            source = "faiss"

        normalized_sources.append({
            "content": content,
            "source": source
        })

    # 7. Fallback
    if not normalized_sources and docs:
        normalized_sources = [
            {
                "content": docs[0],
                "source": "faiss"
            }
        ]

    # Combined filtered text
    filtered_context = "\n\n".join(
        item["content"] for item in normalized_sources
    )

    # 8. Final Return
    return {
        "filtered_context": filtered_context,
        "sources": normalized_sources
    }