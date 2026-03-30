import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import Documents, Embeddings, EmbeddingFunction
import config
from .base import AbstractVectorDB
from memory.embedding_provider import get_embedding_provider

class CustomEmbeddingFunction(EmbeddingFunction):
    """
    Một lớp vỏ (wrapper) tùy chỉnh để tích hợp embedding provider của chúng ta
    với cơ chế EmbeddingFunction của ChromaDB.
    """
    def __init__(self):
        # Lấy nhà cung cấp embedding từ factory ngay khi khởi tạo
        self.provider = get_embedding_provider()

    def __call__(self, input: Documents) -> Embeddings:
        """
        ChromaDB sẽ gọi hàm này và truyền vào một danh sách các văn bản.
        Chúng ta xử lý chúng theo lô.
        """
        embeddings = []
        for text in input:
            # Sử dụng provider đã được khởi tạo để tạo vector
            embeddings.append(self.provider.embed_text(text))
        return embeddings

class ChromaVectorDB(AbstractVectorDB):
    def __init__(self, **kwargs):
        print("Initializing Long-Term Memory with ChromaDB...")
        
        chroma_config = config.VECTOR_DB_CONFIG.get("chroma", {})
        db_path = chroma_config.get("path", "./chroma_db")
        
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = "agent_long_term_memory"
        
        # Khởi tạo và sử dụng CustomEmbeddingFunction
        # Nó sẽ tự động chọn local hoặc openai dựa trên config
        embedding_function = CustomEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_function
        )
        
        print(f"ChromaDB initialized. Provider: {config.EMBEDDING_API_PROVIDER}. Collection '{self.collection_name}' has {self.count()} items.")

    def add_memory(self, text: str):
        doc_id = str(self.count())
        self.collection.add(
            documents=[text],
            ids=[doc_id]
        )

    def retrieve(self, query: str, top_k: int) -> list[str]:
        if self.count() == 0:
            return []
            
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.count())
        )
        
        return results['documents'][0]

    def count(self) -> int:
        return self.collection.count()
        
    def clear_collection(self):
        """Xóa và tạo lại collection để dọn dẹp toàn bộ dữ liệu."""
        print(f"Clearing all data from ChromaDB collection: {self.collection_name}")
        self.client.delete_collection(name=self.collection_name)
        embedding_function = CustomEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=embedding_function
        )
        print("✅ Collection cleared and recreated.")

