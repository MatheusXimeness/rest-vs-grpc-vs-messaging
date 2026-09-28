#!/usr/bin/env python3
"""
Análise estatística dos experimentos de carga (k6), a partir de analysis/data/k6.csv.

Cada linha do k6.csv é UMA execução (repetição) de uma combinação
estratégia × ambiente × cenário. A unidade de análise é a execução: as ~10 repetições
de cada combinação formam a amostra usada nos testes.

Gera em analysis/resultados/:
  descritiva.csv / .md         n, média, DP, mediana, CV, IC 95%, mín., máx.
  testes_estrategias.csv / .md Kruskal-Wallis entre as 3 estratégias e Mann-Whitney par a
                               par (correção de Holm), com delta de Cliff
  testes_ambientes.csv / .md   local × nuvem por estratégia e cenário: Mann-Whitney
                               (posição) e Brown-Forsythe (variabilidade)
  recursos_containers.csv / .md CPU e memória médias por contêiner
  figuras/*.png                boxplots por cenário
  relatorio.md                 tudo acima, com a explicação dos métodos

Uso: python estatistica.py [--dados data/k6.csv] [--saida resultados]
"""

import argparse
import itertools
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from scipy import stats  # noqa: E402

ESTRATEGIAS = ["rest", "grpc", "mensageria"]
NOMES_ESTRATEGIAS = {"rest": "REST", "grpc": "gRPC", "mensageria": "Mensageria"}
CENARIOS = ["baixa", "moderada", "alta", "rampup"]
AMBIENTES = ["local", "nuvem"]
ALFA = 0.05

# (coluna do k6.csv, rótulo, casas decimais). Latências já excluem amostras suspeitas.
METRICAS = [
    ("latencia_media_ms", "Latência média (ms)", 2),
    ("latencia_mediana_ms", "Latência mediana (ms)", 2),
    ("latencia_p95_ms", "Latência p95 (ms)", 2),
    ("throughput_rps", "Throughput (req/s)", 2),
    ("taxa_erro_tecnico_pct", "Erro técnico (%)", 2),
    ("cpu_total_pct", "CPU total (% de 1 núcleo)", 1),
    ("memoria_total_mb", "Memória total (MB)", 1),
]
ROTULO = {m: r for m, r, _ in METRICAS}
CASAS = {m: c for m, _, c in METRICAS}


# --- Utilidades ---

