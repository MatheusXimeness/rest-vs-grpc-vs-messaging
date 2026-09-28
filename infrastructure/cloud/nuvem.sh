#!/usr/bin/env bash
# Ciclo completo do experimento em nuvem (AWS), a partir da máquina local.
#
#   infrastructure/cloud/nuvem.sh criar      # cria a VM (terraform apply) e espera o Docker
#   infrastructure/cloud/nuvem.sh enviar     # copia o código para a VM (rsync)
#   infrastructure/cloud/nuvem.sh teste      # execução curta de validação (1 cenário, 20 s)
#   infrastructure/cloud/nuvem.sh bateria    # inicia a bateria completa na VM (~4,5 h)
#   infrastructure/cloud/nuvem.sh status     # últimas linhas do log da bateria
#   infrastructure/cloud/nuvem.sh baixar     # traz os resultados para metricas/ local
#   infrastructure/cloud/nuvem.sh ssh        # abre um terminal na VM
#   infrastructure/cloud/nuvem.sh destruir   # apaga TUDO na AWS (para a cobrança)
#
# Pré-requisitos: terraform, AWS CLI configurada (aws configure) e chave SSH em
# ~/.ssh/id_ed25519(.pub). A bateria roda dentro de um "nohup" na VM: pode fechar o
# terminal local ou desligar a máquina, e depois usar status/baixar.
#
# Custo: c6i.4xlarge ≈ US$ 0,68/h em us-east-1 → bateria de 4,5 h + preparo ≈ US$ 4.
# Não esqueça o "destruir" ao final.

set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
TF_DIR="$RAIZ/infrastructure/cloud/terraform"
REMOTO=/home/ubuntu/tcc
SSH_OPTS=(-o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30)

tf() { terraform -chdir="$TF_DIR" "$@"; }
ip() { tf output -raw ip_publico; }
remoto() { ssh "${SSH_OPTS[@]}" "ubuntu@$(ip)" "$@"; }

case "${1:-}" in
  criar)
    meu_ip="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')/32"
    echo "Liberando SSH apenas para $meu_ip"
    tf init -input=false
    tf apply -input=false -auto-approve -var "meu_ip=$meu_ip"
    echo "Aguardando a VM instalar o Docker (2 a 4 min)..."
    for _ in $(seq 1 60); do
      remoto test -f /home/ubuntu/.pronto 2>/dev/null && { echo "VM pronta: $(ip)"; exit 0; }
      sleep 10
    done
    echo "ERRO: a VM não ficou pronta em 10 min (ver: nuvem.sh ssh; sudo cat /var/log/cloud-init-output.log)"
    exit 1
    ;;
  enviar)
    rsync -az --delete -e "ssh ${SSH_OPTS[*]}" \
      --exclude .git --exclude metricas --exclude .idea --exclude '__pycache__' \
      --exclude 'infrastructure/cloud/terraform/.terraform*' --exclude '*.tfstate*' \
      "$RAIZ/" "ubuntu@$(ip):$REMOTO/"
    remoto "mkdir -p $REMOTO/metricas"
    echo "Código enviado para $(ip):$REMOTO"
    ;;
  teste)
    remoto "cd $REMOTO && for e in rest grpc mensageria; do load-tests/k6/executar.sh -e \$e -a nuvem -c moderada -r 1 -w 5 -d 20 | grep -E '^\[|AVISO|ERRO'; done; mkdir -p metricas/_testes && mv metricas/*_nuvem_* metricas/_testes/"
    echo "Validação concluída (resultados em metricas/_testes na VM, fora do dataset)."
    ;;
  bateria)
    remoto "cd $REMOTO && nohup load-tests/k6/bateria.sh -a nuvem -r ${REPETICOES:-10} > metricas/bateria_nuvem.log 2>&1 &"
    echo "Bateria iniciada na VM. Acompanhe com: $0 status"
    ;;
  status)
    remoto "tail -n 15 $REMOTO/metricas/bateria_nuvem.log; echo; ls $REMOTO/metricas | grep -c _nuvem_ | xargs echo 'execuções concluídas:'"
    ;;
  baixar)
    rsync -az -e "ssh ${SSH_OPTS[*]}" --include '*_nuvem_*/***' --include 'bateria_nuvem.log' --exclude '*' \
      "ubuntu@$(ip):$REMOTO/metricas/" "$RAIZ/metricas/"
    echo "Resultados copiados para metricas/. Reconsolidando..."
    docker run --rm -v "$RAIZ":/w -w /w/analysis python:3.12-slim python exportar.py | tail -3
    ;;
  ssh)
    remoto
    ;;
  destruir)
    meu_ip="$(curl -fsS https://checkip.amazonaws.com | tr -d '[:space:]')/32"
    tf destroy -input=false -auto-approve -var "meu_ip=$meu_ip"
    ;;
  *)
    sed -n '2,19p' "$0"
    exit 1
    ;;
esac
