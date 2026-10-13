"""Run the report template's experiments without changing submission code/config.

Results are simulator output, not manually supplied report numbers.
Run: python scripts/run_report_experiments.py
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gameday_lab.client import ResilientClient
from gameday_lab.factory import build_client
from gameday_lab.sim.config import load_config
from gameday_lab.sim.engine import evaluate_checks, run_scenario


class UnfilteredClient(ResilientClient):
    """Intentional unsafe control used only for report experiment 3."""

    def ladder(self, task: str) -> list[str]:
        return list(self.order)


def main() -> None:
    out = Path("reports/experiments")
    out.mkdir(parents=True, exist_ok=True)
    records = []

    def run(label, scenarios, client="resilient", changes=None, cache_changes=None, unfiltered=False):
        cfg = copy.deepcopy(load_config(
            "configs/gameday.yaml",
            "configs/scenarios_cache.yaml" if client == "cached" else "configs/scenarios.yaml",
        ))
        if changes:
            cfg.client.update(changes)
        if cache_changes:
            cfg.cache.update(cache_changes)
        for scenario in scenarios:
            instance = (UnfilteredClient(cfg.provider_infos(), cfg.fallback_order, cfg.client, seed=1)
                        if unfiltered else build_client(client, cfg))
            sim = run_scenario(cfg, scenario, instance, cfg.seed)
            metrics = sim.metrics()
            metrics["checks"] = evaluate_checks(metrics, cfg.scenarios[scenario].checks)
            record = {"experiment": label, "scenario": scenario, "seed": cfg.seed,
                      "client": client, "client_settings": cfg.client, "cache_settings": cfg.cache,
                      "unfiltered_tool_ladder": unfiltered, "metrics": metrics}
            records.append(record)
            (out / f"{label}_{scenario}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
            print(label, scenario, "availability=", metrics["availability"],
                  "amplification=", metrics["amplification"])

    core = ["G2_overload_storm", "G3_brownout"]
    run("baseline", core + ["G4_slow_region", "G6_provider_outage"])
    broken = copy.deepcopy(load_config("configs/gameday.yaml", "configs/scenarios.yaml").client["breaker"])
    broken["min_calls"] = 1000000000
    run("breaker_disabled_budget_on", core, changes={"breaker": broken, "max_attempts_per_provider": 5})
    run("breaker_disabled_budget_off", core, changes={
        "breaker": broken, "max_attempts_per_provider": 5, "retry_budget_ratio": 100,
        "retry_budget_max_tokens": 1.0e9, "retry_budget_min_per_s": 1.0e6,
    })
    run("timeout_30", ["G4_slow_region", "G6_provider_outage"], changes={"attempt_timeout_s": 30})
    run("tool_filter_disabled", ["G6_provider_outage"], unfiltered=True)
    for threshold in (0.80, 0.94, 0.97):
        run(f"similarity_{threshold:.2f}", ["C1_faq_outage"], "cached",
            cache_changes={"similarity_threshold": threshold})
    for ttl in (30, 60, 300):
        run(f"ttl_{ttl}", ["C1_faq_outage"], "cached", cache_changes={"ttl_s": ttl})
    run("stale_disabled", ["C1_faq_outage"], "cached", cache_changes={"max_stale_s": 0})
    (out / "results.json").write_text(json.dumps(records, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
