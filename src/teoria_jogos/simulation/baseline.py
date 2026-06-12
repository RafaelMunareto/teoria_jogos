from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ASSETS = ("cash", "tesouro_selic", "tesouro_ipca", "fundos_rf", "renda_variavel")

ASSET_RISK = {
    "cash": 0.01,
    "tesouro_selic": 0.03,
    "tesouro_ipca": 0.08,
    "fundos_rf": 0.05,
    "renda_variavel": 0.22,
}


@dataclass(frozen=True)
class AgentProfile:
    name: str
    risk_aversion: float
    rebalance_speed: float
    imitation_bias: float
    base_weights: dict[str, float]


@dataclass
class InvestorAgent:
    profile: AgentProfile
    weights: dict[str, float]
    wealth: float = 1.0


DEFAULT_PROFILES = (
    AgentProfile(
        name="conservador",
        risk_aversion=8.0,
        rebalance_speed=0.22,
        imitation_bias=0.20,
        base_weights={
            "cash": 0.10,
            "tesouro_selic": 0.45,
            "tesouro_ipca": 0.25,
            "fundos_rf": 0.15,
            "renda_variavel": 0.05,
        },
    ),
    AgentProfile(
        name="moderado",
        risk_aversion=4.5,
        rebalance_speed=0.32,
        imitation_bias=0.35,
        base_weights={
            "cash": 0.05,
            "tesouro_selic": 0.30,
            "tesouro_ipca": 0.25,
            "fundos_rf": 0.20,
            "renda_variavel": 0.20,
        },
    ),
    AgentProfile(
        name="agressivo",
        risk_aversion=2.2,
        rebalance_speed=0.45,
        imitation_bias=0.55,
        base_weights={
            "cash": 0.03,
            "tesouro_selic": 0.15,
            "tesouro_ipca": 0.17,
            "fundos_rf": 0.20,
            "renda_variavel": 0.45,
        },
    ),
)


def run_baseline_simulation(
    macro_records: list[dict[str, float | str]],
    agent_count: int = 300,
    imitation_multiplier: float = 1.0,
    rebalance_cost: float = 0.001,
    seed: int = 42,
    shock_scenario: str = "none",
    rebalance_multiplier: float = 1.0,
    signal_noise: float = 0.0,
    profile_mode: str = "heterogeneous",
) -> tuple[list[dict[str, float | str]], dict[str, float | str]]:
    if not macro_records:
        raise ValueError("macro_records nao pode ser vazio")
    if agent_count <= 0:
        raise ValueError("agent_count deve ser maior que zero")

    rng = random.Random(seed)
    macro_records = apply_shock_scenario(macro_records, shock_scenario)
    asset_returns = build_asset_returns(macro_records, rng)
    agents = create_agents(agent_count, rng, profile_mode=profile_mode)
    market_weights = average_weights(agent.weights for agent in agents)

    history: list[dict[str, float | str]] = []
    peak_wealth = sum(agent.wealth for agent in agents)
    max_drawdown = 0.0

    for period_index, monthly_returns in enumerate(asset_returns):
        month = str(monthly_returns["month"])
        returns_by_asset = {asset: float(monthly_returns[asset]) for asset in ASSETS}
        period_turnovers: list[float] = []
        period_returns: list[float] = []

        for agent in agents:
            previous_weights = dict(agent.weights)
            gross_return = weighted_return(previous_weights, returns_by_asset)

            target_weights = choose_target_weights(
                profile=agent.profile,
                asset_returns=returns_by_asset,
                market_weights=market_weights,
                imitation_multiplier=imitation_multiplier,
                rng=rng,
                signal_noise=signal_noise,
            )
            rebalance_speed = max(0.0, min(1.0, agent.profile.rebalance_speed * rebalance_multiplier))
            agent.weights = blend_weights(previous_weights, target_weights, rebalance_speed)
            turnover = portfolio_turnover(previous_weights, agent.weights)
            net_return = gross_return - (turnover * rebalance_cost)
            agent.wealth *= max(0.0, 1 + net_return)

            period_turnovers.append(turnover)
            period_returns.append(net_return)

        market_weights = average_weights(agent.weights for agent in agents)
        total_wealth = sum(agent.wealth for agent in agents)
        peak_wealth = max(peak_wealth, total_wealth)
        drawdown = (total_wealth / peak_wealth) - 1
        max_drawdown = min(max_drawdown, drawdown)

        history.append(
            {
                "month": month,
                "period": period_index + 1,
                "avg_agent_return": mean(period_returns),
                "avg_turnover": mean(period_turnovers),
                "total_wealth": total_wealth,
                "drawdown": drawdown,
                "hhi_concentration": hhi(market_weights.values()),
                **{f"weight_{asset}": market_weights[asset] for asset in ASSETS},
            }
        )

    summary = summarize(
        history,
        agent_count,
        imitation_multiplier,
        rebalance_cost,
        seed,
        max_drawdown,
        shock_scenario,
        rebalance_multiplier,
        signal_noise,
        profile_mode,
    )
    return history, summary


