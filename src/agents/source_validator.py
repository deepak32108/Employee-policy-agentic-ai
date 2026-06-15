def generate_citations(documents):

    citations = []

    for index, doc in enumerate(documents, start=1):

        source = doc.metadata.get(
            "source",
            "Unknown"
        )

        page = doc.metadata.get(
            "page",
            "Unknown"
        )

        citations.append(
            {
                "id": index,
                "source": source,
                "page": page
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