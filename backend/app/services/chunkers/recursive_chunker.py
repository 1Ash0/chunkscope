from typing import List, Dict, Any
import re
from app.schemas.chunk import ChunkingConfig
from .base import BaseChunker

class RecursiveChunker(BaseChunker):
    """
    Splits text recursively using a list of separators.
    Standard separators: ["\n\n", "\n", " ", ""]
    """
    
    def __init__(self):
        self.separators = ["\n\n", "\n", " ", ""]

    def chunk(self, text: str, config: ChunkingConfig) -> List[Dict[str, Any]]:
        return self._recursive_split(text, self.separators, config.chunk_size, config.overlap)

    def _recursive_split(self, text: str, separators: List[str], chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
        final_chunks = []
        if not separators:
            # Base case: if no separators left, hard split by character
            return self._create_chunks(text, chunk_size, overlap)
            
        separator = separators[0]
        new_separators = separators[1:]
        
        # Split by current separator
        if separator == "":
            splits = list(text)
        else:
            # Use regex literal to escape special chars if needed, or just basic split
            # For simplicity using standard string split for now, but regex is better for consistency
            splits = text.split(separator)
            
        # Re-assemble chunks
        current_chunk = []
        current_len = 0
        
        for split in splits:
            split_len = len(split)
            if current_len + split_len + len(separator) > chunk_size:
                # If current chunk is full, verify if we need to split the LAST element further
                # But here we just finalize current_chunk and start new
                if current_chunk:
                    joined_text = separator.join(current_chunk)
                    if len(joined_text) > chunk_size:
                        # Recursively split this oversized chunk
                        sub_chunks = self._recursive_split(joined_text, new_separators, chunk_size, overlap)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(self._make_chunk(joined_text, text))
                    
                    current_chunk = []
                    current_len = 0
            
            current_chunk.append(split)
            current_len += split_len + len(separator)
            
        # Handle last chunk
        if current_chunk:
            joined_text = separator.join(current_chunk)
            if len(joined_text) > chunk_size:
                sub_chunks = self._recursive_split(joined_text, new_separators, chunk_size, overlap)
                final_chunks.extend(sub_chunks)
            else:
                final_chunks.append(self._make_chunk(joined_text, text))
                
        return final_chunks

    def _create_chunks(self, text: str, size: int, overlap: int) -> List[Dict[str, Any]]:
        """Hard split by character length"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunk_text = text[start:end]
            chunks.append(self._make_chunk(chunk_text, text, start))
            start += size - overlap
        return chunks

    def _make_chunk(self, chunk_text: str, original_text: str, start_index: int = -1) -> Dict[str, Any]:
        # Note: Finding exact start_char in original text can be tricky if duplicates exist.
        # Ideally we pass offsets down the recursion. 
        # For this quick implementation, we'll try to find it or just return text.
        # In a real robust implementation, we track start_offset through recursion.
        
        # This is a simplified version.
        if start_index == -1:
            # Try to find text (this is naive and fails with duplicates)
            start_index = original_text.find(chunk_text)
            
        return {
            "text": chunk_text,
            "start_char": start_index,
            "end_char": start_index + len(chunk_text)
        }
