from src.utils.llm import get_llm
from src.utils.search import search_web

from src.agents.analytics_agent import (
    update_analytics
)

from src.agents.monitoring_agent import (
    log_interaction
)


def _format_search_context(results):
    context_parts = []

    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"Source {index}\n"
            f"Title: {result.get('title', '')}\n"
            f"URL: {result.get('link', '')}\n"
            f"Content: {result.get('body', '')}"
        )

    return "\n\n".join(
        context_parts
    )


def _generate_answer_from_search(question: str, results):
    llm = get_llm()

    prompt = f"""
You are a helpful web research assistant.

Answer the user's question using the web search results below.
Keep the answer clear and concise.
If the results do not contain enough information, say so.

Question:
{question}

Web search results:
{_format_search_context(results)}
"""

    response = llm.invoke(prompt)

    return response.content


def _generate_fallback_answer(question: str):
    llm = get_llm()

    prompt = f"""
You are a helpful assistant.

Live web search is currently unavailable. Answer the user's question using
general knowledge. If the question requires current or real-time information,
clearly say that it should be verified with live sources.

Question:
{question}
"""

    response = llm.invoke(prompt)

    return (
        "Live web search is unavailable right now, so this answer is based on "
        "general model knowledge and may need verification for current facts.\n\n"
        f"{response.content}"
    )


def answer_web_question(
        question: str
):

    search_result = search_web(
        question
    )

    if search_result["success"] and search_result["results"]:
        answer = _generate_answer_from_search(
            question,
            search_result["results"]
        )

        citations = [
            {
                "source": result.get("title", "Web source"),
                "link": result.get("link", "")
            }
            for result in search_result["results"]
        ]

        update_analytics(
            "WEB",
            90,
            False
        )

        log_interaction(
            question,
            "WEB",
            90,
            "WEB_SEARCH"
        )

        return {
            "answer": answer,
            "confidence": 90,
            "verdict": f"WEB_SEARCH_{search_result['provider'].upper()}",
            "citations": citations
        }

    answer = _generate_fallback_answer(
        question
    )

    update_analytics(
        "WEB",
        60,
        True
    )

    log_interaction(
        question,
        "WEB",
        60,
        "LLM_FALLBACK"
    )

    return {
        "answer": answer,
        "confidence": 60,
        "verdict": "LLM_FALLBACK",
        "citations": []
    }
