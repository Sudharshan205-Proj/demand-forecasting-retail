# Phase 14 - R Analysis
#
# Purpose:
# Perform reproducible R-based analysis of the demand forecasting
# and inventory-planning outputs generated in earlier project phases.
#
# This script intentionally uses the compact Phase 13 analytical
# outputs rather than loading the full raw dataset unnecessarily.

required_packages <- c(
  "tidyverse",
  "dplyr",
  "ggplot2",
  "tidymodels",
  "rmarkdown"
)

missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing_packages) > 0) {
  stop(
    paste(
      "Missing required R packages:",
      paste(missing_packages, collapse = ", ")
    )
  )
}

suppressPackageStartupMessages({
  library(tidyverse)
  library(dplyr)
  library(ggplot2)
  library(tidymodels)
})

project_root <- normalizePath(
  file.path(dirname(getwd())),
  winslash = "/",
  mustWork = TRUE
)

# If executed from the repository root, getwd() is already the project root.
if (basename(project_root) != "demand-forecasting-retail") {
  project_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
}

analysis_dir <- file.path(project_root, "data", "analysis")
r_output_dir <- file.path(analysis_dir, "r")
plot_dir <- file.path(r_output_dir, "plots")

dir.create(r_output_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(plot_dir, recursive = TRUE, showWarnings = FALSE)

demand_path <- file.path(
  analysis_dir,
  "inventory_demand_summary.csv"
)

variability_path <- file.path(
  analysis_dir,
  "inventory_variability_summary.csv"
)

scenario_path <- file.path(
  analysis_dir,
  "inventory_scenarios.csv"
)

insights_path <- file.path(
  analysis_dir,
  "forecast_inventory_insights.csv"
)

required_files <- c(
  demand_path,
  variability_path,
  scenario_path,
  insights_path
)

missing_files <- required_files[!file.exists(required_files)]

if (length(missing_files) > 0) {
  stop(
    paste(
      "Required Phase 13 files are missing:",
      paste(missing_files, collapse = ", ")
    )
  )
}

demand <- read_csv(
  demand_path,
  show_col_types = FALSE
)

variability <- read_csv(
  variability_path,
  show_col_types = FALSE
)

scenarios <- read_csv(
  scenario_path,
  show_col_types = FALSE
)

insights <- read_csv(
  insights_path,
  show_col_types = FALSE
)

# -------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------

required_demand_columns <- c(
  "store_id",
  "training_days",
  "total_quantity",
  "mean_daily_demand",
  "median_daily_demand",
  "min_daily_demand",
  "max_daily_demand",
  "coefficient_of_variation"
)

required_variability_columns <- c(
  "store_id",
  "mean_daily_demand",
  "std_daily_demand",
  "variance_daily_demand",
  "p90_daily_demand",
  "p95_daily_demand",
  "p99_daily_demand",
  "coefficient_of_variation"
)

required_scenario_columns <- c(
  "store_id",
  "model",
  "configuration",
  "lead_time_days",
  "service_level",
  "z_value",
  "mean_daily_demand",
  "std_daily_demand",
  "expected_lead_time_demand",
  "safety_stock",
  "reorder_point"
)

stopifnot(all(required_demand_columns %in% names(demand)))
stopifnot(all(required_variability_columns %in% names(variability)))
stopifnot(all(required_scenario_columns %in% names(scenarios)))

stopifnot(nrow(demand) > 0)
stopifnot(nrow(variability) > 0)
stopifnot(nrow(scenarios) > 0)

stopifnot(all(demand$mean_daily_demand >= 0))
stopifnot(all(variability$std_daily_demand >= 0))
stopifnot(all(scenarios$expected_lead_time_demand >= 0))
stopifnot(all(scenarios$safety_stock >= 0))
stopifnot(all(scenarios$reorder_point >= 0))

# -------------------------------------------------------------------
# Tidyverse / dplyr analysis
# -------------------------------------------------------------------

store_analysis <- demand %>%
  select(
    store_id,
    training_days,
    total_quantity,
    mean_daily_demand,
    median_daily_demand,
    min_daily_demand,
    max_daily_demand,
    coefficient_of_variation
  ) %>%
  left_join(
    variability %>%
      select(
        store_id,
        std_daily_demand,
        variance_daily_demand,
        p90_daily_demand,
        p95_daily_demand,
        p99_daily_demand
      ),
    by = "store_id"
  ) %>%
  arrange(desc(mean_daily_demand))

write_csv(
  store_analysis,
  file.path(r_output_dir, "r_store_analysis.csv")
)

# Highest-demand store
highest_demand <- store_analysis %>%
  slice_max(
    order_by = mean_daily_demand,
    n = 1,
    with_ties = FALSE
  )

# Highest-variability store
highest_variability <- store_analysis %>%
  slice_max(
    order_by = coefficient_of_variation,
    n = 1,
    with_ties = FALSE
  )

# -------------------------------------------------------------------
# Inventory scenario analysis
# -------------------------------------------------------------------

scenario_summary <- scenarios %>%
  group_by(lead_time_days, service_level) %>%
  summarise(
    stores = n_distinct(store_id),
    average_reorder_point = mean(reorder_point),
    maximum_reorder_point = max(reorder_point),
    average_safety_stock = mean(safety_stock),
    .groups = "drop"
  ) %>%
  arrange(lead_time_days, service_level)

write_csv(
  scenario_summary,
  file.path(r_output_dir, "r_inventory_scenario_summary.csv")
)

# 14-day / 95% planning scenario
baseline_inventory_scenario <- scenarios %>%
  filter(
    lead_time_days == 14,
    service_level == 0.95
  ) %>%
  select(
    store_id,
    model,
    configuration,
    mean_daily_demand,
    std_daily_demand,
    expected_lead_time_demand,
    safety_stock,
    reorder_point
  ) %>%
  arrange(store_id)

write_csv(
  baseline_inventory_scenario,
  file.path(r_output_dir, "r_baseline_inventory_scenario.csv")
)

# -------------------------------------------------------------------
# Phase 13 consistency check
# -------------------------------------------------------------------

phase13_highest_demand <- insights %>%
  filter(insight_type == "highest_average_demand") %>%
  slice(1)

phase13_highest_variability <- insights %>%
  filter(insight_type == "highest_relative_variability") %>%
  slice(1)

consistency <- tibble(
  check = c(
    "highest_average_demand_store",
    "highest_relative_variability_store"
  ),
  phase_13_store = c(
    as.character(phase13_highest_demand$store_id),
    as.character(phase13_highest_variability$store_id)
  ),
  r_store = c(
    as.character(highest_demand$store_id),
    as.character(highest_variability$store_id)
  )
) %>%
  mutate(
    match = phase_13_store == r_store
  )

write_csv(
  consistency,
  file.path(r_output_dir, "r_phase13_consistency.csv")
)

if (!all(consistency$match)) {
  stop("R analysis does not agree with the Phase 13 store-level findings.")
}

# -------------------------------------------------------------------
# ggplot2 visualizations
# -------------------------------------------------------------------

demand_plot <- ggplot(
  store_analysis,
  aes(
    x = factor(store_id),
    y = mean_daily_demand
  )
) +
  geom_col() +
  labs(
    title = "Average Daily Demand by Store",
    x = "Store",
    y = "Mean Daily Demand"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(plot_dir, "average_daily_demand_by_store.png"),
  plot = demand_plot,
  width = 8,
  height = 5,
  dpi = 150
)

variability_plot <- ggplot(
  store_analysis,
  aes(
    x = factor(store_id),
    y = coefficient_of_variation
  )
) +
  geom_col() +
  labs(
    title = "Relative Demand Variability by Store",
    x = "Store",
    y = "Coefficient of Variation"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(plot_dir, "demand_variability_by_store.png"),
  plot = variability_plot,
  width = 8,
  height = 5,
  dpi = 150
)

scenario_plot <- scenarios %>%
  ggplot(
    aes(
      x = lead_time_days,
      y = reorder_point,
      group = service_level,
      linetype = factor(service_level)
    )
  ) +
  geom_line() +
  geom_point() +
  facet_wrap(~ store_id) +
  labs(
    title = "Scenario Reorder Points by Lead Time and Service Level",
    x = "Lead Time (Days)",
    y = "Reorder Point",
    linetype = "Service Level"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(plot_dir, "inventory_reorder_point_scenarios.png"),
  plot = scenario_plot,
  width = 10,
  height = 7,
  dpi = 150
)

# -------------------------------------------------------------------
# Compact findings
# -------------------------------------------------------------------

findings <- c(
  "Phase 14 R Analysis Findings",
  "",
  paste(
    "Highest average daily demand store:",
    highest_demand$store_id
  ),
  paste(
    "Mean daily demand:",
    round(highest_demand$mean_daily_demand, 3)
  ),
  "",
  paste(
    "Highest relative variability store:",
    highest_variability$store_id
  ),
  paste(
    "Coefficient of variation:",
    round(highest_variability$coefficient_of_variation, 6)
  ),
  "",
  "R-derived analysis agrees with the corresponding Phase 13 store-level findings.",
  "",
  "The inventory scenario analysis remains scenario-based because operational",
  "lead times and service-level requirements are not available in the dataset.",
  "",
  "R is used here as an independent analytical and reporting workflow.",
  "Python remains the primary forecasting implementation."
)

writeLines(
  findings,
  file.path(r_output_dir, "r_analysis_findings.txt")
)

cat("Phase 14 R analysis completed successfully.\n")
cat(
  "R output directory:",
  normalizePath(r_output_dir, winslash = "/"),
  "\n"
)