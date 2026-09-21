"""Tests for the Phase 7 exploratory data analysis module."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

from scripts import exploratory_data_analysis
from scripts.exploratory_data_analysis import (
    CORRELATION_COLUMNS,
    REQUIRED_COLUMNS,
    build_correlation,
    build_eda_summaries,
    create_figures,
    describe_item_demand,
    get_columns,
    pearson_from_accumulators,
    validate_input_columns,
    validate_input_file,
    write_findings,
)


def build_integrated_frame() -> pd.DataFrame:
    """Return a small integrated-dataset fixture."""
    return pd.DataFrame(
        [
            {
                "date": "2024-01-01",
                "item_id": "a",
                "store_id": 1,
                "quantity": 10.0,
                "price_base": 2.0,
                "sum_total": 20.0,
                "dept_name": "DeptA",
                "class_name": "ClassA",
                "subclass_name": "SubA",
                "online_quantity": 1.0,
                "online_sales_value": 2.0,
                "markdown_quantity": 5.0,
                "markdown_record_count": 1,
                "discount_record_count": 1,
                "promo_discount_rate": 0.10,
                "price_change_count": 0,
            },
            {
                "date": "2024-01-15",
                "item_id": "a",
                "store_id": 2,
                "quantity": 20.0,
                "price_base": 2.0,
                "sum_total": 40.0,
                "dept_name": "DeptA",
                "class_name": "ClassA",
                "subclass_name": "SubA",
                "online_quantity": 0.0,
                "online_sales_value": 0.0,
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "discount_record_count": 0,
                "promo_discount_rate": float("nan"),
                "price_change_count": 1,
            },
            {
                "date": "2024-02-01",
                "item_id": "b",
                "store_id": 1,
                "quantity": 30.0,
                "price_base": 3.0,
                "sum_total": 90.0,
                "dept_name": "DeptB",
                "class_name": "ClassB",
                "subclass_name": "SubB",
                "online_quantity": 2.0,
                "online_sales_value": 6.0,
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "discount_record_count": 1,
                "promo_discount_rate": float("inf"),
                "price_change_count": 0,
            },
            {
                "date": "2024-02-10",
                "item_id": "b",
                "store_id": 1,
                "quantity": 40.0,
                "price_base": 3.0,
                "sum_total": 120.0,
                "dept_name": "DeptB",
                "class_name": "ClassB",
                "subclass_name": "SubB",
                "online_quantity": 0.0,
                "online_sales_value": 0.0,
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "discount_record_count": 1,
                "promo_discount_rate": 0.25,
                "price_change_count": 0,
            },
            {
                "date": "2024-02-20",
                "item_id": "c",
                "store_id": 2,
                "quantity": 50.0,
                "price_base": 4.0,
                "sum_total": 200.0,
                "dept_name": None,
                "class_name": None,
                "subclass_name": None,
                "online_quantity": 1.0,
                "online_sales_value": 4.0,
                "markdown_quantity": 15.0,
                "markdown_record_count": 1,
                "discount_record_count": 1,
                "promo_discount_rate": 0.20,
                "price_change_count": 2,
            },
            {
                "date": "2024-03-05",
                "item_id": "c",
                "store_id": 2,
                "quantity": 60.0,
                "price_base": 4.0,
                "sum_total": 240.0,
                "dept_name": "DeptA",
                "class_name": "ClassA",
                "subclass_name": "SubA",
                "online_quantity": 3.0,
                "online_sales_value": 12.0,
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "discount_record_count": 0,
                "promo_discount_rate": float("nan"),
                "price_change_count": 0,
            },
            {
                "date": "2024-03-06",
                "item_id": "a",
                "store_id": 1,
                "quantity": 15.0,
                "price_base": 2.5,
                "sum_total": 37.5,
                "dept_name": "DeptA",
                "class_name": "ClassA",
                "subclass_name": "SubA",
                "online_quantity": 0.0,
                "online_sales_value": 0.0,
                "markdown_quantity": float("nan"),
                "markdown_record_count": 0,
                "discount_record_count": 1,
                "promo_discount_rate": 0.30,
                "price_change_count": 1,
            },
            {
                "date": "2024-03-07",
                "item_id": "d",
                "store_id": 2,
                "quantity": 5.0,
                "price_base": 1.0,
                "sum_total": 5.0,
                "dept_name": "DeptC",
                "class_name": "ClassC",
                "subclass_name": "SubC",
                "online_quantity": 1.0,
                "online_sales_value": 1.0,
                "markdown_quantity": 8.0,
                "markdown_record_count": 1,
                "discount_record_count": 0,
                "promo_discount_rate": float("nan"),
                "price_change_count": 3,
            },
        ]
    )


@pytest.fixture()
def analysis_env(tmp_path, monkeypatch):
    """Point the module at a temporary dataset and output directories."""

    def _configure(
        frame: pd.DataFrame,
        chunk_size: int = 1000,
        file_name: str = "integrated_retail_data.csv",
    ) -> tuple[Path, Path, Path]:
        data_path = tmp_path / file_name

        frame.to_csv(data_path, index=False)

        analysis_dir = tmp_path / "analysis"
        figures_dir = tmp_path / "figures"

        monkeypatch.setattr(
            exploratory_data_analysis,
            "INPUT_PATH",
            data_path,
        )
        monkeypatch.setattr(
            exploratory_data_analysis,
            "ANALYSIS_DIR",
            analysis_dir,
        )
        monkeypatch.setattr(
            exploratory_data_analysis,
            "FIGURES_DIR",
            figures_dir,
        )
        monkeypatch.setattr(
            exploratory_data_analysis,
            "CHUNK_SIZE",
            chunk_size,
        )

        exploratory_data_analysis.initialise_directories()

        return data_path, analysis_dir, figures_dir

    return _configure


def metric_value(summary: pd.DataFrame, name: str) -> object:
    """Return one summary value by metric name."""
    indexed = summary.set_index("metric")

    return indexed.loc[name, "value"]


def correlation_oracle(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the pairwise-complete Pearson matrix computed by pandas."""
    columns = [
        column
        for column in CORRELATION_COLUMNS
        if column in frame.columns
    ]

    values = frame[columns].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return values.corr(
        numeric_only=True
    ).reindex(
        index=columns,
        columns=columns,
    )


