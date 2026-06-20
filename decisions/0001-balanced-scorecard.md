# ADR-0001: Measure experience and economics together, never deflection alone

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Support Operations, Finance |
| **Supersedes** | — |
| **Tags** | metrics, incentives, customer-experience, unit-economics |

---

## Context

The first artifact a support-agent project produces is usually a dashboard, and the first number on that dashboard is usually **deflection rate** — how many contacts the agent handled without a human. It's easy to instrument, it goes up and to the right, and it makes a clean slide.

It's also the wrong number to lead with, and choosing it is a decision even when nobody realizes they're making one.

The metric you choose is the behavior you get. A deflection-only target trains two things to avoid customers: the system *and* the team building it. The agent learns that ending the conversation is the goal, so it gets terse, it dodges, it closes tickets that aren't resolved. The team learns that the way to win is to push the number up, so edge cases get routed away rather than handled. Deflection climbs. CSAT slips. Customers who didn't get helped go quiet — and a quiet customer isn't a solved customer, they're a churning one. By the time churn shows up in a different report three months later, nobody connects it back to the agent that was "performing well."

This is a Goodhart problem dressed as a success metric: the moment deflection becomes the target, it stops measuring resolution and starts measuring avoidance.

I'm treating the scorecard as the first decision in the build, before a line of agent code, because it's load-bearing — every downstream tradeoff (autonomy boundaries, model spend, escalation design) gets judged against it. Get this wrong and you optimize a year of work toward the wrong outcome.

## Decision

Adopt a **balanced scorecard** across three axes, and refuse to ship a single hero number. Each axis carries primary metrics and explicit guardrails, so you cannot win one by quietly destroying another.

**1. Efficiency — are we actually saving money?**
- Automation rate (contacts resolved with no human touch)
- **Cost per resolution** (blended model + infra + human-assist cost ÷ resolved contacts) — the number that belongs in the board pack
- Average handle time

**2. Experience — are customers actually helped?**
- CSAT, measured post-interaction
- First-contact resolution (FCR)
- Escalation-with-context rate (share of handoffs where the human inherited the full thread, not a cold start)

**3. Business outcome — did it move the things the company cares about?**
- Reopen / repeat-contact rate on the same issue (a deflected contact that comes back is a false win, not a saved one)
- Retention of customers who contacted support
- CLV impact, where it can be attributed

**The guardrail rule:** automation rate is never reported without CSAT and reopen rate beside it. If automation climbs while either guardrail degrades, that is a **regression**, even when every efficiency dashboard is green.

## Alternatives considered

**Deflection rate as the primary KPI.** Rejected. Cheapest to instrument, most expensive to live with. It optimizes for getting rid of customers and hides the cost in a metric that surfaces too late to act on. This is the default we are explicitly walking away from.

**CSAT-only / experience-first.** Rejected as a sole target. Protects the customer but gives Finance nothing, and an agent with no economic constraint will happily escalate everything to a human and post a perfect CSAT while saving zero dollars. The point is the *tension* between the axes, not picking the nicer one.

**A single blended "quality score."** Rejected. Collapsing the axes into one composite hides exactly the tradeoff a leader needs to see. The value is in watching efficiency and experience move *against* each other and deciding what to do about it — a blended score launders that signal away.

## Consequences

**What this buys us**
- The agent can't win by avoiding customers; the guardrails make that strategy show up immediately as a regression.
- Finance, Support, and Engineering are reading the same scorecard, so "the agent is doing great" and "support quality dropped" can't be true at the same time in different rooms.
- Every later decision in this design has a clear test to be judged against.

**What it costs us**
- No clean single number for a slide. Reporting is three axes with guardrails, which is more honest and less tidy. I'll take that trade.
- CSAT and reopen-rate instrumentation has to exist *before* launch, not after. That's real up-front work, and it's the work most projects skip — which is why most projects can't tell helped-and-left from gave-up-and-left.
- It will sometimes show the agent making a category of customer *worse* even while saving money. That's not a flaw in the scorecard; that's the scorecard doing its job and handing me a decision.

**Risks and how we hold them**
- *Guardrails get ignored under pressure to show automation gains.* Mitigation: the weekly metric review (below) reads all three axes together, and a guardrail breach is a standing agenda item, not a footnote.
- *CSAT response rates are low and noisy.* Mitigation: pair survey CSAT with behavioral proxies — reopen rate and repeat-contact rate need no survey and are hard to game.

## How we operate it

- **Weekly scorecard review**, all three axes in one view, attended by Engineering, Support Ops, and Finance. A green efficiency board with a red experience guardrail is a failing week, full stop.
- **Ownership:** Engineering owns automation rate and cost per resolution; Support Ops owns CSAT and FCR; the reopen/retention line is shared, because it's the one that catches false wins.
- **Feedback into the system:** every escalation and every reopen is a labeled example of something the agent got wrong, fed back into the evaluation golden set (see ADR-0005). The scorecard isn't just reporting — it's the input that makes the agent narrower and better over time.

---

**In one line, if I had to defend it to a board:** *Deflection measures how many customers we got rid of. I'd rather measure how many we actually helped — and watch what that costs — because the first number looks great right up until it shows up as churn.*
