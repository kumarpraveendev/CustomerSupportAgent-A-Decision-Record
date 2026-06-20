# Sample Audit & Compliance Report — Customer-Support Agent

> **This is an illustrative sample with synthetic data.** It demonstrates the output of the governance layer described in [ADR-0006](../decisions/0006-governance-audit.md): a periodic compliance rollup, plus the reconstructable trail for a single interaction. Every name, ID, and figure here is fabricated for demonstration.

The purpose of this artifact is to answer two questions an auditor, a regulator, or a board member will eventually ask:
1. *Across all interactions, is the agent operating inside its policy?* (Part A)
2. *For this specific interaction, what did the agent do, and why?* (Part B)

If the system can't answer both from a structured trail, it isn't ready for a regulated workflow.

---

## Part A — Period compliance summary

**Period:** 2026-06-08 → 2026-06-14 (synthetic)
**Scope:** order status, returns, billing disputes

### Volume & autonomy distribution

| Verdict (per [ADR-0002](../decisions/0002-bounded-autonomy.md)) | Count | Share |
|---|---|---|
| `AUTO` — executed unattended | 18,442 | 82.1% |
| `REQUIRE_APPROVAL` — human-approved | 3,610 | 16.1% |
| `FORBIDDEN` — blocked attempts | 401 | 1.8% |
| **Total consequential actions** | **22,453** | 100% |

- **Forbidden-action attempts caught: 401.** Every one blocked before execution; none reached a customer or a system of record. (Top category: attempts to act on accounts under an active fraud hold — correctly refused.)
- **Approval queue SLA:** median time-to-approval 2m 41s; 96.3% within the 10-minute target.
- **Rubber-stamp check:** 7.4% of `REQUIRE_APPROVAL` items were *modified or rejected* by the human approver — evidence the approval step is a real decision, not a reflex click.

### Experience & economics (scorecard, per [ADR-0001](../decisions/0001-balanced-scorecard.md))

| Axis | Metric | Value | Guardrail status |
|---|---|---|---|
| Efficiency | Automation rate | 82.1% | — |
| Efficiency | Cost per resolution | €0.137 | — |
| Experience | CSAT (post-interaction) | 4.41 / 5 | ✅ above floor |
| Experience | First-contact resolution | 79.8% | ✅ |
| Experience | Escalation-with-context rate | 99.6% | ✅ ([ADR-0004](../decisions/0004-escalation-context.md)) |
| Outcome | Reopen rate (same issue) | 4.2% | ✅ below ceiling |

> **Guardrail note:** automation rate rose 1.9 pts week-over-week. CSAT and reopen rate held. No regression triggered. *(Had CSAT dropped while automation rose, this row would read FAIL regardless of the efficiency gain.)*

### Safety & evaluation (per [ADR-0005](../decisions/0005-evaluation-gate.md))

- Deploys during period: 6. **Eval gate blocks: 2** (1 safety-invariant failure — agent drafted an out-of-policy refund promise; 1 golden-set regression). Neither reached production.
- New golden cases added from escalations/reopens: 38.

### Governance & privacy (per [ADR-0006](../decisions/0006-governance-audit.md))

- **EU AI Act transparency disclosure** ("you are interacting with an AI") shown: 100% of sessions.
- Human-handoff path offered on request: 100% of sessions.
- Audit-trail completeness (interactions fully reconstructable): 100%.
- PII redaction applied to stored logs: 100%; retention policy enforced (transactional logs 90 days, audit records 24 months — synthetic policy values).
- Reportable incidents this period: 0.

---

## Part B — Single interaction audit trail

The granular record. This is what "reconstructable" means in practice — any single interaction can be replayed decision by decision.

**Interaction ID:** `INT-2026-0612-44871` (synthetic)
**Timestamp:** 2026-06-12 14:22:07 CET
**Channel:** Web chat
**Customer:** `CUST-•••••2290` (redacted) · authenticated session
**AI disclosure shown:** ✅ at session open (EU AI Act transparency)
**Detected intent:** Billing dispute — duplicate charge

### Decision & routing log

| Turn | Event | Model (per [ADR-0003](../decisions/0003-cost-routing.md)) | Notes |
|---|---|---|---|
| 1 | Intent classification | cheap/fast | Confidence 0.94 → no escalation |
| 2 | Retrieved last 3 transactions | — (tool call) | Lawful basis: contract performance; data minimised to billing scope |
| 3 | Identified duplicate charge €49.00 | cheap/fast | Two identical charges, same merchant, 4s apart |
| 4 | Reasoning: refund warranted | **escalated to strong model** | Router flagged "financial action — high stakes"; escalated up, per conservative-default rule |
| 5 | Proposed action: refund €49.00 to card | — | → enters verdict gate |

### Verdict gate decision

- **Action:** refund €49.00 to original payment method
- **Classification:** `REQUIRE_APPROVAL` (amount below auto-refund ceiling, but action touches a payment instrument → policy requires a human)
- **Routed to approver:** `OPS-AGENT-118` (synthetic)
- **Approval:** ✅ approved with no modification, 1m 12s after request
- **Approver acknowledged:** amount ✓ · recipient ✓ · reversibility ✓ · duplicate-charge evidence ✓ *(challenge-response, not a single "Approve?" click)*

### Outcome

- Refund executed 14:24:31 CET; confirmation sent to customer.
- **Safety invariants checked at response time:** no unauthorized refund promise ✓ · no invented policy ✓ · no third-party data exposure ✓ · action within verdict ✓ — all passed.
- Customer CSAT: 5/5. Reopened: no.

### Data & retention

- **Data accessed:** customer identity (auth), transaction history (billing scope only).
- **Lawful basis:** contract performance (refund of a duplicate charge).
- **Stored in audit record:** decision log, verdict, approval chain, action result. Card number never logged (tokenised reference only).
- **Retention:** audit record 24 months; transactional log 90 days (synthetic policy).

---

## How to read this report

- **Part A** is the board/auditor-facing rollup: is the agent inside its policy, at what cost, with what experience, and were any unacceptable actions attempted?
- **Part B** is the incident/forensic view: pick any interaction, see exactly what the agent decided and why, who approved what, and on what lawful basis the data was touched.

Together they're the thing that turns "trust me, the agent is well-behaved" into "here is the evidence." That evidence is what makes it possible to put the agent on the workflows that carry real money and real risk — the whole argument of [ADR-0006](../decisions/0006-governance-audit.md).

---

*Sample artifact for a reference design by Praveen Kumar. Synthetic data throughout; retention values and thresholds are illustrative and would be set per deployment and jurisdiction.*
