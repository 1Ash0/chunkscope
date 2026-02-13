import sys
import os

# Ensure backend is in path
sys.path.append(os.getcwd())

from app.services.chunkers.sentence_window_chunker import SentenceWindowChunker
from app.services.chunkers.paragraph_chunker import ParagraphChunker
from app.services.chunkers.code_aware_chunker import CodeAwareChunker
from app.services.chunkers.heading_based_chunker import HeadingBasedChunker
from app.services.chunkers.recursive_chunker import RecursiveChunker
from app.schemas.chunk import ChunkingConfig

def get_config():
    return ChunkingConfig(
        method="test",
        chunk_size=50,
        overlap=0,
        window_size=2
    )

def test_sentence_window_chunker():
    print("Testing SentenceWindowChunker...")
    try:
        config = get_config()
        chunker = SentenceWindowChunker()
        text = "Sentence one. Sentence two. Sentence three. Sentence four."
        
        # Test 1
        chunks = chunker.chunk(text, config)
        print(f"  Result 1 (window=2, overlap=0): {[c['text'] for c in chunks]}")
        assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
        
        # Test 2
        config.overlap = 1
        chunks = chunker.chunk(text, config)
        print(f"  Result 2 (window=2, overlap=1): {[c['text'] for c in chunks]}")
        assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

def test_paragraph_chunker():
    print("Testing ParagraphChunker...")
    try:
        config = get_config()
        chunker = ParagraphChunker()
        text = "Para 1.\n\nPara 2.\n\nPara 3."
        
        config.chunk_size = 100
        chunks = chunker.chunk(text, config)
        print(f"  Result 1 (size=100): {[c['text'] for c in chunks]}")
        assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
        
        config.chunk_size = 1000
        chunks = chunker.chunk(text, config)
        print(f"  Result 2 (size=1000): {[c['text'] for c in chunks]}")
        assert len(chunks) == 1, f"Expected 1 chunk, got {len(chunks)}"
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

def test_code_aware_chunker():
    print("Testing CodeAwareChunker...")
    try:
        config = get_config()
        chunker = CodeAwareChunker()
        text = "Prose before.\n```\ncode block\n```\nProse after."
        
        chunks = chunker.chunk(text, config)
        print(f"  Result: {[c['text'] for c in chunks]}")
        assert len(chunks) >= 3, f"Expected >=3 chunks, got {len(chunks)}"
        
        code_chunks = [c for c in chunks if c.get("metadata", {}).get("type") == "code"]
        assert len(code_chunks) == 1, "Expected 1 code chunk"
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

def test_heading_based_chunker():
    print("Testing HeadingBasedChunker...")
    try:
        config = get_config()
        chunker = HeadingBasedChunker()
        text = "# Header 1\nContent 1\n## Header 2\nContent 2"
        
        chunks = chunker.chunk(text, config)
        print(f"  Result: {[c['text'] for c in chunks]}")
        assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

def test_recursive_chunker():
    print("Testing RecursiveChunker...")
    try:
        config = get_config()
        chunker = RecursiveChunker()
        text = "A" * 100
        config.chunk_size = 20
        config.overlap = 0
        
        chunks = chunker.chunk(text, config)
        print(f"  Result: {len(chunks)} chunks")
        assert len(chunks) == 5, f"Expected 5 chunks, got {len(chunks)}"
        print("PASS")
    except Exception as e:
        print(f"FAIL: {e}")

if __name__ == "__main__":
    test_sentence_window_chunker()
    test_paragraph_chunker()
    test_code_aware_chunker()
    test_heading_based_chunker()
    test_recursive_chunker()
