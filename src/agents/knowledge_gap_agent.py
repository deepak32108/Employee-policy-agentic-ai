def detect_knowledge_gap(
        answer: str,
        confidence: int
):

    answer = answer.lower()

    gap_phrases = [

        "not available",

        "not found",

        "do not have information",

        "cannot find",

        "not mentioned",

        "not provided"
    ]

    for phrase in gap_phrases:

        if phrase in answer:

            return True

    if confidence < 40:

        return True

    return False


if __name__ == "__main__":

    print(
        detect_knowledge_gap(
            "Information not available.",
            20
        )
    )