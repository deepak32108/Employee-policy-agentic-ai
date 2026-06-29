import json
import os
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


def _read_json(path, default):
    if not os.path.exists(path):
        return default

    with open(
            path,
            "r",
            encoding="utf-8"
    ) as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return default


def _date_from_timestamp(timestamp: str):
    if not timestamp:
        return "Unknown"

    try:
        return datetime.fromisoformat(
            timestamp
        ).date().isoformat()
    except ValueError:
        return timestamp[:10]


def _normalize_rating(rating):
    if isinstance(
            rating,
            int
    ):
        return rating

    if rating == "GOOD":
        return 5

    if rating == "BAD":
        return 1

    return None


@router.get("/analytics")
def analytics():
    analytics_data = _read_json(
        "analytics.json",
        {}
    )

    monitoring_data = _read_json(
        "monitoring.json",
        []
    )

    feedback_data = _read_json(
        "feedback.json",
        []
    )

    user_activity = _read_json(
        "user_activity.json",
        []
    )

    users = {
        item.get("user_id")
        for item in user_activity
        if item.get("user_id")
    }

    users.update(
        {
            item.get("user_id")
            for item in feedback_data
            if item.get("user_id")
        }
    )

    ratings = [
        rating
        for rating in (
            _normalize_rating(
                item.get("rating")
            )
            for item in feedback_data
        )
        if rating is not None
    ]

    rating_distribution = {
        str(star): ratings.count(star)
        for star in range(1, 6)
    }

    average_rating = 0

    if ratings:
        average_rating = round(
            sum(ratings) / len(ratings),
            2
        )

    trend_map = defaultdict(
        lambda: {
            "users": set(),
            "questions": 0,
            "ratings": [],
            "feedback": 0
        }
    )

    for item in user_activity:
        date_key = _date_from_timestamp(
            item.get("timestamp", "")
        )

        trend_map[date_key]["questions"] += 1

        if item.get("user_id"):
            trend_map[date_key]["users"].add(
                item["user_id"]
            )

    for item in feedback_data:
        date_key = _date_from_timestamp(
            item.get("timestamp", "")
        )

        rating = _normalize_rating(
            item.get("rating")
        )

        if rating is not None:
            trend_map[date_key]["ratings"].append(
                rating
            )

            trend_map[date_key]["feedback"] += 1

        if item.get("user_id"):
            trend_map[date_key]["users"].add(
                item["user_id"]
            )

    trend_labels = sorted(
        trend_map.keys()
    )

    trends = {
        "labels": trend_labels,
        "users": [
            len(
                trend_map[label]["users"]
            )
            for label in trend_labels
        ],
        "questions": [
            trend_map[label]["questions"]
            for label in trend_labels
        ],
        "average_rating": [
            round(
                sum(trend_map[label]["ratings"]) /
                len(trend_map[label]["ratings"]),
                2
            )
            if trend_map[label]["ratings"]
            else 0
            for label in trend_labels
        ],
        "feedback": [
            trend_map[label]["feedback"]
            for label in trend_labels
        ]
    }

    total_questions = len(
        user_activity
    )

    if total_questions == 0:
        total_questions = analytics_data.get(
            "total_questions",
            len(monitoring_data)
        )

    return {
        "total_users": len(users),
        "total_questions": total_questions,
        "policy_questions": analytics_data.get(
            "policy_questions",
            0
        ),
        "web_questions": analytics_data.get(
            "web_questions",
            0
        ),
        "knowledge_gaps": analytics_data.get(
            "knowledge_gaps",
            0
        ),
        "average_confidence": analytics_data.get(
            "average_confidence",
            0
        ),
        "total_feedback": len(ratings),
        "average_rating": average_rating,
        "rating_distribution": rating_distribution,
        "trends": trends
    }
