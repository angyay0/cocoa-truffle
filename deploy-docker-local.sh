#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="hanoi-flask"
PORT="${PORT:-8000}"
MAX_N_ENV="${MAX_N:-14}"

echo ">> Construyendo imagen ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}:latest" .

echo ">> Parando contenedor previo (si existe)..."
docker rm -f "${IMAGE_NAME}" >/dev/null 2>&1 || true

echo ">> Iniciando contenedor en puerto ${PORT} (MAX_N=${MAX_N_ENV})..."
docker run -d --name "${IMAGE_NAME}" -p "${PORT}:8000" \
  -e PORT=8000 \
  -e MAX_N="${MAX_N_ENV}" \
  "${IMAGE_NAME}:latest"

echo ">> Salud rápida..."
sleep 0.5
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST \
  -H "Content-Type: application/json" \
  -d '{"size":3,"from":"A","to":"C","aux":"B"}' "http://localhost:${PORT}/apihanoi" || true

echo ">> Ejecuta pruebas funcionales (opcional):"
echo "docker exec -it ${IMAGE_NAME} python tests.py"
