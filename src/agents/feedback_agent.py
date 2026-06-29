import json
import os
from datetime import datetime

FEEDBACK_FILE = "feedback.json"


def save_feedback(
        question: str,
        answer: str,
        rating,
        comment: str = "",
        user_id: str = "",
        answer_id: str = ""
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
            rating,

        "comment":
            comment,

        "user_id":
            user_id,

        "answer_id":
            answer_id
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

    ratings = []

    for item in data:
        rating = item.get(
            "rating"
        )

        if isinstance(
                rating,
                int
        ):
            ratings.append(
                rating
            )

        elif rating == "GOOD":
            ratings.append(
                5
            )

        elif rating == "BAD":
            ratings.append(
                1
            )

    total = len(
        ratings
    )

    distribution = {
        str(star): ratings.count(star)
        for star in range(1, 6)
    }

    average_rating = 0

    if total > 0:
        average_rating = round(
            sum(ratings) / total,
            2
        )

    return {

        "total":
            total,

        "average_rating":
            average_rating,

        "rating_distribution":
            distribution
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
