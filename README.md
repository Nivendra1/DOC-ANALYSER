# 🧠 AI-Powered Document Analysis & Extraction

An intelligent document processing API that extracts, analyses, and summarises content from PDF, DOCX, and image files using AI.

## 🚀 Live Demo

**Base URL:** `https://your-app.onrender.com`

---

## 📋 Features

- ✅ **Multi-format support** — PDF, DOCX, JPG, PNG
- ✅ **Text extraction** — Native extraction + OCR fallback for scanned PDFs
- ✅ **AI Summarisation** — Concise 2-4 sentence summaries via Groq (Llama 3.3 70B)
- ✅ **Entity Extraction** — Names, organizations, locations, dates, monetary amounts
- ✅ **Sentiment Analysis** — Positive / Negative / Neutral with confidence score
- ✅ **Document Type Detection** — Invoice, Resume, Contract, Report, etc.
- ✅ **Keyword Extraction** — Top 5 relevant keywords
- ✅ **Language Detection** — Auto-detects document language
- ✅ **Word Count & Reading Time** — Metadata for every document

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| PDF Extraction | PyMuPDF |
| DOCX Extraction | python-docx |
| OCR | Tesseract |
| AI Model | Groq API — Llama 3.3 70B |
| Language Detection | langdetect |
| Deployment | Render (free tier) |

---

## 📡 API Reference

### `GET /`
Returns API info and available endpoints.

### `GET /health`
Health check endpoint.

### `POST /analyse`

Analyse a document file.

**Headers:**
```
Authorization: your-api-key
```

**Body:** `multipart/form-data`
```
file: <your PDF/DOCX/image file>
```

**Response:**
```json
{
  "filename": "sample.pdf",
  "document_type": "Invoice",
  "language": "en",
  "word_count": 342,
  "reading_time_minutes": 1.7,
  "summary": "This is an invoice from Acme Corp...",
  "keywords": ["invoice", "payment", "due date", "acme", "amount"],
  "entities": {
    "names": ["John Doe"],
    "organizations": ["Acme Corp", "XYZ Ltd"],
    "locations": ["Chennai", "Mumbai"],
    "dates": ["2026-01-01", "2026-01-31"],
    "monetary_amounts": ["$5,000", "₹42,000"],
    "other": []
  },
  "sentiment": {
    "label": "neutral",
    "confidence": 0.88
  },
  "extraction_method": "native"
}
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10+
- Tesseract OCR installed

**Install Tesseract:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/Nivendra1/doc-analyzer.git
cd doc-analyzer

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and APP_API_KEY

# 5. Run the server
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` to see the API running.

---

## 🌐 Deployment on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repo
4. Set environment variables:
   - `GROQ_API_KEY` → your Groq API key
   - `APP_API_KEY` → your chosen API key for judges
5. Build command:
   ```
   apt-get update && apt-get install -y tesseract-ocr && pip install -r requirements.txt
   ```
6. Start command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

---

## 🤖 AI Tools Used

| Tool | Usage |
|------|-------|
| Claude (Anthropic) | Architecture planning, code structure, debugging assistance |
| Groq API — Llama 3.3 70B | Document summarisation, entity extraction, sentiment analysis |

---

## ⚠️ Known Limitations

- Very large files (>10MB) may be slow on free tier
- Handwritten text in images may have lower OCR accuracy
- Non-English documents supported for extraction but AI analysis optimised for English

---

## 📁 Project Structure

```
doc-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app & routes
│   ├── extractor.py     # PDF/DOCX/Image text extraction
│   └── analyser.py      # Groq AI analysis
├── requirements.txt
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

## 👤 Author

**Nivendra** — Built for AI Hackathon 2026
