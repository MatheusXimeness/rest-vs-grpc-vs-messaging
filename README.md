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
├── services/          # Código-fonte dos microserviços
├── infrastructure/    # Docker Compose e configuração de infraestrutura
├── analysis/          # Scripts de coleta de métricas e geração de gráficos
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
- **Métricas:** Prometheus
- **Geração de carga:** k6

## Como executar

```bash
# Ambiente local com banco em memória (mock)
docker compose -f infrastructure/docker/docker-compose.mock.yml up --build

# Ambiente local com banco Postgres
docker compose -f infrastructure/docker/docker-compose.yml up --build
```

## Testes de carga (k6)

```bash
# Todos os cenários (baixa, moderada, alta, rampup), 10 repetições cada, modo postgres
load-tests/k6/executar.sh

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

Para reprocessar e reconsolidar: `cd analysis && python exportar.py` (Python 3.10+).
