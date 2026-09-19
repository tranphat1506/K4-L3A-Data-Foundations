import re
from pathlib import Path
from typing import Dict, Any
from src.models import Document
from src.chunking import HeadingChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.embeddings import GeminiEmbedder
import os
from dotenv import load_dotenv

load_dotenv()

def parse_markdown(file_path: Path) -> tuple[Dict[str, Any], str]:
    text = file_path.read_text(encoding="utf-8")
    parts = text.split('---')
    if len(parts) >= 3:
        frontmatter_str = parts[1]
        content = '---'.join(parts[2:]).strip()
        metadata = dict(re.findall(r'^(\w+):\s*(.+)$', frontmatter_str, re.M))
        return metadata, content
    return {}, text.strip()

def run_benchmark():
    # 1. Đọc file & tách frontmatter
    data_dir = Path("data/kytucxa")
    md_files = sorted(data_dir.glob("*.md"))
    
    # 2. Chunking (Sử dụng HeadingChunker)
    chunker = HeadingChunker()
    all_docs = []
    
    for path in md_files:
        metadata, content = parse_markdown(path)
        metadata["doc_id"] = path.stem  # Gắn doc_id bằng tên file
        
        chunks = chunker.chunk(content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                id=f"{path.stem}#{i}",
                content=chunk,
                metadata=metadata
            )
            all_docs.append(doc)
            
    # 3. Nạp vào Store (Dùng GeminiEmbedder thay cho Mock)
    embedder = GeminiEmbedder()
    store = EmbeddingStore(embedding_fn=embedder)
    store.add_documents(all_docs)
    
    # Khởi tạo mô hình AI (Gemini 1.5 Flash) để sinh câu trả lời
    from google import genai
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def real_llm(prompt: str) -> str:
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"[Lỗi gọi API sau {max_retries} lần thử]: {e}"
                time.sleep(2 * (attempt + 1))
            
    agent = KnowledgeBaseAgent(store, llm_fn=real_llm)
    
    # 4. Chạy 5 query benchmark (Bộ FAQ mới)
    queries = [
        {"q": "Khi ở KTX cần lưu ý điều gì?", "filter": None},
        {"q": "Thời hạn lưu trú và phụ trội điện nước được tính như thế nào?", "filter": None},
        {"q": "Điểm uy tín (CFD score) là gì và dùng để làm gì?", "filter": {"audience": "student"}},
        {"q": "Làm thế nào để gửi yêu cầu tới Ban Quản lý KTX?", "filter": None},
        {"q": "Làm thế nào để báo cáo sửa chữa đồ dùng trong phòng?", "filter": None},
    ]
    
    with open("ket_qua_benchmark.txt", "w", encoding="utf-8") as f:
        f.write(f"Đã nạp {len(all_docs)} chunks từ {len(md_files)} files.\n\n")
        
        for idx, q_info in enumerate(queries, 1):
            q = q_info["q"]
            m_filter = q_info["filter"]
            
            f.write(f"--- QUERY {idx}: {q} ---\n")
            f.write(f"Filter: {m_filter}\n")
            
            results = store.search_with_filter(q, top_k=3, metadata_filter=m_filter)
            for i, rec in enumerate(results, 1):
                doc_id = rec['metadata'].get('doc_id')
                score = rec.get('score', 0)
                f.write(f"  Top {i}: {doc_id} (Score: {score:.4f})\n")
                f.write(f"  Content: {rec['content'][:100]}...\n\n")
                
            ans = agent.answer(q, metadata_filter=m_filter)
            f.write(f"AGENT ANSWER:\n{ans}\n\n")
            f.write("="*60 + "\n")
            
    print("Đã hoàn tất! Xem kết quả tại file ket_qua_benchmark.txt")

if __name__ == "__main__":
    run_benchmark()
