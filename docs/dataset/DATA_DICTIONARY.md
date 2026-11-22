# Data dictionary — `dld_sales_transactions.{csv,parquet}`

One row per DLD-registered sale transaction. 1,372,277 rows, 20 columns.

| Column | Type | Description |
|---|---|---|
| `transaction_id` | string | DLD's own transaction identifier. Unique per row (natural key). |
| `instance_date` | date (`YYYY-MM-DD`) | Date the transaction was registered with the DLD. |
| `reg_type_label` | string | `Ready` (existing/completed property) or `Off-Plan` (pre-completion). These are two different DLD registration procedures, not two samples of the same process — see "Off-plan vs ready" below. |
| `area_id` | integer | DLD's numeric community/area code. |
| `area_name_en` | string | Cadastral area name in English (e.g. "Al Barsha South Fourth"). This is the DLD's official name, not the marketing name some areas are commonly known by (e.g. this file says "Al Barsha South Fourth", not "Jumeirah Village Circle" — DRED's own site maps a curated marketing-name layer on top of this, see `/areas` on the site). |
| `project_name` | string, nullable | Registered project name, where disclosed. Empty for older/resale transactions with no associated project. |
| `master_project_name` | string, nullable | Master community name, where disclosed. |
| `building_name` | string, nullable | Building name, where disclosed. |
| `property_type_label` | string | `Land`, `Building`, `Unit` (apartment) or `Villa`. |
| `property_sub_type` | string, nullable | Finer DLD sub-type (e.g. "Flat", "Villa", "Office", "Shop"). |
| `usage_label` | string | `Residential`, `Commercial` or `Other`. **`property_type = Unit` also covers shops, offices and hotel units** — usage is what separates a home from a business premise inside that type. |
| `rooms_bucket` | integer, nullable | `0` = studio, `1`–`5` = number of bedrooms (5 = "5 or more"). Null where the DLD source doesn't record room count for that row (common on older/resale rows). |
| `has_parking` | boolean | Whether a parking space is included in the registration. |
| `area_sqm` | float | Registered procedure area, in square metres. For `Land`, this is plot area, not built area. |
| `price_aed` | integer | Registered transaction price, in AED (whole dirhams). |
| `price_psf` | float, nullable | Price per square foot = `price_aed / (area_sqm × 10.7639)`, precomputed. Null where area or price is missing/non-positive, or where the raw value would overflow (an extreme data-entry artifact). **Do not average this column directly — see "Computing a price-per-sqft median" below.** |
| `procedure_id` | integer | DLD's own procedure code (e.g. `11` = Sell, `41` = Delayed Sell, `102` = Sell – Pre-registration). |
| `procedure_name_en` | string | DLD's own name for `procedure_id`, from its `lkp_transaction_procedures` lookup. |
| `is_pre_registration` | boolean | `true` for the off-plan/pre-registration twin of a procedure (DLD's own flag). Matches `reg_type_label = Off-Plan` with zero exceptions in this file. |
| `quality_flags` | integer (bitmask) | `0` = passes every check. See the table below for what each bit means. **Rows are never deleted for failing a check — they stay in the file, flagged, so nothing is silently dropped.** |

## `quality_flags` bitmask

Sum of whichever of these apply (a row failing two checks carries both bits added together):

| Bit | Meaning | Condition |
|---|---|---|
| 1 | `PRICE_FLOOR` | `price_aed` is missing or ≤ 10,000 AED |
| 2 | `AREA_RANGE` | `area_sqm` is missing or outside [5, 100,000] m² |
| 4 | `PSF_OUTLIER` | `price_psf` falls outside the P1–P99 band for its (year × `property_type_label` × `reg_type_label`) — see below |
| 8 | `MISSING_CORE` | both `price_aed` and `area_sqm` are missing |
| 16 | `BAD_DATE` | `instance_date` is missing, before 1990-01-01, or in the future (a small number of rows carry Hijri-calendar date artifacts from the source system) |

**How the P1–P99 band is computed:** for every (calendar year of `instance_date` × `property_type_label` × `reg_type_label`) group, the 1st and 99th percentile of `price_psf` is computed over rows that already pass the price-floor, area-range and date checks. A row's `price_psf` outside its own group's [P1, P99] band gets the `PSF_OUTLIER` bit. This mirrors exactly what [dubairealestatedata.com](https://www.dubairealestatedata.com) computes in production (methodology v2.1) — recomputing it from this file should reproduce the same bands.

## Computing a price-per-sqft median (reproducing the site's headline number)

The site's published median price-per-sqft is computed from exactly this population:

```sql
select median(price_psf)
from dld_sales_transactions
where quality_flags = 0
  and property_type_label in ('Unit', 'Villa')
  and usage_label = 'Residential'
  and instance_date >= <window start>
```

Two exclusions matter and are easy to get wrong:
- **`property_type_label in ('Unit', 'Villa')`** — excludes `Land` (which trades on plot area at orders-of-magnitude lower psf) and `Building` (whole-building deals price wholesale).
- **`usage_label = 'Residential'`** — `Unit` also covers shops, offices and hotel units, which price on a different logic than homes. Leaving this out is the single most common way to get a psf median that looks plausible but is quietly wrong.

**Transaction counts and total value should NOT apply these two restrictions** — every registered sale counts toward volume/value figures; only price-per-sqft is restricted to built residential.

## Off-plan vs ready

`reg_type_label` splits the data into two genuinely different DLD registration procedures — pre-construction sales (`Off-Plan`) and completed-property sales (`Ready`) — not two samples of one process. Any comparison across the two should keep this split explicit rather than blending them; DRED's own `/market` page reports both a combined and a split view for exactly this reason.

## Known limitations

- **No bedroom-count field for a meaningful share of older rows** (`rooms_bucket` is null) — DLD did not consistently record it in earlier years.
- **`project_name` / `building_name` / `master_project_name` are free text as registered**, with real-world spelling/casing variation (not deduplicated or normalized in this file).
- **This is a point-in-time snapshot** (through 5 Oct 2026, refreshed monthly) — see the README's "Staying current" section.
- **`transaction_id` is guaranteed unique in this file.** A small number of transactions get amended or re-registered by the DLD after they were first published; this export carries only the current record of each (the pipeline upserts by `transaction_id`), so a join on `transaction_id` never fans out.
