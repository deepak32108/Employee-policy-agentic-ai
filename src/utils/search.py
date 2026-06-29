import os

import requests
from duckduckgo_search import DDGS


def _search_tavily(query: str, max_results: int):
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return None

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results
        },
        timeout=15
    )

    response.raise_for_status()
    payload = response.json()

    return [
        {
            "title": item.get("title", ""),
            "body": item.get("content", ""),
            "link": item.get("url", "")
        }
        for item in payload.get("results", [])
    ]


def _search_duckduckgo(query: str, max_results: int):
    with DDGS() as ddgs:
        results = list(
            ddgs.text(
                query,
                max_results=max_results
            )
        )

    return [
        {
            "title": r.get("title", ""),
            "body": r.get("body", ""),
            "link": r.get("href", "")
        }
        for r in results
    ]


def search_web(query: str, max_results: int = 5):
    errors = []

    try:
        results = _search_tavily(
            query,
            max_results
        )

        if results is not None:
            return {
                "success": True,
                "provider": "tavily",
                "error": "",
                "results": results
            }

    except Exception as exc:
        errors.append(
            f"Tavily: {exc}"
        )

    try:
        results = _search_duckduckgo(
            query,
            max_results
        )

        return {
            "success": True,
            "provider": "duckduckgo",
            "error": "",
            "results": results
        }

    except Exception as exc:
        errors.append(
            f"DuckDuckGo: {exc}"
        )

    return {
        "success": False,
        "provider": "",
        "error": " | ".join(
            errors
        ),
        "results": []
    }
