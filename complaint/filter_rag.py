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
    prompt = f"""
You are an expert context filtering system for Indian banking complaints.

Your task is to extract ONLY the parts of the retrieved documents
that are directly useful for resolving the complaint.

USER COMPLAINT:
{text}

RETRIEVED DOCUMENTS:
{combined_context}

INSTRUCTIONS:
1. Review all documents.
2. Extract only the useful parts.
3. Ignore irrelevant, duplicate, or generic information.
4. For each extracted part, preserve the exact source.
5. If the source is from FAISS, set source as "faiss".
6. If the source is from API, set source as the exact URL.
7. Do not explain your reasoning.

Return ONLY valid JSON.

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