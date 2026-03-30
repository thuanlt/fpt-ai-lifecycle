# ./memory/vector_db/base.py
from abc import ABC, abstractmethod
from typing import List, Any

class AbstractVectorDB(ABC):
    """
    Abstract Base Class for a vector database.
    It defines the common interface that all vector database implementations must follow,
    ensuring they are interchangeable within the LongTermMemory manager.
    """

    @abstractmethod
    def add_memories(self, texts: List[str]):
        """
        Adds multiple text memories to the vector database in bulk.
        
        Args:
            texts (List[str]): A list of text contents to add.
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> List[str]:
        """
        Retrieves the top_k most relevant memories for a given query text.

        Args:
            query (str): The text query to search for.
            top_k (int): The number of most relevant results to return.

        Returns:
            List[str]: A list of the original text content of the most relevant memories.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Returns the total number of items in the vector database collection.

        Returns:
            int: The total count of vectors/documents.
        """
        pass

    @abstractmethod
    def clear_collection(self):
        """
        Deletes all items from the collection, effectively resetting it.
        """
        pass
