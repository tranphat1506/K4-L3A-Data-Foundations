# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** SH
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và Hướng dẫn sinh hoạt tại Ký túc xá Đại học FPT Hà Nội.

**Tại sao nhóm chọn chủ đề này?**
> *Viết 2-3 câu:* Đây là chủ đề thiết thực, sát với nhu cầu thực tế của sinh viên đặc biệt là tân sinh viên. Bộ tài liệu có sẵn các luồng quy trình (nhận phòng), nội quy (xử phạt) và câu hỏi thường gặp, rất phù hợp để xây dựng hệ thống tư vấn hỏi đáp RAG.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Hướng dẫn nhận phòng KTX | daihoc.fpt.edu.vn | 01/09/2023 | 2500+ | doc_id, audience: all |
| 2 | Kinh nghiệm cuộc sống KTX | daihoc.fpt.edu.vn | 01/09/2023 | 4800+ | doc_id, audience: student |
| 3 | Nội quy KTX Hòa Lạc | ocd.fpt.edu.vn/Files | v1.0 | 7000+ | doc_id, audience: student |
| 4 | Cổng OCD Portal | ocd.fpt.edu.vn | 2026 | 5000+ | doc_id, audience: all |
| 5 | Tiện ích tại KTX | daihoc.fpt.edu.vn | 09/01/2023 | 2000+ | doc_id, audience: all |
| 6 | Quy định kiểm tra phòng BQL | Tài liệu nội bộ | 2026 | 1500+ | doc_id, audience: staff |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student`, `staff`, `all` | Dùng để phân quyền và lọc tài liệu. Giúp AI không vô tình lấy nhầm quy trình của Ban quản lý đi trả lời cho sinh viên. |
| `doc_id` | string | `fpt-noi-quy-ktx-hl` | Giúp định danh, tìm kiếm nguồn trích dẫn và hỗ trợ xóa tài liệu (delete_document) khi tài liệu bị lỗi thời. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Nội quy | FixedSizeChunker (`fixed_size`) | ~25 | 300 ký tự | Kém (cắt đứt câu chữ giữa chừng) |
| Nội quy | SentenceChunker (`by_sentences`) | ~30 | 250 ký tự | Khá (giữ trọn vẹn câu, nhưng mất tính liên kết đoạn) |
| Nội quy | RecursiveChunker (`recursive`) | ~20 | 350 ký tự | Tốt (cắt theo đoạn văn, xuống dòng) |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên của bạn]**
- **Loại chiến lược:** Custom (HeadingChunker)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng regex cắt văn bản theo các thẻ Heading `# ` của Markdown. Tài liệu nội quy/hướng dẫn thường được phân mục rất rõ ràng, cắt theo Heading giúp giữ trọn vẹn ngữ cảnh của từng Điều luật mà không làm đứt gãy ý.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def chunk(self, text: str) -> list[str]:
        if not text: return []
        parts = re.split(r'(?m)^(?=#+ )', text)
        return [p.strip() for p in parts if p.strip()]
```

**Thành viên 2 — (Để trống do làm cá nhân)**

**Thành viên 3 — (Để trống do làm cá nhân)**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Bạn | HeadingChunker | 10/10 | Giữ trọn vẹn 1 điều luật, rất tốt cho Q&A | Cần tài liệu chuẩn Markdown |
| (Trống) | RecursiveChunker | N/A | Cắt đệ quy linh hoạt, chống tràn | Dễ làm đứt gãy câu chữ |
| (Trống) | SentenceChunker | N/A | Tránh lẫn lộn các ý | Dễ mất ngữ cảnh (context) |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):* HeadingChunker là phương pháp xuất sắc nhất cho chủ đề Nội quy KTX. Bởi vì các bộ luật hoặc quy định thường được cấu trúc dưới dạng các mục lớn (Điều 1, Điều 2). Cắt theo mục giúp AI hiểu toàn bộ quy định của một chủ đề cụ thể mà không bị cắt xé giữa chừng như RecursiveChunker.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Khi ở KTX cần lưu ý điều gì? | Không được nuôi thú cưng, rượu bia, nấu ăn. Giới nghiêm 22:30. | `fpt-ocd-portal` |
| 2 | Thời hạn lưu trú và phụ trội điện nước được tính như thế nào? | Spring (1-4), Summer (5-8), Fall (9-12). Free 200 điện & 12 nước. | `fpt-ocd-portal` |
| 3 | Điểm uy tín (CFD score) là gì và dùng để làm gì? | Là tiêu chí đánh giá ý thức, dùng để xét duyệt ở KTX. | `fpt-ocd-portal` |
| 4 | Làm thế nào để gửi yêu cầu tới Ban Quản lý KTX? | Vào My request -> Create new request -> Điền form. | `fpt-ocd-portal` |
| 5 | Làm thế nào để báo cáo sửa chữa đồ dùng trong phòng? | Vào My request -> Báo cáo vấn đề kỹ thuật -> Điền form trên CIM. | `fpt-ocd-portal` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Lưu ý khi ở KTX | HeadingChunker | Có (Top 1) | 2 điểm |
| 2 | Lưu trú và phụ trội điện nước | HeadingChunker | Có (Top 1) | 2 điểm |
| 3 | Điểm uy tín là gì? (Filter: student) | HeadingChunker | Có (Top 1) | 2 điểm (Sau khi tự fix code) |
| 4 | Gửi yêu cầu BQL | HeadingChunker | Có (Top 1) | 2 điểm |
| 5 | Báo cáo sửa chữa | HeadingChunker | Có (Top 1) | 2 điểm |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:* Rất hữu ích nhưng cũng tiềm ẩn rủi ro (Failure Case). Ban đầu, Câu 3 (Điểm uy tín) bị thất bại do filter tìm cứng ngắc chữ `student`, làm văng mất tài liệu OCD Portal (mang tag `all`). Nhóm đã chủ động phân tích lỗi này và sửa lại logic code trong `store.py` để filter có thể match cả giá trị `all`. Nhờ thế, câu 3 đã truy xuất thành công mĩ mãn!

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*
> 1. HeadingChunker là phương pháp chia nhỏ (chunk) tốt nhất cho file Markdown, vì nó gom được toàn bộ nội dung của một Điều Luật thay vì cắt xé nhỏ ra như SentenceChunker.
> 2. Sự khác biệt một trời một vực giữa MockEmbedder (lấy random) và Gemini API (lấy chính xác ngữ nghĩa tiếng Việt).

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?* Nếu cắt văn bản quá nhỏ (theo câu), đoạn text sẽ bị mất ngữ cảnh (không biết câu này thuộc phần Quy định hay Lợi ích). Nếu cắt theo đoạn văn bản lớn theo mục (HeadingChunker), Vector Store sẽ có đầy đủ ngữ cảnh để chấm điểm tương đồng chính xác hơn rất nhiều.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:* Nhóm sẽ cố gắng thu thập các bộ tài liệu lớn hơn nữa và bóc tách metadata kỹ hơn (như gán thêm thẻ `category: y_te`, `category: an_ninh` cho từng đoạn văn bản) để lọc filter tốt hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
