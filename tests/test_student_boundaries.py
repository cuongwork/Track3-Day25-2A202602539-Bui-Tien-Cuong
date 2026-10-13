"""Additional student tests; the supplied tests are unchanged."""

from gameday_lab.slo.alerting import error_budget_report


def test_exactly_exhausted_budget_freezes_releases() -> None:
    exhausted = error_budget_report([100000], [500], slo=0.995)
    assert exhausted["budget_remaining"] == 0.0
    assert exhausted["freeze_releases"] is True
    assert error_budget_report([100000], [499], slo=0.995)["freeze_releases"] is False
