from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.chunk import ChunkingConfig

class BaseChunker(ABC):
    """
    Abstract base class for all chunking methods.
    """
    
    @abstractmethod
    def chunk(self, text: str, config: ChunkingConfig) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        
        Args:
            text: The text to chunk
            config: Configuration for chunking (contains window_size, overlap, etc.)
            
        Returns:
            List of dicts, each containing:
            - text: str
            - start_char: int
            - end_char: int
            - metadata: dict (optional)
        """
        pass
