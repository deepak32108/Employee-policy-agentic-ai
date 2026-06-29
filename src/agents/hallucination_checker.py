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

    answer_words = _tokens(
        answer
    )

    context_words = _tokens(
        context
    )

    if not answer_words:
        return {
            "verdict": "NOT_SUPPORTED",
            "confidence": 0
        }

    overlap = len(
        answer_words.intersection(
            context_words
        )
    )

    support_ratio = overlap / len(answer_words)

    confidence = min(
        100,
        max(
            50,
            round(support_ratio * 100)
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
