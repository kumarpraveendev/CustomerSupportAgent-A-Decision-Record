# ADR-0006: Governance is a deliverable, not paperwork

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Legal/Risk, Support Operations |
| **Supersedes** | — |
| **Tags** | governance, audit, compliance, eu-ai-act, privacy |

---

## Context

In a consumer FAQ bot, governance feels like overhead. In an agent that moves money and touches customer accounts in a regulated market, it's the thing that decides whether you're *allowed* to deploy into the valuable workflows at all. An auditable trail isn't a tax on the system — it's the permission slip for putting the agent on higher-stakes problems with the business's confidence behind it.

The mistake is treating compliance as a pre-launch checklist: build the agent, then bolt on logging and a policy review the week before go-live. Retrofitting an audit trail into a system that wasn't instrumented for it is painful, incomplete, and exactly the kind of gap an auditor finds. Governance designed in from the start is an enabler; governance bolted on at the end is a blocker wearing a deadline.

I've built the GDPR-aware version of this before (an audit logger for a regulated voice agent) and mapped EU AI Act risk classification for an AI hiring tool, so this is drawn from that, not theory.

## Decision

**Structured audit logging from day one, and a compliance/audit report as a first-class output of the system.**

- Every consequential decision, action, approval (ADR-0002), and the reasoning behind it is logged in a structured, queryable form — enough to *reconstruct* any single interaction after the fact.
- A compliance/audit artifact is generated as an actual deliverable (see [`/artifacts/sample-audit-report.md`](../artifacts/sample-audit-report.md)), not assembled by hand in a fire drill when someone asks.
- **EU AI Act posture is decided up front.** A general support agent typically carries transparency-type obligations (the customer should know they're talking to AI). But the moment the agent's actions touch something like access to essential services or creditworthiness-adjacent decisions, the risk tier rises — so the design assumes the stricter case and degrades gracefully to the lighter one, rather than the reverse.

## Alternatives considered

**Application logs only.** Rejected. Good for debugging, useless for audit — you can't reconstruct *why* the agent decided what it did from a stack of `INFO` lines.

**Bolt compliance on before launch.** Rejected. Too late to instrument cleanly, and the gaps are precisely the high-risk paths. Audit trails are a property you design for, not a feature you append.

**Full manual compliance review of interactions.** Rejected as the mechanism. Doesn't scale past a pilot, and humans reviewing transcripts by hand is neither complete nor repeatable. Structured logging makes review *possible*; it doesn't replace human judgment, it equips it.

## Consequences

**What this buys us**
- Any agent decision is reconstructable, which is what lets us deploy into regulated, higher-value workflows with board confidence rather than crossed fingers.
- When something goes wrong, the trail explains it — incident response (and the eval golden set in ADR-0005) start from facts, not guesses.
- Governance becomes a *selling point* of the system, especially in enterprise and regulated verticals, rather than a cost center.

**What it costs us**
- Logging overhead, storage, and a schema to maintain. Real, but cheap relative to the workflows it unlocks.
- PII handling becomes a first-order concern — the audit trail is, by design, full of customer data.

**Risks and how we hold them**
- *The audit trail itself becomes a privacy liability.* Mitigation: redaction and retention policy designed in — log what's needed to reconstruct a decision, minimize and time-bound the rest.
- *Audit theater — we log everything and no one ever reads it.* Mitigation: the trail is wired into the weekly review and the incident process, so it's load-bearing, not decorative.

## How we operate it

- The audit report is generated on a cadence and on demand, not reconstructed manually under pressure.
- Redaction and retention are policy, owned jointly with Legal/Risk and reviewed as regulation evolves.
- The trail is the first thing consulted in any incident — it's the system's memory of what it decided and why.

---

**In one line, if I had to defend it to a board:** *Governance done early is what lets you put the agent on the problems worth solving. Done late, it's the thing that stops you the week before launch.*
