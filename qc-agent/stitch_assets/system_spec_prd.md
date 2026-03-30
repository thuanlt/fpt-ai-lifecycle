# ĐẶC TẢ HỆ THỐNG SIÊU ĐIỀU KHIỂN QC-AGENT (SDET MULTI-AGENT SYSTEM)

## 1. Tầm nhìn kiến trúc (Architectural Vision)
Hệ thống là một nỗ lực hiện đại hóa quy trình QA/QC truyền thống, chuyển đổi từ việc viết test case thủ công sang mô hình "Human-in-the-loop Automation". Hệ thống vận hành theo kiến trúc Workflow Hierarchical Loop (Vòng lặp phân cấp thứ bậc) với sự phối hợp của nhiều tầng Agent trí tuệ nhân tạo.

## 2. Các tính năng giao diện (UI Functional Features)

### Bảng điều khiển RAG & LTM (Vector Memory Hub)
*   **Nạp kiến thức đa tầng:** Quản lý tài liệu SRS, kỹ thuật qua Text, URL (Crawl), và đa định dạng file (PDF, Docx, Excel, PPT).
*   **Giám sát Vector DB Real-time:** Hiển thị chi tiết nhà cung cấp (Qdrant/Chroma), mô hình nhúng (Embedding Model) và tổng số lượng item đang được quản lý.
*   **Playground tìm kiếm:** Cho phép truy vấn thử nghiệm độ chính xác của bộ nhớ dài hạn.

### Trung tâm kiểm thử Fast Track (Fast Track MVP)
*   **Tích hợp Jira 360:** Khả năng quét Cycle, xử lý đệ quy các Test Case có tiền điều kiện (Preconditions) phức tạp bằng thuật toán DFS (Depth-First Search) để đảm bảo trình tự kiểm thử logic.
*   **Lập kế hoạch đa nhiệm (Multi-Task Planning):** Chế độ Fast Planner tự động phân rã Instruction thành các nhiệm vụ cô đọng, gán vai trò (Senior Tester, UI Specialist) và ánh xạ ID Jira thông minh.
*   **Trình biên tập kịch bản tương tác (Interactive SDET Editor):** Một ô soạn thảo Markdown chuyên dụng cho phép Tester/QC chỉnh sửa lại kết quả sinh ra từ AI trước khi "đưa lên kệ" (Jira).

## 3. Sức mạnh cốt lõi đằng sau (Technical Core & Data Flow)

### Hệ thống Bộ nhớ lai (Hybrid Memory System)
*   **Shared Memory (RAM-based):** Sử dụng SharedMemory (cấu trúc deque) để làm cầu nối trao đổi nhật ký thực thi (log) giữa Planner và các Worker Tester trong thời gian thực.
*   **Long-Term Memory (LTM):** Cơ sở dữ liệu Vector Qdrant đảm nhiệm vai trò RAG, cung cấp ngữ cảnh sâu về nghiệp vụ.

### Cơ chế Thực thi "Bọc thép" (Armor-Plated Execution)
*   **Phân cấp Agent:** Senior Tester không phải một LLM call đơn thuần mà là một hệ thống bao gồm: Orchestrator (Nhạc trưởng), Verifier (Mắt thần kiểm chứng), và Executor (Người thực thi gọi Tool).
*   **Tự phục hồi (Self-Healing):** Cơ chế Retry lên đến 20 lần với Verifier liên tục đánh giá trạng thái (DONE, FAILED, INPROGRESS) để đảm bảo kết quả cuối cùng đạt chất lượng cao nhất.

### Cầu nối MCP (Model Context Protocol)
*   Tích hợp đa giao thức kết nối với các ứng dụng bên ngoài (Playwright, Filesystem) thông qua Stdio, SSE, và Direct connection, cho phép Agent tương tác trực tiếp với môi trường thực tế.

## 4. Luồng dữ liệu (Data Pipeline)
1.  **Input:** Nhận User Instruction từ Web UI.
2.  **Planning:** Planner lắp ráp Context (LTM + SRS) -> Phân rã thành BatchTask (JSON).
3.  **Execution:** Workers lấy kế hoạch từ Shared Memory -> Gọi LLM Gateway (FPT Cloud) -> Sinh Evidence.
4.  **Integration:** Người dùng duyệt/sửa kết quả trên UI -> Đẩy lên Jira & Gửi thông báo Team/Telegram qua luồng Integration Layer.

## Ghi chú cho Thiết kế/Nâng cấp
Hệ thống yêu cầu sự nhất quán giữa logic mã nguồn (Python) và hiển thị (HTML/JS). Khi nâng cấp UI, cần đảm bảo các nút lệnh như "Sync Cycle" hay "Push Jira" phải có phản hồi thị giác (Loading loaders) vì các tác vụ gọi AI Agent thường kéo dài (30s - 180s) và cần độ trễ thời gian thực.