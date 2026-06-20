# ADR-0005: Nothing reaches a customer without passing an eval gate

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Support Operations |
| **Supersedes** | — |
| **Tags** | evaluation, safety, ci-cd, quality |

---

## Context

A support agent fails in ways a search box never could. It can promise a refund the business won't honor. It can confidently invent a return policy that doesn't exist. It can, on a bad day, surface another customer's information. These aren't bugs you find in production and patch next sprint — they're releases that should never have shipped, because the cost lands on a real customer and on the company's word.

The discipline that separates a demo from something I'd put in front of customers is evaluation: knowing, before deploy, that the change doesn't break the things that must not break. I've built this before — a CI evaluation harness for an agentic system — and it's the single highest-leverage piece of process in the whole design.

## Decision

A **CI evaluation harness gates every deploy.** Two layers:

- **Safety invariants** — hard, deterministic pass/fail checks on the things that must never happen: don't promise an unauthorized refund, don't invent policy, don't reveal another customer's data, don't exceed the autonomy verdict from ADR-0002. A failure here blocks the deploy. No exceptions, no override-for-this-one-release.
- **Golden cases** — a curated set of representative and historically-hard scenarios with expected outcomes. Regression against the golden set blocks merge.

LLM-as-judge is used for the graded, qualitative cases, but the safety-critical invariants are deterministic, because "the judge model thought it was fine" is not the assurance I want on whether the agent gave away money.

## Alternatives considered

**Ship and watch — quality assessed in production.** Rejected. Acceptable for low-stakes UI; unacceptable when the failure modes move money and customer trust. Some mistakes you don't get to make even once.

**Manual QA before each release.** Rejected as the gate. Doesn't scale, isn't repeatable, and depends on whoever's testing remembering the nasty edge case from three months ago. A gate has to be automatic and consistent, or it isn't a gate.

**LLM-as-judge for everything, including safety.** Rejected for the safety layer. Useful for nuance and tone; not trustworthy as the sole arbiter of "did the agent just do something forbidden." Anchor the critical checks on deterministic rules; use the judge above that line.

## Consequences

**What this buys us**
- The unacceptable failures can't reach a customer through the front door — they're blocked at merge.
- The golden set is a compounding asset: every escalation and reopen (ADR-0001) becomes a new case, so the agent gets *narrower and better*, not broader and shakier.
- "How do you know it's safe to ship?" has a concrete, demonstrable answer.

**What it costs us**
- Building and maintaining the harness and the golden set is real, ongoing work — it's why the team (see README staffing) has someone who *owns* evals as a standing responsibility, not a side task.
- Slower merges. A change that breaks an invariant doesn't ship today. That's the point.

**Risks and how we hold them**
- *The golden set goes stale or has coverage gaps.* Mitigation: it's continuously fed from production escalations and reopens, so coverage tracks the failures the agent actually produces.
- *Flaky LLM-judge results cause false blocks/passes.* Mitigation: keep the safety-critical layer deterministic; reserve the judge for graded quality where some noise is tolerable.

## How we operate it

- One person owns the harness and golden-case curation. Evals are the safety system, and the safety system has an owner.
- Every escalation and reopen is a candidate golden case; curation is a weekly habit, not a launch task.
- Deploys are blocked on any safety-invariant failure or golden-set regression — automatically, in CI, before merge.

---

**In one line, if I had to defend it to a board:** *I won't let a support agent reach a customer without a gate that proves it won't promise something the business can't deliver. Eval discipline is the line between a demo and a system I'd stake my name on.*
