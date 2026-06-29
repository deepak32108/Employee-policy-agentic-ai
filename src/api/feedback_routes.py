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

    rating: int

    comment: str = ""

    user_id: str = ""

    answer_id: str = ""


@router.post("/feedback")
def feedback(
        request: FeedbackRequest
):

    return save_feedback(

        request.question,

        request.answer,

        request.rating,

        request.comment,

        request.user_id,

        request.answer_id
    )


@router.get("/feedback/stats")
def feedback_stats():

    return get_feedback_stats()
