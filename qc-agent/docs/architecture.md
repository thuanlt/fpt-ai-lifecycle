# Kiến Trúc Hệ Thống: Auto-QA Multi-Agent (qc-agent-master)

Chào bạn, dựa trên việc khảo sát thực tế source code của dự án `qc-agent-master`, tôi xin phân tích và giải thích hệ thống dưới góc nhìn của một Senior Software Architect. Đây là một hệ thống **Agent-based Quality Assurance (Auto-QA)** cực kỳ thú vị, có nhiệm vụ tự động hóa quá trình sinh và chạy test script (như Playwright) trực tiếp từ các mô tả bằng ngôn ngữ tự nhiên hoặc từ Test Cases trên Jira.

Dưới đây là nội dung phân tích chi tiết:

---

## 1. Kiến Trúc Tổng Thể (Architecture)

Hệ thống không đi theo hướng Monolithic hay MVC truyền thống, mà tuân theo mô hình **Multi-Agent Architecture** (Kiến trúc đa tác nhân) kết hợp với thiết kế **Event/Workflow-driven**. Đặc biệt, nó áp dụng khuôn mẫu **Hierarchical Control** (Điều khiển phân cấp) giữa các Agent.

*   **Mô hình Multi-Agent (Đội ngũ QC ảo):** Core của hệ thống nằm ở các Agent (được xây dựng dựa trên LLMs). Thay vì một monolithic agent làm lôm côm mọi việc, dự án chia nhỏ thành các "Role" riêng biệt (`Orchestrator`, `Verifier`, `Executor`).
*   **Model Context Protocol (MCP):** Đây là một công nghệ rất nổi bật trong dự án. Để Agent có thể tương tác với "thế giới thực" (trình duyệt, file system, debug tool), dự án sử dụng MCP. Các Agents không gắn chặt (tightly-coupled) với Playwright, mà giao tiếp qua một `mcpclient` chuẩn hóa.
*   **Sandbox / Containerization:** Các script automation được thực thi trong một môi trường cô lập hoặc docker container (thể hiện qua `sandbox.py`, `sandbox_docker.py`) để bảo mật và tránh làm rác máy local.

---

## 2. Luồng Dữ Liệu Chính (Data Flow)

Dữ liệu đi theo một đường ống khép kín (End-to-End Pipeline) từ việc nạp Requirement -> Lên Plan -> Thực thi -> Báo cáo:

1.  **Ingestion (Đầu vào từ Jira):**
    *   Hệ thống bắt đầu ở `app_test_cycle.py`. Từ ID của Test Cycle (vd: `NCPP-C203`), script sử dụng `jira_client.py` gọi API lên Jira để kéo toàn bộ Test Cases.
    *   **Xử lý Preconditions:** Module `TestProcessor` phân tích đệ quy (recursive) các preconditions để sắp xếp tuyến tính (flatten) các Test Case theo đúng thứ tự cần chạy (A cần xong trước mới chạy B). Sau đó merge tất cả test steps thành một danh sách JSON.
2.  **Planning (Giai đoạn Lên Kế Hoạch):**
    *   Danh sách các step thô được đẩy vào `OrchestratorAgent`.
    *   `OrchestratorAgent` gọi LLM để phiên dịch ra 2 nhóm: `testing_plan` (các bước thực thi Playwright/Web cụ thể) và `post_testing_plan` (sinh script automation, gom báo cáo, chụp màn hình).
3.  **Execution Loop (Vòng lặp Thực Thi Thực Tế):**
    Với mỗi step trong plan, hệ thống vào vòng lặp kiểm chứng (Verifier-Executor Loop):
    *   **VerifierAgent:** "Nhìn" vào trạng thái hiện tại (screen, HTML, logs) và đối chiếu với expected_result. Nếu chưa đạt, nó đưa ra `next_action`.
    *   **ExecutorAgent:** Nhận `next_action` (vd: click nút Login, điền username) -> Dịch thành lệnh thông qua `mcpclient` -> đẩy xuống môi trường thực (chạy lệnh bash, hoặc gọi Playwright API trong môi trường ảo/sandbox).
    *   Vòng lặp này lặp lại cho tới khi `VerifierAgent` trả về trạng thái `"DONE"`, `"SKIP"` hoặc bị timeout/hết lượt thử.
