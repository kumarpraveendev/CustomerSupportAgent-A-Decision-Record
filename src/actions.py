"""Actions an agent can propose, and the policy that classifies their risk.

The policy is keyed on action *type* and described in terms of blast radius and
reversibility — deliberately NOT model confidence. See
decisions/0002-bounded-autonomy.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Action:
    """A side-effecting action a sub-agent proposes to take.

    ``model_confidence`` is recorded for the audit trail (ADR-0006) but, by
    design, is never an input to risk classification. See
    :func:`src.verdict_gate.classify`.
    """

    type: str
    amount: Optional[Decimal] = None          # for monetary actions
    customer_id: Optional[str] = None
    model_confidence: float = 1.0             # audit metadata only — never gates


@dataclass(frozen=True)
class ActionPolicy:
    """Risk policy for one action type.

    Every field below is a property of the *action*, not of how sure the model
    is. Any one disqualifier is enough to pull the action out of AUTO.
    """

    action_type: str
    in_mandate: bool                          # False -> FORBIDDEN, always
    reversible: bool                          # irreversible -> at least approval
    touches_payment_instrument: bool          # True -> never AUTO
    account_mutating: bool = False            # changes account/security state -> approval
    auto_ceiling: Optional[Decimal] = None    # monetary: max amount eligible for AUTO


# A small, explicit policy table. Action types absent from this registry default
# to REQUIRE_APPROVAL — an unknown action never earns silent AUTO.
DEFAULT_POLICIES: dict[str, ActionPolicy] = {
    p.action_type: p
    for p in [
        ActionPolicy("order_lookup", in_mandate=True, reversible=True,
                     touches_payment_instrument=False),
        ActionPolicy("send_tracking_link", in_mandate=True, reversible=True,
                     touches_payment_instrument=False),
        ActionPolicy("initiate_return", in_mandate=True, reversible=True,
                     touches_payment_instrument=False),
        ActionPolicy("store_credit", in_mandate=True, reversible=True,
                     touches_payment_instrument=False, auto_ceiling=Decimal("20")),
        ActionPolicy("refund", in_mandate=True, reversible=False,
                     touches_payment_instrument=True, auto_ceiling=Decimal("0")),
        ActionPolicy("address_change", in_mandate=True, reversible=True,
                     touches_payment_instrument=False, account_mutating=True),
        # Outside the agent's mandate -> FORBIDDEN regardless of anything else.
        ActionPolicy("account_close", in_mandate=False, reversible=False,
                     touches_payment_instrument=False),
        ActionPolicy("override_fraud_hold", in_mandate=False, reversible=False,
                     touches_payment_instrument=False),
    ]
}
