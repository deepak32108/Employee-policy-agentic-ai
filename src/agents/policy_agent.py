from src.retriever.retriever import retrieve_documents
from src.utils.llm import get_llm
from src.memory.chat_memory import memory

from src.agents.hallucination_checker import (
    check_hallucination
)

from src.agents.source_validator import (
    generate_citations
)

from src.agents.decision_agent import (
    should_retry,
    execute_retry
)

from src.agents.knowledge_gap_agent import (
    detect_knowledge_gap
)

from src.agents.analytics_agent import (
    update_analytics
)

from src.agents.monitoring_agent import (
    log_interaction
)


def answer_policy_question(question: str):

    docs = retrieve_documents(question)
    if not docs:
        return {
            "answer": "I could not find relevant information in the policy documents.",
            "confidence": 0,
            "verdict": "NOT_SUPPORTED",
            "citations": [],
            "knowledge_gap": True
        }
    context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    memory_context = memory.get_context()

    prompt = f"""
You are an HR Policy Assistant.

Conversation History:

{memory_context}

Context:

{context}

Question:

{question}

Rules:
- Answer only using policy documents.
- Never guess.
- Keep answer concise.
"""

    llm = get_llm()

    response = llm.invoke(prompt)

    answer = response.content

    verification = check_hallucination(
        question,
        answer,
        context
    )

    if should_retry(
            verification["confidence"]
    ):

        answer = execute_retry(
            question,
            answer
        )

        verification = check_hallucination(
            question,
            answer,
            context
        )

    citations = generate_citations(
        docs
    )

    knowledge_gap = detect_knowledge_gap(
        answer,
        verification["confidence"]
    )

    update_analytics(
        "POLICY",
        verification["confidence"],
        knowledge_gap
    )

    log_interaction(
        question,
        "POLICY",
        verification["confidence"],
        verification["verdict"]
    )

    memory.add_message(
        "User",
        question
    )

    memory.add_message(
        "Assistant",
        answer
    )

    return {

        "answer":
            answer,

        "confidence":
            verification["confidence"],

        "verdict":
            verification["verdict"],

        "citations":
            citations,

        "knowledge_gap":
            knowledge_gap
    }