from src.agents.self_correct_agent import (
    improve_answer
)


def should_retry(
        confidence: int,
        threshold: int = 70
):

    return confidence < threshold


def execute_retry(
        question: str,
        answer: str
):

    return improve_answer(
        question,
        answer
    )