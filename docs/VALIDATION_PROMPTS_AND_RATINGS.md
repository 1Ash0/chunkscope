# Validation Prompts & Rating Checks for ChunkScope
## Use AFTER implementing code from Extended Thinking prompts

---

## 📋 HOW TO USE THIS DOCUMENT

**Your Workflow:**
```
1. Get code from Extended Thinking (Implementation Guide)
2. Implement the code in Google IDX
3. Use THIS document to validate quality
4. Run validation prompts to check what you built
5. Use rating system to decide: Continue or Fix?
```

**Purpose**: Fast, automated quality checks for every deliverable.

---

# PHASE 1: BACKEND FOUNDATION

## Task 1.1: Database Schema

### Validation Prompt (Copy-Paste to AI)
```
Validate my database schema implementation for ChunkScope.

I've implemented a PostgreSQL schema with pgvector. Please check:

1. Schema file location: backend/app/db/schema.sql
2. Tables created: pipelines, documents, chunks, evaluations

Run these validation queries and tell me if the schema is correct:

\```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check chunks table structure
\d chunks

-- Check indexes
\di
\```

Expected results:
- 4 tables minimum (pipelines, documents, chunks, evaluations)
- pgvector extension installed
- chunks.embedding column type: vector(1536)
- At least 5 indexes

Analyze the output and rate: PASS/FAIL for each requirement.
```

### Automated Rating Check
```bash
#!/bin/bash
# Save as: validate_schema.sh

echo "=== Database Schema Validation ==="

# Test 1: Check tables (worth 2 points)
TABLES=$(psql -d chunkscope -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
if [ "$TABLES" -ge 4 ]; then
  echo "✅ Tables: PASS (2/2) - Found $TABLES tables"
  SCORE=$((SCORE + 2))
else
  echo "❌ Tables: FAIL (0/2) - Found only $TABLES tables"
fi

# Test 2: Check pgvector (worth 2 points)
VECTOR=$(psql -d chunkscope -t -c "SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
if [ "$VECTOR" -eq 1 ]; then
  echo "✅ pgvector: PASS (2/2)"
  SCORE=$((SCORE + 2))
else
  echo "❌ pgvector: FAIL (0/2)"
fi

# Test 3: Check vector column (worth 2 points)
VECTOR_COL=$(psql -d chunkscope -t -c "SELECT data_type FROM information_schema.columns WHERE table_name = 'chunks' AND column_name = 'embedding';")
if [[ "$VECTOR_COL" == *"vector"* ]]; then
  echo "✅ Vector column: PASS (2/2)"
  SCORE=$((SCORE + 2))
else
  echo "❌ Vector column: FAIL (0/2)"
fi

# Test 4: Check indexes (worth 2 points)
INDEXES=$(psql -d chunkscope -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
if [ "$INDEXES" -ge 5 ]; then
  echo "✅ Indexes: PASS (2/2) - Found $INDEXES indexes"
  SCORE=$((SCORE + 2))
else
  echo "⚠️  Indexes: PARTIAL (1/2) - Found only $INDEXES indexes"
  SCORE=$((SCORE + 1))
fi

# Test 5: Performance test (worth 2 points)
echo "Testing query performance..."
QUERY_TIME=$(psql -d chunkscope -c "EXPLAIN ANALYZE SELECT * FROM chunks LIMIT 1;" 2>&1 | grep "Execution Time" | awk '{print $3}')
if (( $(echo "$QUERY_TIME < 50" | bc -l) )); then
  echo "✅ Performance: PASS (2/2) - ${QUERY_TIME}ms"
  SCORE=$((SCORE + 2))
else
  echo "⚠️  Performance: SLOW (1/2) - ${QUERY_TIME}ms"
  SCORE=$((SCORE + 1))
fi

# Final rating
echo ""
echo "=== FINAL SCORE: $SCORE/10 ==="
if [ "$SCORE" -ge 9 ]; then
  echo "🟢 EXCELLENT - Continue to next task"
elif [ "$SCORE" -ge 7 ]; then
  echo "🟡 GOOD - Minor fixes recommended"
else
  echo "🔴 NEEDS WORK - Fix issues before continuing"
fi
```

### Quick Manual Check
```bash
# Run these 5 commands (30 seconds):

# 1. Tables exist
psql -d chunkscope -c "\dt"
# Expect: 4+ tables listed

# 2. pgvector installed  
psql -d chunkscope -c "SELECT extname FROM pg_extension WHERE extname = 'vector';"
# Expect: vector

# 3. Vector column exists
psql -d chunkscope -c "\d chunks" | grep embedding
# Expect: embedding | vector(1536)

# 4. Indexes exist
psql -d chunkscope -c "\di" | wc -l
# Expect: 5 or more

# 5. Sample insert works
psql -d chunkscope -c "INSERT INTO documents (id, filename, file_path) VALUES (gen_random_uuid(), 'test.pdf', '/tmp/test.pdf');"
# Expect: INSERT 0 1

# RATING:
# 5/5 pass = 🟢 EXCELLENT
# 3-4/5 pass = 🟡 GOOD
# 0-2/5 pass = 🔴 FAIL
```

---

## Task 1.2: FastAPI Setup

