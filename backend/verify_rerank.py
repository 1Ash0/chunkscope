import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from app.services.rerankers.cohere_reranker import CohereReranker

async def test():
    try:
        reranker = CohereReranker()
        docs = [{"text": "Hello world"}, {"text": "Privacy matters"}]
        results = await reranker.rerank("What is data privacy?", docs, top_k=2)
        print(f"RESULTS: {results}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())