def run_scenario_comparison(
    macro_records: list[dict[str, float | str]],
    imitation_levels: Iterable[float],
    agent_count: int = 300,
    rebalance_cost: float = 0.001,
    seed: int = 42,
    shock_scenario: str = "none",
) -> list[dict[str, float | str]]:
    comparison = []

    for imitation_level in imitation_levels:
        _, summary = run_baseline_simulation(
            macro_records,
            agent_count=agent_count,
            imitation_multiplier=imitation_level,
            rebalance_cost=rebalance_cost,
            seed=seed,
            shock_scenario=shock_scenario,
        )
        comparison.append({"scenario": f"imitation_{imitation_level:g}", **summary})

    return comparison


def run_shock_comparison(
    macro_records: list[dict[str, float | str]],
    shock_scenarios: Iterable[str],
    agent_count: int = 300,
    imitation_multiplier: float = 1.0,
    rebalance_cost: float = 0.001,
    seed: int = 42,
) -> list[dict[str, float | str]]:
    comparison = []

    for shock_scenario in shock_scenarios:
        _, summary = run_baseline_simulation(
            macro_records,
            agent_count=agent_count,
            imitation_multiplier=imitation_multiplier,
            rebalance_cost=rebalance_cost,
            seed=seed,
            shock_scenario=shock_scenario,
        )
        comparison.append({"scenario": shock_scenario, **summary})

    return comparison


def run_rebalance_comparison(
    macro_records: list[dict[str, float | str]],
    agent_count: int = 300,
    imitation_multiplier: float = 1.0,
    rebalance_cost: float = 0.001,
    seed: int = 42,
) -> list[dict[str, float | str]]:
    scenarios = [
        ("slow_clean", 0.5, 0.0),
        ("base_clean", 1.0, 0.0),
        ("fast_clean", 1.5, 0.0),
        ("fast_noisy", 1.5, 0.010),
        ("very_fast_noisy", 2.0, 0.020),
    ]
    comparison = []

    for scenario_name, rebalance_multiplier, signal_noise in scenarios:
        _, summary = run_baseline_simulation(
            macro_records,
            agent_count=agent_count,
            imitation_multiplier=imitation_multiplier,
            rebalance_cost=rebalance_cost,
            seed=seed,
            rebalance_multiplier=rebalance_multiplier,
            signal_noise=signal_noise,
        )
        comparison.append({"scenario": scenario_name, **summary})

    return comparison


def run_profile_comparison(
    macro_records: list[dict[str, float | str]],
    agent_count: int = 300,
    imitation_multiplier: float = 1.0,
    rebalance_cost: float = 0.001,
    seed: int = 42,
) -> list[dict[str, float | str]]:
    profile_modes = [
        "heterogeneous",
        "homogeneous_conservador",
        "homogeneous_moderado",
        "homogeneous_agressivo",
    ]
    comparison = []

    for profile_mode in profile_modes:
        _, summary = run_baseline_simulation(
            macro_records,
            agent_count=agent_count,
            imitation_multiplier=imitation_multiplier,
            rebalance_cost=rebalance_cost,
            seed=seed,
            profile_mode=profile_mode,
        )
        comparison.append({"scenario": profile_mode, **summary})

    return comparison


