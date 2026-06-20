from decimal import Decimal

import pytest

from src.actions import Action
from src.verdict_gate import Verdict, classify


def test_cheap_reversible_action_is_auto():
    assert classify(Action("order_lookup")).verdict is Verdict.AUTO


def test_small_store_credit_within_ceiling_is_auto():
    assert classify(Action("store_credit", amount=Decimal("10"))).verdict is Verdict.AUTO


def test_store_credit_over_ceiling_requires_approval():
    d = classify(Action("store_credit", amount=Decimal("50")))
    assert d.verdict is Verdict.REQUIRE_APPROVAL
    assert "ceiling" in d.reason


def test_refund_requires_approval_even_for_small_amounts():
    assert classify(Action("refund", amount=Decimal("1"))).verdict is Verdict.REQUIRE_APPROVAL


def test_account_mutating_action_requires_approval():
    assert classify(Action("address_change")).verdict is Verdict.REQUIRE_APPROVAL


def test_out_of_mandate_action_is_forbidden():
    assert classify(Action("account_close")).verdict is Verdict.FORBIDDEN


def test_unknown_action_never_gets_silent_auto():
    d = classify(Action("issue_gift_card"))
    assert d.verdict is Verdict.REQUIRE_APPROVAL
    assert "unknown" in d.reason


@pytest.mark.parametrize("confidence", [0.01, 0.5, 0.99, 1.0])
def test_confidence_never_changes_a_high_blast_verdict(confidence):
    # The whole point of ADR-0002: confidence does not buy autonomy.
    d = classify(Action("refund", amount=Decimal("500"), model_confidence=confidence))
    assert d.verdict is Verdict.REQUIRE_APPROVAL


@pytest.mark.parametrize("confidence", [0.01, 0.5, 0.99, 1.0])
def test_confidence_never_lowers_a_safe_verdict_either(confidence):
    d = classify(Action("order_lookup", model_confidence=confidence))
    assert d.verdict is Verdict.AUTO


def test_every_decision_carries_an_audit_reason():
    for action in [Action("order_lookup"), Action("refund", amount=Decimal("5")),
                   Action("account_close")]:
        assert classify(action).reason
