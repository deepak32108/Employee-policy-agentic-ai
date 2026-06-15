from fastapi import APIRouter

from src.agents.monitoring_agent import (
    get_monitoring_data
)

router = APIRouter()


@router.get("/monitoring")
def monitoring():

    return get_monitoring_data()