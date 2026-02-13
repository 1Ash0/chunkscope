from .base import BaseEmbedder
from .openai_embedder import OpenAIEmbedder
from .local_embedder import LocalHuggingFaceEmbedder
from .cohere_embedder import CohereEmbedder

def get_embedder(provider: str, model_name: str, **kwargs) -> BaseEmbedder:
    """
    Factory function to get an embedder instance.
    """
    if provider == "openai":
        return OpenAIEmbedder(model_name=model_name, **kwargs)
    elif provider == "cohere":
        return CohereEmbedder(model_name=model_name, **kwargs)
    elif provider == "local":
        return LocalHuggingFaceEmbedder(model_name=model_name)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")

__all__ = ["BaseEmbedder", "OpenAIEmbedder", "CohereEmbedder", "LocalHuggingFaceEmbedder", "get_embedder"]
