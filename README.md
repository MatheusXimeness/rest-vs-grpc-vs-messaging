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

## Métricas coletadas

Latência média, latência p95, throughput, taxa de erro, uso de CPU e memória — coletadas automaticamente pelo serviço `collector` e salvas em `metricas/`.