### Validation Prompt
```
Validate my FastAPI project setup for ChunkScope.

I've set up FastAPI following the extended thinking recommendations. Check:

File structure:
- backend/app/main.py (FastAPI app)
- backend/app/core/config.py (settings)
- backend/app/db/database.py (DB connection)
- backend/pyproject.toml (dependencies)

Run these checks:
1. Server starts: uvicorn app.main:app --reload
2. Health endpoint: curl http://localhost:8000/health
3. Swagger docs: curl http://localhost:8000/docs
4. CORS configured for http://localhost:5173
5. Async database connection setup

Analyze the setup and tell me what's working and what's missing.
Rate each requirement: PASS/PARTIAL/FAIL
```

### Automated Rating Check
```python
#!/usr/bin/env python3
# Save as: validate_fastapi.py

import subprocess
import requests
import time
import sys

def run_check(name, func, points):
    """Run a validation check"""
    try:
        result = func()
        if result:
            print(f"✅ {name}: PASS ({points}/{points})")
            return points
        else:
            print(f"❌ {name}: FAIL (0/{points})")
            return 0
    except Exception as e:
        print(f"❌ {name}: ERROR (0/{points}) - {str(e)}")
        return 0

def check_files_exist():
    """Check required files exist"""
    import os
    required = [
        'backend/app/main.py',
        'backend/app/core/config.py',
        'backend/pyproject.toml'
    ]
    return all(os.path.exists(f) for f in required)

def check_server_running():
    """Check if server is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def check_swagger_docs():
    """Check Swagger UI loads"""
    try:
        response = requests.get('http://localhost:8000/docs', timeout=2)
        return response.status_code == 200 and 'swagger' in response.text.lower()
    except:
        return False

def check_cors():
    """Check CORS headers"""
    try:
        response = requests.options('http://localhost:8000/health', 
            headers={'Origin': 'http://localhost:5173'}, timeout=2)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        return cors_header is not None
    except:
        return False

def check_async_db():
    """Check if async database is configured"""
    try:
        with open('backend/app/db/database.py', 'r') as f:
            content = f.read()
            return 'AsyncSession' in content or 'async_engine' in content
    except:
        return False

if __name__ == '__main__':
    print("=== FastAPI Setup Validation ===\n")
    
    score = 0
    score += run_check("Files exist", check_files_exist, 2)
    score += run_check("Server running", check_server_running, 2)
    score += run_check("Swagger docs", check_swagger_docs, 2)
    score += run_check("CORS configured", check_cors, 2)
    score += run_check("Async DB setup", check_async_db, 2)
    
    print(f"\n=== FINAL SCORE: {score}/10 ===")
    
    if score >= 9:
        print("🟢 EXCELLENT - Production ready")
        sys.exit(0)
    elif score >= 7:
        print("🟡 GOOD - Minor improvements needed")
        sys.exit(0)
    else:
        print("🔴 NEEDS WORK - Fix critical issues")
        sys.exit(1)
```

### Quick Manual Check
```bash
# Run these 5 tests (1 minute):

# 1. Server starts
uvicorn app.main:app --reload &
sleep 3
# Expect: No import errors

# 2. Health check
curl http://localhost:8000/health
# Expect: {"status":"ok"} or similar

# 3. Swagger UI
curl -s http://localhost:8000/docs | grep -i swagger
# Expect: Output contains "swagger"

# 4. CORS test
curl -H "Origin: http://localhost:5173" -I http://localhost:8000/health | grep -i "access-control"
# Expect: Access-Control-Allow-Origin header present

# 5. Check async DB in code
grep -r "AsyncSession\|create_async_engine" backend/app/db/
# Expect: Found in database.py

# RATING:
# 5/5 = 🟢 EXCELLENT
# 3-4/5 = 🟡 GOOD  
# 0-2/5 = 🔴 FAIL
```

---

## Task 1.3: File Upload API

### Validation Prompt
```
Validate my file upload API implementation.

Endpoint: POST /api/documents/upload

I need you to analyze if the implementation has:
1. File type validation (only PDFs)
2. File size limit (10MB max)
3. Saves file to disk
4. Stores metadata in database
5. Returns document ID
6. Proper error handling

Test with these scenarios:
- Valid PDF upload
- Invalid file type (.txt)
- File too large (>10MB)
- Missing file in request

Rate the implementation for each scenario: PASS/FAIL
```