def test_required_columns_are_defined() -> None:
    assert REQUIRED_COLUMNS == [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]


def test_valid_schema_passes() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
    ]

    validate_input_columns(columns)


def test_missing_required_column_fails() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "store_id",
    ]

    with pytest.raises(ValueError):
        validate_input_columns(columns)


def test_extra_columns_are_allowed() -> None:
    columns = [
        "date",
        "item_id",
        "quantity",
        "price_base",
        "sum_total",
        "store_id",
        "dept_name",
        "online_quantity",
    ]

    validate_input_columns(columns)


def test_missing_input_file_raises_actionable_error(
    tmp_path,
    monkeypatch,
) -> None:
    missing_path = tmp_path / "absent.csv"

    monkeypatch.setattr(
        exploratory_data_analysis,
        "INPUT_PATH",
        missing_path,
    )

    with pytest.raises(FileNotFoundError) as error:
        validate_input_file()

    assert "integrate_retail_data.py" in str(error.value)


def test_get_columns_reads_only_the_header(analysis_env) -> None:
    frame = build_integrated_frame()

    analysis_env(frame)

    assert get_columns() == frame.columns.tolist()


def test_build_eda_summaries_reports_dataset_metrics(analysis_env) -> None:
    analysis_env(build_integrated_frame())

    summary = build_eda_summaries()["summary"]

    assert metric_value(summary, "rows") == 8
    assert float(metric_value(summary, "total_quantity")) == pytest.approx(
        230.0
    )
    assert float(metric_value(summary, "total_revenue")) == pytest.approx(
        752.5
    )
    assert metric_value(summary, "date_min") == "2024-01-01"
    assert metric_value(summary, "date_max") == "2024-03-07"
    assert metric_value(summary, "unique_stores") == 2
    assert metric_value(summary, "unique_items") == 4


