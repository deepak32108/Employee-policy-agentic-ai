import json
import os
from datetime import datetime

FEEDBACK_FILE = "feedback.json"


def save_feedback(
        question: str,
        answer: str,
        rating: str
):

    data = []

    if os.path.exists(
            FEEDBACK_FILE
    ):

        with open(
                FEEDBACK_FILE,
                "r",
                encoding="utf-8"
        ) as f:

            try:
                data = json.load(f)

            except:
                data = []

    data.append({

        "timestamp":
            str(
                datetime.now()
            ),

        "question":
            question,

        "answer":
            answer,

        "rating":
            rating
    })

    with open(
            FEEDBACK_FILE,
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )

    return {
        "status":
            "saved"
    }


def get_feedback_stats():

    if not os.path.exists(
            FEEDBACK_FILE
    ):

        return {

            "good": 0,

            "bad": 0,

            "total": 0,

            "satisfaction_score": 0
        }

    with open(
            FEEDBACK_FILE,
            "r",
            encoding="utf-8"
    ) as f:

        data = json.load(f)

    good = len([
        x for x in data
        if x["rating"] == "GOOD"
    ])

    bad = len([
        x for x in data
        if x["rating"] == "BAD"
    ])

    total = good + bad

    score = 0

    if total > 0:

        score = round(
            (good / total) * 100,
            2
        )

    return {

        "good":
            good,

        "bad":
            bad,

        "total":
            total,

        "satisfaction_score":
            score
    }


if __name__ == "__main__":

    save_feedback(
        "How many casual leaves?",
        "6 Days",
        "GOOD"
    )

    print(
        get_feedback_stats()
    )