input: từ jira, link wiki trữ các tài liệu, wireframe,…

output: đẩy testcase vào jira (text hoặc script)

- Tối ưu, chuẩn hóa input, preprocess (Tầng input)
    
    
    | Giai đoạn/Loại Test | Input Thô (Raw Source) | Sub-agent Tiền xử lý | Metadata Output (Gửi cho Claude) |
    | --- | --- | --- | --- |
    | **Mockup / Wireframe** | Ảnh (.png/.jpg) hoặc Export từ Figma API. | **DeepSeek-OCR** | JSON chứa: Danh sách Component (`type`, `label`, `id_dự_kiến`), Tọa độ (`x, y`), và Luồng chuyển trang (`nav_to`). |
    | **Exploratory (Thăm dò)** | Mã nguồn HTML (Full DOM) + Link môi trường Dev. | **Qwen3-32B** | **UI Map:** Cây cấu trúc rút gọn chỉ gồm các thẻ `<input>`, `<button>`, `<a>` kèm theo thuộc tính `name`, `id`, `class`. |
    | **Regression (Hồi quy)** | Git Diff (Patch file) + Danh sách Test Case cũ. | **Kimi-K2.5** | **Impact Zone:** Danh sách các file bị sửa và các hàm (Functions) liên quan bị ảnh hưởng trực tiếp. |
    | **Functional (API)** | Swagger JSON / OpenAPI Spec. | **FPT.AI-KIE-v1.7** | **API Signature:** Danh sách Endpoints, Method, Params bắt buộc, và Schema của Response mẫu. |
    | **Non-Functional (Sec)** | URL Endpoint + Auth Header. | **gpt-oss-120b** | **Attack Surface:** Danh sách các đầu vào nhạy cảm có nguy cơ bị Injection hoặc lỗi Auth. |
    
    ## 1. CẤU TRÚC PAYLOAD TỔNG QUÁT (UNIVERSAL SCHEMA)
    
    Mọi yêu cầu gửi lên Claude đều phải tuân thủ schema JSON sau để đảm bảo tính nhất quán:
    
    ```
    {
      "request_id": "UUID_STRING",
      "test_phase": "MOCKUP | EXPLORATORY | REGRESSION | FUNCTIONAL",
      "objective": "Mô tả ngắn gọn mục tiêu cần đạt được",
      "metadata": {
         // Dữ liệu đã được nén bởi FPT Models
      },
      "context_pointers": {
         // Đường dẫn đến dữ liệu thô (Claude không đọc, chỉ để chuyển tiếp cho Worker)
      },
      "constraints": {
        "target_framework": "Playwright",
        "language": "TypeScript",
        "output_format": "JSON_TOOL_CALL"
      }
    }
    ```
    
    ## 2. CHI TIẾT THEO TỪNG GIAI ĐOẠN (SCENARIO-BASED)
    
    ### A. Giai đoạn: Mockup / Wireframe
    
    - **Người thực hiện tiền xử lý:** `DeepSeek-OCR` hoặc `Qwen3-VL`.
    - **Thông tin gửi Claude:**
        
        ```
        "metadata": {
          "screen_name": "Login_Dashboard",
          "elements_detected": [
            {"id": "input_01", "type": "text_field", "label": "Email Address"},
            {"id": "btn_02", "type": "button", "label": "Login with Google"},
            {"id": "link_03", "type": "hyperlink", "label": "Forgot Password?"}
          ],
          "layout_description": "Form nằm chính giữa, logo phía trên, nút Submit ở cuối form."
        },
        "context_pointers": { "image_ref": "s3://bucket/wireframe_v1.png" }
        ```
        
    
    ### B. Giai đoạn: Exploratory (Thăm dò - Dev vừa xong)
    
    - **Người thực hiện tiền xử lý:** `Qwen3-32B` (Nén HTML).
    - **Thông tin gửi Claude:**
        
        ```
        "metadata": {
          "ui_map": {
            "critical_selectors": ["#login-email", "#login-pass", ".submit-action"],
            "api_associations": ["POST /api/v1/login", "GET /api/v1/user-profile"]
          },
          "new_features_detected": "Bổ sung thêm checkbox 'Remember me' và ReCaptcha v3."
        },
        "context_pointers": { "full_dom_ref": "s3://bucket/dom_snapshot.html" }
        ```
        
    
    ### C. Giai đoạn: Regression (Hồi quy)
    
    - **Người thực hiện tiền xử lý:** `Kimi-K2.5` (Phân tích Impact).
    - **Thông tin gửi Claude:**
        
        ```
        "metadata": {
          "impact_analysis": {
            "modified_files": ["auth_service.py", "login_controller.ts"],
            "affected_modules": ["Authentication", "Session Management"],
            "risk_level": "High (Sửa logic mã hóa mật khẩu)"
          },
          "existing_tests_to_rerun": ["test_auth_flow.spec.ts", "test_logout.spec.ts"]
        },
        "context_pointers": { "git_diff_ref": "s3://bucket/commit_hash.patch" }
        ```
        
    
    ### D. Loại hình: Non-Functional (API / Security / Performance)
    
    - **Thông tin gửi Claude:**
        
        ```
        "metadata": {
          "api_contract": {
            "endpoint": "/api/v1/payment/checkout",
            "method": "POST",
            "required_headers": ["Authorization", "X-Trace-ID"]
          },
          "perf_targets": { "max_latency": "500ms", "concurrency": 200 }
        },
        "context_pointers": { "swagger_ref": "s3://bucket/payment_api.json" }
        ```
        
