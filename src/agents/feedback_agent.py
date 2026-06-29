import json
import os
import re
from collections import Counter
from datetime import datetime

FEEDBACK_FILE = "feedback.json"


def _summarize_comments(data):
    topic_patterns = {
        "lengthy answer": r"\b(lengthy|long|too much|verbose|short|brief|concise)\b",
        "slow process": r"\b(slow|delay|late|loading|wait|waiting|time)\b",
        "incorrect answer": r"\b(wrong|incorrect|not correct|bad answer|inaccurate)\b",
        "missing details": r"\b(missing|incomplete|not enough|more detail)\b",
        "source issue": r"\b(source|citation|pdf|page)\b"
    }

    topics = Counter()
    recent_comments = []

    for item in data:
        comment = str(
            item.get("comment", "")
        ).strip()

        if not comment:
            continue

        recent_comments.append(
            {
                "timestamp": item.get("timestamp", ""),
                "rating": item.get("rating"),
                "comment": comment
            }
        )

        lowered = comment.lower()

        for label, pattern in topic_patterns.items():
            if re.search(pattern, lowered):
                topics[label] += 1

    if not topics:
        topics["no written feedback yet"] = 0

    return {
        "topics": [
            {
                "label": label,
                "count": count
            }
            for label, count in topics.most_common()
        ],
        "recent_comments": recent_comments[-10:][::-1]
    }


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
            distribution,

        "feedback_summary":
            _summarize_comments(data)
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
