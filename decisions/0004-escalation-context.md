# ADR-0004: The handoff carries the full context, always

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Support Operations |
| **Supersedes** | — |
| **Tags** | customer-experience, escalation, handoff |

---

## Context

Every agent escalates eventually — because it hit a `REQUIRE_APPROVAL` verdict (ADR-0002), because the problem is genuinely beyond it, or because the customer simply asked for a person. The handoff is therefore not an edge case; it's a core, recurring moment, and it's the one that decides whether the customer remembers the agent as helpful or as a wall they had to get past.

The common failure is a "transfer to agent" that drops a human into a cold thread. The customer re-explains everything they just told the bot. From their seat, the automation didn't save them time — it added a step. At that point the agent is a tax on the support team, not a multiplier, and the experience half of the scorecard (ADR-0001) is paying for it.

No amount of model quality fixes a broken handoff. So the handoff gets designed, not left as an afterthought.

## Decision

When the agent escalates, the human inherits **everything**: the full conversation, the customer's relevant history, and the agent's own reasoning — what it tried, what it concluded, and *why* it escalated. The human surface leads with a short structured summary (who, what, what's been attempted, what's blocked) and keeps the complete thread one click away.

Escalation is built as a feature of the experience, not a dumping of a failed session.

## Alternatives considered

**Cold "transfer to a human."** Rejected. Cheapest to build, worst to receive. Makes the customer repeat themselves and turns automation into friction.

**Summary-only handoff.** Rejected as the sole mechanism. A summary alone is lossy; the human ends up digging for the detail the summary dropped, usually the detail that matters. Summary *plus* full thread, not summary *instead of*.

**Force self-service / no human path.** Rejected. Trapping a customer who's asked for a person is how you manufacture a one-star review and a churn event in the same interaction.

## Consequences

**What this buys us**
- The customer doesn't start over; the human is faster because they walk in already informed.
- Escalation stops being a quality cliff and becomes a smooth gear-change, which protects CSAT and FCR.
- The escalation-with-context rate becomes a metric we can actually move (ADR-0001).

**What it costs us**
- We build the context-packaging layer and integrate it into the human agent's desktop. The handoff has a real surface to design and maintain.
- We depend on the channel/platform's handoff capabilities — which is one input into the build-vs-buy line in ADR-0007.

**Risks and how we hold them**
- *Context overload — we dump so much the human can't find the signal.* Mitigation: structured summary first, full thread available but not in their face. The summary is the product; the thread is the backup.
- *The context carries PII into another system/seat.* Mitigation: governed by ADR-0006 — what's passed, where it's stored, and how long it's retained is a policy, not an accident.

## How we operate it

- Escalation-with-context rate sits on the scorecard, and human agents give structured feedback on handoff quality — they're the ones who feel a bad one.
- Every escalation is also a labeled gap for the eval golden set (ADR-0005): the agent escalated because it didn't know something, and that something is now a test case.

---

**In one line, if I had to defend it to a board:** *A handoff that makes the customer start over is worse than no automation at all — it added a step and burned goodwill. So when the agent gives up, the human walks in already knowing the whole story.*
