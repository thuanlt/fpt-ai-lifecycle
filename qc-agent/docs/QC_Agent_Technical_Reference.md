# 📖 QC-Agent Hệ Thống: Cẩm Nang Kỹ Thuật (Technical Reference Manual)

*Tài liệu này cung cấp phân tích chuyên sâu ở cấp độ mã nguồn (code-level) cho tất cả các modules quan trọng nhất của hệ thống Auto-QA Multi-Agent. Được viết dành cho vị trí Architechs và Senior Engineers để phục vụ viêc bảo trì, fix bug và nâng cấp kiến trúc.*

---

## MỤC LỤC
1. [Module 1: Test Cycle Management (Xử lý Đầu vào)](#module-1-test-cycle-management)
   - 1.1 Logic Gỡ rối Preconditions (`app_test_cycle.py`)
   - 1.2 Phân tích Class `TestProcessor` 
   - 1.3 Rủi ro tiềm ẩn (Edge Cases)
2. [Module 2: Đội Ngũ Tác Nhân Trí Tuệ (QC Team 3)](#module-2-đội-ngũ-tác-nhân-trí-tuệ-core-agents)
   - 2.1 Nhạc Trưởng - `OrchestratorAgent`
   - 2.2 Người Đánh Giá - `VerifierAgent`
   - 2.3 Người Thực Thi - `ExecutorAgent`
3. [Module 3: Clients & Tích Hợp Xuyên Hệ Thống](#module-3-clients--tích-hợp)
   - 3.1 Model Context Protocol Client (`mcpclient.py`)
   - 3.2 Tương tác Atlassian Jira (`jira_client.py`)

---

## MODULE 1: TEST CYCLE MANAGEMENT

### 1.1 Khởi tạo và Phân bố Dữ liệu (`app_test_cycle.py`)

**Ý nghĩa:** Trái tim của quá trình nạp dữ liệu. Nó đóng vai trò biến một luồng các cấu trúc Test Case phân mảnh trên Jira thành một luồng thực thi chạy thẳng (flattened workflow) có thứ tự.

**Logic Xử lý Bên trong (Internal Logic):**
1. Gọi API `get_test_cycle_info(test_cycle_id)` để lấy danh sách toàn bộ các Test Run Items.
2. Sắp xếp thứ tự chạy bằng hàm `get_sort_key` dựa trên tiền tố là chữ số (ví dụ: `1. Login`, `2. Add to Cart`).
3. Khởi tạo `TestProcessor` để duyệt qua từng Test Case, giải quyết "bài toán đệ quy" của Test Case phụ thuộc (Preconditions).
4. Gửi mảng `final_step_list` đã dẹp phẳng chứa mô tả các steps cho `OrchestratorAgent`.

### 1.2 Class `TestProcessor`

**Hàm quan trọng: `_build_execution_order(self, test_case_key, ordered_test_cases, visited_keys)`**
*   **Tham số:**
    *   `test_case_key` (str): Mã Jira test case (VD: *"NCPP-T4802"*).
    *   `ordered_test_cases` (List): Con trỏ lưu mảng output cuối cùng.
    *   `visited_keys` (Set): Cấu trúc Set giám sát các node đã được duyệt để chặn vòng lặp vô hạn.
*   **Phân tích Code chi tiết:**
    ```python
    if test_case_key in visited_keys:
        return # [Dòng 70] NGĂN CHẶN DEADLOCK nếu phát hiện chu trình đóng.
    
    current_case = self.test_case_map.get(test_case_key)
    # [Dòng 81] Bóc tách chuỗi precondition ra thành mảng: "TC-1, TC-2" -> ["TC-1", "TC-2"]
    precondition_keys = [key.strip() for key in precondition_str.split(',')]
    
    for pre_key in precondition_keys:
        # [Dòng 84] Gọi đệ quy cực kỳ quan trọng: Duyệt bề sâu (DFS) các điều kiện tiên quyết.
        self._build_execution_order(pre_key, ordered_test_cases, visited_keys)
    ```

### 1.3 Rủi ro tiềm ẩn (Edge Cases) của Module này
- **Lỗi Circular Dependency (Sự phụ thuộc vòng):** TC-A yêu cầu TC-B, nhưng TC-B lại cài precondition là TC-A.
  *   *Cách hệ thống xử lý:* Kiểm tra điều kiện `if test_case_key in visited_keys:` sẽ trả về (return ngay lập tức) để bẻ gãy chuỗi đệ quy lặp vô tận.
- **Precondition trỏ tới Test Case lỗi/bị xóa:**
  *   *Cách hệ thống xử lý:* Kiểm tra biến logic `current_case`. Nếu mảng map không có `key` này, in ra *"Warning: Test case with key '{test_case_key}' not found..."* và nhảy qua step tiếp theo thay vì văng Exception làm đứt gãy luồng chính.

---

## MODULE 2: ĐỘI NGŨ TÁC NHÂN TRÍ TUỆ (CORE AGENTS)

Cốt lõi kiến trúc tập trung ở `src/agent/qcteam/team_3/` hoạt động theo mô thức Workflow Hierarchical Loop (Vòng lặp phân cấp thứ bậc).

### 2.1 The Brain: `OrchestratorAgent` (`orchestrator_agent.py`)

Đây là trung tâm chỉ huy chiến dịch. 

**Vòng Đời Hoạt Động:**
1. **Pha Sinh Kế Hoạch (Planning Phase):** Gọi hàm `_generate_plans()`. LLM sẽ đọc list các Test Steps thô từ Module 1 và phải ép ra (Structured Output) đúng chuẩn 2 mảng là `testing_plan` và `post_testing_plan`.
2. **Pha Thực Thi (Execution Phase):** Lặp qua các plan trên bằng hàm trợ thủ `_execute_plan_steps()`.

**Hàm cốt lõi: `_execute_plan_steps(...)`**
*   **Tham số truy vấn:** `plan`, `final_results`, `step_index_offset`, `max_retries_per_step` (default: 20).
*   **Phân tích Logic Vòng lặp Kiểm Chứng:**
    ```python
    for attempt in range(max_retries_per_step):  # Cơ chế Retry bọc thép
        # [1] Ném bối cảnh cho VerifierAgent để kiểm tra thực trạng
        verification = await self.verifier.run(...)
        step_status = verification.get("status", "FAILED")
        
        # [2] Nếu xong HOẶC skip, bẻ gãy vòng lặp attempt
        if step_status in ["DONE", "SKIP"]: break
        
        # [3] Hard Limit check: Fail tới 5 lần thì đánh thức hệ thống dừng bước này lại.
        if step_status == "FAILED" and failed_retry_count >= 5: break
        
        # [4] Uỷ quyền thực thi Action do Verifier đưa ra cho ExecutorAgent
        execution_result = await self.executor.run(...)
    ```
*   **Edge Cases:** LLM bị mất bối cảnh (hallucinations) dẫn tới kẹt vòng lặp làm 1 thứ mãi. Hệ thống đang bảo mật chặt lỗi này thông qua check `failed_retry_count >= 5` và ngắt ngay nếu status là `FAILED` 5 lần liên tiếp.

### 2.2 Mắt Thần: `VerifierAgent` (`verifier_agent.py`)

Tránh cho Orchestrator phải "gồng" quá nhiều bối cảnh, hệ thống tách ra Verifier Agent là một LLM prompt hoàn toàn chuyên biệt cho tác vụ "Điều Tra" & "Đánh Giá".

**Logic phân tích nội bộ:**
- Tham số `current_step_goal` và `execution_history` đóng vai trò như Memory (trí nhớ ngắn hạn) mà VerifierAgent bơm vào bối cảnh hệ thống.
- Ép LLM luôn trả về chuẩn JSON nghiêm ngặt (Strict Schema Format): `{"status": enum[DONE, SKIP, FAILED, INPROGRESS], "analysis": str, "next_action": str}`.

**Edge Cases & Handle Error:**
- Hệ thống cố gắng serialize response của LLM qua JSON. Nếu LLM trả về markdown dạng ` ```json ... ``` ` dẫn tới parse crash -> Khối `except (json.JSONDecodeError, AttributeError, IndexError)` sẽ bắt lỗi và chủ động reset Status về lại trạng thái `"FAILED"` phòng xa, tiếp tục tiến hành error handler bên ngoài bảo vệ luồng sống sót của pipeline.

### 2.3 Người Hành Quyết: `ExecutorAgent` (`executor_agent.py`)

Là Agent duy nhất có khả năng kết nối Tools. Đọc `next_action` bằng ngôn ngữ tự nhiên, phân tích và chọn Tool phù hợp bằng tính năng Function Calling / Tool Calling của LLM.

**Tham số trong `run(...)`:**
- `analysis` (str): Chuỗi giải nghĩa lý do cho hành động.
- `next_action` (str): Lệnh được chỉ định từ Verifier.

**Kết nối Model Context Protocol (MCP):**
- ExecutorAgent không tự tay chạy browser, nó chứa `BrowserUseAgent` và `FileManagerAgent` là những sub-agents. 
- Nó kết nối các sub-agents này với `MCPClient` bằng cấu hình nằm ở biến môi trường (`MCP_SERVERS_CONFIG`), chia rẽ các servers `"playwright"` và `"filesystem"`. 

**Rủi ro tiềm ẩn hạn chế (Edge cases handled):**
- Khi `tool_calls` từ LLM bị rỗng do model tạch (failed to match a tool): Dòng 103 `if not decision_response or not decision_response.choices[0].message.tool_calls` bắt lỗi và trả về chuỗi báo lỗi *"Executor LLM failed to select a tool/agent"* chuẩn xác.
- Khi truy cập sub-agent không tồn tại, văng `ValueError` được bắt gọn ở cuối khối Try-Catch và ném lên bề mặt Logging UI.

---

## MODULE 3: CLIENTS & TÍCH HỢP

### 3.1 Model Context Protocol Client (`mcpclient.py`)

Đây là một cầu nối kiến trúc tân tiến, biến code python local của chúng ta trở thành client của các dịch vụ bên ngoài tuân theo chuẩn MCP.

**Logic Xử Lý Bên Trong:**
- Khởi tạo kết nối qua một trong 4 giao thức Transport (Hỗ trợ qua constructor config json `{"protocol": value}`): 
  1. **HTTP/SSE (`streamablehttp_client`, `sse_client`):** Truy xuất thông qua REST/Server-sent Events với port network.
  2. **Stdio (`stdio_client`):** Sinh kết nối luồng I/O trức tiếp qua Process PIPE (STDIN/STDOUT).
  3. **Direct (Internal Module):** Chạy ngay trong cùng Python Runtime qua Memory Pipe ngầm mà không cần tạo process khác (Rất mạnh mẽ cho local integration).
- `list_openai_tools()`: Chức năng wrap toàn bộ đặc tả (schema) khai báo từ MCP server vào thành format JSON Schema tiêu chuẩn để gửi rắp-ráp lên Endpoint OpenAI.
- `execute_tool()`: Hàm wrap lời gọi thực hiện. Nếu nhận chuỗi String thay vì Dict Parameters, nó sẽ tự cast qua JSON bằng khối try/catch.

### 3.2 Tương tác Atlassian Jira (`jira_client.py`)

Cung cấp SDK kết nối Atlassian qua Basic Authentication. Mọi thứ thiết kế tĩnh cho mục đích đồng bộ hoá.

**Phân tích kĩ năng bảo vệ code (Armor-Plated functions):**
- Truy xuất các endpoints của Jira thông qua library `requests`.
- Khi API gặp sự cố (Rate Limit, Server down, Network timeout), thay vì return im lặng, luồng sử dụng `response.raise_for_status()` để quăng exception HttpError. Exception này sẽ chặn luồng thực thi `app_test_cycle.py` để tránh hệ thống chạy auto-qa trên tập data NULL (dẫn đến xóa nhầm file local/logs rác).
- **Hàm xử lý Array Matching Dòng 112:**
  ```python
  matchedItem = next((item for item in items_list if item["$lastTestResult"]["testCase"]["id"] == target_id), None)
  ```
  Cách xử lý Pythonic xuất sắc để lấy testRunItemId thay cho một vòng lặp `for` lồng 4 nhánh if-else cồng kềnh. Trả ra `None` hoàn hảo nếu không match được target.

---

*Biên soạn bởi Technical Architect. Mọi thông tin chi tiết trên đóng vai trò là Sổ Tay Tham Chiếu (Reference Book) đảm bảo hiểu biết sâu sắc nhất lúc can thiệp vào tầng base của QC-Agent.*
