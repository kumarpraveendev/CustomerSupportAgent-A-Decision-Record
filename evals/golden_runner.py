"""Golden-case runner. Doubles as the CI eval gate (exit 1 on any failure).

Each case exercises the real components — the verdict gate, the router, or the
safety invariants — against an expected outcome. Cases are sourced from
production escalations and reopens over time (ADR-0001, ADR-0005); the file here
is a representative seed set.

Run: ``python -m evals.golden_runner``
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.actions import Action
from src.router import Router, StubProvider, Tier, Turn
from src.verdict_gate import Verdict, classify
from evals.safety_invariants import ExecutedAction, ResponseContext, passed

CASES_PATH = Path(__file__).with_name("golden_cases.json")

# A representative, always-available provider pool for routing cases.
_ROUTER = Router([
    StubProvider("cheap-a", Tier.CHEAP),
    StubProvider("cheap-b", Tier.CHEAP),
    StubProvider("strong-a", Tier.STRONG),
    StubProvider("strong-b", Tier.STRONG),
])


@dataclass(frozen=True)
class Result:
    name: str
    passed: bool
    detail: str


def _run_verdict(case: dict[str, Any]) -> Result:
    a = case["action"]
    action = Action(
        type=a["type"],
        amount=Decimal(a["amount"]) if "amount" in a else None,
        model_confidence=a.get("model_confidence", 1.0),
    )
    got = classify(action).verdict
    want = Verdict[case["expect"].upper()]
    return Result(case["name"], got is want, f"want {want.value}, got {got.value}")


def _run_routing(case: dict[str, Any]) -> Result:
    t = case["turn"]
    turn = Turn(
        intent=t["intent"],
        intent_confidence=t["intent_confidence"],
        high_stakes=t.get("high_stakes", False),
        requires_multistep=t.get("requires_multistep", False),
    )
    got = _ROUTER.route(turn).tier
    want = Tier(case["expect"])
    return Result(case["name"], got is want, f"want {want.value}, got {got.value}")


def _run_invariant(case: dict[str, Any]) -> Result:
    c = case["context"]
    ctx = ResponseContext(
        session_customer_id=c["session_customer_id"],
        text=c.get("text", ""),
        policy_claims=c.get("policy_claims", []),
        refund_promised=c.get("refund_promised", False),
        approved_refund_exists=c.get("approved_refund_exists", False),
        mentioned_customer_ids=c.get("mentioned_customer_ids", []),
        executed_actions=[
            ExecutedAction(e["action_type"], Verdict[e["verdict"]], e.get("approved_by"))
            for e in c.get("executed_actions", [])
        ],
    )
    got = passed(ctx)
    want = case["expect_pass"]
    return Result(case["name"], got == want, f"want pass={want}, got pass={got}")


_DISPATCH = {"verdict": _run_verdict, "routing": _run_routing, "invariant": _run_invariant}


def load_cases(path: Path = CASES_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def run_all(cases: list[dict[str, Any]]) -> list[Result]:
    return [_DISPATCH[c["kind"]](c) for c in cases]


def main() -> int:
    results = run_all(load_cases())
    failures = [r for r in results if not r.passed]
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        print(f"[{mark}] {r.name}" + ("" if r.passed else f"  ({r.detail})"))
    print(f"\n{len(results) - len(failures)}/{len(results)} passed.")
    if failures:
        print("EVAL GATE: BLOCKED — regression(s) detected.")
        return 1
    print("EVAL GATE: PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
