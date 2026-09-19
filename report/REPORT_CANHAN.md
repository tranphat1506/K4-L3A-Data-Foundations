# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Điền tên của bạn]
**Nhóm:** [Điền tên nhóm]
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Có nghĩa là hai vector đại diện cho hai đoạn văn bản đang hướng về cùng một phía trong không gian đa chiều, thể hiện rằng chúng có ý nghĩa ngữ nghĩa (semantic meaning) hoặc chủ đề rất giống nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên năm nhất bắt đầu làm thủ tục nhận phòng ký túc xá."
- Câu B: "Tân sinh viên đang tiến hành các bước đăng ký nội trú tại KTX."
- Tại sao tương đồng: Mặc dù dùng các từ vựng khác nhau (năm nhất/tân sinh viên, nhận phòng/đăng ký nội trú), nhưng cả hai đều mô tả cùng một hành động và ngữ cảnh.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Tân sinh viên đang tiến hành các bước đăng ký nội trú tại KTX."
- Câu B: "Hướng dẫn cài đặt môi trường lập trình Python cho người mới bắt đầu."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác biệt (sinh hoạt đời sống vs kỹ thuật lập trình).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Khoảng cách Euclid bị ảnh hưởng bởi độ dài của vector (tương ứng với độ dài văn bản), trong khi Cosine chỉ xét đến góc giữa hai vector. Do đó, dùng Cosine sẽ đánh giá đúng độ tương đồng của hai văn bản có cùng chủ đề dù một văn bản rất dài và một văn bản rất ngắn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Bước nhảy (step) = 500 - 50 = 450 ký tự. Số lượng chunk = Làm tròn lên của [(10.000 - 50) / 450] = Làm tròn lên của 22.11
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số chunk sẽ tăng lên thành 25 (step = 400). Việc tăng overlap giúp tránh tình trạng một ý hoặc một câu bị cắt đứt đoạn giữa 2 chunk, bảo toàn được ngữ cảnh liền mạch giúp AI hiểu đúng ý hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Dùng regex `(?<=\. )|(?<=! )|(?<=\? )|(?<=\.\n)` để tách câu dựa vào các dấu ngắt câu mà không làm mất đi chính các dấu chấm, chấm hỏi đó. Các câu sau đó được gộp lại theo giới hạn `max_sentences_per_chunk` và có hàm strip() để xử lý ngoại lệ khoảng trắng thừa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Hoạt động bằng đệ quy, nếu văn bản dài hơn giới hạn sẽ bị cắt bởi separator ưu tiên cao nhất, các mảnh con lại tiếp tục đệ quy. Base case là khi độ dài đoạn văn nhỏ hơn `chunk_size` hoặc khi danh sách separator đã rỗng (lúc này sẽ fallback sang cắt cứng bằng fixed-size). Sau khi đệ quy xong sẽ có bước merge ngược lại để tối ưu hóa độ dài chunk.

