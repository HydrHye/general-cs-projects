from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Optional

from docx import Document
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from openai import OpenAI, OpenAIError
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="OpenAI TTS Reader")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".doc", ".docx"}
MAX_CHARACTERS = 40_000


def _read_text_file(upload: UploadFile) -> str:
    raw = upload.file.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _read_pdf_file(upload: UploadFile) -> str:
    reader = PdfReader(upload.file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _read_docx_file(upload: UploadFile) -> str:
    doc = Document(upload.file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def _read_doc_file(upload: UploadFile) -> str:
    try:
        import textract  # type: ignore
    except ImportError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Reading .doc files requires optional dependency 'textract' "
                "and a system parser such as antiword/catdoc. "
                "Install dependencies and try again."
            ),
        ) from exc

    suffix = Path(upload.filename or "file.doc").suffix or ".doc"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(upload.file.read())
        tmp_path = Path(tmp.name)

    try:
        return textract.process(str(tmp_path)).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to parse .doc file. Ensure antiword/catdoc is installed.",
        ) from exc
    finally:
        tmp_path.unlink(missing_ok=True)


def extract_text(upload: UploadFile) -> str:
    filename = upload.filename or ""
    suffix = Path(filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    if suffix == ".txt":
        text = _read_text_file(upload)
    elif suffix == ".pdf":
        text = _read_pdf_file(upload)
    elif suffix == ".docx":
        text = _read_docx_file(upload)
    else:
        text = _read_doc_file(upload)

    return text.strip()


def generate_audio(
    text: str,
    model: str,
    voice: str,
    speed: float,
    response_format: str,
    instructions: Optional[str],
) -> bytes:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is missing. Set it in your environment or .env file.",
        )

    client = OpenAI()

    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "speed": speed,
        "response_format": response_format,
    }

    if instructions:
        payload["instructions"] = instructions

    try:
        speech = client.audio.speech.create(**payload)
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI API request failed: {exc}") from exc

    if hasattr(speech, "read"):
        return speech.read()

    content = getattr(speech, "content", None)
    if content:
        return content

    raise HTTPException(status_code=500, detail="Unexpected response from TTS API")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/read")
def read_aloud(
    text: str = Form(default=""),
    file: Optional[UploadFile] = File(default=None),
    model: str = Form(default="gpt-4o-mini-tts"),
    voice: str = Form(default="alloy"),
    speed: float = Form(default=1.0),
    response_format: str = Form(default="mp3"),
    instructions: str = Form(default=""),
) -> Response:
    candidate_text = text.strip()

    if file and file.filename:
        extracted = extract_text(file)
        if not extracted:
            raise HTTPException(status_code=400, detail="No readable text found in uploaded file")
        candidate_text = extracted

    if not candidate_text:
        raise HTTPException(status_code=400, detail="Provide direct text or upload a document")

    if len(candidate_text) > MAX_CHARACTERS:
        raise HTTPException(
            status_code=400,
            detail=f"Text too long ({len(candidate_text)} chars). Max allowed is {MAX_CHARACTERS}.",
        )

    if not 0.25 <= speed <= 4.0:
        raise HTTPException(status_code=400, detail="Speed must be between 0.25 and 4.0")

    audio_bytes = generate_audio(
        text=candidate_text,
        model=model,
        voice=voice,
        speed=speed,
        response_format=response_format,
        instructions=instructions.strip() or None,
    )

    content_type = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "opus": "audio/ogg",
        "aac": "audio/aac",
        "flac": "audio/flac",
    }.get(response_format, "application/octet-stream")

    return Response(
        content=audio_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="speech.{response_format}"'},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
