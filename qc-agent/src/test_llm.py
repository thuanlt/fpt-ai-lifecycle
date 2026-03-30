import os
import requests
from dotenv import load_dotenv
import urllib.request
print("🔍 Proxy mà môi trường này đang dùng để ra mạng là:", urllib.request.getproxies())

# Load các biến môi trường từ file .env
load_dotenv()

def test_fpt_model():
    # Lấy thông tin từ file .env
    api_key = os.getenv("FPT_API_KEY")
    base_url = os.getenv("FPT_BASE_URL", "https://mkp-api.fptcloud.com").rstrip("/")
    model_name = "Qwen3-32B"
    
    # Endpoint cho chat completions
    endpoint_url = f"{base_url}/v1/chat/completions"
    
    if not api_key:
        print("❌ Lỗi: Không tìm thấy FPT_API_KEY trong file .env")
        return

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt được gửi tới model
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say this is test"}
    ]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    print(f"🚀 Đang gửi yêu cầu test tới model: '{model_name}'...")
    print(f"🔗 URL API: {endpoint_url}")
    
    try:
        response = requests.post(endpoint_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Lấy nội dung câu trả lời
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "Không có nội dung")
            
            print("\n" + "="*60)
            print(f"🤖 PHẢN HỒI TỪ {model_name}:")
            print("="*60)
            print(content)
            print("="*60)
            
            # In ra thống kê số token sử dụng (nếu có)
            usage = result.get("usage", {})
            if usage:
                print(f"\n📊 Thống kê token: Tổng = {usage.get('total_tokens', 0)} "
                      f"(Prompt = {usage.get('prompt_tokens', 0)}, "
                      f"Sinh ra = {usage.get('completion_tokens', 0)})")
        else:
            print(f"❌ Lỗi HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"⚠️ Đã xảy ra lỗi hệ thống: {e}")

if __name__ == "__main__":
    test_fpt_model()