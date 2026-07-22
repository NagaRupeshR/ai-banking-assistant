# 🏦 AI Banking Complaint Resolution Assistant

An AI-powered Banking Complaint Resolution System that combines **Machine Learning**, **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)** to analyze customer complaints and generate RBI-compliant resolution guidance.

The system classifies banking complaints, retrieves relevant RBI regulations, supplements them with real-world banking discussions, and produces explainable complaint resolution reports.

---

# Features

- **Machine Learning Complaint Classification**
  - TF-IDF + Sentence Transformer (SBERT) embeddings
  - Hybrid feature representation
  - Predicts Top-6 complaint categories

- **AI Complaint Analysis**
  - Groq Llama 3.3 70B
  - Strict structured prompting
  - Urgency prediction
  - Priority prediction
  - Ombudsman eligibility
  - Success probability
  - Resolution timeline
  - Preventive advice

- **Hybrid RAG**
  - FAISS Vector Search over RBI documents
  - RBI Annual Reports
  - RBI Ombudsman Guidelines
  - Banking Circulars
  - External Web Retrieval (DuckDuckGo API)
  - Intelligent relevance filtering

- **Explainable AI**
  - Displays supporting RBI document chunks
  - Displays supporting external references
  - Confidence score
  - Top classifier predictions

- **Professional Report**
  - Complaint Summary
  - Resolution Plan
  - Timeline
  - Similar Historical Cases
  - Official RBI Resources
  - Complaint Resolution Flowchart
  - PDF Report Generation

---

# Tech Stack

### Backend

- Django
- Python

### Machine Learning

- Scikit-learn
- Sentence Transformers
- TF-IDF
- Joblib

### Retrieval

- FAISS
- LangChain
- DuckDuckGo Search API

### AI

- Groq API
- Llama 3.3 70B

### Database

- SQLite

### Frontend

- HTML
- CSS
- JavaScript
- Mermaid.js

---

# Project Structure

```bash
AI_BANKING_ASSISTANT/
│
├── complaint/
│   ├── analyzer.py               # LLM analysis
│   ├── classifier.py             # ML classifier
│   ├── rag.py                    # FAISS retrieval
│   ├── rag_api.py                # External Web Retrieval
│   ├── pdf_utils.py              # PDF generation
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │     ├── home.html
│   │     └── result.html
│   └── static/
│
├── vector_db/
│     └── FAISS Index
│
├── models/
│     ├── model.pkl
│     ├── tfidf.pkl
│     └── label_encoder.pkl
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# System Architecture

```
User Complaint
      │
      ▼
ML Classifier
(TF-IDF + SBERT)
      │
      ▼
Predicted Category
      │
      ▼
Hybrid RAG
      │
 ┌───────────────┐
 │               │
 ▼               ▼
FAISS RBI Docs   DuckDuckGo API
 │               │
 └──────┬────────┘
        ▼
Merged Context
        │
        ▼
Groq Llama 3.3 70B
        │
        ▼
Structured Banking Analysis
        │
        ▼
Professional Report + PDF
```

---

# Machine Learning Pipeline

```
Complaint Text

      │

      ▼

TF-IDF Features

      +

SBERT Embeddings

      │

      ▼

Feature Concatenation

      │

      ▼

Trained ML Classifier

      │

      ▼

Top-6 Complaint Predictions
```

---

# RAG Pipeline

```
Complaint

      │

      ▼

Category Prediction

      │

      ▼

Retrieve RBI Chunks

      │

      ▼

Retrieve Web Insights

      │

      ▼

Relevance Filtering

      │

      ▼

Combined Context

      │

      ▼

Groq LLM
```

---

# AI Output

The AI generates

- Complaint Category
- Confidence Score
- Urgency
- Priority
- Success Probability
- Resolution Plan
- Resolution Timeline
- Similar Historical Cases
- RBI Ombudsman Eligibility
- Preventive Advice
- Flowchart
- Supporting RBI Evidence
- External Banking Insights

---

# API Endpoints

## Analyze Complaint

```
POST /
```

Accepts

```json
{
    "complaint":"Complaint Text"
}
```

Returns

- AI Banking Report
- Flowchart
- RAG Evidence
- Classifier Predictions

---

# Setup Instructions

```bash
git clone https://github.com/yourusername/AI-Banking-Complaint-Assistant.git

cd AI-Banking-Complaint-Assistant
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create

```
.env
```

```text
GROQ_API_KEY=YOUR_GROQ_KEY
```

Run

```bash
python manage.py migrate

python manage.py runserver
```

Open

```
http://127.0.0.1:8000
```

---

# Explainability

Unlike traditional chatbots, every recommendation is supported using

- RBI Regulations
- RBI Ombudsman Guidelines
- Banking Circulars
- External Banking Knowledge
- ML Confidence Scores

This makes the system more transparent and trustworthy.

---

# Future Improvements

- OCR support for transaction receipts
- Multi-language complaint analysis
- Voice complaint support
- Complaint summarization
- Fine-tuned banking LLM
- Real RBI CMS complaint filing
- Email complaint generation
- Complaint tracking dashboard
- Authentication & user history
- Docker deployment
- PostgreSQL support

---

# Screenshots

Add screenshots here

- Home Page
- Complaint Analysis
- Flowchart
- Explainability Section
- PDF Report

---

# License

This project is developed for educational and portfolio purposes.