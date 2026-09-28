# TCC — Estratégias de Comunicação entre Microserviços

**Aluno:** Matheus Ximenes Ferreira  
**Orientadora:** Prof.ª Ariel Da Silva Dias  
**Curso:** MBA em Engenharia de Software — USP/Esalq

---

## Sobre o projeto

Pesquisa experimental que compara três estratégias de comunicação entre microserviços — **REST**, **gRPC** e **Mensageria** — em ambientes local (Docker) e nuvem, avaliando métricas de desempenho e consumo de recursos.

O sistema simula um cenário de e-commerce com quatro microserviços independentes: **pedidos**, **usuário**, **pagamento** e **estoque**.

## Estrutura do repositório

```
├── services/          # Código-fonte dos microserviços (arquitetura hexagonal)
├── communication/     # Contratos: .proto do gRPC e filas da mensageria
├── infrastructure/    # Docker Compose (local) e Terraform (nuvem AWS)
├── analysis/          # Coleta, exportação e análise estatística
├── metricas/          # Resultados das coletas (gerado automaticamente)
├── load-tests/        # Cenários de carga com k6
├── monitoring/        # Configurações de Prometheus e Grafana
└── docs/              # Documentação e referências bibliográficas
```

## Tecnologias

- **Linguagem:** Python 3.12.0
- **Framework:** FastAPI
- **Banco de dados:** PostgreSQL
- **Containers:** Docker + Docker Compose
- **Comunicação:** REST (FastAPI + aiohttp), gRPC (grpcio), Mensageria (RabbitMQ + aio-pika)
- **Métricas:** Prometheus (servidor), k6 (cliente) e docker stats (recursos)
- **Geração de carga:** k6
- **Nuvem:** AWS EC2 provisionada com Terraform
- **Análise:** pandas + SciPy (testes não paramétricos)

## Estratégias de comunicação

O k6 sempre chama `POST /orders/` (REST) no serviço de pedidos. O que muda entre as
estratégias é como o **pedidos** conversa com **usuário**, **estoque** e **pagamento**:

| `ESTRATEGIA` | Transporte interno | Adaptadores |
|---|---|---|
| `rest` | HTTP/1.1 + JSON | `clients/http/` → routers FastAPI |
| `grpc` | HTTP/2 + Protobuf | `clients/grpc/` → `infrastructure/grpc/server.py` |
| `mensageria` | AMQP (RabbitMQ), RPC sobre fila | `clients/amqp/` → `infrastructure/amqp/consumer.py` |

Os casos de uso e o domínio são os mesmos nas três: só os adaptadores de infraestrutura mudam.
Contratos em `communication/grpc/proto/ecommerce.proto` e `communication/messaging/rabbitmq/`.

## Como executar

```bash
# Ambiente local com banco em memória (mock)
docker compose -f infrastructure/docker/docker-compose.mock.yml up --build

# Ambiente local com banco Postgres
docker compose -f infrastructure/docker/docker-compose.yml up --build

# Outra estratégia (a mensageria precisa do perfil que sobe o RabbitMQ)
ESTRATEGIA=grpc docker compose -f infrastructure/docker/docker-compose.yml up --build
ESTRATEGIA=mensageria docker compose -f infrastructure/docker/docker-compose.yml --profile mensageria up --build
```

## Testes de carga (k6)

```bash
# Bateria completa: 3 estratégias × 4 cenários × 10 repetições, estratégias intercaladas (~4,5 h)
load-tests/k6/bateria.sh -a local

# Uma estratégia, todos os cenários (baixa, moderada, alta, rampup), 10 repetições
load-tests/k6/executar.sh -e grpc

# Subconjunto, com menos repetições
load-tests/k6/executar.sh -c "baixa moderada" -r 5

# Opções: -e estratégia, -a ambiente, -m postgres|mock, -w aquecimento (s), -d medição (s)
load-tests/k6/executar.sh -h
```

Cada repetição parte de um ambiente limpo (`down -v` + `up`), aquece por 30 s e mede por 60 s,
pelo lado do cliente (k6) e do servidor (coletor Prometheus) na mesma janela. Recursos por
contêiner são fixados nos docker-compose (`CPUS_SERVICO`, `MEM_SERVICO`, `CPUS_BANCO`, `MEM_BANCO`).

## Métricas coletadas

Latência média, latência p95, throughput, taxa de erro, uso de CPU e memória, salvas em `metricas/`:

- `k6_resumo.json` / `k6.csv` — medição do cliente (latência exata: média, mediana, p90/p95/p99)
- `endpoints.csv` / `servicos.csv` / `tabela.md` — medição do servidor, por endpoint e serviço
- `analysis/data/` — todas as execuções consolidadas, e `resumo_k6.md` com média ± desvio padrão
  entre repetições

- `docker_stats.csv` / `recursos.csv` — CPU e memória por contêiner (inclui bancos e broker)

## Análise estatística

```bash
analysis/analisar.sh   # reconsolida e gera analysis/resultados/ (relatorio.md, CSVs, figuras)
```

Descritiva (média, DP, mediana, CV, IC 95%), Kruskal-Wallis + Mann-Whitney com correção de Holm
e delta de Cliff entre estratégias, e Mann-Whitney + Brown-Forsythe entre ambientes.

## Ambiente em nuvem (AWS)

```bash
infrastructure/cloud/nuvem.sh criar     # VM c6i.4xlarge via Terraform
infrastructure/cloud/nuvem.sh enviar    # copia o código
infrastructure/cloud/nuvem.sh bateria   # roda a bateria na VM (~4,5 h, ~US$ 4)
infrastructure/cloud/nuvem.sh baixar    # traz os resultados
infrastructure/cloud/nuvem.sh destruir  # apaga tudo (encerra a cobrança)
```

A VM roda o mesmo docker-compose, com os mesmos limites por contêiner e o k6 no mesmo host.
