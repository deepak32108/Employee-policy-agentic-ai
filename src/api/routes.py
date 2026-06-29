from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
import json
from datetime import datetime

from src.graph.workflow import graph
from src.utils.search import search_web
from src.agents.monitoring_agent import log_interaction

from src.api.analytics_routes import router as analytics_router
from src.api.monitoring_routes import router as monitoring_router
from src.api.feedback_routes import router as feedback_router

app = FastAPI(
    title="Employee Policy Agentic AI"
)

# -------------------------------
# CORS
# -------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Include Routers
# -------------------------------

app.include_router(
    analytics_router
)

app.include_router(
    monitoring_router
)

app.include_router(
    feedback_router
)

# -------------------------------
# Frontend
# -------------------------------

app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)


@app.get("/")
def home():

    return RedirectResponse(
        url="/frontend/index.html"
    )


# -------------------------------
# Request Model
# -------------------------------

class QuestionRequest(BaseModel):

    question: str

    search_web: bool = False

    user_id: str = ""


def record_user_activity(
        user_id: str,
        question: str,
        search_web: bool = False,
        route: str = ""
):
    activity_file = "user_activity.json"
    data = []

    if os.path.exists(
            activity_file
    ):
        with open(
                activity_file,
                "r",
                encoding="utf-8"
        ) as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []

    data.append(
        {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "question": question,
            "search_web": search_web,
            "route": route
        }
    )

    with open(
            activity_file,
            "w",
            encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4
        )


# -------------------------------
# Chat Endpoint
# -------------------------------

@app.post("/ask")
def ask_question(
        request: QuestionRequest
):

    result = graph.invoke(
        {
            "question": request.question,
            "search_web": request.search_web
        }
    )

    if not request.search_web:
        record_user_activity(
            request.user_id,
            request.question,
            request.search_web,
            result.get("route", "")
        )

    if result["route"] == "OUTSIDE_POLICY" and not request.search_web:
        log_interaction(
            request.question,
            "OUTSIDE_POLICY",
            0,
            "CONFIRM_WEB",
            request.user_id
        )

        return {

            "route": "OUTSIDE_POLICY",

            "answer":
                "This question is outside company policies. Would you like me to search the web?",

            "requires_confirmation": True
        }

    return result
# -------------------------------
# Health Check
# -------------------------------

@app.get("/health")
def health():

    return {
        "status": "running"
    }


@app.get("/debug/web-search")
def debug_web_search():

    result = search_web(
        "who is google ceo",
        max_results=1
    )

    return {
        "tavily_key_configured": bool(
            os.getenv("TAVILY_API_KEY")
        ),
        "success": result["success"],
        "provider": result["provider"],
        "results_count": len(
            result["results"]
        ),
        "error": result["error"][:300]
    }
