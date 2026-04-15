FROM python:3.12-slim

WORKDIR /app

# Install uv (copy binary directly — no pip overhead)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create virtual environment
RUN uv venv .venv

# Activate venv by adding it to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN uv pip install -r requirements.txt

# Copy application code
COPY live_transcription.py .

# Railway injects $PORT at runtime; default to 8000 for local runs
ENV PORT=8000

EXPOSE 8000

CMD uvicorn live_transcription:app --host 0.0.0.0 --port ${PORT}
