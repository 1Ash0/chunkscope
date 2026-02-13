import pytest
from app.services.chunkers.sentence_window_chunker import SentenceWindowChunker
from app.services.chunkers.paragraph_chunker import ParagraphChunker
from app.services.chunkers.code_aware_chunker import CodeAwareChunker
from app.services.chunkers.heading_based_chunker import HeadingBasedChunker
from app.services.chunkers.recursive_chunker import RecursiveChunker
from app.schemas.chunk import ChunkingConfig

SAMPLE_TEXT = """# Section 1
This is the first paragraph. It has two sentences.

This is the second paragraph.
It spans multiple lines.

## Subsection 1.1
Here is some code:
```python
def hello():
    print("Hello world")
    return True
```

### Subsection 1.1.1
Final paragraph here."""

@pytest.fixture
def config():
    return ChunkingConfig(
        method="test",
        chunk_size=50,
        overlap=0,
        window_size=2
    )

def test_sentence_window_chunker(config):
    chunker = SentenceWindowChunker()
    text = "Sentence one. Sentence two. Sentence three. Sentence four."
    
    # window_size=2, overlap=0 -> chunks of 2 sentences, step 2
    # [1, 2], [3, 4]
    chunks = chunker.chunk(text, config)
    assert len(chunks) == 2
    assert "Sentence one." in chunks[0]["text"]
    assert "Sentence two." in chunks[0]["text"]
    assert "Sentence three." in chunks[1]["text"]
    
    # window_size=2, overlap=1 -> chunks of 2 sentences, step 1
    # [1, 2], [2, 3], [3, 4]
    config.overlap = 1
    chunks = chunker.chunk(text, config)
    assert len(chunks) == 3
    assert "Sentence two." in chunks[0]["text"]
    assert "Sentence two." in chunks[1]["text"]

def test_paragraph_chunker(config):
    chunker = ParagraphChunker()
    # Paragraphs separated by \n\n
    text = "Para 1.\n\nPara 2.\n\nPara 3."
    
    config.chunk_size = 15 # small enough to force split
    chunks = chunker.chunk(text, config)
    
    assert len(chunks) == 3
    assert chunks[0]["text"] == "Para 1."
    assert chunks[1]["text"] == "Para 2."
    assert chunks[2]["text"] == "Para 3."
    
    # Test combining (if chunk_size is large enough and logic permits)
    # Current implementation greedy adds until full? 
    # Let's re-read implementation: compares (end - current_chunk_start) > config.chunk_size.
    # If size is HUGE, it might combine everything if logic allows?
    # Actually logic is: if adding next EXCEEDS, then split. 
    # So if chunk_size is small, it splits. If large, it combines.
    
    config.chunk_size = 1000
    chunks = chunker.chunk(text, config)
    # Should be 1 chunk properly? 
    # Implementation: 
    # if (end - current_chunk_start) > config.chunk_size: split
    # else: combine
    # So with size 1000, it should combine all 3.
    assert len(chunks) == 1
    assert "Para 3" in chunks[0]["text"]

def test_code_aware_chunker(config):
    chunker = CodeAwareChunker()
    text = "Prose before.\n```\ncode block\n```\nProse after."
    
    chunks = chunker.chunk(text, config)
    
    # Should detect 3 parts: Prose, Code, Prose
    assert len(chunks) >= 3
    
    # Find code chunk
    code_chunks = [c for c in chunks if c.get("metadata", {}).get("type") == "code"]
    assert len(code_chunks) == 1
    assert "code block" in code_chunks[0]["text"]
    assert "```" in code_chunks[0]["text"]

def test_heading_based_chunker(config):
    chunker = HeadingBasedChunker()
    text = "# Header 1\nContent 1\n## Header 2\nContent 2"
    
    chunks = chunker.chunk(text, config)
    
    assert len(chunks) == 2
    assert chunks[0]["metadata"]["heading"] == "Header 1"
    assert chunks[0]["metadata"]["level"] == 1
    assert "Content 1" in chunks[0]["text"]
    
    assert chunks[1]["metadata"]["heading"] == "Header 2"
    assert chunks[1]["metadata"]["level"] == 2
    assert "Content 2" in chunks[1]["text"]

def test_recursive_chunker(config):
    chunker = RecursiveChunker()
    text = "A" * 100
    config.chunk_size = 20
    config.overlap = 0
    
    chunks = chunker.chunk(text, config)
    assert len(chunks) == 5
    assert len(chunks[0]["text"]) == 20
