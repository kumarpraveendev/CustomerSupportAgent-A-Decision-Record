# Building a Customer-Support Agent: A Decision Record

<!-- Replace <your-username> with your GitHub username so the badge renders -->
[![ci](https://github.com/<your-username>/support-agent-decisions/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-username>/support-agent-decisions/actions/workflows/ci.yml)

> A reference design for a production-grade, customer-facing support agent — written as the set of decisions a Head of Engineering actually owns, not a tour of the architecture.

This repository is not a demo of a framework. It is a record of the **judgment calls** that decide whether a support agent earns trust or quietly erodes it: where the agent acts alone, where a human's name goes on the action, what gets measured, what it costs per resolution, and how you prove it's safe before a customer ever sees it.

The architecture is here too — LangGraph orchestration, a multi-provider routing layer, a verdict gate, an evaluation harness — but it sits *underneath* the decisions as evidence, not at the front door. If you only read this README, you should understand how I'd run this, not just how it's wired.

---

## A note on the numbers

This is a reference design. The support-agent figures below (cost per resolution, automation rate, latency) are **design targets**, not production results.

The judgment behind them comes from real work: building a multi-tenant LLM platform, a cascaded multi-provider inference pipeline that cut cost ~70% against a managed baseline and became an org-wide reference, and an agentic on-call system that took on-call load down ~50% — plus a decade embedded with enterprise customers and several years running engineering teams as a manager-of-managers. Where I draw on that, I say so. I'd rather be transparent about what's designed vs. shipped than dress a portfolio up as something it isn't.

---

## The problem, framed as a leader sees it

Most support-agent projects fail not on model quality but on three decisions made badly up front:

1. **They optimize for deflection.** A "how many tickets did we avoid" scorecard rewards an agent for getting rid of customers. That number goes up while CSAT quietly goes down, and nobody notices until churn does.
2. **They never draw the autonomy line.** The agent is allowed to do whatever the prompt permits, which means the first expensive mistake is also the first time anyone thinks about boundaries.
3. **They break context on handoff.** When the agent gives up, the human inherits a blank slate, the customer repeats themselves, and the "AI" is now a tax on the support team rather than a multiplier.

This design treats all three as decisions to be made deliberately, before any code. Scope is deliberately narrow — **order status, returns, and billing disputes** — because a bounded agent that works beats a do-everything agent that mostly doesn't, and shipping the narrow thing first is itself the call I'd make.

---

## The decisions

The spine of this repo. Each links to a full Architecture Decision Record in [`/decisions`](./decisions). Each one is also a tradeoff I can defend out loud.

### 1. Measure experience and economics together, never deflection alone
**Decided:** a balanced scorecard — automation rate and cost per resolution *alongside* CSAT and first-contact resolution.
**Rejected:** a deflection-rate target.
**Why:** the metric you choose is the behavior you get. A deflection-only target trains the system, and the team, to avoid customers. The scorecard is the first thing I'd fix, before a line of agent code.
**Consequence:** every later decision gets judged against both axes, so we never buy automation by spending experience. → [ADR-0001](./decisions/0001-balanced-scorecard.md)

### 2. Bounded autonomy: decide what the agent does alone, what it escalates, what it must never do
**Decided:** a three-state verdict gate on every consequential action — `AUTO` (do it), `REQUIRE_APPROVAL` (a human's name goes on it), `FORBIDDEN` (never, regardless of confidence).
**Rejected:** confidence-threshold autonomy, where a high enough score lets the agent do anything.
**Why:** risk isn't a function of model confidence. Issuing a $5 store credit and processing a $500 refund are different *risk* decisions even when the model is equally sure. The line belongs to me, set by blast radius, not to the model's softmax.
**Consequence:** refunds above a threshold, account changes, and anything irreversible route to a human with full context; the cheap reversible actions run unattended. → [ADR-0002](./decisions/0002-bounded-autonomy.md)

### 3. Spend model dollars only where the conversation gets hard
**Decided:** cascaded multi-provider routing — a cheap fast model handles intent and the easy majority; harder turns escalate to a stronger model.
**Rejected:** a single flagship model on every turn.
**Why:** a frontier model on every message is economically indefensible at support volume. This is the same pattern I used on an inference platform that cut cost ~70% against a managed baseline; here it's retold as **cost per resolution**, which is the number that lands in a board pack.
**Consequence:** target unit economics that survive scaling, with the spend concentrated on the conversations that actually need it. → [ADR-0003](./decisions/0003-cost-routing.md)

### 4. The handoff carries the full context, always
**Decided:** when the agent escalates, the human inherits the complete conversation, the customer's history, and the agent's own reasoning and attempted actions.
**Rejected:** a "transfer to agent" that drops the human into a cold thread.
**Why:** no amount of model quality compensates for broken context. A handoff that makes the customer start over is worse than no automation at all — it adds a step and burns goodwill.
**Consequence:** escalation is designed as a feature of the experience, not an admission of failure. → [ADR-0004](./decisions/0004-escalation-context.md)

### 5. Nothing reaches a customer without passing an eval gate
**Decided:** a CI evaluation harness — golden cases plus safety invariants — that blocks deploys on regression.
**Rejected:** ship-and-watch, with quality assessed in production.
**Why:** a support agent can promise a refund the business can't honor or invent a return policy. That's not a bug to find in prod; it's a release I shouldn't allow. Eval discipline is the difference between a demo and something I'd put in front of customers.
**Consequence:** every change runs against scenarios with hard pass/fail safety checks before it can merge. → [ADR-0005](./decisions/0005-evaluation-gate.md)

### 6. Governance is a deliverable, not paperwork
**Decided:** structured audit logging of every decision, action, and approval, producing a compliance/audit artifact as a first-class output, with EU AI Act posture considered up front.
**Rejected:** treating compliance as a thing to bolt on before launch.
**Why:** in regulated and enterprise settings, an auditable trail is what lets you deploy the agent into higher-value, higher-risk workflows at all. Governance done early is an enabler, not overhead.
**Consequence:** see [`/artifacts/sample-audit-report.md`](./artifacts/sample-audit-report.md) for what ships alongside the system. → [ADR-0006](./decisions/0006-governance-audit.md)

### 7. Buy the platform, build the edge
**Decided:** for a real deployment I'd buy the conversational/contact-center platform and build the **governance, routing, and eval layers** where the domain advantage lives.
**Rejected:** building the whole stack to prove I can.
**Why:** the leadership call is resource judgment, not maximal construction. The orchestration and gate are here in full because they're the parts worth owning; the surrounding platform is a buy. Reasoning about that line honestly is more valuable than a from-scratch everything. → [ADR-0007](./decisions/0007-build-vs-buy.md)

---

## How I'd staff and operate it

A reference design that ignores the org is an architect's document, so:

- **Team shape:** 4–6 engineers. One owns the eval harness and golden-case curation as a standing responsibility — evals are not a side task, they're the safety system.
- **On-call for the agent itself:** the agent is a production service with its own failure modes (a provider outage, a routing regression, a guardrail false-positive). It gets a runbook and a rotation, same as any service.
- **The feedback loop:** every human escalation is a labeled example of something the agent didn't know. Those flow back into the golden set, so the system gets narrower-but-better over time instead of broader-and-shakier.
- **The metric review:** the balanced scorecard from Decision 1 gets read every week. If automation rate climbs while CSAT slips, that's a regression even though every dashboard is green.

---

## What I'd measure

| Axis | Metric | Why it's on the board pack |
|------|--------|----------------------------|
| Efficiency | Automation rate, cost per resolution, handle time | Unit economics that have to survive scale |
| Experience | CSAT, first-contact resolution, escalation-with-context rate | The half of the scorecard deflection targets quietly destroy |
| Risk | Forbidden-action attempts caught, approval latency, audit completeness | Whether you can deploy into higher-value workflows at all |

---

## Architecture (the evidence, briefly)

- **Orchestration:** LangGraph, supervisor + bounded sub-agents per issue category (order status / returns / billing).
- **Routing:** cascaded multi-provider — cheap model for intent and easy turns, escalation to a stronger model on hard ones.
- **Verdict gate:** `AUTO` / `REQUIRE_APPROVAL` / `FORBIDDEN` on every consequential action.
- **Evaluation:** CI harness with golden cases and safety invariants gating every deploy.
- **Observability & audit:** structured logging of every decision, tool call, and approval.

Full walkthrough in [`/docs/architecture.md`](./docs/architecture.md). It's linked, not led with, on purpose.

---

## Repository map

```
.
├── README.md                     ← you are here (the decisions)
├── decisions/                    ← ADRs, one per decision above
│   ├── 0001-balanced-scorecard.md
│   ├── 0002-bounded-autonomy.md
│   ├── 0003-cost-routing.md
│   ├── 0004-escalation-context.md
│   ├── 0005-evaluation-gate.md
│   ├── 0006-governance-audit.md
│   └── 0007-build-vs-buy.md
├── artifacts/
│   └── sample-audit-report.md    ← the compliance deliverable
├── docs/
│   └── architecture.md           ← the wiring, as evidence
├── src/                          ← reference implementation (runs, no API keys)
│   ├── actions.py                ← action model + risk-policy registry
│   ├── verdict_gate.py           ← AUTO / REQUIRE_APPROVAL / FORBIDDEN
│   └── router.py                 ← cascaded cheap→strong routing + failover
├── evals/                        ← the eval gate from ADR-0005
│   ├── safety_invariants.py      ← deterministic must-never-happen checks
│   ├── golden_cases.json         ← seed golden set
│   └── golden_runner.py          ← runs the gate; exit 1 on regression
├── tests/                        ← pytest (33 tests)
└── .github/workflows/ci.yml      ← runs the tests + eval gate on every push
```

## Running the reference slice

The differentiated layer — the verdict gate, the router, the eval harness — is
real, runnable code with no third-party dependencies and no API keys. A confident,
high-blast action is gated exactly like an unsure one, and there's a test that
fails if anyone ever wires model confidence into the verdict.

```bash
pip install -e ".[dev]"
make test   # 33 unit tests
make eval   # the golden-case eval gate (exits non-zero on regression)
```

The same eval gate runs in CI on every push, which is what makes "nothing reaches
a customer without passing the gate" ([ADR-0005](./decisions/0005-evaluation-gate.md))
true in this repo rather than just asserted. The orchestration around these
components (the LangGraph supervisor and sub-agents) is deliberately out of scope —
this is the layer that carries the risk, per [ADR-0007](./decisions/0007-build-vs-buy.md).

---

*Reference design and write-up by Praveen Kumar. The judgment is drawn from production experience building LLM platforms and agentic systems; the support-agent figures are design targets, not shipped results.*
