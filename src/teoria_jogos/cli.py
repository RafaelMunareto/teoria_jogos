from __future__ import annotations

import argparse
from pathlib import Path

from teoria_jogos.data.bcb import download_bcb_macro_dataset, read_macro_csv
from teoria_jogos.simulation.baseline import (
    run_baseline_simulation,
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

    simulate_parser = subparsers.add_parser("simulate", help="Roda a simulacao baseline.")
    simulate_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    simulate_parser.add_argument("--agents", type=int, default=300)
    simulate_parser.add_argument("--imitation", type=float, default=1.0)
    simulate_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    simulate_parser.add_argument("--seed", type=int, default=42)
    simulate_parser.add_argument("--shock-scenario", default="none")
    simulate_parser.add_argument("--history-output", type=Path, default=DEFAULT_HISTORY_PATH)
    simulate_parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_PATH)

    compare_parser = subparsers.add_parser("compare-scenarios", help="Compara niveis de imitacao.")
    compare_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    compare_parser.add_argument("--agents", type=int, default=300)
    compare_parser.add_argument("--imitation-levels", default="0.0,1.0,2.0")
    compare_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    compare_parser.add_argument("--seed", type=int, default=42)
    compare_parser.add_argument("--shock-scenario", default="none")
    compare_parser.add_argument("--output", type=Path, default=DEFAULT_COMPARISON_PATH)

    shock_parser = subparsers.add_parser("compare-shocks", help="Compara cenarios de choque macro.")
    shock_parser.add_argument("--macro", type=Path, default=DEFAULT_MACRO_PATH)
    shock_parser.add_argument("--agents", type=int, default=300)
    shock_parser.add_argument("--imitation", type=float, default=1.0)
    shock_parser.add_argument("--shock-scenarios", default="none,rate_hike,inflation_spike,equity_stress,combined_stress")
    shock_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    shock_parser.add_argument("--seed", type=int, default=42)
    shock_parser.add_argument("--output", type=Path, default=DEFAULT_SHOCK_COMPARISON_PATH)

    run_parser = subparsers.add_parser("run-baseline", help="Baixa dados do BCB e roda o baseline.")
    run_parser.add_argument("--start", default="01/01/2020", help="Data inicial em DD/MM/AAAA.")
    run_parser.add_argument("--end", default="31/12/2025", help="Data final em DD/MM/AAAA.")
    run_parser.add_argument("--agents", type=int, default=300)
    run_parser.add_argument("--imitation", type=float, default=1.0)
    run_parser.add_argument("--rebalance-cost", type=float, default=0.001)
    run_parser.add_argument("--seed", type=int, default=42)
    run_parser.add_argument("--shock-scenario", default="none")
    run_parser.add_argument("--no-ibovespa", action="store_true", help="Nao tenta baixar a serie SGS 7.")

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

    if args.command == "simulate":
        records = read_macro_csv(args.macro)
        history, summary = run_baseline_simulation(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
        )
        write_history_csv(args.history_output, history)
        write_summary_json(args.summary_output, summary)
        print(f"Historico salvo em {args.history_output}.")
        print(f"Resumo salvo em {args.summary_output}.")
        return

    if args.command == "compare-scenarios":
        records = read_macro_csv(args.macro)
        imitation_levels = parse_float_list(args.imitation_levels)
        comparison = run_scenario_comparison(
            records,
            imitation_levels=imitation_levels,
            agent_count=args.agents,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de cenarios salva em {args.output}.")
        return

    if args.command == "compare-shocks":
        records = read_macro_csv(args.macro)
        shock_scenarios = parse_string_list(args.shock_scenarios)
        comparison = run_shock_comparison(
            records,
            shock_scenarios=shock_scenarios,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
        )
        write_comparison_csv(args.output, comparison)
        print(f"Comparacao de choques salva em {args.output}.")
        return

    if args.command == "run-baseline":
        records = download_bcb_macro_dataset(
            args.start,
            args.end,
            DEFAULT_RAW_DIR,
            DEFAULT_MACRO_PATH,
            include_ibovespa=not args.no_ibovespa,
        )
        history, summary = run_baseline_simulation(
            records,
            agent_count=args.agents,
            imitation_multiplier=args.imitation,
            rebalance_cost=args.rebalance_cost,
            seed=args.seed,
            shock_scenario=args.shock_scenario,
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


if __name__ == "__main__":
    main()
