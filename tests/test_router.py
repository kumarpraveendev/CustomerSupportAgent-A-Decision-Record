from src.router import Router, StubProvider, Tier, Turn


def _full_pool():
    return [
        StubProvider("cheap-a", Tier.CHEAP),
        StubProvider("cheap-b", Tier.CHEAP),
        StubProvider("strong-a", Tier.STRONG),
        StubProvider("strong-b", Tier.STRONG),
    ]


def test_easy_high_confidence_turn_stays_cheap():
    r = Router(_full_pool())
    d = r.route(Turn("order_status", intent_confidence=0.95))
    assert d.tier is Tier.CHEAP
    assert not d.degraded


def test_high_stakes_always_escalates_up():
    r = Router(_full_pool())
    d = r.route(Turn("billing_dispute", intent_confidence=0.99, high_stakes=True))
    assert d.tier is Tier.STRONG


def test_low_confidence_escalates_up_conservatively():
    r = Router(_full_pool())
    d = r.route(Turn("ambiguous", intent_confidence=0.4))
    assert d.tier is Tier.STRONG


def test_multistep_escalates_up():
    r = Router(_full_pool())
    d = r.route(Turn("complex", intent_confidence=0.99, requires_multistep=True))
    assert d.tier is Tier.STRONG


def test_within_tier_failover_skips_unhealthy_primary():
    pool = [
        StubProvider("cheap-a", Tier.CHEAP, healthy=False),
        StubProvider("cheap-b", Tier.CHEAP, healthy=True),
        StubProvider("strong-a", Tier.STRONG),
    ]
    d = Router(pool).route(Turn("order_status", intent_confidence=0.95))
    assert d.provider == "cheap-b"
    assert not d.degraded


def test_whole_tier_down_degrades_rather_than_halts():
    pool = [
        StubProvider("cheap-a", Tier.CHEAP, healthy=False),
        StubProvider("cheap-b", Tier.CHEAP, healthy=False),
        StubProvider("strong-a", Tier.STRONG, healthy=True),
    ]
    d = Router(pool).route(Turn("order_status", intent_confidence=0.95))
    assert d.tier is Tier.STRONG
    assert d.degraded


def test_no_providers_raises():
    import pytest
    pool = [StubProvider("cheap-a", Tier.CHEAP, healthy=False)]
    with pytest.raises(RuntimeError):
        Router(pool).route(Turn("order_status", intent_confidence=0.95))
