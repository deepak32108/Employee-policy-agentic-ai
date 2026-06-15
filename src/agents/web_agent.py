from src.utils.search import search_web

from src.agents.analytics_agent import (
    update_analytics
)

from src.agents.monitoring_agent import (
    log_interaction
)


def answer_web_question(
        question: str
):

    result = search_web(
        question
    )

    update_analytics(
        "WEB",
        100,
        False
    )

    log_interaction(
        question,
        "WEB",
        100,
        "WEB"
    )

    return {

        "answer":
            str(result)
    }