# Simple production image for the FastAPI backend
FROM python:3.14-slim

# Tesseract is needed for OCR (pytesseract calls the tesseract binary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render/Railway set $PORT for you; default to 8000 for local docker runs
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]