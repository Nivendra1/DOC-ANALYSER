import os
import uuid
import time
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile

from app.extractor import extract_text
from app.analyser import analyse_document

app = FastAPI(
    title="AI Document Analyser",
    description="Extracts, analyses and summarises PDF, DOCX and image documents using AI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APP_API_KEY = os.getenv("APP_API_KEY", "niv-doc-analyzer-2026")

ALLOWED_EXTENSIONS = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/tiff": ".tiff",
    "image/bmp": ".bmp",
}


def verify_api_key(authorization: str = Header(...)):
    if authorization != APP_API_KEY and authorization != f"Bearer {APP_API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    return authorization


@app.get("/")
def root():
    return {
        "message": "AI Document Analyser API is running.",
        "version": "1.0.0",
        "endpoints": {
            "analyse": "POST /analyse",
            "health": "GET /health"
        }
    }


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}


@app.post("/analyse")
async def analyse(
    file: UploadFile = File(...),
    authorization: str = Depends(verify_api_key)
):
    content_type = file.content_type

    # Try to infer from filename if content_type is generic
    if content_type == "application/octet-stream" or not content_type:
        fname = file.filename.lower()
        if fname.endswith(".pdf"):
            content_type = "application/pdf"
        elif fname.endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif fname.endswith((".jpg", ".jpeg")):
            content_type = "image/jpeg"
        elif fname.endswith(".png"):
            content_type = "image/png"

    if content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Supported: PDF, DOCX, JPG, PNG."
        )

    ext = ALLOWED_EXTENSIONS[content_type]

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        extracted = extract_text(tmp_path, content_type)

        if not extracted["text"].strip():
            raise HTTPException(status_code=422, detail="Could not extract text from document.")

        analysis = analyse_document(extracted["text"])

        return JSONResponse(content={
            "filename": file.filename,
            "document_type": analysis["document_type"],
            "language": extracted.get("language", "en"),
            "word_count": extracted["word_count"],
            "reading_time_minutes": extracted["reading_time_minutes"],
            "summary": analysis["summary"],
            "keywords": analysis["keywords"],
            "entities": analysis["entities"],
            "sentiment": {
                "label": analysis["sentiment"],
                "confidence": analysis["sentiment_confidence"]
            },
            "extraction_method": extracted["method"]
        })

    finally:
        os.unlink(tmp_path)