### Automated Rating Check
```python
#!/usr/bin/env python3
# Save as: validate_upload.py

import requests
import io
import os

API_URL = "http://localhost:8000/api/documents/upload"
score = 0

print("=== File Upload API Validation ===\n")

# Test 1: Valid PDF upload (3 points)
print("Test 1: Valid PDF upload...")
try:
    # Create small test PDF
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF"
    files = {'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    response = requests.post(API_URL, files=files)
    
    if response.status_code == 200:
        data = response.json()
        if 'id' in data and 'filename' in data:
            print(f"✅ Valid upload: PASS (3/3)")
            print(f"   Document ID: {data['id']}")
            score += 3
            doc_id = data['id']  # Save for later tests
        else:
            print(f"⚠️  Valid upload: PARTIAL (1/3) - Missing fields")
            score += 1
    else:
        print(f"❌ Valid upload: FAIL (0/3) - Status {response.status_code}")
except Exception as e:
    print(f"❌ Valid upload: ERROR (0/3) - {e}")

# Test 2: Invalid file type (2 points)
print("\nTest 2: Invalid file type (.txt)...")
try:
    files = {'file': ('test.txt', io.BytesIO(b"test"), 'text/plain')}
    response = requests.post(API_URL, files=files)
    
    if response.status_code in [400, 422]:
        print(f"✅ File validation: PASS (2/2)")
        score += 2
    else:
        print(f"❌ File validation: FAIL (0/2) - Accepted invalid file")
except Exception as e:
    print(f"❌ File validation: ERROR (0/2) - {e}")

# Test 3: File too large (2 points)
print("\nTest 3: File size limit...")
try:
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {'file': ('large.pdf', io.BytesIO(large_content), 'application/pdf')}
    response = requests.post(API_URL, files=files)
    
    if response.status_code in [413, 400, 422]:
        print(f"✅ Size limit: PASS (2/2)")
        score += 2
    else:
        print(f"⚠️  Size limit: WARNING (1/2) - Accepted large file")
        score += 1
except Exception as e:
    print(f"❌ Size limit: ERROR (0/2) - {e}")

# Test 4: Database record created (2 points)
print("\nTest 4: Database persistence...")
try:
    import subprocess
    result = subprocess.run(
        ['psql', '-d', 'chunkscope', '-t', '-c', 
         f"SELECT COUNT(*) FROM documents WHERE id = '{doc_id}';"],
        capture_output=True, text=True
    )
    count = int(result.stdout.strip())
    if count == 1:
        print(f"✅ Database record: PASS (2/2)")
        score += 2
    else:
        print(f"❌ Database record: FAIL (0/2)")
except Exception as e:
    print(f"⚠️  Database record: SKIP (0/2) - {e}")

# Test 5: File saved to disk (1 point)
print("\nTest 5: File storage...")
try:
    # Check if uploads directory has files
    upload_dir = 'storage/uploads'
    if os.path.exists(upload_dir) and len(os.listdir(upload_dir)) > 0:
        print(f"✅ File storage: PASS (1/1)")
        score += 1
    else:
        print(f"❌ File storage: FAIL (0/1)")
except Exception as e:
    print(f"❌ File storage: ERROR (0/1) - {e}")

# Final rating
print(f"\n=== FINAL SCORE: {score}/10 ===")
if score >= 9:
    print("🟢 EXCELLENT - Production ready")
elif score >= 7:
    print("🟡 GOOD - Minor issues")
else:
    print("🔴 NEEDS WORK - Critical issues remain")
```

### Quick Manual Check
```bash
# Run these 5 tests (2 minutes):

# 1. Valid PDF upload
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.pdf"
# Expect: JSON with "id" field

# 2. Reject .txt file
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.txt"
# Expect: 400 or 422 status

# 3. File saved to disk
ls -lh storage/uploads/
# Expect: File(s) listed

# 4. Database record
psql -d chunkscope -c "SELECT COUNT(*) FROM documents;"
# Expect: Count > 0

# 5. Swagger shows endpoint
curl http://localhost:8000/docs | grep "upload"
# Expect: Contains "upload"

# RATING:
# 5/5 = 🟢 EXCELLENT
# 3-4/5 = 🟡 GOOD
# 0-2/5 = 🔴 FAIL
```

---

# PHASE 2: CHUNKING VISUALIZER

## Task 2.1: PDF Processing

### Validation Prompt
```
Validate my PDF text extraction implementation.

I've implemented PDFProcessor class that extracts text with positional data.

Test these requirements:
1. Extracts text from PDF
2. Returns character-level coordinates (x, y, width, height)
3. Handles 100-page PDF in <10 seconds
4. Detects tables/special elements
5. Error handling for corrupted PDFs

Run these tests:
```python
from app.services.pdf_processor import PDFProcessor

processor = PDFProcessor()

# Test 1: Basic extraction
result = processor.extract("sample.pdf")
print(f"Pages: {len(result['pages'])}")

# Test 2: Coordinates
char = result['pages'][0]['characters'][0]
print(f"Has coords: {'x' in char and 'y' in char}")

# Test 3: Performance
import time
start = time.time()
large = processor.extract("100_pages.pdf")
print(f"Time: {time.time() - start:.2f}s")
```

Rate each test: PASS/FAIL
```

