from ddgs import DDGS


def search_web(query: str, max_results: int = 5):

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    return [
        {
            "title": r.get("title", ""),
            "body": r.get("body", ""),
            "link": r.get("href", "")
        }
        for r in results
    ]