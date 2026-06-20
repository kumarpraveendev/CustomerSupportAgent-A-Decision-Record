# ADR-0007: Buy the platform, build the edge

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06 |
| **Owner** | Praveen Kumar (Head of Engineering, this design) |
| **Deciders** | Engineering, Finance, Product |
| **Supersedes** | — |
| **Tags** | build-vs-buy, strategy, resource-allocation, vendor |

---

## Context

The reflex in a portfolio project — and in a lot of real teams — is to build everything, because building everything proves you can. That's an IC instinct. The leadership instinct is the opposite: decide what *not* to build, because engineering time is the scarcest thing you have and pointing it at undifferentiated work is the most common way teams lose a year.

For a customer-support agent, the build-vs-buy line is not "do we use a vendor or not." It's "which layer is actually ours." Channels, ticketing, telephony, the agent desktop, CRM integration — these are solved, and solved better, by vendors whose whole business is solving them. The differentiated, risk-bearing layer is narrower than it looks.

## Decision

**Buy the conversational/contact-center platform. Build the governance, routing, and evaluation layers.**

- **Buy:** channels and telephony, ticketing, the human agent desktop, CRM/system-of-record integration. Undifferentiated heavy lifting where a vendor's version beats anything we'd build in year one.
- **Build:** the orchestration and the **verdict gate** (ADR-0002), the **cost routing** (ADR-0003), and the **eval harness** (ADR-0005). These encode *this company's* specific risk appetite, economics, and quality bar. They are the layer that carries the risk and the differentiation, so they're the layer we own.

The orchestration and gate are present in full in this repo precisely because they're the parts worth owning. Everything around them is a buy.

## Alternatives considered

**Build everything.** Rejected. Reinventing telephony, channel management, and CRM integration — work vendors do better — while the genuinely hard, differentiated work waits. Maximal construction, minimal leverage. Impressive-looking, strategically poor.

**Buy everything, including the agent platform (Sierra / Decagon / Kore and similar) end-to-end.** Rejected *as the default*. For a generic FAQ deflection bot it's the right call. But here it means outsourcing the exact layer — autonomy policy, eval, audit — that is our risk surface *and* our differentiation. When the agent's actions carry money and compliance weight, I'm not comfortable renting the part that decides how much money it can move. Fine for the channels; not fine for the risk policy.

**Buy the platform, build a thin glue layer.** This is the decision. The "glue" is the part that matters — it just isn't the part that's large.

## Consequences

**What this buys us**
- Faster to production: the vendor handles the parts that would otherwise eat the first two quarters.
- Effort concentrates on the owned edge — the layer where domain advantage and risk both live.
- A defensible, explainable allocation of engineering time, which is itself the thing a board wants to see from this role.

**What it costs us**
- Integration surface and some vendor dependency. In particular, we now depend on the platform's escalation and context-passing APIs — which directly constrains ADR-0004, so the platform's handoff quality is a real evaluation criterion, not a footnote.
- The buy/build line is not static. The platform vendors are absorbing more of the agent layer every quarter, and the boundary has to be revisited as they do.

**Risks and how we hold them**
- *Vendor lock-in creeps into the owned layer.* Mitigation: keep the policy, routing, and eval layers **portable** — they don't get welded to one vendor's proprietary agent runtime. We can change platforms without rewriting our risk policy.
- *The platform's limitations quietly cap the experience (e.g. a poor handoff surface).* Mitigation: handoff and context APIs are part of vendor selection, judged against ADR-0004, before we commit.

## How we operate it

- The build/buy boundary is revisited quarterly — this market moves fast enough that last quarter's right answer expires.
- The differentiated layer stays portable by policy, so vendor choice remains a decision we can re-make, not a trap we're in.

---

**In one line, if I had to defend it to a board:** *I'd own the layer that carries the risk and buy the layer that carries the channels. Building everything proves you can code. Deciding what not to build is the part that proves you can lead.*
