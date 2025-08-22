FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    MAX_N=14

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo el codigo relevante al container
COPY app.py .
COPY hanoi_solver.py .
COPY tests.py .
COPY tests_k_algorithm.py .

# Exponer puerto
EXPOSE 8000

# Comando: gunicorn con workers
# -w: workers = 2 * cores + 1 (99.9% Uptime)
# --threads para mayor concurrencia sin bloquear
CMD exec gunicorn app:app \
    --bind 0.0.0.0:${PORT} \
    --workers 3 \
    --threads 4 \
    --timeout 30 \
    --keep-alive 2 \
    --worker-class gthread
