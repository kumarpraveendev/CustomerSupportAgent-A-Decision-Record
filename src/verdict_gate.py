"""The verdict gate: AUTO / REQUIRE_APPROVAL / FORBIDDEN.

Sits between an action being *proposed* and *executed*. The verdict is decided
by policy — blast radius and reversibility — and never by how confident the
model is. A confident, high-blast action is gated exactly like an unsure one.

See decisions/0002-bounded-autonomy.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.actions import Action, ActionPolicy, DEFAULT_POLICIES


class Verdict(Enum):
    AUTO = "AUTO"                          # cheap, reversible, low blast radius
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"  # a human's name goes on it
    FORBIDDEN = "FORBIDDEN"                # never, regardless of confidence


@dataclass(frozen=True)
class VerdictDecision:
    """The gate's output. ``reason`` is written to the audit trail (ADR-0006)."""

    verdict: Verdict
    action_type: str
    reason: str


def classify(
    action: Action,
    registry: dict[str, ActionPolicy] = DEFAULT_POLICIES,
) -> VerdictDecision:
    """Classify a proposed action. Note: ``action.model_confidence`` is never read."""
    policy = registry.get(action.type)

    # Unknown action types are never granted silent autonomy.
    if policy is None:
        return VerdictDecision(
            Verdict.REQUIRE_APPROVAL, action.type,
            "unknown action type; defaults to approval, never silent AUTO",
        )

    # Outside the mandate -> forbidden, full stop.
    if not policy.in_mandate:
        return VerdictDecision(
            Verdict.FORBIDDEN, action.type,
            "action is outside the agent's mandate",
        )

    # Disqualifiers from AUTO, in order. Each is a property of the action's
    # blast radius — none of them is the model's confidence.
    if policy.touches_payment_instrument:
        return VerdictDecision(
            Verdict.REQUIRE_APPROVAL, action.type,
            "touches a payment instrument",
        )
    if not policy.reversible:
        return VerdictDecision(
            Verdict.REQUIRE_APPROVAL, action.type,
            "action is not reversible",
        )
    if policy.account_mutating:
        return VerdictDecision(
            Verdict.REQUIRE_APPROVAL, action.type,
            "mutates account or security state",
        )
    if action.amount is not None:
        if policy.auto_ceiling is None or action.amount > policy.auto_ceiling:
            ceiling = (
                "no auto ceiling for this action"
                if policy.auto_ceiling is None
                else f"above auto ceiling of {policy.auto_ceiling}"
            )
            return VerdictDecision(
                Verdict.REQUIRE_APPROVAL, action.type,
                f"monetary amount {action.amount} {ceiling}",
            )

    return VerdictDecision(
        Verdict.AUTO, action.type,
        "low blast radius: reversible, non-payment, within ceiling",
    )
