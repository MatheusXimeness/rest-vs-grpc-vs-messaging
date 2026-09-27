#!/usr/bin/env python3
"""
Exporta os valores numéricos de cada coleta em CSV e tabela Markdown, e consolida
todas as coletas em um único dataset para a análise estatística.

Chamado automaticamente por coletar_metricas.py a cada coleta. Também pode ser
executado isoladamente para reprocessar coletas antigas e reconsolidar:

    python exportar.py [--metricas ../metricas] [--destino data]
"""

import argparse
import csv
import json
from pathlib import Path

# Endpoints de documentação do FastAPI — não fazem parte do fluxo experimental.
ENDPOINTS_IGNORADOS_TABELA = {"/docs", "/openapi.json", "/docs/oauth2-redirect", "/redoc"}

COLUNAS_META = ["estrategia", "ambiente", "cenario", "timestamp"]

COLUNAS_ENDPOINTS = COLUNAS_META + [
    "servico", "metodo", "endpoint", "requisicoes",
    "latencia_media_ms", "latencia_p95_ms", "throughput_rps", "taxa_erro_pct",
]

COLUNAS_SERVICOS = COLUNAS_META + [
    "servico", "disponivel", "taxa_erro_pct", "cpu_pct", "memoria_mb",
]


# --- Conversão do relatório em linhas ---

def _split_label(label: str) -> tuple[str, str]:
    metodo, _, endpoint = label.partition(" ")
    return metodo, endpoint


def linhas_endpoints(report: dict, meta: dict) -> list[dict]:
    base = {k: meta.get(k, "") for k in COLUNAS_META}
    linhas = []
    for svc, dados in report.items():
        if not dados.get("disponivel"):
            continue
        latencia = dados.get("latencia", {})
        throughput = dados.get("throughput", {})
        erros = dados.get("error_rate_endpoint", {})
        for label in sorted(set(latencia) | set(throughput)):
            metodo, endpoint = _split_label(label)
            lat = latencia.get(label, {})
            linhas.append({
                **base,
                "servico": svc,
                "metodo": metodo,
                "endpoint": endpoint,
                "requisicoes": lat.get("count", ""),
                "latencia_media_ms": lat.get("avg_ms", ""),
                "latencia_p95_ms": lat.get("p95_ms", ""),
                "throughput_rps": throughput.get(label, ""),
                "taxa_erro_pct": erros.get(label, ""),
            })
    return linhas


def linhas_servicos(report: dict, meta: dict) -> list[dict]:
    base = {k: meta.get(k, "") for k in COLUNAS_META}
    return [
        {
            **base,
            "servico": svc,
            "disponivel": dados.get("disponivel", False),
            "taxa_erro_pct": dados.get("error_rate", ""),
            "cpu_pct": dados.get("cpu_percent", ""),
            "memoria_mb": dados.get("memory_mb", ""),
        }
        for svc, dados in report.items()
    ]


# --- Escrita ---

def _write_csv(path: Path, colunas: list[str], linhas: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas)


def _num(valor, casas: int = 3) -> str:
    """Formata no padrão brasileiro (vírgula decimal) para colar no documento do TCC."""
    if valor in ("", None):
        return "—"
    return f"{float(valor):.{casas}f}".replace(".", ",")


