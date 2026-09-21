"""Validation tests for the Phase 1 business understanding documentation."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PHASE_1_DIR = PROJECT_ROOT / "docs" / "phase-1"

PHASE_1_FILES = (
    "analytical-questions.md",
    "business-problem.md",
    "business-requirements.md",
    "decision-log.md",
    "hypothesis-register.md",
    "kpi-definitions.md",
    "phase-1-checklist.md",
    "requirements-traceability.md",
    "scope-and-assumptions.md",
    "stakeholder-analysis.md",
)


def test_phase_1_required_documents_exist_and_are_non_empty():
    """Every Phase 1 planning document must exist and contain content."""
    missing_or_empty = [
        path
        for path in PHASE_1_FILES
        if not (PHASE_1_DIR / path).is_file()
        or not (PHASE_1_DIR / path).read_text(encoding="utf-8").strip()
    ]
    assert not missing_or_empty, f"Missing or empty Phase 1 documents: {missing_or_empty}"


def test_phase_1_business_problem_contains_scope_boundary():
    """The business problem must separate decision support from unsupported claims."""
    text = (PHASE_1_DIR / "business-problem.md").read_text(encoding="utf-8")
    required_phrases = (
        "forecast future product",
        "Forecasts are decision-support inputs",
        "Dataset-specific facts",
        "inventory-planning insights",
        "does not claim that forecasts automatically optimize inventory",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing business-problem safeguards: {missing}"


def test_phase_1_decisions_preserve_temporal_and_evidence_constraints():
    """Key planning decisions must prevent premature model and causal claims."""
    text = (PHASE_1_DIR / "decision-log.md").read_text(encoding="utf-8")
    required_phrases = (
        "Implement ARIMA as a mandatory forecasting model.",
        "RESOLVED",
        "Define the forecast horizon after the dataset is inspected.",
        "Do not claim promotion or holiday effects as causal effects",
        "Select the final forecasting model through evaluation rather than in advance.",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing planning safeguards: {missing}"


def test_phase_1_requirements_cover_internship_forecasting_scope():
    """Business requirements must retain the required forecasting scope and metrics."""
    text = (PHASE_1_DIR / "business-requirements.md").read_text(encoding="utf-8")
    required_phrases = (
        "BR-001 — Historical demand",
        "BR-006 — ARIMA",
        "BR-007 — Additional forecasting approach",
        "BR-008 — Forecast evaluation",
        "BR-014 — Reproducibility",
        "BR-015 — Documentation",
        "NFR-007 Time-series integrity",
        "NFR-008 Leakage prevention",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing Phase 1 requirements: {missing}"


def test_phase_1_kpis_define_zero_safe_mape():
    """MAPE must document its zero-demand limitation before results are reported."""
    text = (PHASE_1_DIR / "kpi-definitions.md").read_text(encoding="utf-8")
    required_phrases = (
        "RMSE",
        "MAPE",
        "MAPE behaves poorly when actual demand is zero or very close to zero.",
        "excludes zero-actual observations from MAPE",
        "Forecast bias",
        "Demand volatility",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing KPI safeguards: {missing}"
