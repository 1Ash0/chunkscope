from typing import List
from app.schemas.chunk import ChunkingConfig
from app.core.logging import get_logger
from app.services.chunkers import get_chunker

logger = get_logger(__name__)

class ChunkingService:
    """
    Service to handle text chunking using various strategies.
    Delegates to specific Chunker implementations.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[dict]:
        """
        Chunk text using the configured method.
        """
        method = config.method if config.method else "recursive"
        logger.info("chunking_text", method=method, length=len(text))
        
        chunker = get_chunker(method)
        return chunker.chunk(text, config)

chunking_service = ChunkingService()

