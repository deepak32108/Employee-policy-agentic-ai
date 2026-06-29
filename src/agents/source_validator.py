import re


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "is",
    "of",
    "or",
    "the",
    "to"
}


def _tokens(text):
    return {
        token
        for token in re.findall(
            r"[a-z0-9]+",
            text.lower()
        )
        if token not in STOP_WORDS
    }


def _snippet(text, max_length=180):
    cleaned = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[:max_length].rsplit(" ", 1)[0] + "..."


def generate_citations(documents, answer=""):

    citations = []
    answer_tokens = _tokens(answer)
    seen_sources = set()

    for index, doc in enumerate(documents, start=1):
        document_tokens = _tokens(
            doc.page_content
        )

        overlap = answer_tokens.intersection(
            document_tokens
        )

        if answer_tokens:
            overlap_ratio = len(overlap) / len(answer_tokens)

            if (
                    len(overlap) < 2
                    or overlap_ratio < 0.2
            ):
                continue

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        source_key = (
            source,
            page
        )

        if source_key in seen_sources:
            continue

        seen_sources.add(
            source_key
        )

        citations.append(
            {
                "id": len(citations) + 1,
                "source": source,
                "page": page,
                "snippet": _snippet(
                    doc.page_content
                )
            }
        )

    if not citations and documents:
        doc = documents[0]
        citations.append(
            {
                "id": 1,
                "source": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "snippet": _snippet(doc.page_content)
            }
        )

    return citations


if __name__ == "__main__":

    class MockDoc:

        def __init__(self):

            self.metadata = {
                "source": "leave_policy.pdf",
                "page": 0
            }

    docs = [MockDoc()]

    print(
        generate_citations(docs)
    )
