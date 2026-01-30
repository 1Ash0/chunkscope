# Semantic Chunking Algorithm Design

## 1. Component Analysis

### Requirements
1.  **Semantic Breakpoints**: Split text where semantic meaning shifts significantly (low cosine similarity between adjacent segments).
2.  **Boundary Integrity**: Never split in the middle of a sentence. Respect paragraph boundaries where possible.
3.  **Adaptability**: Handle various document types (narrative vs. technical). A dynamic threshold (e.g., percentile-based) is preferred over a fixed constant (e.g., 0.75).
4.  **Performance**: Process ~100 pages (~50k tokens) in <10 seconds.
    *   *Note*: This requires a high-throughput embedding model (e.g., `all-MiniLM-L6-v2` or ONNX optimized).
5.  **Tunability**: User can adjust `threshold_percentile` (sensitivity) and `min_chunk_size` / `max_chunk_size`.

### Edge Cases
*   **Uniform Text**: A document with constant theme might have high similarity everywhere. -> *Solution*: Percentile-based threshold ensures splits still occur, or fallback to max token size.
*   **Erratic Text**: Logs or data dumps with random similarity. -> *Solution*: Merge small noise chunks; rely on `min_chunk_size`.
*   **Very Long Sentences**: Legal documents with 500+ word sentences. -> *Solution*: Hard split limit (fallback to recursive character splitting *within* the sentence if absolutely necessary, but preferably warn).
*   **Lists/Tables**: Semantic similarity might fluctuate wildly. -> *Solution*: Detect structure (from PDF extraction) and treat tables as atomic blocks if possible.

### Performance Constraints
*   **Latency**: Dominant factor is **Embedding Generation**.
    *   Model: `all-MiniLM-L6-v2` (~80ms per batch on CPU).
    *   Batching: Essential. Embed all sentences in one pass.
    *   Complexity: $O(N)$ where $N$ is number of sentences. Comparison is $O(N)$ (linear scan).
*   **Memory**:
    *   Model weights: ~90MB (`all-MiniLM-L6-v2`).
    *   Embeddings: $N \times 384$ floats. For 5000 sentences (100 pages), $\approx 7.6$ MB. Negligible.

### Dependencies
*   **`sentence-transformers`**: For embedding generation.
*   **`spacy`** (en_core_web_sm): For robust sentence segmentation (faster/better than NLTK).
*   **`numpy`**: For vector operations.

---

## 2. Algorithm Design

### Approach: "Percentile-Based Gradient Splitting"

Instead of rudimentary adjacent sentence similarity ($S_i$ vs $S_{i+1}$), we use a "combined sentence window" approach for stability, and split based on relative drops in similarity.

#### 1. Sentence Splitting
Split document into sentences $S = [s_0, s_1, ..., s_n]$.

#### 2. Pattern Embedding (Windowing)
To capture context, we embed a window of sentences rather than just one.
Let $W_i$ be the combined text of sentences $[s_{i-1}, s_i, s_{i+1}]$ (buffer size 1).
Generate Embeddings $E = [e_0, e_1, ..., e_n]$.

#### 3. Similarity Calculation
Calculate Cosine Similarity between adjacent windows:
$D_i = CosineSimilarity(e_i, e_{i+1})$
Result is a curve of similarity scores $D$.

#### 4. Adaptive Thresholding
Calculate the splitting threshold based on the data distribution (Percentile):
$Threshold = Percentile(D, P)$
Where $P$ is a user-tunable parameter (e.g., 10th percentile - split at the top 10% biggest drops).

#### 5. Chunk Merging
Iterate through sentences. Accumulate into current chunk.
If $D_i < Threshold$ AND `current_chunk_size > min_size`:
    **SPLIT**. Start new chunk.
Else:
    **CONTINUE**.

#### 6. Refinement (Size Constraints)
*   **Merge**: If a resulting chunk is $< min\_size$ (and not at end), merge with neighbor (preference: merge with neighbor having higher similarity boundary).
*   **Split**: If a chunk is $> max\_size$, apply recursive character splitting (fallback) to force it under limit.

---

## 3. Pseudocode

