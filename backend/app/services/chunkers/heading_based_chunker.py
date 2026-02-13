from typing import List, Dict, Any
import re
from app.schemas.chunk import ChunkingConfig
from .base import BaseChunker

class HeadingBasedChunker(BaseChunker):
    """
    Splits text based on Markdown headings (#, ##, ###).
    Each chunk includes the heading and the content following it.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[Dict[str, Any]]:
        # Regex to match headers: start of line (or string), #+, space, text
        # re.MULTILINE is essential for ^ to match start of lines
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        matches = list(heading_pattern.finditer(text))
        chunks = []
        
        if not matches:
            # No headings, return whole text as one chunk (or fallback to another method?)
            # Returning whole text for now as per "Heading Based" logic
            return [{
                "text": text,
                "start_char": 0,
                "end_char": len(text)
            }]
            
        # Handle text before first heading
        if matches[0].start() > 0:
            chunks.append({
                "text": text[0:matches[0].start()],
                "start_char": 0,
                "end_char": matches[0].start(),
                "metadata": {"heading": None, "level": 0}
            })
            
        for i, match in enumerate(matches):
            start = match.start()
            # End is start of next match, or end of text
            end = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            heading_content = match.group(2).strip()
            level = len(match.group(1))
            
            chunks.append({
                "text": text[start:end],
                "start_char": start,
                "end_char": end,
                "metadata": {
                    "heading": heading_content,
                    "level": level
                }
            })
            
        return chunks
