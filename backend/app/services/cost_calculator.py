from typing import Dict, Any

class EmbeddingCostCalculator:
    """
    Calculates estimated cost for embedding operations.
    """
    
    # Prices per 1,000,000 tokens as of early 2024
    PRICING = {
        "openai": {
            "text-embedding-3-small": 0.02,
            "text-embedding-3-large": 0.13,
            "text-embedding-ada-002": 0.10,
        },
        "local": {
            "all-MiniLM-L6-v2": 0.0,
            "BAAI/bge-large-en-v1.5": 0.0,
            "multi-qa-mpnet-base-dot-v1": 0.0,
        }
    }

    @classmethod
    def calculate(cls, provider: str, model: str, token_count: int) -> float:
        """
        Calculate cost in USD.
        """
        price_per_m = cls.PRICING.get(provider, {}).get(model, 0.0)
        return (token_count / 1_000_000) * price_per_m

    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Returns all pricing and model data for the frontend.
        """
        return cls.PRICING
