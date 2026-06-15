from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.feedback_agent import (
    save_feedback,
    get_feedback_stats
)

router = APIRouter()


class FeedbackRequest(
    BaseModel
):

    question: str

    answer: str

    rating: str


@router.post("/feedback")
def feedback(
        request: FeedbackRequest
):

    return save_feedback(

        request.question,

        request.answer,

        request.rating
    )


@router.get("/feedback/stats")
def feedback_stats():

    return get_feedback_stats()