def build_asset_returns(
    macro_records: list[dict[str, float | str]],
    rng: random.Random,
) -> list[dict[str, float | str]]:
    asset_records: list[dict[str, float | str]] = []

    for record in macro_records:
        selic_return = float(record["selic_return"])
        ipca_rate = float(record["ipca_rate"])
        usd_return = float(record["usd_return"])

        equity_return = float(record.get("equity_return", math.nan))
        if math.isnan(equity_return):
            equity_noise = rng.gauss(0.004, 0.035)
            equity_return = 0.006 + equity_noise + (0.18 * usd_return) - (0.45 * selic_return) - (0.20 * ipca_rate)

        asset_records.append(
            {
                "month": record["month"],
                "cash": selic_return * 0.55,
                "tesouro_selic": selic_return,
                "tesouro_ipca": ipca_rate + 0.0035,
                "fundos_rf": max(-0.02, (selic_return * 0.88) - 0.0004),
                "renda_variavel": max(-0.35, min(0.35, equity_return)),
            }
        )

    return asset_records


def create_agents(agent_count: int, rng: random.Random, profile_mode: str = "heterogeneous") -> list[InvestorAgent]:
    agents: list[InvestorAgent] = []

    for index in range(agent_count):
        profile = select_profile(index, profile_mode)
        weights = jitter_weights(profile.base_weights, rng)
        agents.append(InvestorAgent(profile=profile, weights=weights))

    return agents


def select_profile(index: int, profile_mode: str) -> AgentProfile:
    if profile_mode == "heterogeneous":
        return DEFAULT_PROFILES[index % len(DEFAULT_PROFILES)]
    if profile_mode.startswith("homogeneous_"):
        profile_name = profile_mode.removeprefix("homogeneous_")
        for profile in DEFAULT_PROFILES:
            if profile.name == profile_name:
                return profile
    raise ValueError(f"Modo de perfil invalido: {profile_mode}")


def choose_target_weights(
    profile: AgentProfile,
    asset_returns: dict[str, float],
    market_weights: dict[str, float],
    imitation_multiplier: float,
    rng: random.Random,
    signal_noise: float,
) -> dict[str, float]:
    scores = {}
    market_stress = max(0.0, -asset_returns["renda_variavel"])
    stress_multiplier = 1 + (market_stress * 8)
    imitation_strength = profile.imitation_bias * imitation_multiplier * stress_multiplier

    for asset in ASSETS:
        expected_return = asset_returns[asset] + rng.gauss(0.0, signal_noise)
        risk_penalty = profile.risk_aversion * ASSET_RISK[asset] * 0.004
        base_anchor = profile.base_weights[asset] * 0.018
        imitation_anchor = (market_weights[asset] - profile.base_weights[asset]) * imitation_strength * 0.025
        crowding_penalty = max(0.0, market_weights[asset] - profile.base_weights[asset]) * 0.020
        risk_off_bonus = risk_off_score(asset, market_stress)
        scores[asset] = expected_return - risk_penalty + base_anchor + imitation_anchor - crowding_penalty + risk_off_bonus

    return softmax(scores, temperature=0.060)


