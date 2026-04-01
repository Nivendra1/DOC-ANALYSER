import os
import base64
import tempfile
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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

EXTENSION_MAP = {
    "pdf": ".pdf",
    "docx": ".docx",
    "image": ".png",
    "jpg": ".jpg",
    "jpeg": ".jpg",
    "png": ".png",
    "tiff": ".tiff",
    "bmp": ".bmp",
}

CONTENT_TYPE_MAP = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "tiff": "image/tiff",
    "bmp": "image/bmp",
}


class DocumentRequest(BaseModel):
    fileName: str
    fileType: str
    fileBase64: str


@app.get("/")
def root():
    return {
        "message": "AI Document Analyser API is running.",
        "version": "1.0.0",
        "endpoint": "POST /api/document-analyze"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/document-analyze")
async def analyse(request: DocumentRequest, x_api_key: str = Header(...)):
    # Verify API key
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key.")

    file_type = request.fileType.lower().strip()

    if file_type not in EXTENSION_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported fileType: {file_type}. Supported: pdf, docx, image, png, jpg"
        )

    ext = EXTENSION_MAP[file_type]
    content_type = CONTENT_TYPE_MAP[file_type]

    # Decode base64
    try:
        b64 = request.fileBase64
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        file_bytes = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoded file.")

    # Write to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        extracted = extract_text(tmp_path, content_type)

        if not extracted["text"].strip():
            raise HTTPException(status_code=422, detail="Could not extract text from document.")

        analysis = analyse_document(extracted["text"])

        return JSONResponse(content={
            "status": "success",
            "fileName": request.fileName,
            "summary": analysis["summary"],
            "entities": {
                "names": analysis["entities"].get("names", []),
                "dates": analysis["entities"].get("dates", []),
                "organizations": analysis["entities"].get("organizations", []),
                "amounts": analysis["entities"].get("monetary_amounts", []),
                "locations": analysis["entities"].get("locations", []),
                "other": analysis["entities"].get("other", [])
            },
            "sentiment": analysis["sentiment"].capitalize()
        })

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "fileName": request.fileName,
                "detail": str(e)
            }
        )
    finally:
        os.unlink(tmp_path)
