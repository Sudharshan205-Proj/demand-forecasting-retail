# Project Requirements

## 1. Project

Demand Forecasting for Retail

## 2. Primary goal

Forecast product demand to support inventory planning and optimization.

## 3. Mandatory retail requirements

| Requirement | Where delivered |
|---|---|
| Historical sales data | Phases 2–6 (`sales.csv`, 7,432,685 raw rows) |
| Promotions where available | Phase 6 integration; Phase 8 analysis |
| Holidays where available | Not applicable — the dataset has no holiday field (Phase 2) |
| Time-series forecasting | Phases 9–13 |
| ARIMA | Phase 11, ARIMA(1,1,1) per store |
| An additional permitted forecasting approach, assessed where justified (Prophet / LSTM) | Assessed in Phase 11 and deliberately not implemented |
| RMSE and MAPE evaluation | Phases 11–13 |
| Comparison of forecasting approaches | Phase 12 |
| Future demand forecasts | Phases 11–13 |
| Inventory-related insights | Phase 13 |
| A usable application | Phase 16, Streamlit |
| Reproducible deployment | Phase 16, Streamlit Community Cloud |

## 4. Course requirements

The project incorporates relevant material from all eight internship course
videos, mapped row by row in
[`curriculum-mapping.md`](curriculum-mapping.md) and indexed in
[`../course-coverage.md`](../course-coverage.md).

The analytical methodology is the six-stage lifecycle:

1. Ask
2. Prepare
3. Process
4. Analyze
5. Share
6. Act

## 5. Course areas

The project covers:

### Data analytics foundations

- Data analytics
- Data-driven decision making
- Analytical thinking
- Structured problem solving
- Critical thinking
- Business context
- Stakeholders
- Quantitative and qualitative data
- Data sources
- Data collection
- Ethics
- Privacy
- Security
- Data integrity
- Bias
- Communication
- Collaboration

### Analytical thinking

- Prediction
- Categorization where applicable
- Pattern identification
- Connection discovery
- Theme identification where applicable
- Root-cause thinking
- Problem decomposition
- Contextual thinking
- SMART questions

### Data preparation

- Data types
- Data structures
- Internal/external/open data
- Data relevance
- Data credibility
- Data validity
- Data reliability
- Data bias
- Data context
- ROCCC
- Databases
- Relational tables
- Keys
- Relationships
- Normalization
- Schemas
- Metadata
- Data governance
- File organization
- Versioning
- Security
- Access control

### Data processing

- Cleaning
- Completeness
- Accuracy
- Consistency
- Validation
- Formatting
- Type conversion
- Missing values
- Duplicates
- Incorrect values
- Outliers
- Transformation
- Tidy data
- Change logs
- Error checking
- Verification

### Spreadsheet analysis

- Sorting
- Filtering
- Formulas
- Functions
- SUM
- AVERAGE
- MIN
- MAX
- Cell references
- Conditional formatting
- Pivot tables
- Data validation
- Spreadsheet organization

### SQL

- SELECT
- FROM
- WHERE
- ORDER BY
- GROUP BY
- HAVING
- COUNT
- COUNT DISTINCT
- SUM
- AVG
- JOIN
- Aliases
- Subqueries
- Temporary tables
- Calculated fields
- Validation queries
- Filtering
- Aggregation

### Visualization

- Charts
- Graphs
- Histograms
- Line charts
- Bar charts
- Scatter plots
- Distribution visualization
- Correlation visualization
- Static visualization
- Dynamic visualization
- Dashboards
- Filters
- Labels
- Annotations
- Accessibility
- Direct labeling
- Visualization design
- Audience awareness
- Appropriate scales
- Avoiding clutter

### Tableau

- Tableau Public
- Interactive dashboards
- Filters
- Charts
- Dashboard design
- Accessibility
- Storytelling

### R

- R programming
- R syntax
- Variables
- Functions
- Data structures
- Data manipulation
- Data analysis
- Visualization
- Reproducibility
- Troubleshooting
- Code organization
- ggplot2
- RStudio
- R Markdown

### Case study

The final case study covers:

1. Problem
2. Context
3. Stakeholders
4. Questions
5. Data
6. Preparation
7. Processing
8. Analysis
9. Forecasting/modeling
10. Visualization
11. Findings
12. Recommendations
13. Limitations
14. Future scope
15. Communication

## 6. Engineering requirements

The project includes:

- Git and GitHub
- A Python virtual environment
- Dependency management
- Configuration
- Testing
- Error handling
- Logging
- Data validation
- Model validation
- Reproducibility
- Documentation
- Application development
- Deployment and deployment validation
- A consideration of monitoring, recorded as out of internship scope

## 7. Security requirements

The project does not commit:

- Passwords
- API keys
- Tokens
- Credentials
- Private keys
- Secret environment variables

Secrets are handled through environment configuration. The application requires
none, and a test asserts the application source contains none.

## 8. Quality requirement

The project is an internship/portfolio-quality result rather than a minimal
tutorial. Documentation matches the implementation, and every result, metric,
model, deployment and feature is supported by a generated artifact, a named
test or a documented command.
