#!/usr/bin/env bash
# Bateria completa de um ambiente: 3 estratégias × 4 cenários × N repetições.
#
# As estratégias são intercaladas por repetição, com a ordem rotacionada a cada rodada
# (r1: rest, grpc, mensageria; r2: grpc, mensageria, rest; r3: mensageria, rest, grpc...).
# Assim, uma variação lenta do host ao longo das horas (aquecimento, tarefas em segundo
# plano, vizinhos barulhentos na nuvem) se distribui entre as estratégias, em vez de
# recair sobre a que rodou por último.
#
# Uso: load-tests/k6/bateria.sh [-a local|nuvem] [-r REPETICOES] [-p PRIMEIRA]
#   -p permite retomar uma bateria interrompida a partir da repetição PRIMEIRA.
#
# Duração: ~2,2 min por execução → 120 execuções ≈ 4,5 h.

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
AMBIENTE=local
REPETICOES=10
PRIMEIRA=1
while getopts "a:r:p:h" opt; do
  case $opt in
    a) AMBIENTE=$OPTARG ;;
    r) REPETICOES=$OPTARG ;;
    p) PRIMEIRA=$OPTARG ;;
    *) sed -n '2,13p' "$0"; exit 1 ;;
  esac
done

ESTRATEGIAS=(rest grpc mensageria)
inicio=$(date +%s)
for rep in $(seq "$PRIMEIRA" "$REPETICOES"); do
  for i in 0 1 2; do
    e=${ESTRATEGIAS[$(( (rep - 1 + i) % 3 ))]}
    echo "##### $(date '+%F %T') | rodada $rep/$REPETICOES | $e"
    "$DIR/executar.sh" -e "$e" -a "$AMBIENTE" -r 1 -s "$rep"
  done
done
echo "##### Bateria concluída em $(( ($(date +%s) - inicio) / 60 )) min"
