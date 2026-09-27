from dataclasses import dataclass

from quantum_wiki.wiki.models import WikiPage

from .cosine import cosine_similarity
from .embeddings import HashEmbeddingModel


@dataclass(frozen=True)
class RetrievedPage:
    page: WikiPage
    relevance: float


class Retriever:
    def __init__(self, pages: list[WikiPage], embedding_model=None):
        self.pages = pages
        self.embedding_model = embedding_model or HashEmbeddingModel()
        for page in self.pages:
            if page.embedding is None:
                page.embedding = self.embedding_model.encode(page.content)

    def retrieve(self, query: str, n_candidates: int = 12) -> list[RetrievedPage]:
        query_embedding = self.embedding_model.encode(query)
        # Retrieval is deliberately separate from selection. The selector
        # never sees the whole wiki; it only solves the small problem produced
        # by this classical candidate-generation step.
        ranked = [RetrievedPage(page, cosine_similarity(query_embedding, page.embedding)) for page in self.pages]
        return sorted(ranked, key=lambda item: (-item.relevance, item.page.id))[:n_candidates]
