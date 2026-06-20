"""Cascaded, multi-provider cost router.

A cheap/fast model handles the easy majority of turns; hard turns escalate to a
stronger model. The router defaults *up* when unsure, because a cheap-model
mistake ends up at a human and costs more than the stronger model would have.
Multiple providers per tier give failover: a provider outage degrades, it does
not halt.

See decisions/0003-cost-routing.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Sequence


class Tier(Enum):
    CHEAP = "cheap"
    STRONG = "strong"


@dataclass(frozen=True)
class Turn:
    """One conversational turn the router has to place."""

    intent: str
    intent_confidence: float          # the router's confidence in its own read
    high_stakes: bool = False         # financial / sensitive context
    requires_multistep: bool = False  # needs real reasoning


class Provider(Protocol):
    """Anything that can answer a turn. A real Anthropic/OpenAI client and the
    test ``StubProvider`` implement the same shape."""

    name: str
    tier: Tier
    healthy: bool

    def complete(self, prompt: str) -> str: ...


@dataclass
class StubProvider:
    """Deterministic stand-in so the router runs with no network or API keys."""

    name: str
    tier: Tier
    healthy: bool = True

    def complete(self, prompt: str) -> str:
        return f"[{self.name}] {prompt[:40]}"


@dataclass(frozen=True)
class RoutingDecision:
    tier: Tier
    provider: str
    reason: str
    degraded: bool = False  # True if we fell back to the other tier to stay up


class Router:
    def __init__(self, providers: Sequence[Provider], confidence_threshold: float = 0.75):
        self._providers = list(providers)
        self.confidence_threshold = confidence_threshold

    def select_tier(self, turn: Turn) -> tuple[Tier, str]:
        """Pick a tier. Conservative by design: escalate up whenever unsure."""
        if turn.high_stakes:
            return Tier.STRONG, "high-stakes context -> strong model"
        if turn.requires_multistep:
            return Tier.STRONG, "multi-step reasoning -> strong model"
        if turn.intent_confidence < self.confidence_threshold:
            return Tier.STRONG, (
                f"router confidence {turn.intent_confidence:.2f} below "
                f"{self.confidence_threshold:.2f} -> escalate up"
            )
        return Tier.CHEAP, "easy, high-confidence turn -> cheap model"

    def _healthy_in_tier(self, tier: Tier) -> list[Provider]:
        return [p for p in self._providers if p.tier == tier and p.healthy]

    def route(self, turn: Turn) -> RoutingDecision:
        tier, reason = self.select_tier(turn)

        # Within-tier failover: first healthy provider wins.
        candidates = self._healthy_in_tier(tier)
        if candidates:
            return RoutingDecision(tier, candidates[0].name, reason)

        # Whole tier down -> degrade to the other tier rather than halt.
        other = Tier.STRONG if tier is Tier.CHEAP else Tier.CHEAP
        fallback = self._healthy_in_tier(other)
        if fallback:
            return RoutingDecision(
                other, fallback[0].name,
                f"{reason}; {tier.value} tier unavailable, degraded to {other.value}",
                degraded=True,
            )

        raise RuntimeError("no healthy providers available in any tier")
