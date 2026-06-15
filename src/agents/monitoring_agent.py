import json
import os
from datetime import datetime

MONITOR_FILE = "monitoring.json"


def log_interaction(
        question,
        route,
        confidence,
        verdict
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
            verdict
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