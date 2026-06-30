"""
local_embeddings.py — Offline TF-IDF embeddings using sklearn.
No internet required. Works as a LangChain-compatible embeddings class.
"""
import numpy as np
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

VSTORE = Path(__file__).resolve().parent.parent / "vectorstore"

class TFIDFEmbeddings:
    """Lightweight offline embeddings using TF-IDF."""
    def __init__(self):
        self.vectorizer = None
        model_path = VSTORE / "tfidf_vectorizer.pkl"
        if model_path.exists():
            with open(model_path, "rb") as f:
                self.vectorizer = pickle.load(f)

    def embed_documents(self, texts):
        vecs = self.vectorizer.transform(texts).toarray()
        return normalize(vecs).tolist()

    def embed_query(self, text):
        vec = self.vectorizer.transform([text]).toarray()
        return normalize(vec)[0].tolist()

def train_tfidf(texts, save_path):
    vectorizer = TfidfVectorizer(
        max_features=4096,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words='english',
    )
    vectorizer.fit(texts)
    save_path.mkdir(parents=True, exist_ok=True)
    with open(save_path / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    return vectorizer
