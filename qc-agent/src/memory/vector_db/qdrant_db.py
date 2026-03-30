from qdrant_client import QdrantClient, models
import config
from .base import AbstractVectorDB
from memory.embedding_provider import get_embedding_provider

class QdrantVectorDB(AbstractVectorDB):
    def __init__(self, **kwargs):
        print("Initializing Long-Term Memory with Qdrant...")
        
        # Lấy thông tin kết nối từ config
        qdrant_config = config.VECTOR_DB_CONFIG.get("qdrant", {})
        host = qdrant_config.get("host", "localhost")
        port = qdrant_config.get("port", 6333)

        self.client = QdrantClient(host=host, port=port)
        
        # Lấy nhà cung cấp embedding từ factory
        self.embedding_provider = get_embedding_provider()
        
        self.collection_name = "agent_long_term_memory"
        
        # Kiểm tra collection có tồn tại không
        self._ensure_collection_exists()
        
        print(f"Qdrant initialized. Collection '{self.collection_name}' has {self.count()} items.")

    def _ensure_collection_exists(self):
        """Kiểm tra collection: tồn tại và phải khớp số chiều vector."""
        collections_response = self.client.get_collections()
        existing_collections = [c.name for c in collections_response.collections]
        
        current_dim = self.embedding_provider.get_embedding_dimension()
        
        should_recreate = False
        if self.collection_name not in existing_collections:
            print(f"Collection '{self.collection_name}' not found. Creating a new one.")
            should_recreate = True
        else:
            # Kiểm tra số chiều của collection hiện tại
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            existing_dim = collection_info.config.params.vectors.size
            
            if existing_dim != current_dim:
                print(f"⚠️ Cảnh báo: Lệch số chiều vector (Cũ: {existing_dim}, Mới: {current_dim}). Đang khởi tạo lại bộ nhớ...")
                should_recreate = True
        
        if should_recreate:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=current_dim,
                    distance=models.Distance.COSINE
                )
            )
            print(f"✅ Collection '{self.collection_name}' đã được sẵn sàng với {current_dim} chiều.")

    def add_memories(self, texts: list[str]):
        """Nạp hàng loạt dữ liệu để tối ưu tốc độ."""
        if not texts: return
        
        # 1. Embed toàn bộ cục text
        vectors = self.embedding_provider.embed_batch(texts)
        start_id = self.count()
        
        points = []
        for i, (text, vector) in enumerate(zip(texts, vectors)):
            points.append(
                models.PointStruct(
                    id=start_id + i,
                    vector=vector,
                    payload={"text": text}
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True
        )

    def add_memory(self, text: str):
        self.add_memories([text])

    def retrieve(self, query: str, top_k: int) -> list[str]:
        if self.count() == 0:
            return []
            
        query_vector = self.embedding_provider.embed_text(query)
        
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        return [hit.payload['text'] for hit in search_results]

    def count(self) -> int:
        try:
            return self.client.count(collection_name=self.collection_name, exact=True).count
        except Exception:
            return 0
            
    def clear_collection(self):
        """Xóa và tạo lại collection để dọn dẹp toàn bộ dữ liệu."""
        print(f"Clearing all data from Qdrant collection: {self.collection_name}")
        self.client.delete_collection(collection_name=self.collection_name)
        self._ensure_collection_exists()
        print("✅ Collection cleared and recreated.")

