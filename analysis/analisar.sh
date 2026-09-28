#!/usr/bin/env bash
# Reconsolida os resultados e roda a análise estatística num contêiner Python 3.12
# (a mesma imagem do coletor), sem depender do Python instalado na máquina.
#
# Uso: analysis/analisar.sh
# Saída: analysis/data/ (consolidado) e analysis/resultados/ (relatório, tabelas, figuras)
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
docker build -q -t tcc-analise "$RAIZ/analysis" >/dev/null
docker run --rm -v "$RAIZ":/w -w /w/analysis tcc-analise sh -c "python exportar.py | tail -4 && python estatistica.py"
