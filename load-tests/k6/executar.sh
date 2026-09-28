#!/usr/bin/env bash
# Executa os cenários de carga com repetições, medindo pelo lado do cliente (k6) e do
# servidor (coletor Prometheus) na mesma janela de tempo.
#
# Cada repetição parte de um ambiente limpo (docker compose down -v + up), para que as
# repetições sejam independentes entre si.
#
# Uso: load-tests/k6/executar.sh [opções]
#   -e ESTRATEGIA   rest | grpc | mensageria          (default: rest)
#   -a AMBIENTE     local | nuvem                     (default: local)
#   -m MODO         postgres | mock                   (default: postgres)
#   -c CENARIOS     lista entre aspas                 (default: "baixa moderada alta rampup")
#   -r REPETICOES   repetições por cenário            (default: 10)
#   -w AQUECIMENTO  segundos de aquecimento           (default: 30)
#   -d MEDICAO      segundos de medição               (default: 60)
#
# Exemplo: load-tests/k6/executar.sh -c "baixa moderada" -r 5
#
# Resultados: metricas/<estrategia>_<ambiente>_<cenario>_rNN_<timestamp>/ com k6_resumo.json,
# CSVs e tabela do coletor, e o consolidado em analysis/data/.

set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"

ESTRATEGIA=rest
AMBIENTE=local
MODO=postgres
CENARIOS="baixa moderada alta rampup"
REPETICOES=10
AQUECIMENTO=30
MEDICAO=60

while getopts "e:a:m:c:r:w:d:h" opt; do
  case $opt in
    e) ESTRATEGIA=$OPTARG ;;
    a) AMBIENTE=$OPTARG ;;
    m) MODO=$OPTARG ;;
    c) CENARIOS=$OPTARG ;;
    r) REPETICOES=$OPTARG ;;
    w) AQUECIMENTO=$OPTARG ;;
    d) MEDICAO=$OPTARG ;;
    *) sed -n '2,21p' "$0"; exit 1 ;;
  esac
done

case $MODO in
  postgres) COMPOSE_FILE="$RAIZ/infrastructure/docker/docker-compose.yml" ;;
  mock)     COMPOSE_FILE="$RAIZ/infrastructure/docker/docker-compose.mock.yml" ;;
  *) echo "Modo inválido: $MODO"; exit 1 ;;
esac

# Lidas pelo docker-compose
export ESTRATEGIA AMBIENTE
export COLETA_AUTOMATICA=false

compose() { docker compose -f "$COMPOSE_FILE" "$@"; }

# Espera o k6 começar a enviar pedidos (primeira requisição registrada em /metrics).
aguardar_primeira_requisicao() {
  for _ in $(seq 1 300); do
    curl -s http://localhost:8000/metrics | grep -q 'endpoint="/orders/"' && return 0
    sleep 0.2
  done
  echo "ERRO: o k6 não enviou requisições em 60 s (ver k6.log)"
  exit 1
}

aguardar_servicos() {
  for porta in 8000 8001 8002 8003; do
    for _ in $(seq 1 90); do
      curl -sf "http://localhost:$porta/health" >/dev/null && continue 2
      sleep 1
    done
    echo "ERRO: serviço na porta $porta não respondeu ao /health em 90 s"
    exit 1
  done
}

total=$(( $(wc -w <<< "$CENARIOS") * REPETICOES ))
echo "=== $ESTRATEGIA | $AMBIENTE | modo $MODO | cenários: $CENARIOS | $REPETICOES repetições ==="
echo "    aquecimento ${AQUECIMENTO}s + medição ${MEDICAO}s por execução, $total execuções"

compose build --quiet

n=0
for cenario in $CENARIOS; do
  for rep in $(seq 1 "$REPETICOES"); do
    n=$((n + 1))
    id=$(printf "%s_%s_%s_r%02d_%s" "$ESTRATEGIA" "$AMBIENTE" "$cenario" "$rep" "$(date -u +%Y%m%d_%H%M%S)")
    dir="$RAIZ/metricas/$id"
    mkdir -p "$dir"
    echo "[$n/$total] $cenario — repetição $rep → metricas/$id"

    compose --profile carga down -v --remove-orphans >/dev/null 2>&1
    compose up -d --quiet-pull >/dev/null 2>&1
    aguardar_servicos

    compose --profile carga run --rm -T \
      -e CENARIO="$cenario" -e AQUECIMENTO="$AQUECIMENTO" -e MEDICAO="$MEDICAO" -e SAIDA="/metricas/$id" \
      k6 run --quiet /scripts/scenarios/pedidos.js > "$dir/k6.log" 2>&1 &
    k6_pid=$!

    # Alinha a janela do coletor com a medição do k6: a primeira leitura acontece no fim do
    # aquecimento, contado a partir da primeira requisição, e a segunda MEDICAO s depois.
    aguardar_primeira_requisicao
    inicio=$(awk -v t="$(date +%s.%N)" -v a="$AQUECIMENTO" 'BEGIN { printf "%.3f", t + a }')
    compose exec -T collector python coletar_metricas.py \
      --tipo "$ESTRATEGIA" --ambiente "$AMBIENTE" --cenario "$cenario" --repeticao "$rep" \
      --intervalo "$MEDICAO" --inicio "$inicio" --saida "metricas/$id" > "$dir/coletor.log" 2>&1 \
      || echo "    AVISO: coletor falhou (ver coletor.log)"

    wait "$k6_pid" || echo "    AVISO: k6 terminou com erro (ver k6.log)"
    [ -f "$dir/k6_resumo.json" ] || echo "    AVISO: k6_resumo.json não foi gerado"
  done
done

compose --profile carga down -v --remove-orphans >/dev/null 2>&1

echo "=== Consolidando resultados ==="
docker run --rm -v "$RAIZ":/w -w /w/analysis python:3.12-slim python exportar.py
