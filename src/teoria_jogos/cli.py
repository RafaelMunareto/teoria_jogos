from __future__ import annotations

import argparse
from pathlib import Path

from teoria_jogos.analysis.reports import generate_analysis_outputs
from teoria_jogos.data.b3 import build_b3_equity_dataset, build_b3_equity_dataset_range, enrich_macro_with_equity
from teoria_jogos.data.bcb import download_bcb_macro_dataset, read_macro_csv
from teoria_jogos.data.cvm import build_cvm_summary
from teoria_jogos.data.tesouro import build_tesouro_summary
from teoria_jogos.models.calibration import calibrate_parameters, load_simulation_calibration
from teoria_jogos.simulation.baseline import (
    DEFAULT_CROWDING_PENALTY,
    run_baseline_simulation,
    run_profile_comparison,
    run_rebalance_comparison,
    run_scenario_comparison,
    run_shock_comparison,
    write_comparison_csv,
    write_history_csv,
    write_summary_json,
)


DEFAULT_RAW_DIR = Path("data/raw/bcb")
DEFAULT_MACRO_PATH = Path("data/processed/macro_bcb.csv")
DEFAULT_HISTORY_PATH = Path("outputs/baseline_history.csv")
DEFAULT_SUMMARY_PATH = Path("outputs/baseline_summary.json")
DEFAULT_COMPARISON_PATH = Path("outputs/scenario_comparison.csv")
DEFAULT_SHOCK_COMPARISON_PATH = Path("outputs/shock_comparison.csv")
DEFAULT_REBALANCE_COMPARISON_PATH = Path("outputs/rebalance_comparison.csv")
DEFAULT_PROFILE_COMPARISON_PATH = Path("outputs/profile_comparison.csv")
DEFAULT_B3_RAW_DIR = Path("data/raw/b3")
DEFAULT_B3_DAILY_PATH = Path("data/processed/equity_b3_daily.csv")
DEFAULT_B3_MONTHLY_PATH = Path("data/processed/equity_b3_monthly.csv")
DEFAULT_TESOURO_RAW_PATH = Path("data/raw/tesouro/precotaxatesourodireto.csv")
DEFAULT_TESOURO_SUMMARY_PATH = Path("data/processed/tesouro_rates_summary.csv")
DEFAULT_CVM_RAW_DIR = Path("data/raw/cvm")
DEFAULT_CVM_SUMMARY_PATH = Path("data/processed/cvm_funds_summary.csv")
DEFAULT_CALIBRATION_PATH = Path("data/processed/calibration_params.json")
DEFAULT_REPORT_DIR = Path("outputs/report")
DEFAULT_HYPOTHESIS_PATH = Path("docs/avaliacao_hipoteses.md")
DEFAULT_FINAL_REPORT_PATH = Path("docs/relatorio_final.md")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="teoria-jogos",
        description="Pipeline inicial de decisao financeira multiagente.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch-bcb", help="Baixa series macro do BCB/SGS.")
    fetch_parser.add_argument("--start", default="01/01/2020", help="Data inicial em DD/MM/AAAA.")
    fetch_parser.add_argument("--end", default="31/12/2025", help="Data final em DD/MM/AAAA.")
    fetch_parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    fetch_parser.add_argument("--output", type=Path, default=DEFAULT_MACRO_PATH)
    fetch_parser.add_argument("--no-ibovespa", action="store_true", help="Nao tenta baixar a serie SGS 7.")

    b3_parser = subparsers.add_parser("fetch-b3-equity", help="Baixa B3 COTAHIST e extrai um ativo como proxy de renda variavel.")
    b3_parser.add_argument("--year", type=int, default=None, help="Ano unico. Se informado, sobrepoe start/end year.")
    b3_parser.add_argument("--start-year", type=int, default=2020)
    b3_parser.add_argument("--end-year", type=int, default=2025)
    b3_parser.add_argument("--symbol", default="BOVA11")
    b3_parser.add_argument("--raw-dir", type=Path, default=DEFAULT_B3_RAW_DIR)
    b3_parser.add_argument("--daily-output", type=Path, default=DEFAULT_B3_DAILY_PATH)
    b3_parser.add_argument("--monthly-output", type=Path, default=DEFAULT_B3_MONTHLY_PATH)
    b3_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    b3_parser.add_argument("--enriched-macro-output", type=Path, default=DEFAULT_MACRO_PATH)
    b3_parser.add_argument("--no-enrich-macro", action="store_true")

    tesouro_parser = subparsers.add_parser("fetch-tesouro", help="Baixa e resume taxas do Tesouro Direto.")
    tesouro_parser.add_argument("--raw-output", type=Path, default=DEFAULT_TESOURO_RAW_PATH)
    tesouro_parser.add_argument("--summary-output", type=Path, default=DEFAULT_TESOURO_SUMMARY_PATH)

    cvm_parser = subparsers.add_parser("fetch-cvm-funds", help="Baixa e resume informe diario de fundos da CVM.")
    cvm_parser.add_argument("--year-month", default="202512")
    cvm_parser.add_argument("--raw-dir", type=Path, default=DEFAULT_CVM_RAW_DIR)
    cvm_parser.add_argument("--summary-output", type=Path, default=DEFAULT_CVM_SUMMARY_PATH)

    simulate_parser = subparsers.add_parser("simulate", help="Roda a simulacao baseline.")
    simulate_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    simulate_parser.add_argument("--agents", type=int, default=300)
    simulate_parser.add_argument("--imitation", type=float, default=1.0)
    simulate_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    simulate_parser.add_argument("--seed", type=int, default=42)
    simulate_parser.add_argument("--shock-scenario", default="none")
    simulate_parser.add_argument("--rebalance-multiplier", type=float, default=1.0)
    simulate_parser.add_argument("--signal-noise", type=float, default=0.0)
    simulate_parser.add_argument("--profile-mode", default="heterogeneous")
    simulate_parser.add_argument("--history-output", type=Path, default=DEFAULT_HISTORY_PATH)
    simulate_parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_PATH)
    add_calibration_arguments(simulate_parser)

    compare_parser = subparsers.add_parser("compare-scenarios", help="Compara niveis de imitacao.")
    compare_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    compare_parser.add_argument("--agents", type=int, default=300)
    compare_parser.add_argument("--imitation-levels", default="0.0,1.0,2.0")
    compare_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    compare_parser.add_argument("--seed", type=int, default=42)
    compare_parser.add_argument("--shock-scenario", default="none")
    compare_parser.add_argument("--output", type=Path, default=DEFAULT_COMPARISON_PATH)
    add_calibration_arguments(compare_parser)

    shock_parser = subparsers.add_parser("compare-shocks", help="Compara cenarios de choque macro.")
    shock_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    shock_parser.add_argument("--agents", type=int, default=300)
    shock_parser.add_argument("--imitation", type=float, default=1.0)
    shock_parser.add_argument("--shock-scenarios", default="none,rate_hike,inflation_spike,equity_stress,combined_stress")
    shock_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    shock_parser.add_argument("--seed", type=int, default=42)
    shock_parser.add_argument("--output", type=Path, default=DEFAULT_SHOCK_COMPARISON_PATH)
    add_calibration_arguments(shock_parser)

    rebalance_parser = subparsers.add_parser("compare-rebalance", help="Compara frequencia de rebalanceamento e ruido de sinal.")
    rebalance_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    rebalance_parser.add_argument("--agents", type=int, default=300)
    rebalance_parser.add_argument("--imitation", type=float, default=1.0)
    rebalance_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    rebalance_parser.add_argument("--seed", type=int, default=42)
    rebalance_parser.add_argument("--output", type=Path, default=DEFAULT_REBALANCE_COMPARISON_PATH)
    add_calibration_arguments(rebalance_parser)

    profile_parser = subparsers.add_parser("compare-profiles", help="Compara agentes heterogeneos e homogeneos.")
    profile_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    profile_parser.add_argument("--agents", type=int, default=300)
    profile_parser.add_argument("--imitation", type=float, default=1.0)
    profile_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    profile_parser.add_argument("--seed", type=int, default=42)
    profile_parser.add_argument("--output", type=Path, default=DEFAULT_PROFILE_COMPARISON_PATH)
    add_calibration_arguments(profile_parser)

    report_parser = subparsers.add_parser("generate-report", help="Gera tabelas, graficos SVG e relatorios das hipoteses.")
    report_parser.add_argument("--baseline-summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    report_parser.add_argument("--scenario-comparison", type=Path, default=DEFAULT_COMPARISON_PATH)
    report_parser.add_argument("--shock-comparison", type=Path, default=DEFAULT_SHOCK_COMPARISON_PATH)
    report_parser.add_argument("--rebalance-comparison", type=Path, default=DEFAULT_REBALANCE_COMPARISON_PATH)
    report_parser.add_argument("--profile-comparison", type=Path, default=DEFAULT_PROFILE_COMPARISON_PATH)
    report_parser.add_argument("--output-dir", type=Path, default=DEFAULT_REPORT_DIR)
    report_parser.add_argument("--hypothesis-output", type=Path, default=DEFAULT_HYPOTHESIS_PATH)
    report_parser.add_argument("--final-report-output", type=Path, default=DEFAULT_FINAL_REPORT_PATH)

    calibration_parser = subparsers.add_parser("calibrate-parameters", help="Gera calibracao inicial a partir das bases observadas.")
    calibration_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    calibration_parser.add_argument("--equity-monthly", type=Path, default=DEFAULT_B3_MONTHLY_PATH)
    calibration_parser.add_argument("--tesouro-summary", type=Path, default=DEFAULT_TESOURO_SUMMARY_PATH)
    calibration_parser.add_argument("--cvm-summary", type=Path, default=DEFAULT_CVM_SUMMARY_PATH)
    calibration_parser.add_argument("--output", type=Path, default=DEFAULT_CALIBRATION_PATH)

    run_parser = subparsers.add_parser("run-baseline", help="Baixa dados do BCB e roda o baseline.")
    run_parser.add_argument("--start", default="01/01/2020", help="Data inicial em DD/MM/AAAA.")
    run_parser.add_argument("--end", default="31/12/2025", help="Data final em DD/MM/AAAA.")
    run_parser.add_argument("--agents", type=int, default=300)
    run_parser.add_argument("--imitation", type=float, default=1.0)
    run_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--shock-scenario", default="none")
    run_parser.add_argument("--no-ibovespa", action="store_true", help="Nao tenta baixar a serie SGS 7.")
    add_calibration_arguments(run_parser)

    args = parser.parse_args()

    if args.command == "fetch-bcb":
        records = download_bcb_macro_dataset(
            args.start,
            args.end,
            args.raw_dir,
            args.output,
            include_ibovespa=not args.no_ibovespa,
        )
        print(f"Macro BCB salvo em {args.output} ({len(records)} meses).")
        return

    if args.command == "fetch-b3-equity":
        if args.year is not None:
            records = build_b3_equity_dataset(
                year=args.year,
                symbol=args.symbol,
                raw_dir=args.raw_dir,
                daily_output=args.daily_output,
                monthly_output=args.monthly_output,
            )
        else:
            records = build_b3_equity_dataset_range(
                start_year=args.start_year,
                end_year=args.end_year,
                symbol=args.symbol,
                raw_dir=args.raw_dir,
                daily_output=args.daily_output,
                monthly_output=args.monthly_output,
            )
        print(f"Serie B3 mensal salva em {args.monthly_output} ({len(records)} meses).")
        if not args.no_enrich_macro:
            enriched = enrich_macro_with_equity(args.macro, args.monthly_output, args.enriched_macro_output)
            print(f"Macro enriquecido salvo em {args.enriched_macro_output} ({len(enriched)} meses).")
        return

    if args.command == "fetch-tesouro":
        records = build_tesouro_summary(args.raw_output, args.summary_output)
        print(f"Resumo Tesouro salvo em {args.summary_output} ({len(records)} tipos de titulo).")
        return

    if args.command == "fetch-cvm-funds":
        summary = build_cvm_summary(args.year_month, args.raw_dir, args.summary_output)
        print(f"Resumo CVM salvo em {args.summary_output} ({summary['fundos']} fundos).")
        return

    if args.command == "simulate":
        records = read_macro_csv(args.macro)
        calibration_kwargs = load_calibration_kwargs(args)
        history, summary = run_baseline_simulation(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
            rebalance_multiplier=args.rebalance_multiplier,
            signal_noise=args.signal_noise,
            profile_mode=args.profile_mode,
            **calibration_kwargs,
        )
        write_history_csv(args.history_output, history)
        write_summary_json(args.summary_output, summary)
        print(f"Historico salvo em {args.history_output}.")
        print(f"Resumo salvo em {args.summary_output}.")
        return

    if args.command == "compare-scenarios":
        records = read_macro_csv(args.macro)
        imitation_levels = parse_float_list(args.imitation_levels)
        calibration_kwargs = load_calibration_kwargs(args)
        comparison = run_scenario_comparison(
            records,
            imitation_levels=imitation_levels,
            agent_count=args.agents,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
            **calibration_kwargs,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de cenarios salva em {args.output}.")
        return

    if args.command == "compare-shocks":
        records = read_macro_csv(args.macro)
        shock_scenarios = parse_string_list(args.shock_scenarios)
        calibration_kwargs = load_calibration_kwargs(args)
        comparison = run_shock_comparison(
            records,
            shock_scenarios=shock_scenarios,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            **calibration_kwargs,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de choques salva em {args.output}.")
        return

    if args.command == "compare-rebalance":
        records = read_macro_csv(args.macro)
        calibration_kwargs = load_calibration_kwargs(args)
        comparison = run_rebalance_comparison(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            **calibration_kwargs,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de rebalanceamento salva em {args.output}.")
        return

    if args.command == "compare-profiles":
        records = read_macro_csv(args.macro)
        calibration_kwargs = load_calibration_kwargs(args)
        comparison = run_profile_comparison(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            **calibration_kwargs,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de perfis salva em {args.output}.")
        return

    if args.command == "generate-report":
        generate_analysis_outputs(
            baseline_summary_path=args.baseline_summary,
            scenario_comparison_path=args.scenario_comparison,
            shock_comparison_path=args.shock_comparison,
            rebalance_comparison_path=args.rebalance_comparison,
            profile_comparison_path=args.profile_comparison,
            output_dir=args.output_dir,
            docs_output_path=args.hypothesis_output,
            final_report_path=args.final_report_output,
        )
        print(f"Relatorio gerado em {args.output_dir}.")
        print(f"Avaliacao das hipoteses salva em {args.hypothesis_output}.")
        print(f"Relatorio final salvo em {args.final_report_output}.")
        return

    if args.command == "calibrate-parameters":
        calibration = calibrate_parameters(
            macro_path=args.macro,
            equity_monthly_path=args.equity_monthly,
            tesouro_summary_path=args.tesouro_summary,
            cvm_summary_path=args.cvm_summary,
            output_path=args.output,
        )
        print(f"Calibracao salva em {args.output}.")
        print(f"Vol mensal renda variavel: {calibration['metricas_observadas']['vol_mensal_renda_variavel']:.4f}.")
        return

    if args.command == "run-baseline":
        records = download_bcb_macro_dataset(
            args.start,
            args.end,
            DEFAULT_RAW_DIR,
            DEFAULT_MACRO_PATH,
            include_ibovespa=not args.no_ibovespa,
        )
        calibration_kwargs = load_calibration_kwargs(args)
        history, summary = run_baseline_simulation(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
            **calibration_kwargs,
        )
        write_history_csv(DEFAULT_HISTORY_PATH, history)
        write_summary_json(DEFAULT_SUMMARY_PATH, summary)
        print(f"Macro BCB salvo em {DEFAULT_MACRO_PATH} ({len(records)} meses).")
        print(f"Historico salvo em {DEFAULT_HISTORY_PATH}.")
        print(f"Resumo salvo em {DEFAULT_SUMMARY_PATH}.")


def parse_float_list(value: str) -> list[float]:
    values = []
    for item in value.split(","):
        stripped = item.strip()
        if stripped:
            values.append(float(stripped))
    if not values:
        raise ValueError("A lista de valores nao pode ser vazia.")
    return values


def parse_string_list(value: str) -> list[str]:
    values = [item.strip() for item in value.split(",") if item.strip()]
    if not values:
        raise ValueError("A lista de valores nao pode ser vazia.")
    return values


def add_calibration_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--calibration",
        type=Path,
        default=DEFAULT_CALIBRATION_PATH,
        help="JSON de calibracao. Aplicado automaticamente quando existir.",
    )
    parser.add_argument("--no-calibration", action="store_true", help="Forca uso dos parametros padrao do simulador.")


def load_calibration_kwargs(args: argparse.Namespace) -> dict[str, object]:
    if args.no_calibration or not args.calibration.exists():
        return {
            "asset_risk": None,
            "crowding_penalty": DEFAULT_CROWDING_PENALTY,
            "calibration_source": "default",
        }

    calibration = load_simulation_calibration(args.calibration)
    return {
        "asset_risk": calibration["asset_risk"],
        "crowding_penalty": calibration["crowding_penalty"],
        "calibration_source": calibration["source"],
    }


if __name__ == "__main__":
    main()