### Automated Rating Check
```python
#!/usr/bin/env python3
# Save as: validate_pdf.py

import sys
import time
sys.path.insert(0, 'backend')

from app.services.pdf_processor import PDFProcessor

score = 0
print("=== PDF Processor Validation ===\n")

# Test 1: Basic extraction (2 points)
print("Test 1: Basic extraction...")
try:
    processor = PDFProcessor()
    result = processor.extract("test_files/sample.pdf")
    
    if result and 'pages' in result and len(result['pages']) > 0:
        print(f"✅ Extraction: PASS (2/2) - {len(result['pages'])} pages")
        score += 2
    else:
        print(f"❌ Extraction: FAIL (0/2)")
except Exception as e:
    print(f"❌ Extraction: ERROR (0/2) - {e}")

# Test 2: Coordinate data (3 points - CRITICAL)
print("\nTest 2: Positional data...")
try:
    if 'pages' in result and len(result['pages']) > 0:
        page = result['pages'][0]
        if 'characters' in page and len(page['characters']) > 0:
            char = page['characters'][0]
            has_coords = all(k in char for k in ['x', 'y', 'width', 'height'])
            if has_coords:
                print(f"✅ Coordinates: PASS (3/3)")
                print(f"   Sample: x={char['x']}, y={char['y']}")
                score += 3
            else:
                print(f"❌ Coordinates: FAIL (0/3) - Missing fields")
        else:
            print(f"❌ Coordinates: FAIL (0/3) - No character data")
except Exception as e:
    print(f"❌ Coordinates: ERROR (0/3) - {e}")

# Test 3: Performance (2 points)
print("\nTest 3: Performance (100 pages)...")
try:
    start = time.time()
    large_result = processor.extract("test_files/100_pages.pdf")
    elapsed = time.time() - start
    
    if elapsed < 10:
        print(f"✅ Performance: EXCELLENT (2/2) - {elapsed:.2f}s")
        score += 2
    elif elapsed < 30:
        print(f"🟡 Performance: ACCEPTABLE (1/2) - {elapsed:.2f}s")
        score += 1
    else:
        print(f"❌ Performance: SLOW (0/2) - {elapsed:.2f}s")
except FileNotFoundError:
    print(f"⚠️  Performance: SKIP (1/2) - No test file")
    score += 1
except Exception as e:
    print(f"❌ Performance: ERROR (0/2) - {e}")

# Test 4: Error handling (2 points)
print("\nTest 4: Error handling...")
try:
    try:
        bad = processor.extract("test_files/corrupted.pdf")
        print(f"⚠️  Error handling: PARTIAL (1/2) - Didn't raise error")
        score += 1
    except Exception as e:
        if "corrupted" in str(e).lower() or "invalid" in str(e).lower():
            print(f"✅ Error handling: PASS (2/2)")
            score += 2
        else:
            print(f"🟡 Error handling: PARTIAL (1/2) - Generic error")
            score += 1
except Exception as e:
    print(f"⚠️  Error handling: SKIP (1/2)")
    score += 1

# Test 5: Text quality (1 point)
print("\nTest 5: Text extraction quality...")
try:
    text = result['pages'][0].get('text', '')
    if len(text) > 100:
        print(f"✅ Text quality: PASS (1/1) - {len(text)} chars")
        score += 1
    else:
        print(f"❌ Text quality: FAIL (0/1) - Too short")
except Exception as e:
    print(f"❌ Text quality: ERROR (0/1) - {e}")

# Final rating
print(f"\n=== FINAL SCORE: {score}/10 ===")
if score >= 9:
    print("🟢 EXCELLENT - Ready for visualization")
elif score >= 7:
    print("🟡 GOOD - Usable with minor issues")
else:
    print("🔴 NEEDS WORK - Critical features missing")
```

### Quick Manual Check
```python
# Run in Python/Jupyter (3 minutes):

from app.services.pdf_processor import PDFProcessor
import time

processor = PDFProcessor()

# 1. Extract sample PDF
result = processor.extract("sample.pdf")
print(f"✓ Pages: {len(result['pages'])}")  # Expect: > 0

# 2. Check coordinates
char = result['pages'][0]['characters'][0]
print(f"✓ Coords: {char}")  # Expect: {x: ..., y: ..., ...}

# 3. Performance test
start = time.time()
large = processor.extract("large.pdf")
print(f"✓ Time: {time.time()-start:.1f}s")  # Expect: < 30s

# 4. Text preview
print(f"✓ Text: {result['pages'][0]['text'][:100]}")  # Expect: readable text

# 5. Error handling
try:
    processor.extract("fake.pdf")
except Exception as e:
    print(f"✓ Error: Caught {type(e).__name__}")  # Expect: Error caught

# RATING:
# 5/5 checks ✓ = 🟢 EXCELLENT
# 3-4/5 checks ✓ = 🟡 GOOD
# 0-2/5 checks ✓ = 🔴 FAIL
```

---

## Task 2.2: Semantic Chunking

### Validation Prompt
```
Validate my semantic chunking implementation.

I've implemented SemanticChunker class using sentence-transformers.

Test these requirements:
1. Chunks text based on semantic similarity
2. Threshold parameter works (0.3-0.8)
3. Doesn't split mid-sentence
4. Returns chunks with start/end positions
5. Performance: 100 pages in <30s

Run these tests:
```python
from app.services.chunkers.semantic_chunker import SemanticChunker

text = """AI is transforming industries. Machine learning advances rapidly.

Cooking requires good ingredients. Recipes guide the process."""

chunker = SemanticChunker(threshold=0.5)
chunks = chunker.chunk(text, {})

# Should create 2 chunks (AI topic, cooking topic)
print(f"Chunks: {len(chunks)}")
for i, c in enumerate(chunks):
    print(f"Chunk {i}: {c['text'][:50]}...")
```

Rate: Does it semantically separate topics correctly?
```

