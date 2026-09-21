# Analytical Questions

## 1. Purpose

These questions define what the analysis answers. They guide data preparation,
analysis, forecasting, visualization and recommendations.

## 2. Primary SMART question

> How accurately can future retail product demand be forecast from historical
> sales data, with promotions and holidays incorporated where available, over a
> defined forecasting horizon supported by the selected dataset?

Established in Phases 2 and 9: the forecasting unit is `date × item_id ×
store_id` at a daily frequency, the horizon is the 114-day validation window
(2024-02-11 to 2024-06-03) with the reserved test period left unused, and
"promotions and holidays where available" resolves to promotions from
`discounts_history.csv` and `markdowns.csv`, with holidays not applicable
because the dataset has no holiday field.

## 3. Supporting questions

### Historical demand

1. What products have the highest historical demand?
2. What products have the lowest historical demand?
3. How does demand change over time?
4. Are there identifiable trends in demand?
5. Are there recurring seasonal patterns?

### Promotions

6. How does demand differ between promotional and non-promotional periods?
7. Which products show the largest demand changes during promotions?
8. Are promotional demand effects consistent over time?

### Holidays

9. How does demand during holidays differ from normal periods? — **not
   applicable:** the dataset has no holiday field.
10. Which products or periods appear most affected by holidays? — **not
    applicable:** the dataset has no holiday field.

### Product / store patterns

11. How does demand vary between products?
12. How does demand vary between stores?
13. Which products or stores are more volatile?

### Forecasting

14. How well does a simple baseline forecast perform?
15. How well does ARIMA forecast future demand?
16. Does an additional permitted forecasting approach provide useful
    improvement?
17. Which forecasting approach performs best according to RMSE and MAPE?

### Forecast reliability

18. Which stores or periods are hardest to forecast?
19. Are forecasts systematically biased upward or downward?
20. How large is the forecast error relative to demand?

### Inventory planning

21. Which stores may require greater inventory-planning attention based on
    forecast demand?
22. How much buffer does a lead-time/service-level assumption imply?
23. How can forecast information support inventory planning?

## 4. SMART assessment

| Question | Specific | Measurable | Action-oriented | Relevant | Time-bound |
|---|---|---|---|---|---|
| Future demand forecasting | Yes | Yes | Yes | Yes | Yes — the forecast horizon is defined |
| Promotion impact | Yes | Yes | Yes | Yes | Yes — historical period |
| Holiday impact | Not applicable — no holiday field in the dataset | — | — | — | — |
| Product demand patterns | Yes | Yes | Yes | Yes | Yes |
| Forecast comparison | Yes | Yes | Yes | Yes | Yes |
| Inventory implications | Yes | Yes | Yes | Yes | Yes |

## 5. Fairness and bias

The questions avoid:

- Leading assumptions
- Presuming promotions cause demand increases
- Presuming holidays cause demand increases
- Presuming a particular model will perform best
- Presuming forecasts will improve inventory outcomes

The analysis allows the data to support or contradict the hypotheses.

## 6. Question-to-project mapping

| Question area | Project phase |
|---|---|
| Business context | Phase 1 |
| Data availability | Phase 2 |
| Data quality | Phase 5 |
| Historical patterns | Phase 7 |
| Statistical relationships | Phase 8 |
| Forecast preparation | Phase 9 |
| Forecasting | Phase 11 |
| Evaluation | Phase 12 |
| Inventory insights | Phase 13 |
| R analysis | Phase 14 |
| Visualization | Phase 15 |
| Storytelling | Phase 15 |
| Application | Phase 16 (local and hosted) |

## 7. Final question

> What does the historical retail data tell us about future demand, how reliable
> are those forecasts, and how can the results support inventory planning?