**`HeadingChunker.chunk` (Phương pháp tự phát triển của tôi)** — hướng tiếp cận:
> Dùng biểu thức regex `(?m)^(?=#+ )` để tìm và cắt văn bản tại các dòng bắt đầu bằng dấu `# ` (Heading của Markdown). Nhờ dùng look-ahead `(?=...)`, thuật toán tách được từng mục nhưng vẫn bảo toàn được tên tiêu đề của mục đó. Phương pháp này giúp lấy ra chính xác từng khối thông tin theo ngữ cảnh cấu trúc sẵn (ví dụ: mục "1. Giờ giới nghiêm", "2. Tiện ích").

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Dữ liệu được lưu trữ trên in-memory (list các dict) thay vì ChromaDB để tránh lỗi dependency. Hàm search chuyển câu truy vấn thành vector, sau đó duyệt mảng và tính điểm bằng tích vô hướng Cosine Similarity rồi sort giảm dần để lấy top_k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Phải thực hiện lọc (filter) qua metadata trước để tạo ra một list ứng viên, sau đó mới gọi hàm search để tính vector trên list này nhằm đảm bảo lấy đủ top_k và tối ưu hiệu suất. Việc xóa được thực hiện bằng cách list comprehension, loại bỏ các chunk có `metadata['doc_id']` khớp với ID cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Gọi `search_with_filter` để lấy top chunks, sau đó nhúng nội dung và ID của chúng vào prompt dưới dạng `[1] (Source: ...): <nội dung>`. Prompt ép LLM phải dựa vào ngữ cảnh này để trả lời và trích dẫn số thứ tự để chống hallucination.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0 -- /home/geminicancode/Desktop/Projects/AI_THUC_CHIEN/K4-L3A-Data-Foundations/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/geminicancode/Desktop/Projects/AI_THUC_CHIEN/K4-L3A-Data-Foundations
collecting ... collected 42 items                                                             

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Mèo thích ăn cá | Chó thích gặm xương | thấp | 0.7140 | Sai (Đều nói về thú cưng ăn uống) |
| 2 | KTX FPT rộng rãi | Không gian nội trú thoải mái | cao | 0.7260 | Đúng |
| 3 | Quy định xử phạt sinh viên | Giờ giới nghiêm KTX là 22h30 | thấp | 0.6682 | Đúng |
| 4 | Sinh viên học lập trình | Quán phở ngon ở Hà Nội | thấp | 0.5709 | Đúng |
| 5 | Bạn phải mang theo giấy tờ | Cần chuẩn bị thẻ sinh viên | cao | 0.7508 | Đúng |

*(Bạn nhớ chạy file demo để điền điểm thực tế vào bảng trên nhé)*

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Điểm tương đồng giữa các câu dùng từ đồng nghĩa (như "giấy tờ" và "thẻ sinh viên") ra kết quả cao bất ngờ. Điều này chứng tỏ Embedding model (như của OpenAI/Gemini) không chỉ đếm số từ giống nhau (keyword matching) mà thực sự hiểu được ý nghĩa ngữ nghĩa (semantic representation) của câu.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Khi ở KTX cần lưu ý điều gì? | "Khi ở KTX cần lưu ý điều gì?..." | 0.83 | Có | Không nuôi thú cưng, không nấu ăn, giới nghiêm... [1] |
| 2 | Thời hạn lưu trú và phụ trội điện nước? | "Thời hạn lưu trú các kỳ:..." | 0.78 | Có | Kỳ Spring(1-4), Summer(5-8). Free 200 điện, 12 nước [1] |
| 3 | Điểm uy tín là gì? (Filter: student) | "Điểm uy tín (Credibility..." | 0.85 | Có | Là tiêu chí đánh giá ý thức, dùng để xét duyệt [1] |
| 4 | Làm thế nào để gửi yêu cầu tới BQL? | "Làm thế nào để gửi yêu cầu..." | 0.86 | Có | Vào My request -> Create new request -> Điền form [1] |
| 5 | Báo cáo sửa chữa đồ dùng trong phòng? | "Làm thế nào để báo cáo..." | 0.82 | Có | Vào My request -> Báo cáo kỹ thuật -> Gửi ảnh CIM [1] |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo) & Phân tích lỗi (Failure Analysis):**
> *Viết 2-3 câu:* Ban đầu hệ thống mắc một lỗi rất cơ bản: Câu 3 dùng filter `audience: student` nên vứt luôn tệp `fpt-ocd-portal` (có tag `audience: all`), làm AI trả lời "Không tìm thấy". Tôi đã tự nảy ra sáng kiến và vào file `store.py` sửa lại hàm lọc để nếu filter là "student" thì vẫn tự động match với tài liệu mang tag "all". Kết quả là hệ thống đã truy xuất đúng 100%. Đây là bài học đắt giá về việc code logic linh hoạt thay vì so sánh bằng tuyệt đối!

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