def test_read_numeric_columns_detects_numeric_fields(analysis_env) -> None:
    frame = build_integrated_frame()

    analysis_env(frame)

    numeric = exploratory_data_analysis.read_numeric_columns(
        list(frame.columns)
    )

    assert "quantity" in numeric
    assert "promo_discount_rate" in numeric
    assert "markdown_quantity" in numeric
    assert "dept_name" not in numeric
    assert "item_id" not in numeric
    assert "date" not in numeric


def test_build_eda_summaries_reports_missingness_and_non_finite(
    analysis_env,
) -> None:
    analysis_env(build_integrated_frame())

    summary = build_eda_summaries()["summary"]

    assert metric_value(summary, "missing_dept_name") == 1
    assert metric_value(summary, "missing_markdown_quantity") == 5
    assert metric_value(summary, "missing_promo_discount_rate") == 3
    assert metric_value(summary, "missing_quantity") == 0
    assert metric_value(summary, "infinite_promo_discount_rate") == 1
    assert metric_value(summary, "infinite_quantity") == 0


def test_build_eda_summaries_reports_record_frequency(analysis_env) -> None:
    analysis_env(build_integrated_frame())

    summary = build_eda_summaries()["summary"]

    assert metric_value(summary, "rows_with_discount_record") == 5
    assert metric_value(summary, "rows_with_markdown_record") == 3


def test_build_eda_summaries_aggregates_monthly_demand(analysis_env) -> None:
    analysis_env(build_integrated_frame())

    monthly = build_eda_summaries()["monthly"]

    assert isinstance(monthly, pd.DataFrame)

    assert list(monthly["year_month"]) == [
        "2024-01",
        "2024-02",
        "2024-03",
    ]

    assert list(monthly["quantity"]) == [30.0, 120.0, 80.0]
    assert list(monthly["revenue"]) == [60.0, 410.0, 282.5]
    assert list(monthly["records"]) == [2, 3, 3]


def test_build_eda_summaries_aggregates_store_demand(analysis_env) -> None:
    analysis_env(build_integrated_frame())

    stores = build_eda_summaries()["stores"]

    assert isinstance(stores, pd.DataFrame)

    assert list(stores["store_id"]) == [2, 1]
    assert list(stores["quantity"]) == [135.0, 95.0]
    assert list(stores["records"]) == [4, 4]


def test_build_eda_summaries_aggregates_department_demand(
    analysis_env,
) -> None:
    analysis_env(build_integrated_frame())

    categories = build_eda_summaries()["categories"]

    assert isinstance(categories, pd.DataFrame)

    by_department = categories.set_index(
        categories["dept_name"].fillna("unmatched")
    )["quantity"]

    assert by_department.loc["DeptA"] == pytest.approx(105.0)
    assert by_department.loc["DeptB"] == pytest.approx(70.0)
    assert by_department.loc["DeptC"] == pytest.approx(5.0)
    assert by_department.loc["unmatched"] == pytest.approx(50.0)


def test_build_eda_summaries_aggregates_item_demand(analysis_env) -> None:
    analysis_env(build_integrated_frame())

    results = build_eda_summaries()

    items = results["items"]

    assert isinstance(items, pd.DataFrame)

    assert list(items["item_id"]) == ["c", "b", "a", "d"]
    assert list(items["quantity"]) == [110.0, 70.0, 45.0, 5.0]

    top_items = pd.read_csv(
        exploratory_data_analysis.ANALYSIS_DIR
        / "eda_top_items.csv"
    )

    assert list(top_items["item_id"]) == ["c", "b", "a", "d"]


