# ADR-0002: Bounded autonomy — the agent's risk line is set by blast radius, not by its own confidence

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Support Operations, Legal/Risk |
| **Supersedes** | — |
| **Tags** | autonomy, guardrails, risk, human-in-the-loop |

---

## Context

This agent doesn't just answer questions — it takes actions. It can issue a refund, accept a return, change an address, apply a credit. The moment an agent can *act*, the question stops being "is the answer good?" and becomes "what is it allowed to do on its own?"

The tempting answer is a confidence threshold: if the model is sure enough, let it act. That's the wrong primitive, and it's a subtle trap. **Confidence is not risk.** A model can be equally, genuinely certain that it should issue a $5 store credit and that it should process a $500 refund to a card. The certainty is the same; the blast radius is not. Tie autonomy to confidence and you've handed the most consequential decisions to the component least equipped to weigh consequences.

This decision comes early because it's a policy decision, not a technical one — and policy belongs to a human.

## Decision

Every consequential action passes through a **three-state verdict gate**, and the state is assigned by *policy*, by blast radius and reversibility, not by the model:

- **`AUTO`** — cheap, reversible, low-blast-radius. The agent does it unattended. (Look up order status, send a tracking link, apply a small reversible credit within policy.)
- **`REQUIRE_APPROVAL`** — consequential or hard to reverse. The agent prepares the action with full context, but a human's name goes on the execution. (Refunds above a threshold, account changes, anything touching payment instruments.)
- **`FORBIDDEN`** — never, regardless of how confident the model is. (Actions outside the agent's mandate entirely — e.g. closing an account, overriding fraud holds.)

The classification lives in a policy the team owns and can read, audit, and change. The model proposes; the gate disposes.

## Alternatives considered

**Confidence-threshold autonomy.** Rejected. Conflates certainty with safety. The failure mode is a confident, high-blast-radius mistake — exactly the one you can't afford.

**Human-in-the-loop on everything.** Rejected. Safe, but it deletes the economics from ADR-0003 and the experience from ADR-0001 — you've built a very expensive way to make customers wait. Automation has to mean *something* runs unattended.

**Full autonomy with post-hoc review.** Rejected. Works only if every action is reversible. It isn't. Some actions you cannot un-take, and "we caught it in the weekly review" is not a refund the customer didn't already spend.

## Consequences

**What this buys us**
- The expensive mistakes can't happen unattended, by construction — not by hoping the model stays calibrated.
- The cheap, reversible majority still runs free, so automation rate (ADR-0001) stays real.
- The line is explicit and auditable, so "why did the agent do that" always has an answer (ADR-0006).

**What it costs us**
- Someone maintains the action-classification policy. It's a living document, not a one-time config.
- `REQUIRE_APPROVAL` adds latency to a slice of actions, and a queue that has to be staffed and have an SLA.

**Risks and how we hold them**
- *Misclassification — a high-blast action slips into `AUTO`.* Mitigation: default new action types to `REQUIRE_APPROVAL`; an action earns `AUTO` only after review, never by default.
- *Approval queue becomes a bottleneck and people rubber-stamp.* Mitigation: an approval SLA on the scorecard, and approvals presented as a challenge-response (what, how much, to whom, reversible?) rather than a single "Approve?" button, so the human is actually deciding.

## How we operate it

- The classification policy is owned jointly by Engineering, Support Ops, and Legal/Risk, and reviewed on a cadence — not frozen at launch.
- New action types ship as `REQUIRE_APPROVAL` and graduate to `AUTO` only with evidence.
- Every gate decision is logged with the verdict and the reason, feeding the audit trail in ADR-0006.

---

**In one line, if I had to defend it to a board:** *I don't let the model's confidence decide how much money it can move. A $5 credit and a $500 refund are different risk decisions even when the model is equally sure — so the line is drawn by what the action can break, not by how certain the agent feels.*
