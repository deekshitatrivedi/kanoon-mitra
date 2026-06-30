# ⚖️ Kanoon Mitra — Indian Legal Rights Chatbot

> **Know your rights. In plain language. For free.**

Kanoon Mitra ("Friend of the Law") is a Retrieval-Augmented Generation (RAG) chatbot that answers questions about Indian legal rights — from arrest rights and tenant protections to consumer complaints and women's safety laws. It grounds every answer in actual Indian laws and constitutional articles, never hallucinates.

---

## Demo

![Kanoon Mitra Screenshot](https://via.placeholder.com/800x450.png?text=Add+your+screenshot+here)

---

## Features

- **RAG-powered** — Answers are grounded in a curated knowledge base of Indian laws (IPC, CrPC, Constitution, Consumer Protection Act, RTI Act, Labour Laws, Domestic Violence Act, RERA, IT Act)
- **No hallucinations** — LLM can only answer from retrieved context; if it doesn't know, it says so
- **Plain language** — Complex legal text explained in simple, empathetic language
- **Quick question buttons** — One-click access to 8 most common legal situations
- **Source transparency** — Toggle to see which law chunks were used to generate each answer
- **Free legal aid links** — Every response ends with an actionable next step; sidebar has all helpline numbers
- **Fully offline** - TF-IDF retrieval using Scikit-learn

---

## Tech Stack

| Component    | Technology                         |
| ------------ | ---------------------------------- |
| LLM          | Groq API (Llama 3.3 70B Versatile) |
| Retrieval    | Custom TF-IDF Retrieval            |
| Embeddings   | Scikit-learn TF-IDF                |
| Vector Store | Local NumPy + JSON                 |
| Frontend     | Streamlit                          |
| Backend      | Python                             |
| PDF Support  | PyPDF                              |


---

## Project Structure

```
kanoon-mitra/
├── data/
│   ├── legal_knowledge_base.txt   ← Main curated legal knowledge
│   └── (add more PDFs here)       ← Drop any Indian law PDF to extend
├── vectorstore/
│   ├── chunks.json
│   ├── vectors.npy
│   └── tfidf_vectorizer.pkl                   ← Auto-created by ingest.py
├── src/
│   ├── ingest.py                  ← Build the vector store (run once)
│   ├── rag_chain.py               ← RAG chain: retriever + LLM + prompt
│   └── app.py                     ← Streamlit chatbot UI
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

---

## Setup Instructions
1. Clone the Repository

git clone https://github.com/yourusername/kanoon-mitra.git
cd kanoon-mitra

2. Create a Virtual Environment

Windows
    python -m venv venv
    venv\Scripts\activate

macOS/Linux
    python3 -m venv venv
    source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file in the project root.

Example:
    GROQ_API_KEY=your_groq_api_key_here

Alternatively, copy the example file:

    Windows
        .env.example .env
    macOS/Linux
        nv.example .env

Then open the .env file and replace the placeholder with your Groq API key.

5. Prepare the Knowledge Base

Add your legal documents to the data/ folder.

Supported formats:

.txt
.pdf

**Note**: This repository includes only a sample knowledge base. Replace it or add your own legal documents before building the vector store.

6. Generate the Vector Store

Run the ingestion script to create the searchable TF-IDF index.
    python src/ingest.py

This generates the following files inside the vectorstore/ directory:
    chunks.json
    vectors.npy
    tfidf_vectorizer.pkl

7. Launch the Application

Start the Streamlit application.
    streamlit run src/app.py

8. Open the Application

Once the server starts, open your browser and visit:

http://localhost:8501

You can now ask questions about Indian legal rights through the chatbot interface.

**Notes**

Ensure that your Groq API key is correctly added to the .env file.
Whenever you modify or add documents in the data/ folder, rerun the ingestion script:
**python src/ingest.py**

to regenerate the vector store before launching the application.

---

## Project Specifications

| Component | Details |
|----------|---------|
| Retrieval Technique | TF-IDF Similarity Search |
| Vector Store | Local JSON + NumPy |
| LLM | Llama 3.3 70B Versatile (Groq API) |
| Frontend | Streamlit |
| Backend | Python |
| Knowledge Base | Indian Legal Documents (TXT/PDF) |
| Retrieval Depth | Top-4 Relevant Chunks |

---

## Safety Design

This project was built with careful ethical considerations:

1. **No medical or emergency advice** — For health emergencies or imminent danger, the bot always redirects to emergency services
2. **Grounded answers only** — System prompt explicitly instructs the LLM to only answer from retrieved context
3. **Clear disclaimer** — The UI prominently displays that this is not a substitute for professional legal advice
4. **Helplines always visible** — NALSA (15100), Women Helpline (1091), Cybercrime (1930) are shown on every page
5. **Empathetic framing** — Prompt instructs the LLM to be empathetic, as users may be in distressing situations

---

## Legal Domains Covered

- Fundamental Rights (Part III, Constitution)
- Arrest Rights (CrPC + D.K. Basu Guidelines)
- Tenant & Landlord Rights
- Consumer Protection Act 2019
- Right to Information (RTI Act 2005)
- Women's Rights (PWDVA, POSH, Maternity Benefit, 498A IPC)
- Labour Rights (Minimum Wages, EPF, Gratuity, POSH)
- Property Rights (Hindu Succession Act, RERA)
- Cyber Crime Rights (IT Act 2000, IPC)
- Free Legal Aid (NALSA, DLSA, Lok Adalat)

---

## Author

**Deekshita Trivedi**
 [linkedin.com/in/deekshitatrivedi](https://linkedin.com/in/deekshitatrivedi) | [github.com/deekshitatrivedi](https://github.com/deekshitatrivedi)

---

## License

MIT License — free to use and extend.

---

*"Access to justice is a fundamental right, not a privilege."*
