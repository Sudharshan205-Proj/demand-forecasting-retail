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
        "forecast future product demand",
        "inventory-planning insights",
        "No dataset-specific claims are made",
        "will not claim that forecasts automatically optimize inventory",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing business-problem safeguards: {missing}"


def test_phase_1_decisions_preserve_temporal_and_evidence_constraints():
    """Key planning decisions must prevent premature model and causal claims."""
    text = (PHASE_1_DIR / "decision-log.md").read_text(encoding="utf-8")
    required_phrases = (
        "ARIMA is mandatory.",
        "RESOLVED",
        "Do not define the final forecast horizon until the dataset is inspected.",
        "Do not claim promotion or holiday effects as causal effects",
        "Do not select the final forecasting model before evaluation.",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing planning safeguards: {missing}"


def test_phase_1_requirements_cover_internship_forecasting_scope():
    """Business requirements must retain the required forecasting scope and metrics."""
    text = (PHASE_1_DIR / "business-requirements.md").read_text(encoding="utf-8")
    required_phrases = (
        "BR-001 — Historical Demand",
        "BR-006 — ARIMA",
        "BR-007 — Additional Forecasting Approach",
        "BR-008 — Forecast Evaluation",
        "BR-014 — Reproducibility",
        "BR-015 — Documentation",
        "Time-Series Integrity",
        "Leakage Prevention",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing Phase 1 requirements: {missing}"


def test_phase_1_kpis_define_zero_safe_mape():
    """MAPE must document its zero-demand limitation before results are reported."""
    text = (PHASE_1_DIR / "kpi-definitions.md").read_text(encoding="utf-8")
    required_phrases = (
        "RMSE",
        "MAPE",
        "MAPE can behave poorly when actual demand is zero or very close to zero.",
        "zero-demand observations are handled",
        "Forecast Bias",
        "Demand Volatility",
    )
    missing = [phrase for phrase in required_phrases if phrase not in text]
    assert not missing, f"Missing KPI safeguards: {missing}"
