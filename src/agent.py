from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3, metadata_filter: dict = None) -> str:
        if self.store.get_collection_size() == 0:
            return "Empty store"
            
        results = self.store.search_with_filter(question, top_k=top_k, metadata_filter=metadata_filter)
        if not results:
            return "No matching info"
            
        context_parts = []
        for i, rec in enumerate(results, 1):
            doc_id = rec.get("metadata", {}).get("doc_id", "Unknown")
            context_parts.append(f"[{i}] (Source: {doc_id}): {rec['content']}")
            
        context = "\n\n".join(context_parts)
        
        prompt = f"""Dựa vào các ngữ cảnh sau đây, hãy trả lời câu hỏi.
Vui lòng trích dẫn nguồn bằng ngoặc vuông [1], [2] tương ứng.
Nếu không tìm thấy thông tin, hãy trả lời "Không tìm thấy thông tin".

Ngữ cảnh:
{context}

Câu hỏi: {question}"""

        return self.llm_fn(prompt)
