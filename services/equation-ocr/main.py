import io
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pix2text.latex_ocr import LatexOCR


OCR_MODEL = None

MODEL_DIR = os.getenv(
    "PIX2TEXT_MODEL_DIR",
    "/home/codespace/.pix2text/1.1/mfr-1.5-onnx",
)

MAX_FILE_SIZE = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global OCR_MODEL

    print("Loading Pix2Text model...")

    OCR_MODEL = LatexOCR(
        model_name="mfr-1.5",
        model_backend="onnx",
        model_dir=MODEL_DIR,
        device="cpu",
    )

    print("Pix2Text model loaded successfully.")

    yield

    OCR_MODEL = None
    print("OCR service shutting down.")


app = FastAPI(
    title="Outlier Equation OCR",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": OCR_MODEL is not None,
    }


@app.post("/recognize")
async def recognize_equation(
    file: UploadFile = File(...),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Only PNG, JPEG and WebP images are supported.",
        )

    image_bytes = await file.read(MAX_FILE_SIZE + 1)

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Image exceeds the 8 MB upload limit.",
        )

    try:
        with Image.open(io.BytesIO(image_bytes)) as source:
            source.verify()

        with Image.open(io.BytesIO(image_bytes)) as source:
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=413,
                    detail="Image dimensions are too large.",
                )

            image = source.convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image.",
        )

    if OCR_MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="OCR model is not ready.",
        )

    try:
        result = await run_in_threadpool(
            OCR_MODEL.recognize,
            image,
            use_post_process=True,
        )

        return {
            "success": True,
            "latex": result["text"],
            "score": float(result["score"]),
        }

    except Exception as exc:
        print(f"OCR inference error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Equation recognition failed.",
        )
