import os
from typing import List


class EmbeddingProviderError(RuntimeError):
    pass


def embed_text(texts: List[str]) -> List[List[float]]:
    """
    Retorna vetores (float[]) para cada texto.
    Provider-agnostic:
    - SEMANTIC_EMBEDDINGS_PROVIDER=local: sentence-transformers
    - SEMANTIC_EMBEDDINGS_PROVIDER=openai: OpenAI (placeholder)
    """
    provider = os.getenv("SEMANTIC_EMBEDDINGS_PROVIDER", "local").lower().strip()

    if provider == "local":
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as e:
            raise EmbeddingProviderError(
                "Provider local requer `sentence-transformers`. Instale e configure."
            ) from e
        model_name = os.getenv("SEMANTIC_LOCAL_MODEL", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_name)
        vecs = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() for v in vecs]

    if provider == "openai":
        raise EmbeddingProviderError(
            "Provider openai ainda não conectado. Defina o provider final e eu entrego o conector pronto."
        )

    raise EmbeddingProviderError(f"Provider desconhecido: {provider}")
