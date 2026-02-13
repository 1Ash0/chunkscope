from typing import List, Dict, Any
import re
from app.schemas.chunk import ChunkingConfig
from .base import BaseChunker

class ParagraphChunker(BaseChunker):
    """
    Splits text into paragraphs based on double newlines.
    Combines small paragraphs if they are under min_chunk_size.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[Dict[str, Any]]:
        # Split by double newlines (or more)
        # Using lookahead/lookbehind or just finditer to keep track of offsets
        
        if not text.strip():
            return []
            
        chunks = []
        paragraphs = re.split(r'(\n\s*\n)', text)
        
        current_chunk = ""
        current_start = 0
        pos = 0
        
        for i in range(0, len(paragraphs), 2):
            para = paragraphs[i]
            # Capture separator if it exists (it's in the odd indices)
            sep = paragraphs[i+1] if i + 1 < len(paragraphs) else ""
            
            # Check if adding this paragraph exceeds max_chunk_size
            if len(current_chunk) + len(para) > config.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "start_char": current_start,
                    "end_char": current_start + len(current_chunk)
                })
                # Reset
                current_start = pos
                current_chunk = para + sep
            else:
                current_chunk += para + sep
                
            pos += len(para) + len(sep)
            
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "start_char": current_start,
                "end_char": current_start + len(current_chunk)
            })
            
        return chunks
