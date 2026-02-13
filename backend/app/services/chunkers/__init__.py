from .base import BaseChunker
from .recursive_chunker import RecursiveChunker
from .semantic_chunker import SemanticChunker
from .sentence_window_chunker import SentenceWindowChunker
from .paragraph_chunker import ParagraphChunker
from .code_aware_chunker import CodeAwareChunker
from .heading_based_chunker import HeadingBasedChunker
from app.core.errors import AppException

CHUNKER_REGISTRY = {
    "recursive": RecursiveChunker,
    "semantic": SemanticChunker,
    "sentence_window": SentenceWindowChunker,
    "paragraph": ParagraphChunker,
    "code_aware": CodeAwareChunker,
    "heading_based": HeadingBasedChunker,
}

def get_chunker(method: str) -> BaseChunker:
    """
    Factory function to get a chunker instance.
    """
    chunker_class = CHUNKER_REGISTRY.get(method.lower())
    if not chunker_class:
        # Default fallback or raise error?
        # Requirement: "Maps method names to chunker classes"
        # If unknown, maybe default to recursive? Or raise.
        # Let's raise for now to be explicit.
        raise AppException(f"Unknown chunking method: {method}", 400)
        
    return chunker_class()
