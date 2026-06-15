import json
import os

from fastapi import APIRouter

router = APIRouter()


@router.get("/analytics")
def analytics():

    if not os.path.exists(
            "analytics.json"
    ):

        return {}

    with open(
            "analytics.json",
            "r"
    ) as f:

        return json.load(f)