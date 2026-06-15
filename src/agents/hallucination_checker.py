def check_hallucination(
        question: str,
        answer: str,
        context: str
):

    if not context.strip():

        return {
            "verdict": "NOT_SUPPORTED",
            "confidence": 0
        }

    answer_words = set(
        answer.lower().split()
    )

    context_words = set(
        context.lower().split()
    )

    overlap = len(
        answer_words.intersection(
            context_words
        )
    )

    confidence = min(
        100,
        max(
            50,
            overlap * 2
        )
    )

    verdict = (
        "SUPPORTED"
        if confidence >= 60
        else "NOT_SUPPORTED"
    )

    return {
        "verdict": verdict,
        "confidence": confidence
    }