4.  **Output & Reporting:**
    *   Khi luồng Test chạy xong, chạy tiếp `post_testing_plan`.
    *   Sử dụng các template có sẵn trong `tmp/template`, ghi kết quả tổng hợp ra file text.
    *   Tạo file code TypeScript tự động (Automation Script) lưu vào thư mục `tmp/` (vd: `automation_12345.ts`).
    *   Khép kín quy trình và log toàn bộ lịch sử (SharedMemory).

---

## 3. Các Module Quan Trọng (Thư Mục / File Cốt Lõi)

Dưới đây là chức năng của các "nội tạng" chính trong cấu trúc thư mục của hệ thống:

### Entry Points & Core Scripts
*   **`src/app_test_cycle.py`**: Trái tim khởi chạy hệ thống (Entry point). Khởi tạo kết nối Jira, đệ quy gỡ rối preconditions của Test Cases và châm ngòi nổ cho `OrchestratorAgent`.
*   **`src/test.py`**: (Thường dùng cho việc chạy thử/debug riêng lẻ các tính năng nhỏ ngoài luồng chính).

### `src/agent/` (Não Bộ AI)
Đây là nơi chứa logic thông minh. Dự án đang chia team (`qcteam`), hiện tập trung vào `team_3`:
*   **`orchestrator_agent.py`**: Người Nhạc Trưởng. Không trực tiếp gõ lệnh nghiệm thu, mà chuyên phân tích đề bài, chia nhỏ thành các plan chi tiết.
*   **`verifier_agent.py`**: Đôi mắt & Giám khảo. Viết prompt để LLM đánh giá xem "hành động vừa rồi đã thoả mãn bước test chưa?".
*   **`executor_agent.py`**: Đôi tay. Cấu hình tool và gọi MCP client để thực thi các hành động mà Verifier yêu cầu nghiệm thu. Đoạn code này cũng quản lý việc khởi tạo các kết nối tới mcp tools.

### `src/tools/` (Giao tiếp với Hệ Thống Đích)
*   **`mcpclient.py`**: Cực kỳ quan trọng. Đây là một HTTP/SSE/Stdio Client chuẩn hoá giao thức Model Context Protocol. Nó cho phép các Agents ở phía trên "nói chuyện" được với những công cụ thực thi mệnh lệnh phía dưới mà không cần biết công cụ đó viết bằng gì.

### `src/utils/` (Công cụ dùng chung)
*   **`jira_client.py`**: Library wrap các lệnh call REST API đến Jira để lấy `testRunItems`, `testScript`, `stepByStepScript`.
*   **`sandbox.py` & `sandbox_docker.py`**: Môi trường nhốt code (sandbox). Do agent sẽ tự sinh ra code tự động, hệ thống sử dụng module này để chạy script trong môi trường cách ly (như Docker) nhằm bảo vệ máy tính gốc/server lúc run.
*   **`logger.py`**: System Log Console với rich text in ra màn hình trạng thái của các Agent.

### `src/config/` & Memory
*   **`src/memory/` (`shared_memory.py`)**: Không gian chia sẻ (như bảng đen) để các agents (Orchestrator, Verifier, Executor) có thể biết người trước vừa làm gì, lưu session hiện tại.
*   **`src/prompt/`**: Nơi lưu giữ các template "câu thần chú" System Prompts cho từng loại Agent.
*   Khác: Các file Shell script (`run.sh`, `start_vector_db.sh`) dùng để set up môi trường, chạy Docker, và chạy CSDL Vector (như Chroma/Faiss) nếu trong luồng có sử dụng kĩ thuật RAG.

**Tổng kết:**
Đây là một hệ thống thiết kế rất hiện đại, decoupling tốt. Các Agent không bị trói buộc với một môi trường code nhất định vì đã dùng interface MCP làm middleware. Việc gỡ rối logic Jira Test Cycle bằng đệ quy và chia tay 3 Role (Nhạc Trưởng - Người Làm - Người Kiểm Tra) giúp hệ thống auto-qa scale tốt và tránh bị lẫn lộn context (Ảo giác AI) trong quá trình vận hành phức tạp.
