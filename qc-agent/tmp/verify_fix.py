from memory.vector_db.qdrant_db import QdrantVectorDB
import config
import os

def test_qdrant_fix():
    print("Testing QdrantVectorDB fix...")
    try:
        db = QdrantVectorDB()
        print(f"Collection count: {db.count()}")
        
        # Test add memory
        # db.add_memory("This is a test memory.") # Skip adding to avoid polluting
        
        # Test retrieve
        results = db.retrieve("xin chào", top_k=5)
        print(f"Retrieved {len(results)} results.")
        for res in results:
            print(f"- {res}")
        print("Test PASSED!")
    except Exception as e:
        print(f"Test FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qdrant_fix()
