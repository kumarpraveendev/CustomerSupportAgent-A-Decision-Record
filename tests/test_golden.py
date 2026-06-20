"""Pytest also runs the full golden suite, so `pytest` alone covers the eval gate."""
from evals.golden_runner import load_cases, run_all


def test_golden_suite_has_no_regressions():
    results = run_all(load_cases())
    failures = [r for r in results if not r.passed]
    assert not failures, "golden regressions: " + "; ".join(
        f"{r.name} ({r.detail})" for r in failures
    )


def test_golden_suite_is_non_trivial():
    # Guard against an empty/degenerate suite silently "passing".
    assert len(load_cases()) >= 10
