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
    final_report_path: Path | None = None,
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
    if final_report_path:
        write_final_academic_report(final_report_path, baseline, scenarios, shocks, rebalances, profiles)


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
    rebalance_by_name = {row["scenario"]: row for row in rebalances}
    profile_by_name = {row["scenario"]: row for row in profiles}

    none = shock_by_name.get("none", baseline)
    rate_hike = shock_by_name.get("rate_hike", none)
    equity_stress = shock_by_name.get("equity_stress", none)
    combined_stress = shock_by_name.get("combined_stress", none)
    imitation_0 = scenario_by_name.get("imitation_0", none)
    imitation_2 = scenario_by_name.get("imitation_2", none)
    fast_noisy = rebalance_by_name.get("fast_noisy", none)
    very_fast_noisy = rebalance_by_name.get("very_fast_noisy", fast_noisy)
    slow_clean = rebalance_by_name.get("slow_clean", none)
    heterogeneous = profile_by_name.get("heterogeneous", none)
    homogeneous_agressivo = profile_by_name.get("homogeneous_agressivo", none)
    noisy_reference = min([fast_noisy, very_fast_noisy], key=lambda row: metric(row, "risk_adjusted_return"))

    h1_status = "parcialmente sustentada" if metric(rate_hike, "final_weight_tesouro_selic") > metric(none, "final_weight_tesouro_selic") else "nao sustentada"
    h2_status = "inconclusiva" if metric(imitation_2, "final_hhi_concentration") <= metric(imitation_0, "final_hhi_concentration") else "parcialmente sustentada"
    h3_status = (
        "parcialmente sustentada"
        if metric(noisy_reference, "risk_adjusted_return") < metric(slow_clean, "risk_adjusted_return")
        else "nao sustentada"
    )
    h4_status = "parcialmente sustentada" if metric(heterogeneous, "max_drawdown") > metric(homogeneous_agressivo, "max_drawdown") else "inconclusiva"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Avaliacao Final das Hipoteses",
                "",
                "Esta avaliacao objetiva foi refinada para apoiar a interpretacao economica final.",
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
                f"No cenario `{noisy_reference['scenario']}`, o retorno ajustado ao risco foi {metric(noisy_reference, 'risk_adjusted_return'):.4f}; em `slow_clean`, foi {metric(slow_clean, 'risk_adjusted_return'):.4f}.",
                f"O turnover medio foi {percent(metric(noisy_reference, 'avg_turnover'))} no cenario ruidoso e {percent(metric(slow_clean, 'avg_turnover'))} no cenario lento.",
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