def num(valor, casas: int = 2) -> str:
    """Número no padrão brasileiro (vírgula decimal) para colar no texto do TCC."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "—"
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_p(p: float) -> str:
    if p is None or math.isnan(p):
        return "—"
    return "< 0,001" if p < 0.001 else num(p, 3)


def cliff_delta(x: np.ndarray, y: np.ndarray) -> float:
    """Delta de Cliff: P(X > Y) − P(X < Y). Vai de −1 a 1; 0 = distribuições sobrepostas."""
    maiores = sum((xi > y).sum() for xi in x)
    menores = sum((xi < y).sum() for xi in x)
    return (maiores - menores) / (len(x) * len(y))


def magnitude_cliff(d: float) -> str:
    """Limiares de Romano et al. (2006)."""
    a = abs(d)
    if a < 0.147:
        return "desprezível"
    if a < 0.33:
        return "pequeno"
    if a < 0.474:
        return "médio"
    return "grande"


def holm(pvalores: list[float]) -> list[float]:
    """Correção de Holm-Bonferroni para comparações múltiplas."""
    m = len(pvalores)
    ordem = sorted(range(m), key=lambda i: pvalores[i])
    ajustados = [0.0] * m
    acumulado = 0.0
    for posicao, i in enumerate(ordem):
        acumulado = max(acumulado, (m - posicao) * pvalores[i])
        ajustados[i] = min(1.0, acumulado)
    return ajustados


def _teste_seguro(func, *amostras):
    """Executa o teste; devolve (nan, nan) quando não se aplica (ex.: valores todos iguais)."""
    try:
        resultado = func(*amostras)
        return float(resultado.statistic), float(resultado.pvalue)
    except ValueError:
        return float("nan"), float("nan")


def tabela_md(df: pd.DataFrame) -> str:
    linhas = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for _, row in df.iterrows():
        linhas.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join(linhas)


# --- Carga ---

def carregar(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df = df[df["cenario"].isin(CENARIOS) & df["estrategia"].isin(ESTRATEGIAS)
            & df["ambiente"].isin(AMBIENTES)].copy()
    for m, _, _ in METRICAS:
        if m in df:
            df[m] = pd.to_numeric(df[m], errors="coerce")
    df["cenario"] = pd.Categorical(df["cenario"], CENARIOS, ordered=True)
    df["estrategia"] = pd.Categorical(df["estrategia"], ESTRATEGIAS, ordered=True)
    df["ambiente"] = pd.Categorical(df["ambiente"], AMBIENTES, ordered=True)
    return df


# --- Estatística descritiva ---

def descritiva(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (amb, cen, est), g in df.groupby(["ambiente", "cenario", "estrategia"], observed=True):
        for m, _, _ in METRICAS:
            x = g[m].dropna().to_numpy()
            if len(x) == 0:
                continue
            media = x.mean()
            dp = x.std(ddof=1) if len(x) > 1 else 0.0
            # IC 95% da média pela distribuição t de Student
            meia = stats.t.ppf(0.975, len(x) - 1) * dp / math.sqrt(len(x)) if len(x) > 1 else 0.0
            linhas.append({
                "ambiente": amb, "cenario": cen, "estrategia": est, "metrica": m, "n": len(x),
                "media": media, "dp": dp, "mediana": float(np.median(x)),
                "cv_pct": (dp / media * 100) if media else float("nan"),
                "ic95_inf": media - meia, "ic95_sup": media + meia,
                "min": x.min(), "max": x.max(),
            })
    return pd.DataFrame(linhas)


def descritiva_md(desc: pd.DataFrame) -> str:
    """Uma tabela por ambiente: linhas cenário × estratégia, colunas = métricas (média ± DP)."""
    partes = []
    for amb in AMBIENTES:
        d = desc[desc["ambiente"] == amb]
        if d.empty:
            continue
        linhas = []
        for (cen, est), g in d.groupby(["cenario", "estrategia"], observed=True):
            linha = {"Cenário": cen, "Estratégia": NOMES_ESTRATEGIAS[est], "n": int(g["n"].max())}
            for m, rotulo, casas in METRICAS:
                r = g[g["metrica"] == m]
                linha[rotulo] = (f"{num(r['media'].iloc[0], casas)} ± {num(r['dp'].iloc[0], casas)}"
                                 if not r.empty else "—")
            linhas.append(linha)
        partes.append(f"### Ambiente {amb}\n\n" + tabela_md(pd.DataFrame(linhas)))
    partes.append("Valores: média ± desvio padrão entre as repetições (cada repetição = uma "
                  "execução de 60 s). Intervalos de confiança de 95% e coeficientes de variação "
                  "estão em descritiva.csv.")
    return "\n\n".join(partes)


# --- Testes entre estratégias ---

def testes_estrategias(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (amb, cen), g in df.groupby(["ambiente", "cenario"], observed=True):
        for m, _, _ in METRICAS:
            grupos = {e: g.loc[g["estrategia"] == e, m].dropna().to_numpy() for e in ESTRATEGIAS}
            grupos = {e: x for e, x in grupos.items() if len(x) >= 2}
            if len(grupos) < 2:
                continue
            h, p_kw = _teste_seguro(stats.kruskal, *grupos.values())

            pares = list(itertools.combinations(grupos, 2))
            brutos = [_teste_seguro(lambda a, b: stats.mannwhitneyu(a, b, alternative="two-sided"),
                                    grupos[a], grupos[b]) for a, b in pares]
            ajustados = holm([p if not math.isnan(p) else 1.0 for _, p in brutos])
            for (a, b), (u, p), p_adj in zip(pares, brutos, ajustados):
                d = cliff_delta(grupos[a], grupos[b])
                linhas.append({
                    "ambiente": amb, "cenario": cen, "metrica": m,
                    "kruskal_h": h, "kruskal_p": p_kw,
                    "par": f"{a} × {b}", "mediana_a": float(np.median(grupos[a])),
                    "mediana_b": float(np.median(grupos[b])),
                    "mannwhitney_u": u, "p": p, "p_holm": p_adj if not math.isnan(p) else float("nan"),
                    "cliff_delta": d, "efeito": magnitude_cliff(d),
                    "significativo": (not math.isnan(p)) and p_adj < ALFA,
                })
    return pd.DataFrame(linhas)


def testes_estrategias_md(t: pd.DataFrame) -> str:
    partes = []
    for amb in AMBIENTES:
        d = t[t["ambiente"] == amb]
        if d.empty:
            continue
        linhas = []
        for _, r in d.iterrows():
            a, b = r["par"].split(" × ")
            linhas.append({
                "Cenário": r["cenario"], "Métrica": ROTULO[r["metrica"]],
                "Kruskal-Wallis p": fmt_p(r["kruskal_p"]),
                "Par": f"{NOMES_ESTRATEGIAS[a]} × {NOMES_ESTRATEGIAS[b]}",
                "Medianas": f"{num(r['mediana_a'], CASAS[r['metrica']])} × "
                            f"{num(r['mediana_b'], CASAS[r['metrica']])}",
                "p (Holm)": fmt_p(r["p_holm"]),
                "δ de Cliff": num(r["cliff_delta"], 2) + f" ({r['efeito']})",
                "Sig.": "sim" if r["significativo"] else "não",
            })
        partes.append(f"### Ambiente {amb}\n\n" + tabela_md(pd.DataFrame(linhas)))
    partes.append("δ de Cliff > 0: a primeira estratégia do par tem valores maiores. "
                  f"Significativo: p ajustado por Holm < {num(ALFA, 2)}.")
    return "\n\n".join(partes)


# --- Local × nuvem ---

def testes_ambientes(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (cen, est), g in df.groupby(["cenario", "estrategia"], observed=True):
        for m, _, _ in METRICAS:
            loc = g.loc[g["ambiente"] == "local", m].dropna().to_numpy()
            nuv = g.loc[g["ambiente"] == "nuvem", m].dropna().to_numpy()
            if len(loc) < 2 or len(nuv) < 2:
                continue
            u, p = _teste_seguro(lambda a, b: stats.mannwhitneyu(a, b, alternative="two-sided"), loc, nuv)
            # Brown-Forsythe (Levene centrado na mediana): as variâncias diferem?
            w, p_var = _teste_seguro(lambda a, b: stats.levene(a, b, center="median"), loc, nuv)
            cv = lambda x: x.std(ddof=1) / x.mean() * 100 if x.mean() else float("nan")  # noqa: E731
            d = cliff_delta(nuv, loc)
            linhas.append({
                "cenario": cen, "estrategia": est, "metrica": m,
                "mediana_local": float(np.median(loc)), "mediana_nuvem": float(np.median(nuv)),
                "cv_local_pct": cv(loc), "cv_nuvem_pct": cv(nuv),
                "mannwhitney_u": u, "p": p, "cliff_delta_nuvem_vs_local": d, "efeito": magnitude_cliff(d),
                "brown_forsythe_w": w, "p_variancia": p_var,
            })
    return pd.DataFrame(linhas)


def testes_ambientes_md(t: pd.DataFrame) -> str:
    if t.empty:
        return "_Ainda não há execuções nos dois ambientes para comparar._"
    linhas = []
    for _, r in t.iterrows():
        c = CASAS[r["metrica"]]
        linhas.append({
            "Cenário": r["cenario"], "Estratégia": NOMES_ESTRATEGIAS[r["estrategia"]],
            "Métrica": ROTULO[r["metrica"]],
            "Mediana local × nuvem": f"{num(r['mediana_local'], c)} × {num(r['mediana_nuvem'], c)}",
            "p (posição)": fmt_p(r["p"]),
            "δ nuvem vs local": num(r["cliff_delta_nuvem_vs_local"], 2) + f" ({r['efeito']})",
            "CV local × nuvem (%)": f"{num(r['cv_local_pct'], 1)} × {num(r['cv_nuvem_pct'], 1)}",
            "p (variância)": fmt_p(r["p_variancia"]),
        })
    return (tabela_md(pd.DataFrame(linhas)) + "\n\n"
            "p (posição): Mann-Whitney bilateral. p (variância): Brown-Forsythe. CV: coeficiente de "
            "variação entre repetições; CV maior na nuvem com p (variância) < 0,05 sustenta a "
            "hipótese de maior variabilidade em nuvem.")


# --- Recursos por contêiner ---

def recursos_containers(caminho: Path) -> pd.DataFrame:
    if not caminho.exists():
        return pd.DataFrame()
    r = pd.read_csv(caminho)
    r = r[r["cenario"].isin(CENARIOS) & r["estrategia"].isin(ESTRATEGIAS) & r["ambiente"].isin(AMBIENTES)]
    r = r[~r["container"].isin(["k6", "collector"])]
    if r.empty:
        return pd.DataFrame()
    return (r.groupby(["ambiente", "cenario", "estrategia", "container"])
             .agg(execucoes=("cpu_media_pct", "size"), cpu_media_pct=("cpu_media_pct", "mean"),
                  cpu_dp=("cpu_media_pct", "std"), memoria_media_mb=("memoria_media_mb", "mean"))
             .reset_index())


def recursos_md(rc: pd.DataFrame) -> str:
    if rc.empty:
        return "_Sem dados de docker stats._"
    partes = []
    for (amb, cen), g in rc.groupby(["ambiente", "cenario"], sort=False):
        piv = g.pivot_table(index="container", columns="estrategia", values="cpu_media_pct")
        piv = piv[[e for e in ESTRATEGIAS if e in piv.columns]]
        tab = pd.DataFrame({"Contêiner": piv.index})
        for e in piv.columns:
            tab[NOMES_ESTRATEGIAS[e]] = [num(v, 1) for v in piv[e]]
        partes.append(f"**{amb} — {cen}** (CPU média, % de 1 núcleo)\n\n" + tabela_md(tab))
    return "\n\n".join(partes)


# --- Figuras ---

def figuras(df: pd.DataFrame, destino: Path):
    destino.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    paleta = {"rest": "#4C72B0", "grpc": "#55A868", "mensageria": "#C44E52"}
    for m in ["latencia_mediana_ms", "latencia_p95_ms", "throughput_rps", "cpu_total_pct"]:
        if df[m].dropna().empty:
            continue
        ambientes = [a for a in AMBIENTES if not df[df["ambiente"] == a].empty]
        fig, eixos = plt.subplots(1, len(ambientes), figsize=(6.5 * len(ambientes), 4.5),
                                  squeeze=False, sharey=False)
        for ax, amb in zip(eixos[0], ambientes):
            d = df[df["ambiente"] == amb]
            sns.boxplot(data=d, x="cenario", y=m, hue="estrategia", palette=paleta, ax=ax,
                        order=[c for c in CENARIOS if c in set(d["cenario"])], hue_order=ESTRATEGIAS,
                        showfliers=True, linewidth=1)
            if m.startswith("latencia"):
                ax.set_yscale("log")
            ax.set_title(f"Ambiente {amb}")
            ax.set_xlabel("Cenário de carga")
            ax.set_ylabel(ROTULO[m] + (" — escala log" if m.startswith("latencia") else ""))
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles, [NOMES_ESTRATEGIAS.get(lbl, lbl) for lbl in labels], title="Estratégia")
        fig.tight_layout()
        fig.savefig(destino / f"boxplot_{m}.png", dpi=150)
        plt.close(fig)


# --- Main ---

METODOS = """## Métodos