def test_build_eda_summaries_reports_item_distribution(
    analysis_env,
) -> None:
    analysis_env(build_integrated_frame())

    summary = build_eda_summaries()["summary"]

    assert float(metric_value(summary, "item_demand_q1")) == pytest.approx(
        35.0
    )
    assert float(
        metric_value(summary, "item_demand_median")
    ) == pytest.approx(57.5)
    assert float(metric_value(summary, "item_demand_q3")) == pytest.approx(
        80.0
    )
    assert float(
        metric_value(summary, "item_demand_upper_fence")
    ) == pytest.approx(147.5)
    assert metric_value(summary, "items_above_upper_fence") == 0
    assert metric_value(summary, "top_1pct_item_count") == 1
    assert float(
        metric_value(summary, "top_1pct_item_demand_share")
    ) == pytest.approx(110.0 / 230.0)
    assert float(
        metric_value(summary, "top_10_item_demand_share")
    ) == pytest.approx(1.0)


def test_build_eda_summaries_is_chunk_independent(analysis_env) -> None:
    analysis_env(build_integrated_frame(), chunk_size=1)

    single_row_chunks = build_eda_summaries()

    analysis_env(build_integrated_frame(), chunk_size=1000)

    whole_file_chunks = build_eda_summaries()

    pd.testing.assert_frame_equal(
        single_row_chunks["monthly"],
        whole_file_chunks["monthly"],
    )
    pd.testing.assert_frame_equal(
        single_row_chunks["stores"],
        whole_file_chunks["stores"],
    )
    pd.testing.assert_frame_equal(
        single_row_chunks["items"],
        whole_file_chunks["items"],
    )
    pd.testing.assert_frame_equal(
        single_row_chunks["correlation"],
        whole_file_chunks["correlation"],
    )


def test_build_eda_summaries_accepts_missing_optional_columns(
    analysis_env,
) -> None:
    frame = build_integrated_frame()[REQUIRED_COLUMNS]

    analysis_env(frame)

    results = build_eda_summaries()

    categories = results["categories"]

    assert isinstance(categories, pd.DataFrame)
    assert categories.empty
    assert list(categories.columns) == [
        "dept_name",
        "quantity",
        "revenue",
        "records",
    ]

    summary = results["summary"]

    assert metric_value(summary, "rows") == 8
    assert "missing_dept_name" not in set(summary["metric"])


def test_build_eda_summaries_writes_summary_files(analysis_env) -> None:
    _, analysis_dir, _ = analysis_env(build_integrated_frame())

    build_eda_summaries()

    expected_files = [
        "eda_summary.csv",
        "eda_monthly_demand.csv",
        "eda_store_summary.csv",
        "eda_category_summary.csv",
        "eda_top_items.csv",
        "eda_correlation.csv",
    ]

    for file_name in expected_files:
        path = analysis_dir / file_name

        assert path.exists()
        assert path.stat().st_size > 0

        assert not pd.read_csv(path).empty


def test_describe_item_demand_reports_fences_and_concentration() -> None:
    items = pd.DataFrame(
        {
            "item_id": ["a", "b", "c", "d", "e"],
            "quantity": [100.0, 4.0, 3.0, 2.0, 1.0],
        }
    )

    metrics = {
        row["metric"]: row["value"]
        for row in describe_item_demand(items)
    }

    assert metrics["item_demand_q1"] == pytest.approx(2.0)
    assert metrics["item_demand_median"] == pytest.approx(3.0)
    assert metrics["item_demand_q3"] == pytest.approx(4.0)
    assert metrics["item_demand_upper_fence"] == pytest.approx(7.0)
    assert metrics["items_above_upper_fence"] == 1
    assert metrics["items_above_upper_fence_demand_share"] == pytest.approx(
        100.0 / 110.0
    )
    assert metrics["top_1pct_item_count"] == 1
    assert metrics["top_1pct_item_demand_share"] == pytest.approx(
        100.0 / 110.0
    )
    assert metrics["top_10_item_demand_share"] == pytest.approx(1.0)


