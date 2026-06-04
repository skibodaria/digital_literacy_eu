# `stg_eurostat_baseline` Model
**Description:**  
This model constructs the core macro-level baseline for cross-national EU comparisons. It aggregates all 34+ raw, long-format Eurostat indicators into a single, unified wide table where every column represents an independent feature.  
To handle the asynchronous nature of public open data (where different metrics are published in different years), this model utilizes the Latest Available Year (LAY) approach. For every country-indicator combination, a SQL window function dynamically captures the absolute newest historical record within a modern rolling window.

**Key Features:**
- `[indicator_code]_baseline_value` columns: The primary numeric percentage of the population (`PC_IND`) for the total national demographic (`IND_TOTAL`)
- `[indicator_code]_source_year` columns: Explicit metadata capturing the exact vintage of the data point, used for tracking data freshness and rendering dynamic tooltips in the Streamlit frontend.

**Analytical Readiness:**  
Structured completely without data gaps (`NaN`s) to seamlessly feed downstream machine learning models, Pearson correlation heatmaps, and K-Means clustering scripts.