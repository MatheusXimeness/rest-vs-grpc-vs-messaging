#!/usr/bin/env python3
"""
Coleta métricas dos microserviços e gera gráficos para análise do TCC.
Uso: python coletar_metricas.py --tipo rest [--intervalo 10]
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import requests
import seaborn as sns
from prometheus_client.parser import text_string_to_metric_families

# --- Configuração ---
# URLs configuráveis via env var para funcionar tanto local quanto no Docker

SERVICES = {
    "pedidos": os.getenv("PEDIDOS_URL", "http://localhost:8000"),
    "estoque": os.getenv("ESTOQUE_URL", "http://localhost:8003"),
}

sns.set_theme(style="whitegrid", palette="muted")


# --- Coleta e parse ---

def scrape(service_name: str, base_url: str) -> dict | None:
    """Coleta e parseia as métricas de um serviço. Retorna None se indisponível."""
    try:
        resp = requests.get(f"{base_url}/metrics", timeout=5)
        resp.raise_for_status()
        return _parse(resp.text)
    except Exception as exc:
        print(f"  [AVISO] '{service_name}' indisponível: {exc}")
        return None


def _parse(text: str) -> dict:
    """Converte o formato texto Prometheus para dicionário estruturado."""
    data: dict = {"histograms": {}, "counters": {}, "gauges": {}}

    for family in text_string_to_metric_families(text):
        for sample in family.samples:
            name: str = sample.name
            labels: dict = sample.labels
            value: float = sample.value

            if name.startswith("http_request_duration_seconds"):
                _parse_histogram(data, name, labels, value)
            elif name == "http_requests_total":
                key = (labels.get("method", ""), labels.get("endpoint", ""), labels.get("http_status", ""))
                data["counters"].setdefault("http_requests_total", {})[key] = value
            elif name == "process_cpu_seconds_total":
                data["counters"]["process_cpu_seconds_total"] = value
            elif name == "process_resident_memory_bytes":
                data["gauges"]["process_resident_memory_bytes"] = value

    return data


def _parse_histogram(data: dict, name: str, labels: dict, value: float):
    hist = data["histograms"].setdefault("http_request_duration_seconds", {})
    key = (labels.get("method", ""), labels.get("endpoint", ""))
    entry = hist.setdefault(key, {"buckets": [], "sum": 0.0, "count": 0.0})

    if name.endswith("_bucket"):
        entry["buckets"].append((float(labels.get("le", "inf")), value))
    elif name.endswith("_sum"):
        entry["sum"] = value
    elif name.endswith("_count"):
        entry["count"] = value


# --- Cálculo de métricas ---

def calc_latency(histogram: dict) -> dict:
    """Retorna {label_endpoint: {avg_ms, p95_ms, count}} por endpoint."""
    result = {}
    for (method, endpoint), data in histogram.items():
        count = data["count"]
        if count == 0:
            continue

        avg_ms = (data["sum"] / count) * 1000

        # p95 via interpolação linear nos buckets do histogram
        target = 0.95 * count
        p95_ms = 0.0
        buckets = sorted(data["buckets"], key=lambda x: x[0])
        for i, (le, cum) in enumerate(buckets):
            if cum >= target:
                if i == 0:
                    p95_ms = le * 1000
                else:
                    prev_le, prev_cum = buckets[i - 1]
                    frac = (target - prev_cum) / (cum - prev_cum) if cum != prev_cum else 0
                    p95_ms = (prev_le + frac * (le - prev_le)) * 1000
                break

        result[f"{method} {endpoint}"] = {
            "avg_ms": round(avg_ms, 3),
            "p95_ms": round(p95_ms, 3),
            "count": int(count),
        }

    return result


def calc_throughput(counts1: dict, counts2: dict, interval: float) -> dict:
    """Calcula req/s por endpoint entre duas coletas."""
    totals: dict[str, float] = {}
    for key in set(counts1) | set(counts2):
        method, endpoint, _ = key
        label = f"{method} {endpoint}"
        delta = max(0.0, counts2.get(key, 0) - counts1.get(key, 0))
        totals[label] = totals.get(label, 0.0) + delta
    return {k: round(v / interval, 4) for k, v in totals.items()}


def calc_error_rate(counts: dict) -> float:
    """Retorna % de requisições com status 4xx ou 5xx."""
    total = sum(counts.values())
    errors = sum(v for (_, _, status), v in counts.items() if status.startswith(("4", "5")))
    return round((errors / total * 100), 4) if total > 0 else 0.0


def calc_cpu(cpu1: float | None, cpu2: float, interval: float) -> float | None:
    """Retorna uso de CPU em % calculado entre as duas coletas."""
    if cpu1 is None:
        return None
    return round(max(0.0, (cpu2 - cpu1) / interval * 100), 4)


# --- Consolidação do relatório ---

def build_report(snap1: dict, snap2: dict, interval: int) -> dict:
    report = {}

    for svc in SERVICES:
        s1 = snap1.get(svc)
        s2 = snap2.get(svc)

        if s2 is None:
            report[svc] = {"disponivel": False}
            continue

        entry: dict = {"disponivel": True}

        hist = s2["histograms"].get("http_request_duration_seconds", {})
        if hist:
            entry["latencia"] = calc_latency(hist)

        cnt1 = s1["counters"].get("http_requests_total", {}) if s1 else {}
        cnt2 = s2["counters"].get("http_requests_total", {})
        if cnt2:
            entry["throughput"] = calc_throughput(cnt1, cnt2, interval)
            entry["error_rate"] = calc_error_rate(cnt2)

        cpu1 = s1["counters"].get("process_cpu_seconds_total") if s1 else None
        cpu2 = s2["counters"].get("process_cpu_seconds_total")
        if cpu2 is not None:
            entry["cpu_percent"] = calc_cpu(cpu1, cpu2, interval)

        mem = s2["gauges"].get("process_resident_memory_bytes")
        if mem is not None:
            entry["memory_mb"] = round(mem / (1024 * 1024), 2)

        report[svc] = entry

    return report


# --- Gráficos ---

def _available(report: dict) -> list[str]:
    return [s for s, d in report.items() if d.get("disponivel")]


def _grouped_bars(ax, endpoints: list, series: dict[str, list], ylabel: str, title: str):
    """Desenha barras agrupadas por endpoint com uma série por serviço."""
    n = len(series)
    width = 0.7 / max(n, 1)
    x = range(len(endpoints))

    for i, (label, values) in enumerate(series.items()):
        offset = (i - n / 2) * width + width / 2
        ax.bar([xi + offset for xi in x], values, width, label=label)

    ax.set_xticks(list(x))
    ax.set_xticklabels([ep[:25] for ep in endpoints], rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)


def plot_latency(report: dict, out: Path):
    services = _available(report)
    all_eps = sorted({ep for svc in services for ep in report[svc].get("latencia", {})})
    if not all_eps:
        print("  [INFO] Sem dados de latência para plotar.")
        return

    fig, (ax_avg, ax_p95) = plt.subplots(1, 2, figsize=(14, 5))

    _grouped_bars(ax_avg, all_eps,
                  {svc: [report[svc].get("latencia", {}).get(ep, {}).get("avg_ms", 0) for ep in all_eps]
                   for svc in services},
                  "ms", "Latência Média (ms)")

    _grouped_bars(ax_p95, all_eps,
                  {svc: [report[svc].get("latencia", {}).get(ep, {}).get("p95_ms", 0) for ep in all_eps]
                   for svc in services},
                  "ms", "Latência p95 (ms)")

    fig.suptitle("Latência por Endpoint e Serviço")
    fig.tight_layout()
    fig.savefig(out / "latencia.png", dpi=150)
    plt.close(fig)
    print("  → latencia.png")


def plot_throughput(report: dict, out: Path):
    services = _available(report)
    all_eps = sorted({ep for svc in services for ep in report[svc].get("throughput", {})})
    if not all_eps:
        print("  [INFO] Sem dados de throughput para plotar.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    _grouped_bars(ax, all_eps,
                  {svc: [report[svc].get("throughput", {}).get(ep, 0) for ep in all_eps]
                   for svc in services},
                  "req/s", "Throughput por Endpoint (req/s)")
    fig.tight_layout()
    fig.savefig(out / "throughput.png", dpi=150)
    plt.close(fig)
    print("  → throughput.png")


def plot_error_rate(report: dict, out: Path):
    services = _available(report)
    rates = [report[svc].get("error_rate", 0) for svc in services]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(services, rates, color=sns.color_palette("muted", len(services)))
    ax.set_title("Taxa de Erro por Serviço (%)")
    ax.set_ylabel("%")
    ax.set_ylim(0, max(max(rates, default=0) * 1.3, 5))
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{rate:.2f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "error_rate.png", dpi=150)
    plt.close(fig)
    print("  → error_rate.png")


def plot_cpu(report: dict, out: Path):
    services = _available(report)
    data = [(s, report[s].get("cpu_percent") or 0) for s in services if report[s].get("cpu_percent") is not None]
    if not data:
        print("  [INFO] Sem dados de CPU para plotar.")
        return

    svcs, values = zip(*data)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(svcs, values, color=sns.color_palette("muted", len(svcs)))
    ax.set_title("Uso de CPU por Serviço (%)")
    ax.set_ylabel("%")
    fig.tight_layout()
    fig.savefig(out / "cpu.png", dpi=150)
    plt.close(fig)
    print("  → cpu.png")


def plot_memory(report: dict, out: Path):
    services = _available(report)
    data = [(s, report[s]["memory_mb"]) for s in services if "memory_mb" in report[s]]
    if not data:
        print("  [INFO] Sem dados de memória para plotar.")
        return

    svcs, values = zip(*data)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(svcs, values, color=sns.color_palette("muted", len(svcs)))
    ax.set_title("Uso de Memória por Serviço (MB)")
    ax.set_ylabel("MB")
    fig.tight_layout()
    fig.savefig(out / "memoria.png", dpi=150)
    plt.close(fig)
    print("  → memoria.png")


def plot_consolidated(report: dict, out: Path):
    services = _available(report)
    if not services:
        return

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle("Painel Consolidado de Métricas", fontsize=14, fontweight="bold")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.35)

    lat_eps = sorted({ep for svc in services for ep in report[svc].get("latencia", {})})
    tp_eps = sorted({ep for svc in services for ep in report[svc].get("throughput", {})})

    # Latência média
    ax1 = fig.add_subplot(gs[0, 0])
    _grouped_bars(ax1, lat_eps,
                  {svc: [report[svc].get("latencia", {}).get(ep, {}).get("avg_ms", 0) for ep in lat_eps]
                   for svc in services},
                  "ms", "Latência Média (ms)")

    # Latência p95
    ax2 = fig.add_subplot(gs[0, 1])
    _grouped_bars(ax2, lat_eps,
                  {svc: [report[svc].get("latencia", {}).get(ep, {}).get("p95_ms", 0) for ep in lat_eps]
                   for svc in services},
                  "ms", "Latência p95 (ms)")

    # Throughput
    ax3 = fig.add_subplot(gs[1, 0])
    _grouped_bars(ax3, tp_eps,
                  {svc: [report[svc].get("throughput", {}).get(ep, 0) for ep in tp_eps]
                   for svc in services},
                  "req/s", "Throughput (req/s)")

    # Error rate
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.bar(services, [report[svc].get("error_rate", 0) for svc in services],
            color=sns.color_palette("muted", len(services)))
    ax4.set_title("Taxa de Erro (%)")
    ax4.set_ylabel("%")

    # CPU
    ax5 = fig.add_subplot(gs[2, 0])
    ax5.bar(services, [report[svc].get("cpu_percent") or 0 for svc in services],
            color=sns.color_palette("muted", len(services)))
    ax5.set_title("CPU (%)")
    ax5.set_ylabel("%")

    # Memória
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.bar(services, [report[svc].get("memory_mb") or 0 for svc in services],
            color=sns.color_palette("muted", len(services)))
    ax6.set_title("Memória (MB)")
    ax6.set_ylabel("MB")

    fig.savefig(out / "painel_consolidado.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("  → painel_consolidado.png")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Coleta métricas dos microserviços do TCC")
    parser.add_argument("--tipo", required=True, choices=["rest", "grpc", "mensageria"],
                        help="Estratégia de comunicação sendo testada")
    parser.add_argument("--intervalo", type=int, default=10,
                        help="Segundos entre as duas coletas para calcular rates (default: 10)")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("metricas") / f"{args.tipo}_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== Coleta de Métricas — {args.tipo.upper()} ===")
    print(f"Saída: {output_dir}\n")

    print("[1/2] Primeira coleta...")
    snap1 = {svc: scrape(svc, url) for svc, url in SERVICES.items()}

    print(f"      Aguardando {args.intervalo}s para calcular rates...")
    time.sleep(args.intervalo)

    print("[2/2] Segunda coleta...")
    snap2 = {svc: scrape(svc, url) for svc, url in SERVICES.items()}

    report = build_report(snap1, snap2, args.intervalo)

    json_path = output_dir / "dados_brutos.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nDados brutos: {json_path}")

    print("\nGerando gráficos...")
    plot_latency(report, output_dir)
    plot_throughput(report, output_dir)
    plot_error_rate(report, output_dir)
    plot_cpu(report, output_dir)
    plot_memory(report, output_dir)
    plot_consolidated(report, output_dir)

    print(f"\n✓ Concluído. Resultados em: {output_dir}/")


if __name__ == "__main__":
    main()
