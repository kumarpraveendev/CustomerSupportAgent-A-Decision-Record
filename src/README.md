# src — reference implementation

The differentiated layer from the decision record, built as real, runnable code
([ADR-0007](../decisions/0007-build-vs-buy.md) is the argument for owning exactly
this much and buying the rest). Pure standard library — no API keys, no network.

| File | What it is | Decision |
|------|------------|----------|
| [`actions.py`](actions.py) | Action model + the risk-policy registry (blast radius and reversibility, keyed on action type) | [ADR-0002](../decisions/0002-bounded-autonomy.md) |
| [`verdict_gate.py`](verdict_gate.py) | `classify()` → `AUTO` / `REQUIRE_APPROVAL` / `FORBIDDEN`. Model confidence is deliberately never an input | [ADR-0002](../decisions/0002-bounded-autonomy.md) |
| [`router.py`](router.py) | Cascaded cheap→strong routing; escalates up when unsure; multi-provider failover that degrades rather than halts | [ADR-0003](../decisions/0003-cost-routing.md) |

The single most load-bearing line in the whole repo is in `verdict_gate.classify`:
`action.model_confidence` is recorded for the audit trail and never read by the
classifier. That's the entire point of ADR-0002 expressed as code — and there's a
test that fails if anyone wires confidence into the verdict.

```bash
pip install -e ".[dev]"   # from the repo root
make test                 # 33 unit tests
make eval                 # the golden-case eval gate
```

A full deployment would wrap these in the LangGraph supervisor and sub-agents
described in [`docs/architecture.md`](../docs/architecture.md); that orchestration
layer is intentionally out of scope here so the repo stays focused on the parts
that carry the risk and the judgment.
