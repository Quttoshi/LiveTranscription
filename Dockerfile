FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY live_transcription.py .

# Railway injects $PORT at runtime; default to 8000 for local runs
ENV PORT=8000

EXPOSE 8000

CMD uvicorn live_transcription:app --host 0.0.0.0 --port ${PORT}
