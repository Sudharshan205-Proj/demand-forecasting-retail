# Analytical Questions

## 1. Purpose

These questions define what the analysis must answer.

They will guide data preparation, analysis, forecasting, visualization and recommendations.

## 2. Primary SMART Question

> How accurately can future retail product demand be forecast from historical sales data, with promotions and holidays incorporated where available, over a defined forecasting horizon supported by the selected dataset?

This question will be finalized after the dataset and forecasting frequency are known.

## 3. Supporting Questions

### Historical Demand

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

9. How does demand during holidays differ from normal periods?
10. Which products or periods appear most affected by holidays?

### Product / Store Patterns

11. How does demand vary between products?
12. Where store/location information exists, how does demand vary between locations?
13. Which products or locations are more volatile?

### Forecasting

14. How well does a simple baseline forecast perform?
15. How well does ARIMA forecast future demand?
16. Does an additional permitted forecasting approach provide useful improvement?
17. Which forecasting approach performs best according to RMSE and MAPE?

### Forecast Reliability

18. Which products or periods are hardest to forecast?
19. Are forecasting errors systematically higher during promotions or holidays?
20. Are forecasts systematically biased upward or downward?

### Inventory Planning

21. Which products may require greater inventory-planning attention based on forecast demand?
22. Which future periods may experience unusually high expected demand?
23. How can forecast information support inventory planning?

## 4. SMART Assessment

| Question | Specific | Measurable | Action-Oriented | Relevant | Time-Bound |
|---|---|---|---|---|---|
| Future demand forecasting | Yes | Yes | Yes | Yes | Yes, after horizon defined |
| Promotion impact | Yes | Yes | Yes | Yes | Yes, historical period |
| Holiday impact | Yes | Yes | Yes | Yes | Yes, historical period |
| Product demand patterns | Yes | Yes | Yes | Yes | Yes |
| Forecast comparison | Yes | Yes | Yes | Yes | Yes |
| Inventory implications | Yes | Yes | Yes | Yes | Yes |

## 5. Fairness and Bias

Questions must avoid:

- Leading assumptions
- Presuming promotions cause demand increases
- Presuming holidays cause demand increases
- Presuming a particular model will perform best
- Presuming forecasts will improve inventory outcomes

The analysis must allow the data to support or contradict the hypotheses.

## 6. Question-to-Project Mapping

| Question Area | Project Phase |
|---|---|
| Business context | Phase 1 |
| Data availability | Phase 2 |
| Data quality | Phase 5 |
| Historical patterns | Phase 7 |
| Statistical relationships | Phase 8 |
| Forecast preparation | Phase 9 |
| Forecasting | Phase 11 |
| R analysis | Phase 14 (VERIFIED) |
| Evaluation | Phase 12 |
| Inventory insights | Phase 13 |
| Visualization | Phase 15 |
| Storytelling | Phase 15 |
| Application | Phase 16 |

## 7. Final Question

The final project must be able to answer:

> What does the historical retail data tell us about future demand, how reliable are those forecasts, and how can the results support inventory planning?