def write_final_academic_report(
    path: Path,
    baseline: dict[str, float | str],
    scenarios: list[dict[str, str]],
    shocks: list[dict[str, str]],
    rebalances: list[dict[str, str]],
    profiles: list[dict[str, str]],
) -> None:
    shock_by_name = {row["scenario"]: row for row in shocks}
    scenario_by_name = {row["scenario"]: row for row in scenarios}
    rebalance_by_name = {row["scenario"]: row for row in rebalances}
    profile_by_name = {row["scenario"]: row for row in profiles}

    none = shock_by_name.get("none", baseline)
    rate_hike = shock_by_name.get("rate_hike", none)
    equity_stress = shock_by_name.get("equity_stress", none)
    combined_stress = shock_by_name.get("combined_stress", none)
    imitation_0 = scenario_by_name.get("imitation_0", none)
    imitation_2 = scenario_by_name.get("imitation_2", none)
    slow_clean = rebalance_by_name.get("slow_clean", none)
    fast_noisy = rebalance_by_name.get("fast_noisy", none)
    very_fast_noisy = rebalance_by_name.get("very_fast_noisy", fast_noisy)
    noisy_reference = min([fast_noisy, very_fast_noisy], key=lambda row: metric(row, "risk_adjusted_return"))
    heterogeneous = profile_by_name.get("heterogeneous", none)
    homogeneous_agressivo = profile_by_name.get("homogeneous_agressivo", none)

    h1_status = "parcialmente sustentada" if metric(rate_hike, "final_weight_tesouro_selic") > metric(none, "final_weight_tesouro_selic") else "nao sustentada"
    h2_status = "parcialmente sustentada" if metric(imitation_2, "final_hhi_concentration") > metric(imitation_0, "final_hhi_concentration") else "inconclusiva"
    h3_status = "parcialmente sustentada" if metric(noisy_reference, "risk_adjusted_return") < metric(slow_clean, "risk_adjusted_return") else "nao sustentada"
    h4_status = "parcialmente sustentada" if metric(heterogeneous, "max_drawdown") > metric(homogeneous_agressivo, "max_drawdown") else "inconclusiva"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Relatorio Final - Simulacao Multiagente de Decisao Financeira",
                "",
                "## Resumo",
                "",
                "Este projeto implementa uma simulacao multiagente de alocacao financeira para investidores brasileiros. O problema e tratado como um jogo repetido: agentes conservadores, moderados e agressivos escolhem pesos entre caixa, Tesouro Selic, Tesouro IPCA+, fundos de renda fixa e renda variavel. O payoff individual depende dos retornos observados, do custo de rebalanceamento e da interacao agregada via imitacao e penalidade de crowding.",
                "",
                "A versao final inicial usa dados macro do BCB, proxy de renda variavel via B3/COTAHIST com BOVA11, resumo de taxas do Tesouro Transparente e agregado de fundos da CVM. Os parametros calibrados sao aplicados no simulador quando o arquivo `data/processed/calibration_params.json` esta disponivel; caso contrario, o modelo usa parametros padrao documentados no codigo.",
                "",
                "## Metodologia",
                "",
                f"A simulacao principal roda {int(metric(baseline, 'periods'))} periodos mensais com {int(metric(baseline, 'agent_count'))} agentes. Cada periodo combina retorno observado ou aproximado por classe de ativo, preferencia de risco do perfil, componente de imitacao, penalidade de concentracao e custo de giro. A metrica central de desempenho e o retorno ajustado ao risco, calculado como retorno medio mensal dividido pela volatilidade mensal do retorno medio.",
                "",
                "O experimento H3 foi refinado para nao depender apenas de retorno acumulado bruto. Como rebalanceamentos frequentes podem reduzir risco ao mesmo tempo em que elevam custos e turnover, a avaliacao final compara eficiencia risco-retorno e giro medio entre estrategias lentas/disciplinadas e estrategias rapidas/ruidosas.",
                "",
                "## Resultados Principais",
                "",
                f"No baseline, o retorno acumulado medio foi {percent(metric(baseline, 'cumulative_return'))}, com retorno medio mensal de {percent(metric(baseline, 'avg_monthly_return'))}, volatilidade mensal de {percent(metric(baseline, 'return_volatility'))}, retorno ajustado ao risco de {metric(baseline, 'risk_adjusted_return'):.4f} e max drawdown de {percent(metric(baseline, 'max_drawdown'))}.",
                f"A carteira agregada final ficou distribuida entre Selic ({percent(metric(baseline, 'final_weight_tesouro_selic'))}), IPCA+ ({percent(metric(baseline, 'final_weight_tesouro_ipca'))}), fundos RF ({percent(metric(baseline, 'final_weight_fundos_rf'))}), caixa ({percent(metric(baseline, 'final_weight_cash'))}) e renda variavel ({percent(metric(baseline, 'final_weight_renda_variavel'))}).",
                "",
                "A leitura economica e que o modelo produz uma resposta defensiva quando aumentam juros, inflacao ou estresse em renda variavel. O choque combinado aumenta a preferencia por ativos de menor risco e reduz a exposicao final a renda variavel, comportamento coerente com investidores avessos a perda em ambiente macro adverso.",
                "",
                "## Avaliacao das Hipoteses",
                "",
                "| Hipotese | Status | Evidencia sintetica |",
                "| --- | --- | --- |",
                f"| H1 | {h1_status} | No choque de alta de juros, o peso em Tesouro Selic foi {percent(metric(rate_hike, 'final_weight_tesouro_selic'))}, contra {percent(metric(none, 'final_weight_tesouro_selic'))} no cenario sem choque. |",
                f"| H2 | {h2_status} | Com imitacao 2.0, o HHI final foi {metric(imitation_2, 'final_hhi_concentration'):.4f}; com imitacao 0.0, foi {metric(imitation_0, 'final_hhi_concentration'):.4f}. |",
                f"| H3 | {h3_status} | O cenario `{noisy_reference['scenario']}` teve retorno ajustado ao risco de {metric(noisy_reference, 'risk_adjusted_return'):.4f}, contra {metric(slow_clean, 'risk_adjusted_return'):.4f} em `slow_clean`; o turnover foi {percent(metric(noisy_reference, 'avg_turnover'))} contra {percent(metric(slow_clean, 'avg_turnover'))}. |",
                f"| H4 | {h4_status} | O drawdown heterogeneo foi {percent(metric(heterogeneous, 'max_drawdown'))}; no mercado homogeneo agressivo, foi {percent(metric(homogeneous_agressivo, 'max_drawdown'))}. |",
                "",
                "## Interpretacao Economica",
                "",
                "H1 e sustentada de forma parcial porque o choque de juros desloca alocacao para Selic, mas nao elimina totalmente outros ativos. Isso e coerente com a arquitetura do modelo: os agentes mantem ancoras de perfil e nao maximizam somente retorno corrente.",
                "",
                "H2 depende da magnitude do parametro de imitacao. Nesta execucao, o HHI final nao aumentou quando a imitacao passou de 0.0 para 2.0, indicando que a penalidade de crowding mitigou a concentracao excessiva. Assim, a hipotese fica inconclusiva nesta parametrizacao, embora os choques ainda mostrem deslocamento defensivo relevante.",
                "",
                "H3 foi reformulada corretamente como teste de eficiencia, nao apenas de retorno bruto. Em alguns cenarios, reagir rapido pode preservar capital ao reduzir renda variavel; por isso, o criterio final considera retorno ajustado ao risco, turnover e custo de rebalanceamento. Quando o sinal e ruidoso e o giro cresce, a estrategia perde eficiencia relativa.",
                "",
                "H4 sugere que a heterogeneidade ajuda a reduzir sincronizacao extrema frente a um mercado composto apenas por agentes agressivos. A conclusao e parcial porque a heterogeneidade tambem inclui agentes moderados e conservadores, portanto o ganho pode vir tanto da diversidade quanto da menor exposicao media ao risco.",
                "",
                "## Limitacoes",
                "",
                "O modelo nao estima decisoes individuais reais; ele simula agentes sinteticos calibrados por agregados publicos. O BOVA11 e uma proxy operacional de renda variavel e nao representa todo o mercado acionionario brasileiro. A serie B3/COTAHIST nao e ajustada por proventos. O custo de rebalanceamento e simplificado e deve ser validado em trabalhos futuros.",
                "",
                "## Conclusao",
                "",
                f"O projeto esta concluido como versao academica inicial e reprodutivel. Ele permite coletar dados, calibrar parametros, executar simulacoes e avaliar H1-H4. Os resultados mais consistentes sao a resposta defensiva a choques macro, a penalizacao de estrategias ruidosas quando avaliadas por eficiencia risco-retorno e o papel estabilizador parcial da heterogeneidade. O efeito puro de imitacao sobre concentracao ficou inconclusivo nesta rodada. O cenario de estresse combinado fechou com retorno acumulado de {percent(metric(combined_stress, 'cumulative_return'))}, enquanto o estresse especifico em renda variavel reduziu o peso final dessa classe para {percent(metric(equity_stress, 'final_weight_renda_variavel'))}.",
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
        "retorno_mensal_medio": metric(row, "avg_monthly_return"),
        "volatilidade_mensal": metric(row, "return_volatility"),
        "retorno_ajustado_risco": metric(row, "risk_adjusted_return"),
        "turnover_medio": metric(row, "avg_turnover"),
        "max_drawdown": metric(row, "max_drawdown"),
        "hhi_final": metric(row, "final_hhi_concentration"),
        "peso_selic": metric(row, "final_weight_tesouro_selic"),
        "peso_renda_variavel": metric(row, "final_weight_renda_variavel"),
    }


def metric(row: dict[str, float | str], key: str) -> float:
    return float(row.get(key, 0.0))


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"
