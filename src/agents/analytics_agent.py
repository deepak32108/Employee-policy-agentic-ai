import json
import os


ANALYTICS_FILE = "analytics.json"


def update_analytics(
        route,
        confidence,
        knowledge_gap
):

    if not os.path.exists(
            ANALYTICS_FILE
    ):

        analytics = {

            "total_questions": 0,

            "policy_questions": 0,

            "web_questions": 0,

            "knowledge_gaps": 0,

            "average_confidence": 0
        }

    else:

        with open(
                ANALYTICS_FILE,
                "r"
        ) as f:

            analytics = json.load(f)

    analytics["total_questions"] += 1

    if route == "POLICY":

        analytics[
            "policy_questions"
        ] += 1

    else:

        analytics[
            "web_questions"
        ] += 1

    if knowledge_gap:

        analytics[
            "knowledge_gaps"
        ] += 1

    old_avg = analytics[
        "average_confidence"
    ]

    total = analytics[
        "total_questions"
    ]

    analytics[
        "average_confidence"
    ] = (

        (old_avg * (total - 1))

        + confidence

    ) / total

    with open(
            ANALYTICS_FILE,
            "w"
    ) as f:

        json.dump(
            analytics,
            f,
            indent=4
        )


if __name__ == "__main__":

    update_analytics(
        "POLICY",
        90,
        False
    )