- **Unidade de análise:** cada execução (repetição) de 60 s de medição, após 30 s de aquecimento,
  com ambiente recriado do zero. As métricas de cada execução vêm do k6 (lado do cliente);
  CPU e memória somam os contêineres da aplicação (serviços, bancos e broker) via `docker stats`.
- **Descritiva:** média, desvio padrão, mediana, coeficiente de variação (CV) e intervalo de
  confiança de 95% da média (t de Student).
- **Entre estratégias:** Kruskal-Wallis (3 grupos) seguido de Mann-Whitney bilateral par a par,
  com correção de Holm para comparações múltiplas. Testes não paramétricos porque, com ~10
  repetições por grupo, não se pode assumir normalidade, e métricas de latência costumam ser
  assimétricas.
- **Tamanho de efeito:** delta de Cliff (−1 a 1), com os limiares de Romano et al. (2006):
  < 0,147 desprezível, < 0,33 pequeno, < 0,474 médio, ≥ 0,474 grande. Complementa o p-valor,
  que sozinho não diz se a diferença é relevante.
- **Local × nuvem:** Mann-Whitney (diferença de posição) e Brown-Forsythe (diferença de
  variabilidade), além da comparação dos CVs.
- **Nível de significância:** α = 0,05.
- **Amostras suspeitas:** requisições com duração acima de 2× o timeout (impossíveis na prática,
  causadas por saltos de relógio do host) são excluídas das estatísticas de latência pelo k6 e
  contadas em `amostras_suspeitas`.
