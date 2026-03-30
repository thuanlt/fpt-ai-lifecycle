# longterm_memory.py
"""
Manages long-term memory by acting as a wrapper around a vector database.
This class is responsible for interacting with the chosen vector DB
via a common interface, and optionally reranking the results for higher relevance.
"""
from .vector_db import get_vector_db, AbstractVectorDB
import config

# Conditionally import the CrossEncoder to avoid a hard dependency if not used
if config.USE_RERANKER:
    try:
        from sentence_transformers.cross_encoder import CrossEncoder
    except ImportError:
        print("Warning: `sentence-transformers` is not installed, but USE_RERANKER is True. Reranking will be disabled.")
        print("Please install it with: pip install sentence-transformers")
        CrossEncoder = None
else:
    CrossEncoder = None


class LongTermMemory:
    def __init__(self):
        """
        Initializes the LongTermMemory manager.
        It uses a factory to create the appropriate vector database instance
        and initializes a reranker model if configured to do so.
        """
        print("Initializing Long-Term Memory...")
        
        # Use the factory to get the configured vector database instance
        self.db: AbstractVectorDB = get_vector_db(config.VECTOR_DB_CONFIG)
        
        self.reranker = None
        if config.USE_RERANKER and CrossEncoder:
            print(f"Initializing reranker model: {config.RERANKER_MODEL_NAME}")
            self.reranker = CrossEncoder(config.RERANKER_MODEL_NAME)
        
        print(f"Long-Term Memory initialized with provider: '{config.VECTOR_DB_CONFIG.get('provider')}'. Reranking is {'ENABLED' if self.reranker else 'DISABLED'}.")

    def add_memories(self, texts: list[str]):
        """
        Adds multiple memories to the LTM in batch.
        """
        self.db.add_memories(texts)

    def add_memory(self, text: str):
        self.add_memories([text])

    def retrieve(self, query: str, top_k_broad: int, top_k_final: int) -> list[str]:
        """
        Retrieves relevant memories from the LTM. It performs a broad search
        and then optionally reranks the results for higher relevance.

        Args:
            query (str): The text query to search for.
            top_k_broad (int): The number of results to fetch initially from the vector DB.
            top_k_final (int): The final number of results to return after reranking.

        Returns:
            list[str]: A list of the most relevant memories.
        """
        # 1. Broad retrieval from the vector database
        broad_results = self.db.retrieve(query, top_k_broad)

        if not broad_results:
            return []

        # 2. Conditionally rerank the results
        if self.reranker:
            # print(f"Reranking {len(broad_results)} results for query: '{query}'")
            
            # Create pairs of [query, document] for the cross-encoder
            query_doc_pairs = [[query, doc] for doc in broad_results]
            
            # Predict the relevance scores
            scores = self.reranker.predict(query_doc_pairs)
            
            # Combine scores with documents and sort
            scored_docs = sorted(zip(scores, broad_results), key=lambda x: x[0], reverse=True)
            
            # Extract the top N documents after reranking
            reranked_results = [doc for score, doc in scored_docs]
            
            return reranked_results[:top_k_final]
        else:
            # If no reranker, simply return the top N results from the broad search
            return broad_results[:top_k_final]


    def count(self) -> int:
        """
        Returns the total number of items in the long-term memory.

        Returns:
            int: The total count of items.
        """
        return self.db.count()

