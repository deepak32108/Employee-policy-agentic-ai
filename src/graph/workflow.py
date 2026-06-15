from typing import TypedDict

from langgraph.graph import StateGraph, END

from src.agents.router_agent import route_question
from src.agents.policy_agent import answer_policy_question
from src.agents.web_agent import answer_web_question


class AgentState(TypedDict):
    question: str
    route: str
    answer: str
    confidence: int
    verdict: str
    citations: list
    search_web: bool
    needs_web_confirmation: bool
# -----------------------------------

# Router Node

# -----------------------------------

def router_node(state):

 route = route_question(
    state["question"]
  )

 return {
    "route": route
  }


# -----------------------------------

# Policy Node

# -----------------------------------

def policy_node(state):

 result = answer_policy_question(
    state["question"]
  )

 return {
    "answer": result["answer"],
    "confidence": result["confidence"],
    "verdict": result["verdict"],
    "citations": result["citations"],
    "needs_web_confirmation": False
  }


# -----------------------------------

# Confirmation Node

# -----------------------------------

def confirmation_node(state):

 return {
    "answer": "This question appears to be outside company policies. Would you like me to search the web?",
    "confidence": 0,
    "verdict": "CONFIRM_WEB",
    "citations": [],
    "needs_web_confirmation": True
  }


# -----------------------------------

# Web Node

# -----------------------------------

def web_node(state):

 result = answer_web_question(
    state["question"]
  )

 return {
    "answer": result["answer"],
    "confidence": 100,
    "verdict": "WEB",
    "citations": [],
    "needs_web_confirmation": False
  }
# -----------------------------------

# Route Decision

# -----------------------------------

def decide_route(state):

 if state["route"] == "POLICY":
    return "policy"

 if state.get("search_web", False):
    return "web"

 return "confirm"


# -----------------------------------

# Build Graph

# -----------------------------------

builder = StateGraph(
AgentState
)

builder.add_node(
"router",
router_node
)

builder.add_node(
"policy",
policy_node
)

builder.add_node(
"confirm",
confirmation_node
)

builder.add_node(
"web",
web_node
)

builder.set_entry_point(
"router"
)

builder.add_conditional_edges(
"router",
decide_route,
{
"policy": "policy",
"confirm": "confirm",
"web": "web"
}
)

builder.add_edge(
"policy",
END
)

builder.add_edge(
"confirm",
END
)

builder.add_edge(
"web",
END
)

graph = builder.compile()

# -----------------------------------

# Testing
if __name__ == "__main__":
 while True:

    question = input(
        "\nAsk Question (q to quit): "
    )

    if question.lower() == "q":
        break

    result = graph.invoke(
        {
            "question": question,
            "search_web": False
        }
    )

    print("\nAnswer:\n")

    print(
        result["answer"]
    )

    print(
        "\nConfidence:",
        result["confidence"]
    )

    print(
        "Verdict:",
        result["verdict"]
    )