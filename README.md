# Dubai Real Estate Sales Transactions (DLD, 2004–2026)

**1,372,277 registered property sale transactions in Dubai**, sourced directly from the Dubai Land Department (DLD) via the Dubai Pulse open-data platform. This is not a listings scrape and it is not asking prices — every row is a transaction actually registered with the government.

Published by **[Dubai Real Estate Data](https://www.dubairealestatedata.com)** (dubairealestatedata.com), an independent analytics site that turns this exact DLD data into medians, trends, yields and area profiles for the Dubai market. This dataset is the raw material behind that site, released so researchers, students and other builders can work with it directly instead of re-scraping or re-licensing it themselves.

## What's in it

- **Coverage:** transaction dates from 2004 through **5 October 2026** (the tail before 2004 is thin — ~8.6k rows — and included as-is rather than trimmed). This is a **fixed historical snapshot**, not a live feed — see "Staying current" below.
- **Population:** DLD `trans_group = Sales` only. Mortgages and gifts are a different registration process with a different pricing logic (a mortgage amount is a loan, not a sale price) and are deliberately excluded — see [dubairealestatedata.com/methodology](https://www.dubairealestatedata.com/methodology#sales-transactions).
- **Granularity:** one row per registered transaction — date, area, project/building (where disclosed), property type, size, price, and a transparent data-quality flag.
- **Formats:** CSV (`dld_sales_transactions.csv`, ~239 MB) and Parquet (`dld_sales_transactions.parquet`, ~23 MB, zstd-compressed) — same data, same row order.

See **`DATA_DICTIONARY.md`** for the full column reference, including exactly how the `quality_flags` column is computed and which population to use for a price-per-sqft analysis.

## Why this file, not another Dubai transactions dump

- **Quality flags, not silent cleaning.** Every row keeps a `quality_flags` bitmask instead of being quietly dropped or blended in. You decide what "clean" means for your analysis; we show our own choice (`quality_flags = 0`, 1,343,782 of 1,372,277 rows) so it's reproducible.
- **Outlier bands are computed, not eyeballed.** The P1–P99 price-per-sqft band behind the `PSF_OUTLIER` flag is calculated per (year × property type × registration type) from this exact file — the method is in `DATA_DICTIONARY.md`, not a black box.
- **Medians, never averages, and land is excluded from psf.** Land trades on plot area (a single island can be tens of thousands of m²) and whole-building deals are wholesale — both would distort a "price per sqft" figure. The live site's price-per-sqft population is exactly `property_type in (Unit, Villa) and usage = Residential`, reproduced here so you can recompute the same headline number this file backs.

## Staying current

This file is a snapshot through **5 October 2026**. It is refreshed monthly from the same pipeline. The live site ingests the DLD's rolling open-data gateway weekly and publishes current medians, YoY trends and area rankings at **[dubairealestatedata.com/market](https://www.dubairealestatedata.com/market)**, with a full machine-readable mirror at **[dubairealestatedata.com/market.md](https://www.dubairealestatedata.com/market.md)**. If this dataset is useful to you, check there for anything after this snapshot's cutoff.

## License & attribution

**CC BY 4.0** (Creative Commons Attribution 4.0 International) — the same license the Dubai Land Department publishes its open data under via Dubai Pulse. Free to use, share and adapt, with attribution. See `LICENSE.md`.

When you use this dataset, please cite:

> Dubai Real Estate Data (dubairealestatedata.com), based on Dubai Land Department open data.

- Original source: Dubai Land Department (DLD) open data via Dubai Pulse — https://dubailand.gov.ae/en/open-data/real-estate-data/
- This release: https://www.dubairealestatedata.com/sources
- Methodology: https://www.dubairealestatedata.com/methodology

## Disclaimer

Independent analytics. Not affiliated with, or endorsed by, the Government of Dubai, the Dubai Land Department or any government entity. Not investment advice, not a valuation.
