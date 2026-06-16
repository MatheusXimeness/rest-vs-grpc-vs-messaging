FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Roda o script em loop com intervalo configurável via env var
CMD ["sh", "-c", "\
  while true; do \
    python coletar_metricas.py --tipo ${TIPO:-rest} --intervalo ${INTERVALO_COLETA:-10}; \
    echo \"Próxima coleta em ${INTERVALO_LOOP:-300}s...\"; \
    sleep ${INTERVALO_LOOP:-300}; \
  done"]