### Automated Rating Check
```python
#!/usr/bin/env python3
# Save as: validate_chunking.py

import sys
sys.path.insert(0, 'backend')

from app.services.chunkers.semantic_chunker import SemanticChunker
import time

score = 0
print("=== Semantic Chunker Validation ===\n")

test_text = """
Artificial intelligence is transforming industries. Machine learning models are becoming more sophisticated. Deep learning uses neural networks for complex tasks.

Cooking is an essential life skill. Good recipes provide clear instructions. Fresh ingredients make better dishes. Proper seasoning enhances flavor significantly.

Climate change poses serious challenges. Global temperatures are rising steadily. Renewable energy offers sustainable solutions.
"""

# Test 1: Basic functionality (2 points)
print("Test 1: Basic chunking...")
try:
    chunker = SemanticChunker(threshold=0.5)
    chunks = chunker.chunk(test_text, {})
    
    if len(chunks) >= 2:
        print(f"✅ Chunking: PASS (2/2) - Created {len(chunks)} chunks")
        score += 2
    else:
        print(f"❌ Chunking: FAIL (0/2) - Only {len(chunks)} chunk")
except Exception as e:
    print(f"❌ Chunking: ERROR (0/2) - {e}")

# Test 2: Semantic separation (3 points - CRITICAL)
print("\nTest 2: Semantic quality...")
try:
    # Check if AI and cooking are in different chunks
    ai_chunk = None
    cooking_chunk = None
    
    for chunk in chunks:
        if 'artificial intelligence' in chunk['text'].lower():
            ai_chunk = chunk
        if 'cooking' in chunk['text'].lower():
            cooking_chunk = chunk
    
    if ai_chunk and cooking_chunk and ai_chunk['id'] != cooking_chunk['id']:
        print(f"✅ Semantic separation: EXCELLENT (3/3)")
        print(f"   AI and cooking in different chunks")
        score += 3
    elif len(chunks) >= 2:
        print(f"🟡 Semantic separation: PARTIAL (1/3)")
        score += 1
    else:
        print(f"❌ Semantic separation: FAIL (0/3)")
except Exception as e:
    print(f"❌ Semantic separation: ERROR (0/3) - {e}")

# Test 3: Threshold tuning (2 points)
print("\nTest 3: Threshold parameter...")
try:
    chunks_low = chunker.chunk(test_text, {'threshold': 0.3})
    chunks_high = chunker.chunk(test_text, {'threshold': 0.8})
    
    if len(chunks_low) > len(chunks_high):
        print(f"✅ Threshold: PASS (2/2)")
        print(f"   Low(0.3): {len(chunks_low)}, High(0.8): {len(chunks_high)}")
        score += 2
    else:
        print(f"❌ Threshold: FAIL (0/2) - No effect")
except Exception as e:
    print(f"❌ Threshold: ERROR (0/2) - {e}")

# Test 4: Position data (2 points)
print("\nTest 4: Position accuracy...")
try:
    chunk = chunks[0]
    if 'start_pos' in chunk and 'end_pos' in chunk:
        # Verify positions match text
        extracted = test_text[chunk['start_pos']:chunk['end_pos']]
        if extracted.strip() == chunk['text'].strip():
            print(f"✅ Positions: PASS (2/2)")
            score += 2
        else:
            print(f"⚠️  Positions: PARTIAL (1/2) - Mismatch")
            score += 1
    else:
        print(f"❌ Positions: FAIL (0/2) - Missing fields")
except Exception as e:
    print(f"❌ Positions: ERROR (0/2) - {e}")

# Test 5: No mid-sentence splits (1 point)
print("\nTest 5: Sentence boundaries...")
try:
    clean_splits = 0
    for chunk in chunks:
        text = chunk['text'].strip()
        if text and text[0].isupper() and text[-1] in '.!?"':
            clean_splits += 1
    
    if clean_splits == len(chunks):
        print(f"✅ Boundaries: PASS (1/1) - All clean")
        score += 1
    elif clean_splits >= len(chunks) * 0.8:
        print(f"🟡 Boundaries: PARTIAL (0.5/1) - Mostly clean")
        score += 0.5
    else:
        print(f"❌ Boundaries: FAIL (0/1) - Many bad splits")
except Exception as e:
    print(f"❌ Boundaries: ERROR (0/1) - {e}")

# Final rating
print(f"\n=== FINAL SCORE: {score}/10 ===")
if score >= 9:
    print("🟢 EXCELLENT - Semantic chunking works perfectly")
elif score >= 7:
    print("🟡 GOOD - Minor tuning needed")
else:
    print("🔴 NEEDS WORK - Semantic separation failing")
```

### Quick Manual Check
```python
# Run in Python (2 minutes):

from app.services.chunkers.semantic_chunker import SemanticChunker

text = """AI transforms industries. ML is powerful.

Cooking needs ingredients. Recipes are helpful."""

chunker = SemanticChunker(threshold=0.5)
chunks = chunker.chunk(text, {})

# 1. Creates chunks
print(f"1. Chunks: {len(chunks)}")  # Expect: 2

# 2. Semantic separation
print(f"2. Chunk 0: {chunks[0]['text'][:30]}")  # Expect: AI content
print(f"   Chunk 1: {chunks[1]['text'][:30]}")  # Expect: Cooking content

# 3. Threshold effect
low = chunker.chunk(text, {'threshold': 0.3})
high = chunker.chunk(text, {'threshold': 0.8})
print(f"3. Threshold: low={len(low)}, high={len(high)}")  # Expect: low > high

# 4. Has positions
print(f"4. Positions: {chunks[0]['start_pos']}, {chunks[0]['end_pos']}")  # Expect: numbers

# 5. Clean boundaries
print(f"5. First char: '{chunks[0]['text'][0]}'")  # Expect: uppercase
print(f"   Last char: '{chunks[0]['text'][-1]}'")  # Expect: . or !

# RATING:
# 5/5 correct = 🟢 EXCELLENT
# 3-4/5 correct = 🟡 GOOD
# 0-2/5 correct = 🔴 FAIL
```