"""


def main():
    raiz = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Análise estatística dos experimentos")
    parser.add_argument("--dados", type=Path, default=raiz / "data" / "k6.csv")
    parser.add_argument("--recursos", type=Path, default=raiz / "data" / "recursos.csv")
    parser.add_argument("--saida", type=Path, default=raiz / "resultados")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)

    df = carregar(args.dados)
    if df.empty:
        raise SystemExit(f"Nenhuma execução formal encontrada em {args.dados}")
    contagem = df.groupby(["ambiente", "estrategia", "cenario"], observed=True).size()
    print("Execuções por grupo:\n" + contagem.to_string())

    desc = descritiva(df)
    t_est = testes_estrategias(df)
    t_amb = testes_ambientes(df)
    rc = recursos_containers(args.recursos)

    desc.round(4).to_csv(args.saida / "descritiva.csv", index=False)
    t_est.round(6).to_csv(args.saida / "testes_estrategias.csv", index=False)
    t_amb.round(6).to_csv(args.saida / "testes_ambientes.csv", index=False)
    rc.round(3).to_csv(args.saida / "recursos_containers.csv", index=False)

    secoes = {
        "descritiva.md": "## Estatística descritiva\n\n" + descritiva_md(desc),
        "testes_estrategias.md": "## Comparação entre estratégias\n\n" + testes_estrategias_md(t_est),
        "testes_ambientes.md": "## Comparação entre ambientes (local × nuvem)\n\n" + testes_ambientes_md(t_amb),
        "recursos_containers.md": "## CPU por contêiner\n\n" + recursos_md(rc),
    }
    for nome, texto in secoes.items():
        (args.saida / nome).write_text(texto + "\n", encoding="utf-8")

    figuras(df, args.saida / "figuras")

    suspeitas = int(pd.to_numeric(df.get("amostras_suspeitas"), errors="coerce").fillna(0).sum())
    cabecalho = (f"# Resultados dos experimentos\n\nGerado por `analysis/estatistica.py` a partir de "
                 f"{len(df)} execuções. Amostras suspeitas excluídas (saltos de relógio): {suspeitas}.\n")
    (args.saida / "relatorio.md").write_text(
        cabecalho + "\n" + METODOS + "\n" + "\n\n".join(secoes.values())
        + "\n\n## Figuras\n\n" + "\n".join(f"![{p.stem}](figuras/{p.name})"
                                           for p in sorted((args.saida / "figuras").glob("*.png"))) + "\n",
        encoding="utf-8")
    print(f"\nResultados em {args.saida}/ (relatorio.md, CSVs e figuras)")


if __name__ == "__main__":
    main()
