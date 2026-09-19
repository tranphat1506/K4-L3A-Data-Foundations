from dotenv import load_dotenv
load_dotenv()
from src.embeddings import GeminiEmbedder
from src.chunking import compute_similarity

embedder = GeminiEmbedder()
pairs = [
    ("Mèo thích ăn cá", "Chó thích gặm xương"),
    ("KTX FPT rộng rãi", "Không gian nội trú thoải mái"),
    ("Quy định xử phạt sinh viên", "Giờ giới nghiêm KTX là 22h30"),
    ("Sinh viên học lập trình", "Quán phở ngon ở Hà Nội"),
    ("Bạn phải mang theo giấy tờ", "Cần chuẩn bị thẻ sinh viên"),
]

for a, b in pairs:
    va = embedder(a)
    vb = embedder(b)
    score = compute_similarity(va, vb)
    print(f"{score:.4f}")