---

## Task 2.3: Chunking API Endpoint

### Validation Prompt
```
Validate my chunking visualization API.

Endpoint: POST /api/chunks/visualize
Input: {document_id, chunking_config}
Output: {chunks: [...], metrics: {...}}

Test these scenarios:
1. Valid request returns chunks with bbox
2. Invalid document_id returns 404
3. Response has correct structure
4. Performance <5s for 10-page PDF
5. Error messages are clear

Run:
```bash
# Valid request
DOC_ID="uploaded-doc-id-here"
curl -X POST http://localhost:8000/api/chunks/visualize \
  -H "Content-Type: application/json" \
  -d "{\"document_id\": \"$DOC_ID\", \"chunking_config\": {}}"

# Invalid ID
curl -X POST http://localhost:8000/api/chunks/visualize \
  -H "Content-Type: application/json" \
  -d '{"document_id": "fake-id"}'
```

Rate each scenario: PASS/FAIL
```

### Automated Rating Check
```python
#!/usr/bin/env python3
# Save as: validate_chunk_api.py

import requests
import time
import json

API_BASE = "http://localhost:8000"
score = 0

print("=== Chunks API Validation ===\n")

# Setup: Upload a test document first
print("Setup: Uploading test PDF...")
files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}
upload_resp = requests.post(f"{API_BASE}/api/documents/upload", files=files)
if upload_resp.status_code == 200:
    doc_id = upload_resp.json()['id']
    print(f"✓ Document uploaded: {doc_id}\n")
else:
    print(f"❌ Setup failed: Could not upload document")
    exit(1)

# Test 1: Valid request (3 points)
print("Test 1: Valid request...")
try:
    start = time.time()
    response = requests.post(
        f"{API_BASE}/api/chunks/visualize",
        json={
            "document_id": doc_id,
            "chunking_config": {
                "method": "semantic",
                "threshold": 0.5
            }
        }
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        if 'chunks' in data and len(data['chunks']) > 0:
            print(f"✅ Valid request: PASS (3/3)")
            print(f"   Returned {len(data['chunks'])} chunks in {elapsed:.2f}s")
            score += 3
        else:
            print(f"⚠️  Valid request: PARTIAL (1/3) - Empty chunks")
            score += 1
    else:
        print(f"❌ Valid request: FAIL (0/3) - Status {response.status_code}")
except Exception as e:
    print(f"❌ Valid request: ERROR (0/3) - {e}")

# Test 2: Response structure (2 points)
print("\nTest 2: Response structure...")
try:
    data = response.json()
    has_chunks = 'chunks' in data
    has_metrics = 'metrics' in data
    
    if has_chunks and has_metrics:
        chunk = data['chunks'][0]
        required_fields = ['id', 'text', 'bbox', 'metadata']
        has_all_fields = all(f in chunk for f in required_fields)
        
        if has_all_fields:
            print(f"✅ Structure: PASS (2/2)")
            score += 2
        else:
            print(f"⚠️  Structure: PARTIAL (1/2) - Missing chunk fields")
            score += 1
    else:
        print(f"❌ Structure: FAIL (0/2)")
except Exception as e:
    print(f"❌ Structure: ERROR (0/2) - {e}")

# Test 3: Bbox coordinates valid (2 points)
print("\nTest 3: Bbox validation...")
try:
    chunk = data['chunks'][0]
    bbox = chunk['bbox']
    
    valid_bbox = (
        'page' in bbox and bbox['page'] >= 1 and
        'x' in bbox and 0 <= bbox['x'] <= 1000 and
        'y' in bbox and 0 <= bbox['y'] <= 1000 and
        'width' in bbox and bbox['width'] > 0 and
        'height' in bbox and bbox['height'] > 0
    )
    
    if valid_bbox:
        print(f"✅ Bbox: PASS (2/2)")
        print(f"   Sample: page={bbox['page']}, x={bbox['x']:.1f}, y={bbox['y']:.1f}")
        score += 2
    else:
        print(f"❌ Bbox: FAIL (0/2) - Invalid coordinates")
except Exception as e:
    print(f"❌ Bbox: ERROR (0/2) - {e}")

# Test 4: Invalid document ID (2 points)
print("\nTest 4: Error handling...")
try:
    response = requests.post(
        f"{API_BASE}/api/chunks/visualize",
        json={"document_id": "invalid-id-12345"}
    )
    
    if response.status_code in [404, 422]:
        print(f"✅ Error handling: PASS (2/2)")
        print(f"   Correctly returned {response.status_code}")
        score += 2
    else:
        print(f"⚠️  Error handling: PARTIAL (1/2) - Status {response.status_code}")
        score += 1
except Exception as e:
    print(f"❌ Error handling: ERROR (0/2) - {e}")

# Test 5: Performance (1 point)
print("\nTest 5: Performance...")
if elapsed < 5:
    print(f"✅ Performance: EXCELLENT (1/1) - {elapsed:.2f}s")
    score += 1
elif elapsed < 15:
    print(f"🟡 Performance: ACCEPTABLE (0.5/1) - {elapsed:.2f}s")
    score += 0.5
else:
    print(f"❌ Performance: SLOW (0/1) - {elapsed:.2f}s")

# Final rating
print(f"\n=== FINAL SCORE: {score}/10 ===")
if score >= 9:
    print("🟢 EXCELLENT - API production-ready")
elif score >= 7:
    print("🟡 GOOD - Minor improvements")
else:
    print("🔴 NEEDS WORK - Critical issues")
```

