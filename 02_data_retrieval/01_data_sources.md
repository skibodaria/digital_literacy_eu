# Digital Literacy EU | Project's Data Sources

The main data sources I use for this projects are coming from the European Comission. All of them are publicly available, well-established, and organized. Below you can find the overview of the main data sources with additional documentation and links provided.
--- 
## 1. Eurostat Data
**Eurostat** (European Statistical Office) is a Directorate-General od the European Commission. It's [main goal and responsibility](https://ec.europa.eu/eurostat/web/main/about-us/mission-values) is to provide high-quality statistics and data on Europe. The procedures for the data collection are standartizes across the European countries and conducted in the framework of [the European Statistical System](https://ec.europa.eu/eurostat/web/european-statistical-system/overview).

### Pros and Cons of Using Eurostat Data:
* **The Pros**:
    - *Harmonized Methodology*: Eurostat data doesn’t just translate questions; it enforces strict legal and statistical frameworks (the European Statistical System). National statistical institutes must align their definitions, meaning "internet usage in the last 3 months" is measured exactly the same way in Germany as it is in France, ensuring highly accurate cross-country baseline comparisons.
    - *Massive Sample Sizes and Hard Metrics*: Because these statistics feed directly into EU policy and funding allocations, they capture actual behavioral data and hard demographics from massive national sample sizes. This provides a far more stable and objective picture of infrastructure, digital skills, and country-level trends than public sentiment surveys.
    - *Modern Access*: Eurostat provides excellent open-data infrastructure. Instead of wrestling with files manually,one can avoid manual downloads entirely by using programmatic APIs or dedicated developer tools (like the `eurostat` package in Python integrations) to query and pull clean data directly into your environment.
* **The Cons**
    - *Significant Publication Lags*: Because Eurostat acts as a consolidator, it must wait for all member states to collect, clean, verify, and submit their national data. This extensive pipeline means that complex socioeconomic or digital economy datasets can sometimes face a publication lag of 12 to 24 months, making it tough to analyze "real-time" technological shifts.
    - *The "Break in Time Series" Trap*: Eurostat regularly updates its classification frameworks, definitions, and methodology to keep pace with modern realities (for example, redefining what constitutes a "digital skill"). While this keeps data relevant, it frequently introduces "breaks in time series" (marked as `:b` in their database), which can instantly break a longitudinal analysis or make historical data comparison messy.
    - *Varying Regional Compliance*: While the frameworks are unified, the execution capacity varies by country. Some member states submit provisional data, use slightly different data-imputation methods to fill gaps, or run late on deadlines, leading to missing values or varying data reliability across certain specific regions.


---
## 2. Eurobarometer
**Eurobarometer** is a specific public opinion survey which is conducted on behalf of the European Comission since 1970s. There are several types of Eurobarometers, and in the current research I'm using two of them:
* **Standard Eurobarometer**: regular survey; focuses of the EU citizens' perceptions of many topics. In the current research project I mainly use the data from the following two surveys:
    - **Standard Eurobarometer STD104 (104) - Autumn 2025**
        - [documentation](https://europa.eu/eurobarometer/surveys/detail/3378)
        - [data](https://data.europa.eu/data/datasets/s3378_104_1_std104_eng?locale=en)
    - **Standard Eurobarometer STD105 (105) - Spring 2026** 
        - [documentation](https://europa.eu/eurobarometer/surveys/detail/3613)
        - [data](https://data.europa.eu/data/datasets/s3613_105_2_std105_eng?locale=en)
* **Special Eurobarometer SP566: The Digital Decade 2025**: special survey, focused on Internet-usage, digital technologies, and AI
    - [documentation](https://europa.eu/eurobarometer/surveys/detail/3362)
    - [data](https://data.europa.eu/data/datasets/s3362_103_2_sp566_eng?locale=en)

### Pros and Cons of Using Eurobarometer Data:
* **The Pros:**
    - *Rich Media and Digital Insights*: It contains excellent, dedicated data tracking citizen internet usage, digital habits, and online behavior across Europe.
    - *Faster Release Cycles*: Eurobarometer data is processed and published significantly faster than alternative academic surveys (like the European Social Survey), enabling work with fresher data.
    - *Unified Cross-National Structure*: The data is fully synchronized and standardized across all EU countries from day one, making multi-country comparisons straightforward.

* **The Cons:** 
    - *Messy Excel Format* (`.xlsx`): It is annoying to clean. The files are optimized for human reading rather than machine analysis, requiring extensive parsing and reshaping before one can build a clean dataframe.
    - *Translation and Cultural Inequivalence*: Because the survey is translated into dozens of languages, subtle shifts in wording mean a question about internet habits or trust might be interpreted differently from country to country.
    * Lack of Micro-Level Granularity*: Demographic variables (like age, income, or region) are grouped into broad, rigid categories rather than precise numbers, which limits the ability to do hyper-specific statistical modeling.
