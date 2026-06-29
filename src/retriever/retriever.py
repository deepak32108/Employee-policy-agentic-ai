import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader


DATA_FOLDER = Path("data")
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150
TOP_K = 3


@dataclass
class RetrievedDocument:
    page_content: str
    metadata: dict


def _tokenize(text: str) -> set[str]:
    return set(
        re.findall(
            r"[a-z0-9]+",
            text.lower()
        )
    )


def _chunk_text(text: str) -> list[str]:
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(
            text[start:end].strip()
        )

        if end >= len(text):
            break

        start = max(
            0,
            end - CHUNK_OVERLAP
        )

    return chunks


@lru_cache(maxsize=1)
def _load_policy_documents() -> tuple[RetrievedDocument, ...]:
    documents = []

    for pdf_path in sorted(DATA_FOLDER.glob("*.pdf")):
        reader = PdfReader(str(pdf_path))

        for page_index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            for chunk_index, chunk in enumerate(_chunk_text(text), start=1):
                documents.append(
                    RetrievedDocument(
                        page_content=chunk,
                        metadata={
                            "source": pdf_path.name,
                            "page": page_index,
                            "chunk": chunk_index
                        }
                    )
                )

    return tuple(documents)


def retrieve_documents(question: str):
    query_tokens = _tokenize(question)

    if not query_tokens:
        return []

    scored_documents = []

    for document in _load_policy_documents():
        document_tokens = _tokenize(document.page_content)
        overlap = len(query_tokens.intersection(document_tokens))

        if overlap:
            scored_documents.append(
                (
                    overlap,
                    len(document_tokens),
                    document
                )
            )

    scored_documents.sort(
        key=lambda item: (
            item[0],
            -item[1]
        ),
        reverse=True
    )

    return [
        document
        for _, _, document in scored_documents[:TOP_K]
    ]


def get_retriever():
    return retrieve_documents