def test_describe_item_demand_handles_empty_input() -> None:
    assert describe_item_demand(pd.DataFrame()) == []

    empty_items = pd.DataFrame(
        columns=["item_id", "quantity"],
    )

    assert describe_item_demand(empty_items) == []


def test_describe_item_demand_handles_zero_demand() -> None:
    items = pd.DataFrame(
        {
            "item_id": ["a", "b"],
            "quantity": [0.0, 0.0],
        }
    )

    assert describe_item_demand(items) == []


def test_describe_item_demand_handles_single_item() -> None:
    items = pd.DataFrame(
        {
            "item_id": ["a"],
            "quantity": [10.0],
        }
    )

    assert describe_item_demand(items) == []


def test_build_correlation_matches_pandas_oracle(analysis_env) -> None:
    frame = build_integrated_frame()

    analysis_env(frame)

    result = build_correlation()

    matrix = result.set_index("variable")

    oracle = correlation_oracle(frame)

    assert list(matrix.columns) == list(oracle.columns)
    assert list(matrix.index) == list(oracle.index)

    assert (
        np.diag(matrix.to_numpy(dtype="float64")) == 1.0
    ).all()

    np.testing.assert_allclose(
        matrix.to_numpy(dtype="float64"),
        oracle.to_numpy(dtype="float64"),
        atol=1e-9,
        equal_nan=True,
    )


def test_build_correlation_excludes_non_finite_values(analysis_env) -> None:
    frame = build_integrated_frame()

    analysis_env(frame)

    matrix = build_correlation().set_index("variable")

    promo = matrix.loc[
        "promo_discount_rate",
        [
            "quantity",
            "price_base",
            "sum_total",
        ],
    ]

    assert np.isfinite(promo.to_numpy(dtype="float64")).all()

    oracle = correlation_oracle(frame)

    assert promo.tolist() == pytest.approx(
        oracle.loc[
            "promo_discount_rate",
            [
                "quantity",
                "price_base",
                "sum_total",
            ],
        ].tolist()
    )


def test_build_correlation_reports_unavailable_pairs(analysis_env) -> None:
    frame = build_integrated_frame()

    frame["markdown_quantity"] = float("nan")

    analysis_env(frame)

    matrix = build_correlation().set_index("variable")

    assert matrix.loc["markdown_quantity"].isna().all()
    assert np.isfinite(
        matrix.loc["quantity", "price_base"]
    )


def test_build_correlation_is_chunk_independent(analysis_env) -> None:
    analysis_env(build_integrated_frame(), chunk_size=1)

    single_row_chunks = build_correlation()

    analysis_env(build_integrated_frame(), chunk_size=1000)

    whole_file_chunks = build_correlation()

    pd.testing.assert_frame_equal(
        single_row_chunks,
        whole_file_chunks,
    )


def test_pearson_from_accumulators_requires_two_usable_rows() -> None:
    result = pearson_from_accumulators(
        counts=np.array([[1.0, 0.0], [0.0, 2.0]]),
        centered_sums=np.zeros((2, 2)),
        centered_products=np.zeros((2, 2)),
        centered_squares=np.zeros((2, 2)),
        columns=["first", "second"],
    )

    matrix = result.set_index("variable")

    assert np.isnan(matrix.loc["first", "first"])
    assert np.isnan(matrix.loc["first", "second"])
    assert np.isnan(matrix.loc["second", "second"])


def test_pearson_from_accumulators_returns_correlation() -> None:
    result = pearson_from_accumulators(
        counts=np.array([[3.0, 3.0], [3.0, 3.0]]),
        centered_sums=np.zeros((2, 2)),
        centered_products=np.array([[2.0, 4.0], [4.0, 8.0]]),
        centered_squares=np.array([[2.0, 1.0], [1.0, 8.0]]),
        columns=["first", "second"],
    )

    matrix = result.set_index("variable")

    assert matrix.loc["first", "first"] == pytest.approx(1.0)
    assert matrix.loc["first", "second"] == pytest.approx(1.0)


