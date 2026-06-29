def get_embeddings():
    raise RuntimeError(
        "Local HuggingFace embeddings were removed to keep Render deployment "
        "within memory limits. The app now uses src.retriever.retriever for "
        "lightweight PDF retrieval."
    )
