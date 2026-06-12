from __future__ import annotations

import csv
import json
from pathlib import Path


def generate_analysis_outputs(
    baseline_summary_path: Path,
    scenario_comparison_path: Path,
    shock_comparison_path: Path,
    rebalance_comparison_path: Path,
    profile_comparison_path: Path,
    output_dir: Path,
    docs_output_path: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = read_json(baseline_summary_path)
    scenarios = read_csv(scenario_comparison_path)
    shocks = read_csv(shock_comparison_path)
    rebalances = read_csv(rebalance_comparison_path)
    profiles = read_csv(profile_comparison_path)

    write_final_metrics(output_dir / "final_metrics.csv", baseline, scenarios, shocks, rebalances, profiles)
    write_bar_chart_svg(
        output_dir / "shock_returns.svg",
        shocks,
        label_key="scenario",
        value_key="cumulative_return",
        title="Retorno acumulado por cenario de choque",
    )
    write_bar_chart_svg(
        output_dir / "shock_equity_weights.svg",
        shocks,
        label_key="scenario",
        value_key="final_weight_renda_variavel",
        title="Peso final em renda variavel por cenario",
    )
    write_hypothesis_evaluation(docs_output_path, baseline, scenarios, shocks, rebalances, profiles)


def write_final_metrics(
    path: Path,
    baseline: dict[str, float | str],
    scenarios: list[dict[str, str]],
    shocks: list[dict[str, str]],
    rebalances: list[dict[str, str]],
    profiles: list[dict[str, str]],
) -> None:
    rows = [
        {"grupo": "baseline", "cenario": "baseline", **select_metrics(baseline)},
        *({"grupo": "imitacao", "cenario": row["scenario"], **select_metrics(row)} for row in scenarios),
        *({"grupo": "choque", "cenario": row["scenario"], **select_metrics(row)} for row in shocks),
        *({"grupo": "rebalanceamento", "cenario": row["scenario"], **select_metrics(row)} for row in rebalances),
        *({"grupo": "perfis", "cenario": row["scenario"], **select_metrics(row)} for row in profiles),
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_hypothesis_evaluation(
    path: Path,
    baseline: dict[str, float | str],
    scenarios: list[dict[str, str]],
    shocks: list[dict[str, str]],
    rebalances: list[dict[str, str]],
    profiles: list[dict[str, str]],
) -> None:
    shock_by_name = {row["scenario"]: row for row in shocks}
    scenario_by_name = {row["scenario"]: row for row in scenarios}

    none = shock_by_name.get("none", baseline)
    rate_hike = shock_by_name.get("rate_hike", none)
    equity_stress = shock_by_name.get("equity_stress", none)
    combined_stress = shock_by_name.get("combined_stress", none)
    imitation_0 = scenario_by_name.get("imitation_0", none)
    imitation_2 = scenario_by_name.get("imitation_2", none)
    rebalance_by_name = {row["scenario"]: row for row in rebalances}
    profile_by_name = {row["scenario"]: row for row in profiles}
    fast_noisy = rebalance_by_name.get("fast_noisy", none)
    slow_clean = rebalance_by_name.get("slow_clean", none)
    heterogeneous = profile_by_name.get("heterogeneous", none)
    homogeneous_agressivo = profile_by_name.get("homogeneous_agressivo", none)

    h1_status = "parcialmente sustentada" if metric(rate_hike, "final_weight_tesouro_selic") > metric(none, "final_weight_tesouro_selic") else "nao sustentada"
    h2_status = "inconclusiva" if metric(imitation_2, "final_hhi_concentration") <= metric(imitation_0, "final_hhi_concentration") else "parcialmente sustentada"
    h3_status = "parcialmente sustentada" if metric(fast_noisy, "cumulative_return") < metric(slow_clean, "cumulative_return") else "nao sustentada"
    h4_status = "parcialmente sustentada" if metric(heterogeneous, "max_drawdown") > metric(homogeneous_agressivo, "max_drawdown") else "inconclusiva"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Avaliacao Inicial das Hipoteses",
                "",
                "Esta avaliacao e automatica e deve ser revisada na interpretacao final.",
                "",
                "## H1",
                f"Status: {h1_status}.",
                f"No choque `rate_hike`, o peso em Tesouro Selic foi de {percent(metric(rate_hike, 'final_weight_tesouro_selic'))}, contra {percent(metric(none, 'final_weight_tesouro_selic'))} no baseline.",
                "",
                "## H2",
                f"Status: {h2_status}.",
                f"Com `imitation=2.0`, o HHI final foi {metric(imitation_2, 'final_hhi_concentration'):.4f}; com `imitation=0.0`, foi {metric(imitation_0, 'final_hhi_concentration'):.4f}.",
                f"No choque `equity_stress`, a renda variavel caiu para {percent(metric(equity_stress, 'final_weight_renda_variavel'))}.",
                "",
                "## H3",
                f"Status: {h3_status}.",
                f"No cenario `fast_noisy`, o retorno acumulado medio foi {percent(metric(fast_noisy, 'cumulative_return'))}; em `slow_clean`, foi {percent(metric(slow_clean, 'cumulative_return'))}.",
                "",
                "## H4",
                f"Status: {h4_status}.",
                f"O max drawdown heterogeneo foi {percent(metric(heterogeneous, 'max_drawdown'))}; no perfil homogeneo agressivo, foi {percent(metric(homogeneous_agressivo, 'max_drawdown'))}.",
                "",
                "## Observacao",
                f"No cenario `combined_stress`, o retorno acumulado medio foi {percent(metric(combined_stress, 'cumulative_return'))}.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_bar_chart_svg(
    path: Path,
    rows: list[dict[str, str]],
    label_key: str,
    value_key: str,
    title: str,
) -> None:
    width = 920
    height = 420
    margin = 56
    chart_height = 260
    values = [metric(row, value_key) for row in rows]
    max_value = max(values) if values else 1
    min_value = min(0.0, min(values) if values else 0.0)
    span = max_value - min_value if max_value != min_value else 1
    bar_width = (width - (2 * margin)) / max(len(rows), 1)

    bars = []
    for index, row in enumerate(rows):
        value = metric(row, value_key)
        bar_height = ((value - min_value) / span) * chart_height
        x = margin + index * bar_width + 10
        y = margin + (chart_height - bar_height)
        bars.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width - 20:.1f}" height="{bar_height:.1f}" fill="#2f6f73" />'
        )
        bars.append(
            f'<text x="{x + (bar_width - 20) / 2:.1f}" y="{height - 64}" text-anchor="middle" font-size="12">{row[label_key]}</text>'
        )
        bars.append(
            f'<text x="{x + (bar_width - 20) / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" font-size="12">{percent(value)}</text>'
        )

    path.write_text(
        "\n".join(
            [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                '<rect width="100%" height="100%" fill="#f7f4ed" />',
                f'<text x="{margin}" y="34" font-size="20" font-family="Arial" fill="#17201f">{title}</text>',
                f'<line x1="{margin}" y1="{margin + chart_height}" x2="{width - margin}" y2="{margin + chart_height}" stroke="#17201f" stroke-width="1" />',
                *bars,
                "</svg>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def read_json(path: Path) -> dict[str, float | str]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def select_metrics(row: dict[str, float | str]) -> dict[str, float]:
    return {
        "retorno_acumulado": metric(row, "cumulative_return"),
        "max_drawdown": metric(row, "max_drawdown"),
        "hhi_final": metric(row, "final_hhi_concentration"),
        "peso_selic": metric(row, "final_weight_tesouro_selic"),
        "peso_renda_variavel": metric(row, "final_weight_renda_variavel"),
    }


def metric(row: dict[str, float | str], key: str) -> float:
    return float(row[key])


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"