def test_create_figures_writes_all_figures(analysis_env) -> None:
    _, _, figures_dir = analysis_env(build_integrated_frame())

    results = build_eda_summaries()

    create_figures(results)

    expected_figures = [
        "eda_demand_over_time.png",
        "eda_monthly_demand.png",
        "eda_store_demand.png",
        "eda_top_categories.png",
        "eda_demand_distribution.png",
    ]

    for file_name in expected_figures:
        path = figures_dir / file_name

        assert path.exists()
        assert path.stat().st_size > 0


def test_write_findings_writes_readable_summary(analysis_env) -> None:
    _, analysis_dir, _ = analysis_env(build_integrated_frame())

    results = build_eda_summaries()

    write_findings(results)

    findings = (analysis_dir / "eda_findings.txt").read_text(
        encoding="utf-8"
    )

    assert "Rows analysed: 8" in findings
    assert "Total quantity: 230.000" in findings
    assert "Total revenue: 752.500" in findings
    assert "Date range: 2024-01-01 to 2024-03-07" in findings
    assert "Highest-demand month: 2024-02 (120.000)" in findings
    assert "Lowest-demand month: 2024-01 (30.000)" in findings
    assert "Highest-demand store: 2 (135.000)" in findings
    assert "Highest-demand department: DeptA (105.000)" in findings
    assert "Distribution and concentration observations:" in findings
    assert "Top 1% of items (1)" in findings
    assert "Promotion and markdown observations:" in findings
    assert "Rows with a discount record: 5" in findings
    assert "Rows with a markdown record: 3" in findings
    assert "Rows with non-finite analytical values" in findings
    assert "Data note:" in findings


def test_chart_labels_replace_missing_values() -> None:
    labels = exploratory_data_analysis.chart_labels(
        pd.Series(["DeptA", None, "DeptB"])
    )

    assert labels.tolist() == ["DeptA", "(unknown)", "DeptB"]
    assert all(isinstance(value, str) for value in labels)

    unmatched = exploratory_data_analysis.chart_labels(
        pd.Series(["DeptA", None]),
        fallback="(unmatched)",
    )

    assert unmatched.tolist() == ["DeptA", "(unmatched)"]


def test_create_figures_handles_unmatched_department_labels(
    analysis_env,
) -> None:
    _, _, figures_dir = analysis_env(build_integrated_frame())

    results = build_eda_summaries()

    categories = results["categories"]

    assert isinstance(categories, pd.DataFrame)
    assert categories["dept_name"].isna().any()

    create_figures(results)

    assert (figures_dir / "eda_top_categories.png").stat().st_size > 0


def test_format_helpers_avoid_float_artefacts() -> None:
    assert exploratory_data_analysis.format_identifier(4.0) == "4"
    assert exploratory_data_analysis.format_identifier(4) == "4"
    assert exploratory_data_analysis.format_identifier("item") == "item"
    assert exploratory_data_analysis.format_identifier(
        4.5
    ) == "4.5"
    assert (
        exploratory_data_analysis.format_metric(
            41949529.910000004
        )
        == "41,949,529.910"
    )
    assert exploratory_data_analysis.format_metric(None) == "None"
    assert exploratory_data_analysis.format_metric(float("nan")) == "nan"


def test_main_runs_end_to_end(analysis_env, capsys) -> None:
    _, analysis_dir, figures_dir = analysis_env(
        build_integrated_frame(),
        chunk_size=2,
    )

    exploratory_data_analysis.main()

    output = capsys.readouterr().out

    assert "completed successfully" in output
    assert (analysis_dir / "eda_summary.csv").exists()
    assert (analysis_dir / "eda_findings.txt").exists()
    assert (figures_dir / "eda_demand_over_time.png").exists()
