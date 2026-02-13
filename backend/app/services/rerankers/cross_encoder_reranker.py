import logging
from typing import List, Dict, Any
from app.services.rerankers.base import BaseReranker

logger = logging.getLogger(__name__)

class CrossEncoderReranker(BaseReranker):
    """
    Local reranker using sentence-transformers CrossEncoder.
    Models run locally on CPU/GPU.
    """
    
    _models = {}

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"):
        self.model_name = model_name
        self._load_model()

    def _load_model(self):
        if self.model_name not in CrossEncoderReranker._models:
            try:
                from sentence_transformers import CrossEncoder
                logger.info(f"Loading CrossEncoder model: {self.model_name}")
                CrossEncoderReranker._models[self.model_name] = CrossEncoder(self.model_name)
            except ImportError:
                logger.error("sentence-transformers not installed. Run 'pip install sentence-transformers'")
                raise
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder model {self.model_name}: {e}")
                raise

    @property
    def model(self):
        return CrossEncoderReranker._models[self.model_name]

    async def rerank(
        self, 
        query: str, 
        documents: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        if not documents:
            return []

        try:
            doc_texts = [doc.get("text", "") for doc in documents]
            
            # Prepare pairs for cross-encoder
            pairs = [[query, text] for text in doc_texts]
            
            # Predict scores
            scores = self.model.predict(pairs)
            
            # Pair scores with documents
            results = []
            for i, score in enumerate(scores):
                doc_copy = documents[i].copy()
                doc_copy["rerank_score"] = float(score)
                results.append(doc_copy)
                
            # Sort by score descending
            results.sort(key=lambda x: x["rerank_score"], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"CrossEncoder Rerank failed: {e}")
            return documents[:top_k]
