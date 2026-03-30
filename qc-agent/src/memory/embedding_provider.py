from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import config

class AbstractEmbeddingProvider(ABC):
    """
    Một giao diện trừu tượng cho các nhà cung cấp dịch vụ embedding.
    """
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Tạo vector embedding cho một đoạn văn bản."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Tạo vector embedding cho nhiều đoạn văn bản cùng lúc."""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Trả về số chiều của vector embedding."""
        pass

class OpenAIEmbeddingProvider(AbstractEmbeddingProvider):
    """Sử dụng API của OpenAI hoặc nhà cung cấp tương thích để tạo embedding."""
    def __init__(self):
        import requests
        self.api_key = config.EMBEDDING_MODEL_API_KEY
        base_url = config.EMBEDDING_MODEL_BASE_URL.rstrip("/")
        if "/v1" not in base_url:
            base_url += "/v1"
        self.endpoint_url = f"{base_url}/embeddings"
        self.model_name = config.EMBEDDING_MODEL_NAME_OPENAI
        self._dimension = config.EMBEDDING_DIMENSION_OPENAI
        print(f"🔌 FPT Cloud Embedding Provider initialized. Model: {self.model_name}, Dimension: {self._dimension}")

    def embed_text(self, text: str) -> list[float]:
        embeddings = self.embed_batch([text])
        return embeddings[0] if embeddings else [0.0] * self._dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        import requests
        import json
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Tiền xử lý: e5 model require 'query: ' prefix
        processed_texts = []
        is_e5 = "e5" in self.model_name.lower()
        for t in texts:
            if is_e5:
                processed_texts.append(f"query: {t}")
            else:
                processed_texts.append(t)

        payload = {
            "model": self.model_name,
            "input": processed_texts
        }
        
        try:
            response = requests.post(
                self.endpoint_url, 
                headers=headers, 
                json=payload, 
                timeout=120.0 # Tăng timeout khi nạp batch
            )
            if response.status_code == 200:
                result = response.json()
                # Phải lấy đúng thứ tự từ response.data
                data_list = result.get("data", [])
                # Sắp xếp theo index nếu có (OpenAI API trả về index)
                sorted_data = sorted(data_list, key=lambda x: x.get('index', 0))
                return [item.get("embedding", []) for item in sorted_data]
            else:
                print(f"[EMBED-LOG] ❌ Lỗi API Embedding Batch: {response.status_code} - {response.text}")
                return [[0.0] * self._dimension] * len(texts)
        except Exception as e:
            print(f"[EMBED-LOG] ❌ Lỗi kết nối Embedding Batch: {str(e)}")
            return [[0.0] * self._dimension] * len(texts)

    def get_embedding_dimension(self) -> int:
        return self._dimension

class LocalEmbeddingProvider(AbstractEmbeddingProvider):
    """Sử dụng mô hình SentenceTransformer chạy trên máy cục bộ."""
    def __init__(self):
        print(f"Đang tải mô hình embedding cục bộ: {config.EMBEDDING_MODEL_NAME_LOCAL}...")
        self.encoder = SentenceTransformer(config.EMBEDDING_MODEL_NAME_LOCAL)
        print("✅ Tải mô hình cục bộ thành công.")

    def embed_text(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # sentence-transformers trực tiếp hỗ trợ list đầu vào cho việc batching hiệu quả
        return self.encoder.encode(texts).tolist()

def get_embedding_provider() -> AbstractEmbeddingProvider:
    """
    Factory function: Đọc config và trả về instance của provider tương ứng.
    """
    provider = config.EMBEDDING_API_PROVIDER.lower()
    if provider == "openai":
        print("🔌 Sử dụng OpenAI (API) để tạo embedding.")
        return OpenAIEmbeddingProvider()
    elif provider == "local":
        print("💻 Sử dụng SentenceTransformer (cục bộ) để tạo embedding.")
        return LocalEmbeddingProvider()
    else:
        raise ValueError(f"Nhà cung cấp embedding không xác định: {provider}. Vui lòng kiểm tra config.py.")
