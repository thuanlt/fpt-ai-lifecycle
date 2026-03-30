# ./memory/vector_db/factory.py
from .base import AbstractVectorDB
from .chroma_db import ChromaVectorDB
from .qdrant_db import QdrantVectorDB

def get_vector_db(db_config: dict) -> AbstractVectorDB:
    """
    Factory function to create a vector database instance based on configuration.

    Args:
        db_config (dict): A dictionary containing the database provider and its specific config.
                          Example:
                          {
                              "provider": "qdrant",
                              "config": {
                                  "location": ":memory:",
                                  "collection_name": "agent_ltm",
                                  "embedding_model_name": "all-MiniLM-L6-v2"
                              }
                          }

    Returns:
        AbstractVectorDB: An instance of a class that inherits from AbstractVectorDB.
    
    Raises:
        ValueError: If the provider in the config is not supported.
    """
    provider = db_config.get("provider")
    config = db_config.get("config", {})

    if provider == "chroma":
        return ChromaVectorDB(**config)
    elif provider == "qdrant":
        return QdrantVectorDB(**config)
    else:
        raise ValueError(f"Unsupported vector database provider: '{provider}'")
