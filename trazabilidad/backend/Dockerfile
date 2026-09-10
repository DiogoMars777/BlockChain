FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Invalidate Docker cache on Railway
ARG CACHEBUST=2026-09-10-v2-bitacora
ENV CACHEBUST=${CACHEBUST}

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
