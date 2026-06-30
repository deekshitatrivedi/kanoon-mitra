"""
rag_chain.py — RAG chain using offline TF-IDF retrieval + Groq LLM.
"""
import json, pickle
from pathlib import Path
import numpy as np
from sklearn.preprocessing import normalize
from groq import Groq

BASE_DIR   = Path(__file__).resolve().parent.parent
VSTORE_DIR = BASE_DIR / "vectorstore"

SYSTEM_PROMPT = """You are Kanoon Mitra (Friend of the Law), a helpful and empathetic Indian legal rights assistant.

Your job is to explain Indian legal rights in simple, clear language that any ordinary citizen can understand.

RULES:
1. Answer ONLY based on the provided context below. Do not invent laws or rights.
2. Always cite which law, act, or constitutional article your answer comes from.
3. If the context does not contain enough information, say: "I don't have enough information on that specific point. Please consult a lawyer or contact NALSA helpline 15100 for free legal aid."
4. Be empathetic — the user may be in a stressful situation.
5. At the end of every answer, mention one concrete action the user can take.
6. Keep answers concise (5-10 sentences) unless the question needs more.

CONTEXT FROM INDIAN LEGAL KNOWLEDGE BASE:
{context}"""


class KanoonMitraChain:
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)

        with open(VSTORE_DIR / "tfidf_vectorizer.pkl", "rb") as f:
            self.vectorizer = pickle.load(f)
        with open(VSTORE_DIR / "chunks.json", encoding="utf-8") as f:
            self.chunks = json.load(f)
        self.vectors = np.load(str(VSTORE_DIR / "vectors.npy"))

    def retrieve(self, query: str, k: int = 4):
        q_vec = normalize(self.vectorizer.transform([query]).toarray())
        scores = (self.vectors @ q_vec.T).flatten()
        top_k = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top_k]

    def invoke(self, question: str) -> str:
        hits = self.retrieve(question)
        context = "\n\n---\n\n".join(
            f"[Source {i+1}]:\n{chunk}" for i, (chunk, _) in enumerate(hits)
        )
        system = SYSTEM_PROMPT.format(context=context)
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": question},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def get_sources(self, question: str) -> list[str]:
        hits = self.retrieve(question)
        return [chunk[:300] + "..." for chunk, _ in hits]