def tabela_markdown(endpoints: list[dict], servicos: list[dict], meta: dict) -> str:
    """Tabela no formato da Tabela 2 dos resultados preliminares, com valores exatos."""
    por_servico = {s["servico"]: s for s in servicos}

    linhas = [
        f"Estratégia: {meta.get('estrategia', '')} | Ambiente: {meta.get('ambiente', '')} | "
        f"Cenário: {meta.get('cenario', '')} | Coleta: {meta.get('timestamp', '')}",
        "",
        "| Endpoint / Serviço | Requisições | Lat. Média (ms) | Lat. p95 (ms) | "
        "Throughput (req/s) | Erro (%) | CPU (%) | Memória (MB) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for e in endpoints:
        if e["endpoint"] in ENDPOINTS_IGNORADOS_TABELA:
            continue
        svc = por_servico.get(e["servico"], {})
        linhas.append(
            f"| {e['metodo']} {e['endpoint']} ({e['servico']}) "
            f"| {e['requisicoes']} "
            f"| {_num(e['latencia_media_ms'])} "
            f"| {_num(e['latencia_p95_ms'])} "
            f"| {_num(e['throughput_rps'], 4)} "
            f"| {_num(e['taxa_erro_pct'], 2)} "
            f"| {_num(svc.get('cpu_pct'), 2)} "
            f"| {_num(svc.get('memoria_mb'), 2)} |"
        )

    if len(linhas) == 4:
        linhas.append("| _sem requisições registradas nesta coleta_ | | | | | | | |")

    linhas += [
        "",
        "Latência e taxa de erro: acumuladas desde o início do processo. "
        "Throughput e CPU: calculados na janela entre as duas coletas. "
        "p95 estimado por interpolação nos buckets do histograma Prometheus.",
        "",
    ]
    return "\n".join(linhas)


def exportar_coleta(report: dict, meta: dict, out_dir: Path):
    """Gera metadados.json, endpoints.csv, servicos.csv e tabela.md em out_dir."""
    endpoints = linhas_endpoints(report, meta)
    servicos = linhas_servicos(report, meta)

    with open(out_dir / "metadados.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    _write_csv(out_dir / "endpoints.csv", COLUNAS_ENDPOINTS, endpoints)
    _write_csv(out_dir / "servicos.csv", COLUNAS_SERVICOS, servicos)
    (out_dir / "tabela.md").write_text(tabela_markdown(endpoints, servicos, meta), encoding="utf-8")
    print("  → metadados.json, endpoints.csv, servicos.csv, tabela.md")


# --- Reprocessamento e consolidação ---

def _meta_da_pasta(pasta: Path) -> dict:
    """Metadados de uma coleta; infere a partir do nome da pasta em coletas antigas."""
    arquivo = pasta / "metadados.json"
    if arquivo.exists():
        return json.loads(arquivo.read_text(encoding="utf-8"))
    estrategia, _, timestamp = pasta.name.partition("_")
    return {"estrategia": estrategia, "ambiente": "local", "cenario": "funcional", "timestamp": timestamp}


def _coletas(metricas_dir: Path) -> list[Path]:
    return sorted(p for p in metricas_dir.iterdir() if (p / "dados_brutos.json").exists())


def reprocessar(metricas_dir: Path):
    for pasta in _coletas(metricas_dir):
        print(f"{pasta.name}:")
        report = json.loads((pasta / "dados_brutos.json").read_text(encoding="utf-8"))
        exportar_coleta(report, _meta_da_pasta(pasta), pasta)


def consolidar(metricas_dir: Path, destino: Path):
    destino.mkdir(parents=True, exist_ok=True)
    for nome, colunas in (("endpoints", COLUNAS_ENDPOINTS), ("servicos", COLUNAS_SERVICOS)):
        linhas = []
        for pasta in _coletas(metricas_dir):
            arquivo = pasta / f"{nome}.csv"
            if arquivo.exists():
                with open(arquivo, encoding="utf-8") as f:
                    linhas.extend(csv.DictReader(f))
        saida = destino / f"{nome}.csv"
        _write_csv(saida, colunas, linhas)
        print(f"Consolidado: {saida} ({len(linhas)} linhas)")


def main():
    raiz = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Exporta e consolida as métricas coletadas")
    parser.add_argument("--metricas", type=Path, default=raiz.parent / "metricas",
                        help="Pasta com as coletas (default: ../metricas)")
    parser.add_argument("--destino", type=Path, default=raiz / "data",
                        help="Pasta do dataset consolidado (default: analysis/data)")
    args = parser.parse_args()

    reprocessar(args.metricas)
    consolidar(args.metricas, args.destino)


if __name__ == "__main__":
    main()
