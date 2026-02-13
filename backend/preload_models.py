import os
import sys

# Ensure backend is in path
sys.path.append(os.getcwd())

print("Preloading models to avoid runtime timeouts...")

# 1. Spacy
try:
    import spacy
    print("Checking spacy model 'en_core_web_sm'...")
    if not spacy.util.is_package("en_core_web_sm"):
        print("Downloading 'en_core_web_sm'...")
        from spacy.cli import download
        download("en_core_web_sm")
    else:
        print("'en_core_web_sm' already installed.")
    nlp = spacy.load("en_core_web_sm")
    print("Spacy model loaded successfully.")
except Exception as e:
    print(f"Error loading spacy: {e}")

# 2. Sentence Transformers
try:
    from sentence_transformers import SentenceTransformer
    print("Checking sentence-transformer model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Sentence Transformer model loaded successfully.")
except Exception as e:
    print(f"Error loading sentence-transformer: {e}")

print("All models preloaded.")
