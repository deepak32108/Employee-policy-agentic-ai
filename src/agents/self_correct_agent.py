from src.retriever.retriever import retrieve_documents
from src.utils.llm import get_llm


def improve_answer(
        question: str,
        previous_answer: str
):

    docs = retrieve_documents(
        question
    )

    extended_context = "\n\n".join(
        [
            doc.page_content
            for doc in docs
        ]
    )

    llm = get_llm()

    prompt = f"""
You are an expert HR Policy Auditor.

A previous answer may be incomplete.

Question:

{question}

Previous Answer:

{previous_answer}

Additional Context:

{extended_context}

Task:

1. Verify previous answer.
2. Correct mistakes.
3. Provide improved answer.
4. Use only document information.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    result = improve_answer(
        "How many casual leaves are allowed?",
        "I think employees get 5 leaves."
    )

    print(result)