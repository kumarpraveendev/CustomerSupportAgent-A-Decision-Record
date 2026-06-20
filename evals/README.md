# evals — evaluation harness

The gate from [ADR-0005](../decisions/0005-evaluation-gate.md), built and running.
Nothing ships past it.

| File | What it is |
|------|------------|
| [`safety_invariants.py`](safety_invariants.py) | Deterministic, rule-based invariants: no unauthorized refund promise, no invented policy, no third-party data exposure, no action exceeding its verdict |
| [`golden_cases.json`](golden_cases.json) | A representative seed set of cases (verdict, routing, invariant). In production this set is fed by escalations and reopens |
| [`golden_runner.py`](golden_runner.py) | Runs every case against the real components and exits non-zero on any regression — so it works as a CI gate |

The safety invariants are deliberately deterministic, not model-judged: *"the
judge model thought it was fine"* is not the assurance I want on whether the agent
gave away money. An LLM-as-judge belongs above this line, for tone and nuance —
not on the checks that must never fail.

```bash
python -m evals.golden_runner   # prints a PASS/FAIL report, exit 1 on regression
```

This same command runs in CI on every push (see `.github/workflows/ci.yml`), which
is what makes "nothing reaches a customer without passing the gate" literally true
in this repo rather than just asserted.
