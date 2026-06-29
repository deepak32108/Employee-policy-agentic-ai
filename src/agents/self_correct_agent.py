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
You are an HR Policy Assistant.

A previous answer may be incomplete.

Question:

{question}

Previous Answer:

{previous_answer}

Additional Context:

{extended_context}

Task:
- Return only the final corrected answer.
- Use only document information.
- Keep the answer under 100 words.
- Use short bullets only when useful.
- Do not describe verification steps.
"""

    response = llm.invoke(prompt)

    return response.content


if __name__ == "__main__":

    result = improve_answer(
        "How many casual leaves are allowed?",
        "I think employees get 5 leaves."
    )

    print(result)
