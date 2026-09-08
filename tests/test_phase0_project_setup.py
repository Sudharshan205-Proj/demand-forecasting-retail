"""Validation tests for the Phase 0 project setup and curriculum audit."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PHASE_0_FILES = (
    "README.md",
    ".gitignore",
    "requirements.txt",
    "pyproject.toml",
    "docs/phase-0/project-requirements.md",
    "docs/phase-0/project-plan.md",
    "docs/phase-0/curriculum-mapping.md",
    "docs/phase-0/architecture.md",
    "docs/phase-0/environment.md",
    "docs/phase-0/data-strategy.md",
    "docs/phase-0/reproducibility.md",
    "docs/phase-0/security.md",
    "docs/phase-0/project-state.md",
)

DATA_DIRECTORY_KEEPS = (
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "data/interim/.gitkeep",
    "data/external/.gitkeep",
)

PHASE_0_PYTHON_PACKAGES = (
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "scikit-learn",
    "statsmodels",
    "openpyxl",
    "jupyter",
    "pytest",
)


def test_phase_0_required_files_exist():
    """All files established by Phase 0 must remain available."""
    missing = [
        path for path in PHASE_0_FILES if not (PROJECT_ROOT / path).is_file()
    ]
    assert not missing, f"Missing Phase 0 files: {missing}"


def test_data_directory_placeholders_exist():
    """Raw and derived-data directories must have tracked placeholders."""
    missing = [
        path for path in DATA_DIRECTORY_KEEPS if not (PROJECT_ROOT / path).is_file()
    ]
    assert not missing, f"Missing data directory placeholders: {missing}"


def test_gitignore_excludes_secrets_and_keeps_data_structure():
    """Secrets and generated data must stay untracked while placeholders remain tracked."""
    gitignore_text = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    required_patterns = (
        ".env",
        "credentials.json",
        "service-account*.json",
        "*.pem",
        "data/raw/*",
        "!data/raw/.gitkeep",
        "!data/processed/.gitkeep",
        "!data/interim/.gitkeep",
        "!data/external/.gitkeep",
    )

    missing = [
        pattern for pattern in required_patterns if pattern not in gitignore_text
    ]
    assert not missing, f"Missing required .gitignore rules: {missing}"


def test_requirements_include_phase_0_packages():
    """The initial Phase 0 dependency set must remain declared."""
    requirements = (
        PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8")
    declared = {
        line.strip().split("==", 1)[0].split(">=", 1)[0].strip()
        for line in requirements.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    missing = [
        package for package in PHASE_0_PYTHON_PACKAGES if package not in declared
    ]
    assert not missing, f"Missing Phase 0 dependencies: {missing}"


def test_pyproject_configures_pytest():
    """Pytest must collect the repository's test suite and support Python 3.11+."""
    pyproject_text = (
        PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

    required_settings = (
        'testpaths = ["tests"]',
        'python_files = ["test_*.py"]',
        'requires-python = ">=3.11"',
    )
    missing = [
        setting for setting in required_settings if setting not in pyproject_text
    ]
    assert not missing, f"Missing required pyproject settings: {missing}"
