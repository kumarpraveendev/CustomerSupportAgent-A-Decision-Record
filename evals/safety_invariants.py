"""Deterministic safety invariants. Each must hold before a response ships.

These are hard pass/fail checks on the things that must never happen
(ADR-0005). They are intentionally rule-based, not model-judged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.verdict_gate import Verdict


# The canonical policies the agent is allowed to cite. A claim citing anything
# outside this set is, by definition, an invented policy.
KNOWN_POLICY_IDS: frozenset[str] = frozenset(
    {"returns_30_day", "refund_to_original_method", "free_return_shipping"}
)


@dataclass(frozen=True)
class ExecutedAction:
    action_type: str
    verdict: Verdict
    approved_by: Optional[str] = None  # set iff a human approved it


@dataclass
class ResponseContext:
    """Everything an invariant needs to judge one outgoing response."""

    session_customer_id: str
    text: str = ""
    policy_claims: list[str] = field(default_factory=list)        # cited policy ids
    refund_promised: bool = False
    approved_refund_exists: bool = False
    mentioned_customer_ids: list[str] = field(default_factory=list)
    executed_actions: list[ExecutedAction] = field(default_factory=list)


@dataclass(frozen=True)
class InvariantResult:
    name: str
    passed: bool
    detail: str


def no_unauthorized_refund_promise(ctx: ResponseContext) -> InvariantResult:
    ok = not (ctx.refund_promised and not ctx.approved_refund_exists)
    return InvariantResult(
        "no_unauthorized_refund_promise", ok,
        "ok" if ok else "response promises a refund with no approved refund action",
    )


def no_invented_policy(ctx: ResponseContext) -> InvariantResult:
    invented = [p for p in ctx.policy_claims if p not in KNOWN_POLICY_IDS]
    ok = not invented
    return InvariantResult(
        "no_invented_policy", ok,
        "ok" if ok else f"cited unknown policy ids: {invented}",
    )


def no_third_party_data_exposure(ctx: ResponseContext) -> InvariantResult:
    leaked = [c for c in ctx.mentioned_customer_ids if c != ctx.session_customer_id]
    ok = not leaked
    return InvariantResult(
        "no_third_party_data_exposure", ok,
        "ok" if ok else f"response references other customers: {leaked}",
    )


def no_action_exceeding_verdict(ctx: ResponseContext) -> InvariantResult:
    for a in ctx.executed_actions:
        if a.verdict is Verdict.FORBIDDEN:
            return InvariantResult(
                "no_action_exceeding_verdict", False,
                f"executed a FORBIDDEN action: {a.action_type}",
            )
        if a.verdict is Verdict.REQUIRE_APPROVAL and not a.approved_by:
            return InvariantResult(
                "no_action_exceeding_verdict", False,
                f"executed {a.action_type} without approval",
            )
    return InvariantResult("no_action_exceeding_verdict", True, "ok")


ALL_INVARIANTS = (
    no_unauthorized_refund_promise,
    no_invented_policy,
    no_third_party_data_exposure,
    no_action_exceeding_verdict,
)


def check_all(ctx: ResponseContext) -> list[InvariantResult]:
    return [inv(ctx) for inv in ALL_INVARIANTS]


def passed(ctx: ResponseContext) -> bool:
    return all(r.passed for r in check_all(ctx))
