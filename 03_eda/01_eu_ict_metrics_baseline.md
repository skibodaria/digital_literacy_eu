# `stg_eurostat_baseline` Model
**Description:**  
This model constructs the core macro-level baseline for cross-national EU comparisons. It aggregates all 34+ raw, long-format Eurostat indicators into a single, unified wide table where every column represents an independent feature.  
To handle the asynchronous nature of public open data (where different metrics are published in different years), this model utilizes the Latest Available Year (LAY) approach. For every country-indicator combination, a SQL window function dynamically captures the absolute newest historical record within a modern rolling window.

**Key Features:**
- `[indicator_code]_baseline_value` columns: The primary numeric percentage of the population (`PC_IND`) for the total national demographic (`IND_TOTAL`)
- `[indicator_code]_source_year` columns: Explicit metadata capturing the exact vintage of the data point, used for tracking data freshness and rendering dynamic tooltips in the Streamlit frontend.

**Analytical Readiness**:  
Structured completely without data gaps (`NaN`s) to seamlessly feed downstream machine learning models, Pearson correlation heatmaps, and K-Means clustering scripts.

**Core Metrics**:
- `I_DSK2_AB`: Individuals with above basic overall digital skills (all five component indicators are at above basic level).
- `I_DSK2_B`: Individuals with basic overall digital skills (all five component indicators are at basic or above basic level, without being all above basic).
- `I_DSK2_X`: Individuals with no overall digital skills.
- `I_IDAY`: Frequency of internet access: daily.
- `I_IEID`: Individuals who have used their eID to access online services for private purpose in the last 12 months.
- `I_IGOVAPR`: Internet use: making an appointment or a reservation (last 12 months).
- `I_IGOVTAX2`: Internet use: submitting my tax declaration (in the last 12 months) (as of 2024).
- `I_IMT12`: Last internet use: more than a year ago or never.
- `I_IREIDNO`: Individuals not using their eID in the last 12 months because they didn’t have one.
- `I_IUAI`: Use of generative AI tools: in the last 3 months.
- `I_IUGOV1`: Internet use: interaction with public authorities (last 12 months) (as of 2022).
- `I_IUPOL2`: Internet use: expressing opinions on civic or political issues on websites or in social media (e.g. Facebook, Twitter, Instagram, YouTube).
- `I_IUX`: Internet use: never.
- `I_MAPS`: Individuals manage access to personal data on the internet (3 months).
- `I_TIC`: Individuals have checked the truthfulness of the information or content they found on the internet news sites or social media (3 months).
- `I_UDI`: Individuals have seen untrue or doubtful information or content on the internet news sites or social media (3 months).