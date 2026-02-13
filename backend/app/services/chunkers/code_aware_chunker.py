from typing import List, Dict, Any
import re
from app.schemas.chunk import ChunkingConfig
from .base import BaseChunker

class CodeAwareChunker(BaseChunker):
    """
    Detects code blocks (```...```) and keeps them intact.
    Splits non-code text by newlines.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[Dict[str, Any]]:
        # Regex to find code blocks: ```...```
        # flags=re.DOTALL to match newlines inside .*?
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        
        chunks = []
        last_idx = 0
        
        for match in code_block_pattern.finditer(text):
            start, end = match.span()
            
            # Process text BEFORE the code block (prose)
            if start > last_idx:
                prose_text = text[last_idx:start]
                if prose_text.strip():
                    self._process_prose(prose_text, last_idx, chunks, config)
            
            # Add the code block as a single chunk (or split if HUGE? For now keep intact per requirements)
            chunks.append({
                "text": text[start:end],
                "start_char": start,
                "end_char": end,
                "metadata": {"type": "code"}
            })
            
            last_idx = end
            
        # Process remaining text
        if last_idx < len(text):
            prose_text = text[last_idx:]
            if prose_text.strip():
                self._process_prose(prose_text, last_idx, chunks, config)
                
        return chunks

    def _process_prose(self, text: str, offset: int, chunks: List[Dict[str, Any]], config: ChunkingConfig):
        # Split prose by newlines or just add as is?
        # Requirement: "Preserves code structure and indentation" - mostly applies to code blocks
        # "Detects code blocks... Keeps code blocks intact"
        # For prose, let's do a simple split if it's too long, or just paragraph split
        # To be safe and simple, let's treat prose as "ParagraphChunker" logic or simple newline split
        
        # Simple implementation: Split by double newlines for prose sections
        pattern = re.compile(r'\n\s*\n')
        last_end = 0
        for match in pattern.finditer(text):
            p_start, p_end = match.span()
            if p_start > last_end:
                chunks.append({
                    "text": text[last_end:p_start],
                    "start_char": offset + last_end,
                    "end_char": offset + p_start,
                    "metadata": {"type": "prose"}
                })
            last_end = p_end
            
        if last_end < len(text):
            chunks.append({
                "text": text[last_end:],
                "start_char": offset + last_end,
                "end_char": offset + len(text),
                "metadata": {"type": "prose"}
            })
