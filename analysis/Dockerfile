FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Roda o script em loop com intervalo configurável via env var.
# Com COLETA_AUTOMATICA=false o contêiner fica ocioso e as coletas são disparadas
# pelo executor dos testes de carga (load-tests/k6/executar.sh) via docker exec.
CMD ["sh", "-c", "\
  if [ \"${COLETA_AUTOMATICA:-true}\" = \"false\" ]; then \
    echo 'Coleta automática desativada; aguardando disparos manuais.'; \
    exec sleep infinity; \
  fi; \
  while true; do \
    python coletar_metricas.py --tipo ${TIPO:-rest} --intervalo ${INTERVALO_COLETA:-10}; \
    echo \"Próxima coleta em ${INTERVALO_LOOP:-300}s...\"; \
    sleep ${INTERVALO_LOOP:-300}; \
  done"]