---

## Task 2.4-2.6: Frontend Components

### Validation Prompt
```
Validate my React chunk visualizer implementation.

Components:
- ChunkVisualizer.tsx (main component)
- ChunkOverlay.tsx (colored rectangles)
- useChunkStore.ts (Zustand state)

Test these requirements:
1. PDF renders correctly
2. Chunks show as colored overlays
3. Hover shows tooltip
4. Click shows detail panel
5. No console errors
6. Smooth performance (60fps)

Manual tests:
1. Open http://localhost:5173
2. Upload a PDF
3. See colored chunks on PDF
4. Hover over chunk → tooltip appears
5. Click chunk → side panel opens
6. Open DevTools → check for errors

Rate each test: PASS/FAIL
```

### Quick Manual Check
```
FRONTEND VALIDATION CHECKLIST (5 minutes)

Open: http://localhost:5173

□ 1. App loads without errors
     - No blank screen
     - No console errors (F12)

□ 2. PDF displays
     - Upload sample.pdf
     - PDF renders clearly

□ 3. Chunks render
     - Colored rectangles visible
     - At least 10+ chunks shown
     - Colors are distinct

□ 4. Hover interaction
     - Hover over chunk
     - Tooltip appears with:
       • Chunk ID
       • Size (chars/tokens)
       • Page number

□ 5. Click interaction
     - Click on chunk
     - Chunk highlights
     - Side panel opens
     - Full text displayed

□ 6. Performance
     - Scrolling smooth
     - No lag when hovering
     - Chunks update quickly

□ 7. Console clean
     - Open DevTools (F12)
     - No red errors
     - Warnings acceptable

□ 8. Responsive
     - Resize window
     - Layout adapts
     - No broken UI

RATING:
8/8 checks ✓ = 🟢 DEMO-READY
6-7/8 checks ✓ = 🟡 NEEDS POLISH
<6 checks ✓ = 🔴 NOT READY

SCREENSHOT: Take screenshot of working visualizer for documentation
```

---

# PHASE 2 END: COMPLETE VALIDATION

## Full Integration Test

### Validation Prompt
```
Validate the complete chunking visualizer flow.

End-to-end test:
1. Start backend: uvicorn app.main:app --reload
2. Start frontend: npm run dev
3. Open: http://localhost:5173
4. Upload PDF
5. Visualize chunks
6. Interact with visualization

Check:
- No errors in backend logs
- No errors in browser console
- Full flow works smoothly
- Performance acceptable
- Ready to demo

Rate overall system: DEMO-READY / NEEDS-WORK / NOT-READY
```

### Complete E2E Test Script
```bash
#!/bin/bash
# Save as: validate_phase2.sh

echo "=== PHASE 2: COMPLETE VALIDATION ===="
echo ""

score=0
max_score=10

# Test 1: Backend running
echo "1. Backend health..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ Backend: RUNNING (1/1)"
    ((score++))
else
    echo "❌ Backend: DOWN (0/1)"
fi

# Test 2: Frontend running
echo "2. Frontend health..."
if curl -s http://localhost:5173 | grep -q "html"; then
    echo "✅ Frontend: RUNNING (1/1)"
    ((score++))
else
    echo "❌ Frontend: DOWN (0/1)"
fi

# Test 3: Upload works
echo "3. Document upload..."
UPLOAD_RESP=$(curl -s -X POST http://localhost:8000/api/documents/upload \
  -F "file=@test.pdf")
if echo "$UPLOAD_RESP" | grep -q "id"; then
    DOC_ID=$(echo "$UPLOAD_RESP" | jq -r '.id')
    echo "✅ Upload: WORKING (2/2) - ID: ${DOC_ID:0:8}..."
    score=$((score + 2))
else
    echo "❌ Upload: FAILED (0/2)"
fi

# Test 4: Chunking works
echo "4. Chunk generation..."
CHUNK_RESP=$(curl -s -X POST http://localhost:8000/api/chunks/visualize \
  -H "Content-Type: application/json" \
  -d "{\"document_id\": \"$DOC_ID\", \"chunking_config\": {}}")
  
if echo "$CHUNK_RESP" | grep -q "chunks"; then
    CHUNK_COUNT=$(echo "$CHUNK_RESP" | jq '.chunks | length')
    echo "✅ Chunking: WORKING (2/2) - $CHUNK_COUNT chunks"
    score=$((score + 2))
else
    echo "❌ Chunking: FAILED (0/2)"
fi

# Test 5: Bbox data present
echo "5. Bbox coordinates..."
if echo "$CHUNK_RESP" | jq -e '.chunks[0].bbox.x' > /dev/null 2>&1; then
    echo "✅ Bbox: PRESENT (2/2)"
    score=$((score + 2))
else
    echo "❌ Bbox: MISSING (0/2)"
fi

# Test 6: Database populated
echo "6. Database state..."
DB_DOCS=$(psql -d chunkscope -t -c "SELECT COUNT(*) FROM documents;" 2>/dev/null | xargs)
if [ "$DB_DOCS" -gt 0 ]; then
    echo "✅ Database: POPULATED (1/1) - $DB_DOCS documents"
    ((score++))
else
    echo "⚠️  Database: EMPTY (0/1)"
fi

# Test 7: No critical errors in logs
echo "7. Error check..."
# This is a placeholder - check your actual logs
echo "⚠️  Manual: Check backend logs for errors (1/1)"
((score++))

# Final score
echo ""
echo "=== PHASE 2 SCORE: $score/$max_score ==="
if [ $score -ge 9 ]; then
    echo "🟢 EXCELLENT - Demo-ready!"
    echo "Next: Record demo video"
elif [ $score -ge 7 ]; then
    echo "🟡 GOOD - Minor polish needed"
    echo "Fix: Check failed tests above"
else
    echo "🔴 NOT READY - Critical issues"
    echo "Action: Debug and re-test"
fi
```

