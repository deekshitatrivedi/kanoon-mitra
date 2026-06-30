"""
ingest.py — Loads legal knowledge base, splits into chunks,
builds TF-IDF embeddings (offline), stores in a simple JSON index.

Run once: python3 src/ingest.py
"""
import json, pickle, sys, re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
VSTORE_DIR = BASE_DIR / "vectorstore"
VSTORE_DIR.mkdir(exist_ok=True)

CHUNK_SIZE    = 700
CHUNK_OVERLAP = 150

def load_texts():
    texts = []
    for f in DATA_DIR.glob("*.txt"):
        print(f"  Loading: {f.name}")
        texts.append(f.read_text(encoding="utf-8"))
    try:
        import pypdf
        for f in DATA_DIR.glob("*.pdf"):
            print(f"  Loading PDF: {f.name}")
            reader = pypdf.PdfReader(str(f))
            texts.append("\n".join(p.extract_text() or "" for p in reader.pages))
    except Exception as e:
        print(f"  (PDF skipped: {e})")
    if not texts:
        print("ERROR: No documents found in data/"); sys.exit(1)
    return "\n\n".join(texts)

def split_chunks(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    # Split on double newlines first, then merge into size chunks
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 2 < size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            # Overlap: keep last `overlap` chars of previous chunk
            current = (current[-overlap:] + "\n\n" + para).strip() if current else para
    if current:
        chunks.append(current)
    return chunks

def build_index(chunks):
    print(f"  Training TF-IDF on {len(chunks)} chunks ...")
    vectorizer = TfidfVectorizer(
        max_features=8192, ngram_range=(1,2),
        sublinear_tf=True, stop_words="english",
    )
    matrix = vectorizer.fit_transform(chunks)
    vectors = normalize(matrix).toarray()

    # Save everything
    with open(VSTORE_DIR / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(VSTORE_DIR / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    np.save(str(VSTORE_DIR / "vectors.npy"), vectors)
    print(f"  Saved {len(chunks)} chunks to {VSTORE_DIR}")

def main():
    print("\n=== Kanoon Mitra — Ingestion Pipeline ===\n")
    print("Step 1: Loading documents ...")
    text = load_texts()
    print(f"  Total characters: {len(text):,}")

    print("\nStep 2: Splitting into chunks ...")
    chunks = split_chunks(text)
    print(f"  Total chunks: {len(chunks)}")

    print("\nStep 3: Building offline TF-IDF index ...")
    build_index(chunks)

    print("\nDone! Run: streamlit run src/app.py\n")

if __name__ == "__main__":
    main()
