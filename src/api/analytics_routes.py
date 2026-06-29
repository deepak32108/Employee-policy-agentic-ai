import json
import os
import re
from collections import defaultdict, Counter
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


def _comment_topics(feedback_data):
    topic_patterns = {
        "lengthy answer": r"\b(lengthy|long|too much|verbose|short|brief|concise)\b",
        "slow process": r"\b(slow|delay|late|loading|wait|waiting|time)\b",
        "incorrect answer": r"\b(wrong|incorrect|not correct|bad answer|inaccurate)\b",
        "missing details": r"\b(missing|incomplete|not enough|more detail)\b",
        "source issue": r"\b(source|citation|pdf|page)\b"
    }

    topics = Counter()
    recent_comments = []

    for item in feedback_data:
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

    answered_routes = [
        item
        for item in monitoring_data
        if item.get("route") in {"POLICY", "WEB", "OUTSIDE_POLICY"}
    ]

    routed_activity = [
        item
        for item in user_activity
        if item.get("route")
    ]

    source_for_counts = (
        answered_routes
        if answered_routes
        else routed_activity
    )

    policy_questions = sum(
        1
        for item in source_for_counts
        if item.get("route") == "POLICY"
    )

    outside_policy_questions = sum(
        1
        for item in source_for_counts
        if item.get("route") != "POLICY"
    )

    total_questions = len(
        source_for_counts
    )

    if total_questions == 0:
        total_questions = analytics_data.get(
            "total_questions",
            0
        )
        policy_questions = analytics_data.get(
            "policy_questions",
            0
        )
        outside_policy_questions = analytics_data.get(
            "web_questions",
            0
        )

    knowledge_gaps = sum(
        1
        for item in monitoring_data
        if item.get("verdict") == "NOT_SUPPORTED"
        or item.get("confidence", 100) < 70
    )

    if not monitoring_data:
        knowledge_gaps = analytics_data.get(
            "knowledge_gaps",
            0
        )

    confidences = [
        item.get("confidence")
        for item in monitoring_data
        if isinstance(item.get("confidence"), (int, float))
    ]

    average_confidence = (
        round(sum(confidences) / len(confidences), 2)
        if confidences
        else analytics_data.get("average_confidence", 0)
    )

    trend_map = defaultdict(
        lambda: {
            "users": set(),
            "questions": 0,
            "ratings": [],
            "feedback": 0
        }
    )

    for item in source_for_counts:
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

    return {
        "total_users": len(users),
        "total_questions": total_questions,
        "policy_questions": policy_questions,
        "outside_policy_questions": outside_policy_questions,
        "web_questions": outside_policy_questions,
        "knowledge_gaps": knowledge_gaps,
        "average_confidence": average_confidence,
        "total_feedback": len(ratings),
        "average_rating": average_rating,
        "rating_distribution": rating_distribution,
        "feedback_summary": _comment_topics(feedback_data),
        "trends": trends
    }