def write_history_csv(path: Path, history: Iterable[dict[str, float | str]]) -> None:
    rows = list(history)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_summary_json(path: Path, summary: dict[str, float | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)


def write_comparison_csv(path: Path, rows: Iterable[dict[str, float | str]]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize(
    history: list[dict[str, float | str]],
    agent_count: int,
    imitation_multiplier: float,
    rebalance_cost: float,
    seed: int,
    max_drawdown: float,
    shock_scenario: str,
    rebalance_multiplier: float,
    signal_noise: float,
    profile_mode: str,
) -> dict[str, float | str]:
    final = history[-1]
    returns = [float(row["avg_agent_return"]) for row in history]

    return {
        "agent_count": agent_count,
        "periods": len(history),
        "imitation_multiplier": imitation_multiplier,
        "rebalance_cost": rebalance_cost,
        "seed": seed,
        "shock_scenario": shock_scenario,
        "rebalance_multiplier": rebalance_multiplier,
        "signal_noise": signal_noise,
        "profile_mode": profile_mode,
        "final_total_wealth": float(final["total_wealth"]),
        "cumulative_return": (float(final["total_wealth"]) / agent_count) - 1,
        "avg_monthly_return": mean(returns),
        "return_volatility": stdev(returns),
        "max_drawdown": max_drawdown,
        "final_hhi_concentration": float(final["hhi_concentration"]),
        **{f"final_weight_{asset}": float(final[f"weight_{asset}"]) for asset in ASSETS},
    }


def apply_shock_scenario(
    macro_records: list[dict[str, float | str]],
    shock_scenario: str,
) -> list[dict[str, float | str]]:
    if shock_scenario == "none":
        return [dict(record) for record in macro_records]

    supported = {"rate_hike", "inflation_spike", "equity_stress", "combined_stress"}
    if shock_scenario not in supported:
        raise ValueError(f"Cenario de choque invalido: {shock_scenario}")

    shocked_records: list[dict[str, float | str]] = []
    shock_start = len(macro_records) // 2

    for index, record in enumerate(macro_records):
        shocked = dict(record)
        if index >= shock_start:
            if shock_scenario in {"rate_hike", "combined_stress"}:
                shocked["selic_return"] = float(shocked["selic_return"]) + 0.004
                shocked["equity_return"] = _adjust_equity_return(shocked, -0.015)
            if shock_scenario in {"inflation_spike", "combined_stress"}:
                shocked["ipca_rate"] = float(shocked["ipca_rate"]) + 0.006
                shocked["equity_return"] = _adjust_equity_return(shocked, -0.010)
            if shock_scenario in {"equity_stress", "combined_stress"}:
                shocked["usd_return"] = float(shocked["usd_return"]) + 0.030
                shocked["equity_return"] = _adjust_equity_return(shocked, -0.060)
            shocked["equity_return_source"] = f"{shocked.get('equity_return_source', 'synthetic_fallback')}+shock"
        shocked_records.append(shocked)

    return shocked_records


def _adjust_equity_return(record: dict[str, float | str], delta: float) -> float:
    current = float(record.get("equity_return", math.nan))
    if math.isnan(current):
        current = 0.0
    return max(-0.60, min(0.60, current + delta))


def risk_off_score(asset: str, market_stress: float) -> float:
    if market_stress <= 0:
        return 0.0
    if asset in {"cash", "tesouro_selic"}:
        return market_stress * 0.20
    if asset == "renda_variavel":
        return -market_stress * 0.28
    return 0.0


def weighted_return(weights: dict[str, float], returns_by_asset: dict[str, float]) -> float:
    return sum(weights[asset] * returns_by_asset[asset] for asset in ASSETS)


def blend_weights(
    previous_weights: dict[str, float],
    target_weights: dict[str, float],
    rebalance_speed: float,
) -> dict[str, float]:
    blended = {
        asset: ((1 - rebalance_speed) * previous_weights[asset]) + (rebalance_speed * target_weights[asset])
        for asset in ASSETS
    }
    return normalize_weights(blended)


def jitter_weights(base_weights: dict[str, float], rng: random.Random) -> dict[str, float]:
    jittered = {
        asset: max(0.001, weight + rng.gauss(0, 0.025))
        for asset, weight in base_weights.items()
    }
    return normalize_weights(jittered)


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in weights.values())
    if total <= 0:
        return {asset: 1 / len(ASSETS) for asset in ASSETS}
    return {asset: max(0.0, weights[asset]) / total for asset in ASSETS}


def average_weights(weight_sets: Iterable[dict[str, float]]) -> dict[str, float]:
    totals = {asset: 0.0 for asset in ASSETS}
    count = 0
    for weights in weight_sets:
        count += 1
        for asset in ASSETS:
            totals[asset] += weights[asset]
    if count == 0:
        return {asset: 1 / len(ASSETS) for asset in ASSETS}
    return {asset: totals[asset] / count for asset in ASSETS}


def portfolio_turnover(previous_weights: dict[str, float], current_weights: dict[str, float]) -> float:
    return sum(abs(current_weights[asset] - previous_weights[asset]) for asset in ASSETS) / 2


def hhi(values: Iterable[float]) -> float:
    return sum(value * value for value in values)


def softmax(scores: dict[str, float], temperature: float) -> dict[str, float]:
    max_score = max(scores.values())
    exp_values = {
        asset: math.exp((score - max_score) / temperature)
        for asset, score in scores.items()
    }
    total = sum(exp_values.values())
    return {asset: value / total for asset, value in exp_values.items()}


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def stdev(values: Iterable[float]) -> float:
    values = list(values)
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    variance = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)
