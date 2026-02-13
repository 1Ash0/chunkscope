"""
Chunker Service
Centralized logic for different text chunking strategies.
"""
import re
from typing import Any, Dict, List

def apply_chunking(
    text: str,
    method: str,
    chunk_size: int = 512,
    overlap: int = 50,
    **kwargs
) -> List[Dict[str, Any]]:
    """Apply chunking strategy to text."""
    if method == "fixed":
        return fixed_size_chunking(text, chunk_size, overlap)
    elif method == "sentence":
        return sentence_chunking(text, chunk_size, overlap)
    elif method == "paragraph":
        return paragraph_chunking(text, chunk_size)
    elif method == "recursive":
        return recursive_chunking(text, chunk_size, overlap)
    elif method == "semantic":
        # Note: In a real implementation, this would call the embedding model.
        # For preview purposes, we'll use a fast heuristic or the existing implementation if available.
        # For now, default to recursive if not fully implemented.
        return recursive_chunking(text, chunk_size, overlap)
    else:
        # Default to recursive
        return recursive_chunking(text, chunk_size, overlap)

def fixed_size_chunking(text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    """Simple fixed-size chunking with overlap."""
    chunks = []
    start = 0
    if chunk_size <= 0: chunk_size = 512
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "text": text[start:end],
            "start": start,
            "end": end,
        })
        if end >= len(text):
            break
        start = end - overlap if end < len(text) else len(text)
        if start >= end: # Safety against infinite loop
            start = end
    
    return chunks

def sentence_chunking(text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    """Chunk by sentences, respecting chunk_size limit."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    current_start = 0
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
                "end": current_start + len(current_chunk),
            })
            overlap_text = current_chunk[-overlap:] if overlap else ""
            current_start = current_start + len(current_chunk) - len(overlap_text)
            current_chunk = overlap_text
        
        current_chunk += sentence + " "
    
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start,
            "end": current_start + len(current_chunk),
        })
    
    return chunks

def paragraph_chunking(text: str, chunk_size: int) -> List[Dict[str, Any]]:
    """Chunk by paragraphs."""
    paragraphs = text.split("\n\n")
    
    chunks = []
    current_chunk = ""
    current_start = 0
    char_pos = 0
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "start": current_start,
                "end": current_start + len(current_chunk),
            })
            current_start = char_pos
            current_chunk = ""
        
        current_chunk += para + "\n\n"
        char_pos += len(para) + 2
    
    if current_chunk.strip():
        chunks.append({
            "text": current_chunk.strip(),
            "start": current_start,
            "end": current_start + len(current_chunk),
        })
    
    return chunks

def recursive_chunking(text: str, chunk_size: int, overlap: int) -> List[Dict[str, Any]]:
    """Recursive character text splitter."""
    separators = ["\n\n", "\n", ". ", " ", ""]
    
    def split_text(text: str, separators: List[str]) -> List[str]:
        if not separators:
            return [text]
        
        separator = separators[0]
        splits = text.split(separator) if separator else list(text)
        
        chunks = []
        current = ""
        
        for split in splits:
            piece = split + separator if separator else split
            if len(current) + len(piece) > chunk_size:
                if current:
                    chunks.append(current)
                if len(piece) > chunk_size:
                    chunks.extend(split_text(piece, separators[1:]))
                    current = ""
                else:
                    current = piece
            else:
                current += piece
        
        if current:
            chunks.append(current)
        
        return chunks
    
    raw_chunks = split_text(text, separators)
    
    chunks = []
    pos = 0
    for chunk in raw_chunks:
        # Avoid empty chunks
        if not chunk.strip():
            pos += len(chunk)
            continue
            
        chunks.append({
            "text": chunk,
            "start": pos,
            "end": pos + len(chunk),
        })
        pos += len(chunk)
    
    return chunks