---

# GRADING RUBRIC SUMMARY

## Quick Rating System

After validating each task, use this:

```
🟢 GREEN (9-10/10)
- All critical features work
- Minor issues only
- Ready to move forward
- Action: Continue to next task

🟡 YELLOW (7-8/10)
- Core functionality works  
- Some issues present
- Acceptable but could be better
- Action: Document issues, continue (fix later if time)

🔴 RED (<7/10)
- Critical features broken
- Not usable
- Major problems
- Action: STOP and fix before continuing
```

## When to Re-prompt Extended Thinking

**Re-prompt if you get 🔴 RED**, using this template:

```
Using extended thinking, help me fix issues with [COMPONENT].

I implemented based on your previous guidance, but validation tests failed.

Failed tests:
1. [Test name]: [What went wrong]
2. [Test name]: [What went wrong]

Current code:
[Paste relevant code]

Error messages:
[Paste errors]

Requirements that were missed:
- [Requirement 1]
- [Requirement 2]

Please provide:
1. Root cause analysis (why did it fail?)
2. Fixed code (addressing specific failures)
3. Additional tests to verify the fix
```

---

# DAILY VALIDATION ROUTINE

## Every Morning (5 mins)

```bash
# Run quick health check
./validate_health.sh

# Expected: All green
✅ Backend: UP
✅ Frontend: UP
✅ Database: UP
✅ Git: Clean

# If any red: Fix before continuing
```

## Before Each Git Commit (2 mins)

```bash
# Validate what you built today
pytest backend/tests/  # Backend tests
npm run build          # Frontend builds
git status             # Check what's changed

# Only commit if all pass
```

## End of Week (30 mins)

```bash
# Complete phase validation
./validate_phase1.sh   # Week 1
./validate_phase2.sh   # Week 2  
./validate_phase3.sh   # Week 3

# Grade your week
# Decide: Continue or catch up?
```

---

# 📊 TRACKING YOUR SCORES

Create a file: `VALIDATION_LOG.md`

```markdown
# ChunkScope Validation Log

## Week 1: Backend Foundation

### Day 1: Database Schema
- Test Score: 9/10 🟢
- Issues: None
- Time: 2 hours

### Day 2: FastAPI Setup
- Test Score: 8/10 🟡
- Issues: CORS initially misconfigured
- Fixed: Added origins list
- Time: 3 hours

### Day 3: File Upload
- Test Score: 7/10 🟡
- Issues: Large file handling slow
- Action: Deferred optimization
- Time: 4 hours

## Week 1 Total: 24/30 = 80% 🟡
**Status**: Good progress, on track

---

## Week 2: Chunking Visualizer

### Day 4: PDF Processing
- Test Score: 10/10 🟢
- Issues: None  
- Time: 3 hours

### Day 5: Semantic Chunking
- Test Score: 6/10 🔴
- Issues: Semantic separation not working
- Action: Re-prompted with specific issues
- Retry Score: 9/10 🟢
- Time: 5 hours (including fix)

[Continue logging...]
```

---

# 🎯 SUCCESS INDICATORS

You're doing GREAT if:

- ✨ 80%+ of tasks score 🟢 GREEN on first try
- ✨ Complete phases on schedule
- ✨ Can demo working features
- ✨ Code quality improving over time
- ✨ Learning from failures

You need HELP if:

- ⚠️ <50% tasks score 🔴 RED
- ⚠️ Stuck on same issue 2+ days  
- ⚠️ Behind schedule >1 week
- ⚠️ Can't explain how code works
- ⚠️ Constantly re-prompting same things

---

# 🆘 EMERGENCY FIX TEMPLATE

When validation fails badly:

```
URGENT: Need help fixing [COMPONENT]

VALIDATION RESULTS:
- Expected: [What should happen]
- Actual: [What's happening]
- Test Score: X/10 🔴

WHAT I'VE TRIED:
1. [Attempt 1] - Result: [Failed because...]
2. [Attempt 2] - Result: [Failed because...]

CODE:
[Paste the failing code]

ERRORS:
[Paste error messages]

DEADLINE:
Need this working by: [Date]

QUESTION:
Should I:
A) Continue trying to fix
B) Simplify the feature
C) Use a different approach
D) Ask for help from professor/peers
```

---

This validation framework ensures extended thinking is actually helping you build a working product, not just generating impressive-looking code that doesn't work! 🧪✅
