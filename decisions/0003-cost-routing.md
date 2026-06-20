# ADR-0003: Spend model dollars only where the conversation gets hard

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Finance |
| **Supersedes** | — |
| **Tags** | cost, routing, unit-economics, reliability |

---

## Context

Cost per resolution is on the scorecard (ADR-0001) because at support volume it's the number that decides whether this agent is a margin win or a margin leak. And the single biggest lever on it is the most boring one: which model answers which turn.

The default is to point every turn at one strong model because it's simplest and the demo looks great. At a few hundred conversations it's invisible. At a few hundred thousand it's the line item Finance circles. Most support turns are not hard — "where's my order," "how do I start a return," "what's your policy on X." Paying frontier prices to answer "where's my order" is indefensible once you can see the bill.

I've made this exact call before, on an inference platform where a cascaded multi-provider pipeline cut cost roughly 70% against a managed baseline and became the org-wide reference pattern. This is that pattern, retold for support and measured in cost per resolution.

## Decision

**Cascaded, multi-provider routing.** A cheap, fast model handles intent classification and the easy majority of turns. Harder turns — low router confidence, multi-step reasoning, sensitive or high-stakes context — escalate to a stronger model. Using more than one provider also buys resilience: a provider outage degrades, it doesn't halt.

The router is a first-class component with its own evaluation, not a hidden `if` statement, because a bad route is a quality regression in disguise.

## Alternatives considered

**One flagship model on every turn.** Rejected on economics. Simple and expensive; the cost doesn't survive scale, and it's the easiest large saving to leave on the table.

**One cheap model on every turn.** Rejected on quality. It floors out on the hard cases, which then escalate to a *human* — and a human-handled contact costs far more than a stronger model would have. You didn't save money; you moved it somewhere worse and annoyed the customer on the way.

**Fine-tune a single model for support.** Rejected for v1, not forever. Premature optimization with real ops burden (retraining, drift, eval) before we even know the traffic shape. Routing first; fine-tuning is a later decision made with data.

## Consequences

**What this buys us**
- Unit economics that survive scale, because spend concentrates on the minority of turns that need it.
- Provider redundancy, so a single vendor's bad day is a degradation, not an outage.
- A cost-per-resolution number I can put in front of Finance and defend.

**What it costs us**
- The router is a component to build, evaluate, and maintain. Complexity has a price; this one earns it.
- A wrong route can hurt quality — sending a hard case to the cheap model produces a worse answer or an unnecessary escalation.

**Risks and how we hold them**
- *Cost routing quietly degrades CSAT.* Mitigation: route quality is judged against the balanced scorecard, never against cost alone. A cheaper blend that drops CSAT or raises reopen rate is a regression (ADR-0001), full stop.
- *The router becomes the bottleneck or a single point of failure.* Mitigation: conservative defaults — when the router is unsure, it escalates *up*, not down. Cheap-model errors are the expensive kind here.

## How we operate it

- Routing thresholds are tuned against the scorecard, with cost and CSAT read together, not cost in isolation.
- Cost per resolution and the cheap/strong split are tracked weekly alongside the experience metrics.
- Provider failover is tested, not assumed — a runbook exists for "primary provider is down."

---

**In one line, if I had to defend it to a board:** *I won't pay frontier-model prices to answer "where's my order." The model dollars go to the conversations that actually need them — that's the difference between automation that helps the margin and automation that quietly eats it.*