```python
class SemanticChunker:
    def __init__(self, model_name="all-MiniLM-L6-v2", threshold_percentile=90):
        self.model = SentenceTransformer(model_name)
        self.nlp = spacy.load("en_core_web_sm")
        self.threshold_percentile = threshold_percentile

    def chunk(self, text: str) -> List[Chunk]:
        # 1. Split Sentences
        sentences = [sent.text for sent in self.nlp(text).sents]
        
        # 2. Prepare Windows (Contextual Embedding)
        # Combine sentence with neighbors for richer signal
        windows = self._create_sliding_windows(sentences, window_size=1)
        
        # 3. Batch Embed
        embeddings = self.model.encode(windows, batch_size=64)
        
        # 4. Calculate Distance (Cosine Sim)
        distances = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(embeddings[i], embeddings[i+1])
            distances.append(sim)
            
        # 5. Determine Threshold (Adaptive)
        # We want to split where distance is LOW (similarity is LOW).
        # So we look for the "valleys".
        # If percentile is 20, we split at the lowest 20% of similarity scores.
        threshold = np.percentile(distances, self.threshold_percentile)
        
        # 6. Form Chunks
        chunks = []
        current_chunk = [sentences[0]]
        
        for i in range(len(distances)):
            # distances[i] is score between sent[i] and sent[i+1]
            if distances[i] <= threshold:
                # Semantic Gap Detected
                chunks.append(" ".join(current_chunk))
                current_chunk = []
            
            current_chunk.append(sentences[i+1])
            
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
```

---

## 4. Complexity Analysis

| Step | Operation | Time Complexity | Notes |
|------|-----------|-----------------|-------|
| 1 | Sentence Splitting (Spacy) | $O(T)$ | T = characters. Highly optimized. |
| 2 | Window Creation | $O(N)$ | N = sentences. Negligible. |
| 3 | Embedding (Transformer) | $O(N \times L^2)$ | Dominant step. L = Sequence Length. Quadratic with seq len, linear with N. |
| 4 | Similarity Calc | $O(N)$ | Fast vector ops. |
| 5 | Percentile Calc | $O(N \log N)$ | Fast sorting. |

**Total Time**: Dominated by Step 3.
**Estimate**: With `all-MiniLM-L6-v2` (384 dim), processing 3k sentences (~100 pages):
*   CPU: ~3-8 seconds (depending on hardware/AVX).
*   Structure Overhead: < 0.5 seconds.
*   **Result**: Fits within <10s requirement.

## 5. Comparison: vs Recursive Character Splitting

| Feature | Semantic Chunking | Recursive Character Splitting |
|---------|-------------------|-------------------------------|
| **Logic** | Meaning-based | Structure-based (paragraphs, newlines) |
| **Coherence** | **High**. Keeps topics together. | **Medium**. Can split mid-thought if tokens limit hit. |
| **Speed** | Slow (Model inference required). | **Instant**. |
| **Cost** | Compute heavy. | Compute cheap. |
| **Use Case** | RAG, QA, Summarization. | Simple indexing, low-resource. |

## 6. Hyperparameter Tuning Guide

*   **`buffer_size` (Window)**:
    *   *Default*: 1 (Current sentence + 1 neighbor).
    *   *Increase*: For "smoother" transitions (less sensitive to outlier sentences).
    *   *Decrease*: For precise sentence-level cuts.
*   **`breakpoint_percentile_threshold`**:
    *   *Default*: 10-20 (Split at lowest 10-20% similarity scores).
    *   *Higher (e.g., 40)*: More chunks, smaller chunks.
    *   *Lower (e.g., 5)*: Fewer chunks, larger broad-topic blocks.

---

## 7. Test Strategy

### Unit Tests
1.  **Mocked Embeddings**: Inject specific vectors to test split logic.
    *   `vec_a` (topic A), `vec_a`, `vec_b` (topic B).
    *   Assert split occurs exactly between unique vectors.
2.  **Threshold Logic**: Verify percentile math works (e.g., 50th percentile splits half the time).
3.  **Sentence Integrity**: Verify no words are lost or duplicated during merge.

### Integration Tests
1.  **Real Model**: `all-MiniLM-L6-v2` loading and inference.
2.  **Performance**: Timer check on 50-page Lorem Ipsum vs Real Text.
3.  **Degenerate Cases**: Empty text, single sentence, identical repeated sentences.

