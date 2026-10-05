import re


def _normalize(text: str) -> str:
    """
    Normalize text for comparison.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def check_hallucination(question: str, answer: str, context: str):
    """
    Rule-based hallucination checker.

    Confidence Levels:
    -------------------
    100 -> Answer is almost entirely present in context
    95  -> Strongly supported
    85  -> Mostly supported
    70  -> Partially supported
    50  -> Weak support
    0   -> Unsupported
    """

    if not answer.strip():
        return {
            "confidence": 0,
            "verdict": "NOT_SUPPORTED"
        }

    answer_norm = _normalize(answer)
    context_norm = _normalize(context)

    answer_words = set(answer_norm.split())
    context_words = set(context_norm.split())

    if len(answer_words) == 0:
        return {
            "confidence": 0,
            "verdict": "NOT_SUPPORTED"
        }

    matched_words = answer_words.intersection(context_words)

    overlap = len(matched_words) / len(answer_words)

    if overlap >= 0.90:
        confidence = 100
        verdict = "SUPPORTED"

    elif overlap >= 0.75:
        confidence = 95
        verdict = "SUPPORTED"

    elif overlap >= 0.60:
        confidence = 85
        verdict = "SUPPORTED"

    elif overlap >= 0.40:
        confidence = 70
        verdict = "SUPPORTED"

    elif overlap >= 0.20:
        confidence = 50
        verdict = "PARTIALLY_SUPPORTED"

    else:
        confidence = 0
        verdict = "NOT_SUPPORTED"

    return {
        "confidence": confidence,
        "verdict": verdict
    }