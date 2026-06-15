from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.graph.workflow import graph

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

    return FileResponse(
        "frontend/index.html"
    )


# -------------------------------
# Request Model
# -------------------------------

class QuestionRequest(BaseModel):

    question: str

    search_web: bool = False


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

    if result["route"] == "OUTSIDE_POLICY" and not request.search_web:

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