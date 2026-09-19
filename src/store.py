from __future__ import annotations

import copy
from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        
        # Bỏ nhánh ChromaDB theo hướng dẫn của bài lab để không bị sập test
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = copy.deepcopy(doc.metadata) if doc.metadata else {}
        
        # Đảm bảo có doc_id trong metadata
        if "doc_id" not in metadata:
            if "#" in doc.id:
                metadata["doc_id"] = doc.id.split("#")[0]
            else:
                metadata["doc_id"] = doc.id
                
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content)
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_emb = self._embedding_fn(query)
        
        results = []
        for rec in records:
            score = _dot(query_emb, rec["embedding"])
            results.append({
                "id": rec["id"],
                "content": rec["content"],
                "metadata": rec["metadata"],
                "score": score
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        filtered_records = self._store
        
        if metadata_filter:
            filtered_records = []
            for rec in self._store:
                match = True
                for k, v in metadata_filter.items():
                    val = rec["metadata"].get(k)
                    # Nếu filter là 'student', nó vẫn sẽ match nếu metadata của tài liệu là 'all'
                    if val != v and val != "all":
                        match = False
                        break
                if match:
                    filtered_records.append(rec)
                    
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        initial_len = len(self._store)
        self._store = [rec for rec in self._store if rec["metadata"].get("doc_id") != doc_id]
        return len(self._store) < initial_len