- Tối ưu kiến trúc điều phối và loại model FPT sử dụng (Tầng orchestrator)
    
    **Nhiệm vụ:** Lập kế hoạch chiến lược và Xuất lệnh thực thi có cấu trúc.
    
    - **Model:** **Claude 3.5 Sonnet**.
    - **Cơ chế vận hành:** * Nhận Metadata tinh gọn từ Lớp 1.
        - Sử dụng khả năng suy luận (Reasoning) để chia nhỏ yêu cầu kiểm thử thành các nhiệm vụ con (Sub-tasks).
        - **Xuất Tool-calls:** Claude trực tiếp trả về định dạng JSON chứa: tên Worker cần gọi, tham số thực thi và Context Pointer cần thiết.
    - **Yêu cầu kỹ thuật:** Sử dụng System Prompt nghiêm ngặt để ép Claude luôn trả về dữ liệu có cấu trúc (Strict JSON mode), loại bỏ các đoạn hội thoại giải thích dư thừa.
    - Đầu ra:
    
    ```
    {
      "header": {
        "task_id": "UUID",
        "parent_request_id": "UUID",
        "worker_type": "CODE_GEN | VISION_ANALYSIS | LOG_SUMMARY",
        "priority": "P0 | P1 | P2"
      },
      "task_specification": {
        "action": "Tên hành động cụ thể (e.g., GEN_PLAYWRIGHT_SCRIPT)",
        "description": "Mô tả chi tiết mục tiêu của tác vụ con này",
        "granularity": "Nhiệm vụ này là Atomic hay cần thêm các bước nhỏ?"
      },
      "context_references": {
        "pointers": [
          {"type": "HTML_DOM", "ref": "s3://path/to/dom.json", "description": "Cấu trúc UI đã nén"},
          {"type": "SWAGGER_SPEC", "ref": "s3://path/to/api.json", "description": "Định nghĩa API"},
          {"type": "WIREFRAME_METADATA", "ref": "s3://path/to/vision.json", "description": "Dữ liệu OCR từ thiết kế"}
        ],
        "metadata_summary": "Bản tóm tắt ngắn gọn từ tầng Pre-processing để Worker có 'Big Picture'."
      },
      "technical_constraints": {
        "framework": "Playwright | Pytest | K6",
        "language": "TypeScript | Python",
        "design_pattern": "Page Object Model (POM) | AAA Pattern",
        "naming_convention": "camelCase | snake_case"
      },
      "output_specification": {
        "format": "STRICT_JSON",
        "required_fields": ["code_content", "test_data", "selectors_used", "potential_risks"],
        "schema_ref": "s3://schemas/worker_output_v1.json"
      }
    }
    ```
    
    [Danh sách model in modas](https://www.notion.so/Danh-s-ch-model-in-modas-327963d2aa078094a841e61cf6ed6a98?pvs=21)
    
    - Phát triển sau: SaoLa-planner (The Adapter)
        
         Phát triển thêm (claude chỉ cần gửi ý định, saola sẽ tạo json action)
        
- Tối ưu system prompt, Agent skill (Tầng worker)
    - Bảng system prompt cho từng agent
    - Bảng tổng hợp các skill cho từng agent
    - Cần agent review code của các file test
    - Chạy file test và đưa ra kết quả + nguyên nhân fail + phân loại bug (thông qua code của dev + file test) → gợi ý solution để sửa
    - Đưa kết quả lên jira và thông báo trong group (tele, teams), assign trực tiếp người quản lý đoạn code đấy
    
    Mọi Worker sau khi hoàn thành nhiệm vụ phải trả về một JSON theo cấu trúc sau:
    
    ```
    {
      "header": {
        "task_id": "UUID",
        "status": "SUCCESS | FAILED | RECOVERED",
        "worker_id": "Qwen3-Coder-480B | DeepSeek-V3.2",
        "duration_ms": 12500
      },
      "artifacts": {
        "code_content": "Chuỗi mã nguồn (Base64 hoặc Plain text)",
        "file_path": "path/to/test/script.spec.ts",
        "test_data": {
          "payload": "Dữ liệu mock đã sinh",
          "format": "JSON"
        }
      },
      "verification_report": {
        "syntax_check": "PASS | FAIL",
        "sandbox_run": {
          "result": "PASS | FAIL",
          "logs": "Tóm tắt log từ sandbox",
          "retries": 1
        }
      },
      "insights": {
        "complexity_score": 0.75,
        "confidence_score": 0.92,
        "potential_risks": ["Selector có thể bị thay đổi nếu UI update", "API timeout potential"],
        "summary": "Mô tả ngắn gọn những gì đã thực hiện"
      },
      "telemetry": {
        "prompt_tokens": 1200,
        "completion_tokens": 2500,
        "total_cost_usd": 0.0035
      }
    }
    ```