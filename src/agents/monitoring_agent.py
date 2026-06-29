import json
import os
from datetime import datetime

MONITOR_FILE = "monitoring.json"
USER_ACTIVITY_FILE = "user_activity.json"


def log_interaction(
        question,
        route,
        confidence,
        verdict,
        user_id=""
):

    data = []

    if os.path.exists(
            MONITOR_FILE
    ):

        with open(
                MONITOR_FILE,
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

        "route":
            route,

        "confidence":
            confidence,

        "verdict":
            verdict,

        "user_id":
            user_id
    })

    with open(
            MONITOR_FILE,
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def log_user_activity(
        user_id,
        question,
        search_web=False
):

    data = []

    if os.path.exists(
            USER_ACTIVITY_FILE
    ):

        with open(
                USER_ACTIVITY_FILE,
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

        "user_id":
            user_id,

        "question":
            question,

        "search_web":
            search_web
    })

    with open(
            USER_ACTIVITY_FILE,
            "w",
            encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def get_monitoring_data():

    if not os.path.exists(
            MONITOR_FILE
    ):

        return []

    with open(
            MONITOR_FILE,
            "r",
            encoding="utf-8"
    ) as f:

        return json.load(f)
