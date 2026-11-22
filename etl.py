"""
ETL pipeline: Dubai DLD Sales Transactions (CSV) -> star schema -> MySQL `dld`.

Run:  myenv\\Scripts\\python.exe etl.py            (full pipeline, loads MySQL)
      myenv\\Scripts\\python.exe etl.py --no-load  (stop after saving CSVs)

Steps: extract -> profile -> transform -> build_star_schema -> save_csv -> load -> validate
"""
import argparse
import logging
import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

from utils.config import DB_CONFIG
from utils.db import make_engine

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
RAW_CSV = "data/raw/dld_sales_transactions.csv"
OUT_DIR = "data/processed"
LOG_DIR = "log"

# Analysis window. Pre-2004 data is very thin (~8.4k clean rows over 30 years),
# so the window starts in 2004 as the README recommends. Snapshot ends 2026-10-05.
START_DATE = "2004-01-01"
END_DATE = None  # None = up to the last date in the file

SQM_TO_SQFT = 10.7639
UNKNOWN = "Unknown"
ROOMS_LABELS = {0: "Studio", 1: "1 BR", 2: "2 BR", 3: "3 BR", 4: "4 BR", 5: "5+ BR"}

RAW_DTYPES = {
    "transaction_id": "string",
    "instance_date": "string",
    "reg_type_label": "string",
    "area_id": "Int64",
    "area_name_en": "string",
    "project_name": "string",
    "master_project_name": "string",
    "building_name": "string",
    "property_type_label": "string",
    "property_sub_type": "string",
    "usage_label": "string",
    "rooms_bucket": "Int64",
    "has_parking": "boolean",
    "area_sqm": "float64",
    "price_aed": "int64",
    "price_psf": "float64",
    "procedure_id": "Int64",
    "procedure_name_en": "string",
    "is_pre_registration": "boolean",
    "quality_flags": "int64",
}

os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/etl_{datetime.now():%Y%m%d}.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)
log = logging.getLogger("etl")


# ----------------------------------------------------------------------------
# 1. Extract
# ----------------------------------------------------------------------------
def extract(path: str = RAW_CSV) -> pd.DataFrame:
    log.info("EXTRACT start: %s", path)
    df = pd.read_csv(path, dtype=RAW_DTYPES, parse_dates=["instance_date"])
    log.info("EXTRACT done: %s rows x %s cols", f"{len(df):,}", df.shape[1])
    return df


# ----------------------------------------------------------------------------
# 2. Profile (logged, not modified)
# ----------------------------------------------------------------------------
def profile(df: pd.DataFrame) -> None:
    log.info("PROFILE start")
    log.info("transaction_id unique: %s", df["transaction_id"].is_unique)
    log.info("full-row duplicates: %s", df.duplicated().sum())
    nulls = df.isna().sum()
    for col, n in nulls[nulls > 0].items():
        log.info("  null %-22s %9s", col, f"{n:,}")
    log.info("date range: %s -> %s", df["instance_date"].min().date(), df["instance_date"].max().date())
    log.info("quality_flags != 0: %s", f"{(df['quality_flags'] != 0).sum():,}")
    log.info("price_aed mean %.0f vs median %.0f (right-skewed)", df["price_aed"].mean(), df["price_aed"].median())
    log.info("PROFILE done")


# ----------------------------------------------------------------------------
# 3. Transform
# ----------------------------------------------------------------------------
def _clean_text(s: pd.Series) -> pd.Series:
    """Trim and collapse inner whitespace; empty -> NA."""
    s = s.str.strip().str.replace(r"\s+", " ", regex=True)
    return s.mask(s == "")


def _unify_case(s: pd.Series) -> pd.Series:
    """Spellings that differ only by case are mapped to their most frequent form."""
    key = s.str.casefold()
    counts = pd.DataFrame({"key": key, "val": s}).dropna().value_counts()
    canonical = counts.reset_index().drop_duplicates("key").set_index("key")["val"]
    return key.map(canonical).astype("string")


def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("TRANSFORM start: %s rows", f"{len(df):,}")
    df = df.copy()
    n0 = len(df)

    # 3.1 Filter rows
    df = df[df["quality_flags"] == 0]
    log.info("  drop quality_flags != 0: -%s", f"{n0 - len(df):,}")
    n1 = len(df)
    end = pd.Timestamp(END_DATE) if END_DATE else df["instance_date"].max()
    df = df[(df["instance_date"] >= START_DATE) & (df["instance_date"] <= end)]
    log.info("  drop outside %s..%s: -%s", START_DATE, end.date(), f"{n1 - len(df):,}")

    # 3.3 Standardise text
    text_cols = ["area_name_en", "project_name", "master_project_name", "building_name",
                 "property_sub_type", "procedure_name_en"]
    for c in text_cols:
        df[c] = _clean_text(df[c])
    for c in ["project_name", "master_project_name", "building_name"]:
        before = df[c].nunique()
        df[c] = _unify_case(df[c])
        log.info("  %s: %s -> %s distinct after case unification", c, before, df[c].nunique())

    # 3.2a Recover procedure_id: transaction_id is "<n>-<procedure_id>-<year>-<seq>".
    # Verified: the prefix equals procedure_id on 100% of rows where both exist.
    id_proc = pd.to_numeric(df["transaction_id"].str.split("-").str[1], errors="coerce").astype("Int64")
    known = df["procedure_id"].notna()
    match_rate = (id_proc[known] == df.loc[known, "procedure_id"]).mean()
    log.info("  transaction_id prefix == procedure_id on known rows: %.4f", match_rate)
    proc_names = (df.loc[known, ["procedure_id", "procedure_name_en"]].drop_duplicates()
                  .set_index("procedure_id")["procedure_name_en"])
    missing = df["procedure_id"].isna()
    df.loc[missing, "procedure_id"] = id_proc[missing]
    df.loc[missing, "procedure_name_en"] = df.loc[missing, "procedure_id"].map(proc_names)
    log.info("  procedure_id recovered from transaction_id: %s rows",
             f"{(missing & df['procedure_name_en'].notna()).sum():,}")

    # 3.2b Missing values: descriptive -> Unknown / 0
    df["area_id"] = df["area_id"].fillna(0)
    df["area_name_en"] = df["area_name_en"].fillna(UNKNOWN)
    df["procedure_id"] = df["procedure_id"].fillna(0)
    df["procedure_name_en"] = df["procedure_name_en"].fillna(UNKNOWN)
    for c in ["project_name", "master_project_name", "building_name", "property_sub_type"]:
        df[c] = df[c].fillna(UNKNOWN)
    df["parking_label"] = df["has_parking"].map({True: "Yes", False: "No"}).fillna(UNKNOWN)
    df["has_parking"] = df["has_parking"].astype("Int8")  # 1/0/NULL for numeric analysis

    # 3.6 Feature engineering
    df["rooms_label"] = df["rooms_bucket"].map(ROOMS_LABELS).fillna(UNKNOWN).astype("string")
    df["date_id"] = df["instance_date"].dt.strftime("%Y%m%d").astype("int32")
    df["is_offplan"] = (df["reg_type_label"] == "Off-Plan").astype("int8")
    psf_check = df["price_aed"] / (df["area_sqm"] * SQM_TO_SQFT)
    max_diff = (psf_check - df["price_psf"]).abs().max()
    log.info("  price_psf recompute max abs diff: %.4f", max_diff)

    # 3.4 Outlier cross-check with IQR (informational; PSF_OUTLIER already applied)
    q1, q3 = df["price_psf"].quantile([0.25, 0.75])
    iqr = q3 - q1
    n_iqr = ((df["price_psf"] < q1 - 1.5 * iqr) | (df["price_psf"] > q3 + 1.5 * iqr)).sum()
    log.info("  IQR check on remaining psf: %s rows outside [%.0f, %.0f] (kept, group-level P1-P99 already applied)",
             f"{n_iqr:,}", q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    # 3.5 Drop redundant columns
    assert (df["is_pre_registration"].isna() | (df["is_pre_registration"] == (df["is_offplan"] == 1))).all()
    df = df.drop(columns=["is_pre_registration", "quality_flags"])

    log.info("TRANSFORM done: %s rows kept (%.2f%% of raw)", f"{len(df):,}", 100 * len(df) / n0)
    return df.reset_index(drop=True)


# ----------------------------------------------------------------------------
# 4. Star schema
# ----------------------------------------------------------------------------
def build_star_schema(df: pd.DataFrame) -> dict:
    log.info("MODEL start")

    # dim_date: continuous calendar
    dates = pd.date_range(df["instance_date"].min(), df["instance_date"].max(), freq="D")
    dim_date = pd.DataFrame({"full_date": dates})
    dim_date["date_id"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype("int32")
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["quarter_label"] = "Q" + dim_date["quarter"].astype(str)
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["year_month_label"] = dim_date["full_date"].dt.strftime("%Y-%m")
    dim_date["weekday_num"] = dim_date["full_date"].dt.weekday + 1  # 1 = Monday
    dim_date["weekday_name"] = dim_date["full_date"].dt.day_name()
    dim_date["is_weekend"] = dim_date["full_date"].dt.weekday.isin([5, 6]).astype("int8")
    # Snapshot cutoff (e.g. 2026-10-05) leaves the last month/year incomplete:
    # flag them so YoY/MoM trends can exclude them.
    last = dates.max()
    month_cut = last != last + pd.offsets.MonthEnd(0)      # last day is not a month end
    year_cut = not (last.month == 12 and last.day == 31)   # last day is not Dec 31
    in_last_month = dim_date["full_date"].dt.to_period("M") == last.to_period("M")
    in_last_year = dim_date["year"] == last.year
    dim_date["is_complete_month"] = (~(in_last_month & month_cut)).astype("int8")
    dim_date["is_complete_year"] = (~(in_last_year & year_cut)).astype("int8")
    dim_date["full_date"] = dim_date["full_date"].dt.date
    dim_date = dim_date[["date_id", "full_date", "year", "quarter", "quarter_label", "month",
                         "month_name", "year_month_label", "weekday_num", "weekday_name", "is_weekend",
                         "is_complete_month", "is_complete_year"]]

    # dim_area: natural key (0 = Unknown)
    dim_area = (df[["area_id", "area_name_en"]].drop_duplicates()
                .sort_values("area_id").reset_index(drop=True))
    if 0 not in dim_area["area_id"].values:
        dim_area = pd.concat([pd.DataFrame({"area_id": [0], "area_name_en": [UNKNOWN]}), dim_area])

    # dim_procedure: natural key (0 = Unknown, Ready)
    dim_procedure = (df[["procedure_id", "procedure_name_en", "reg_type_label"]].drop_duplicates()
                     .sort_values("procedure_id").reset_index(drop=True))

    # dim_project: surrogate key, 0 = all-Unknown
    proj_cols = ["project_name", "master_project_name", "building_name"]
    dim_project = df[proj_cols].drop_duplicates()
    is_unknown = (dim_project == UNKNOWN).all(axis=1)
    dim_project = pd.concat([dim_project[is_unknown],
                             dim_project[~is_unknown].sort_values(proj_cols)]).reset_index(drop=True)
    if not is_unknown.any():
        dim_project = pd.concat([pd.DataFrame([[UNKNOWN] * 3], columns=proj_cols), dim_project],
                                ignore_index=True)
    dim_project.insert(0, "project_id", range(len(dim_project)))

    # dim_property: junk dimension, surrogate key from 1
    prop_cols = ["property_type_label", "property_sub_type", "usage_label",
                 "rooms_bucket", "rooms_label", "has_parking", "parking_label"]
    dim_property = (df[prop_cols].drop_duplicates()
                    .sort_values(prop_cols, na_position="last").reset_index(drop=True))
    dim_property.insert(0, "property_id", range(1, len(dim_property) + 1))

    # fact_sales
    n = len(df)
    fact = df.merge(dim_project, on=proj_cols, how="left")
    fact = fact.merge(dim_property, on=prop_cols, how="left")
    assert len(fact) == n, "fact row count changed after merge (duplicate dim keys)"
    assert fact[["project_id", "property_id"]].notna().all().all(), "unmatched dim keys"
    fact_sales = fact[["transaction_id", "date_id", "area_id", "project_id", "property_id",
                       "procedure_id", "price_aed", "area_sqm", "price_psf"]].copy()
    fact_sales["price_psf"] = fact_sales["price_psf"].round(2)

    tables = {
        "dim_date": dim_date,
        "dim_area": dim_area,
        "dim_procedure": dim_procedure,
        "dim_project": dim_project,
        "dim_property": dim_property,
        "fact_sales": fact_sales,
    }
    for name, t in tables.items():
        log.info("  %-14s %10s rows x %s cols", name, f"{len(t):,}", t.shape[1])
    log.info("MODEL done")
    return tables


# ----------------------------------------------------------------------------
# 5. Save + Load
# ----------------------------------------------------------------------------
def save_csv(tables: dict, out_dir: str = OUT_DIR) -> None:
    os.makedirs(out_dir, exist_ok=True)
    for name, t in tables.items():
        t.to_csv(f"{out_dir}/{name}.csv", index=False, encoding="utf-8")
    log.info("SAVE done: %s/*.csv", out_dir)


DDL = [
    """CREATE TABLE dim_date (
        date_id INT PRIMARY KEY, full_date DATE NOT NULL, year SMALLINT NOT NULL,
        quarter TINYINT NOT NULL, quarter_label CHAR(2) NOT NULL, month TINYINT NOT NULL,
        month_name VARCHAR(10) NOT NULL, year_month_label CHAR(7) NOT NULL,
        weekday_num TINYINT NOT NULL, weekday_name VARCHAR(10) NOT NULL, is_weekend TINYINT NOT NULL,
        is_complete_month TINYINT NOT NULL, is_complete_year TINYINT NOT NULL)""",
    """CREATE TABLE dim_area (
        area_id INT PRIMARY KEY, area_name_en VARCHAR(100) NOT NULL)""",
    """CREATE TABLE dim_procedure (
        procedure_id INT PRIMARY KEY, procedure_name_en VARCHAR(100) NOT NULL,
        reg_type_label VARCHAR(10) NOT NULL)""",
    """CREATE TABLE dim_project (
        project_id INT PRIMARY KEY, project_name VARCHAR(255) NOT NULL,
        master_project_name VARCHAR(255) NOT NULL, building_name VARCHAR(255) NOT NULL)""",
    """CREATE TABLE dim_property (
        property_id INT PRIMARY KEY, property_type_label VARCHAR(20) NOT NULL,
        property_sub_type VARCHAR(100) NOT NULL, usage_label VARCHAR(20) NOT NULL,
        rooms_bucket TINYINT NULL, rooms_label VARCHAR(10) NOT NULL,
        has_parking TINYINT NULL, parking_label VARCHAR(10) NOT NULL)""",
    """CREATE TABLE fact_sales (
        transaction_id VARCHAR(50) PRIMARY KEY,
        date_id INT NOT NULL, area_id INT NOT NULL, project_id INT NOT NULL,
        property_id INT NOT NULL, procedure_id INT NOT NULL,
        price_aed BIGINT NOT NULL, area_sqm DECIMAL(12,2) NOT NULL, price_psf DECIMAL(12,2) NOT NULL,
        FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
        FOREIGN KEY (area_id) REFERENCES dim_area(area_id),
        FOREIGN KEY (project_id) REFERENCES dim_project(project_id),
        FOREIGN KEY (property_id) REFERENCES dim_property(property_id),
        FOREIGN KEY (procedure_id) REFERENCES dim_procedure(procedure_id),
        INDEX ix_date (date_id), INDEX ix_area (area_id))""",
]
LOAD_ORDER = ["dim_date", "dim_area", "dim_procedure", "dim_project", "dim_property", "fact_sales"]


def ensure_database(cfg: dict) -> None:
    server = create_engine(
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}@{cfg['host']}:{cfg['port']}/")
    with server.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
                          "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    server.dispose()


def load(tables: dict, cfg: dict = DB_CONFIG):
    """Drop + recreate the 6 tables, then append. Re-running never duplicates rows."""
    log.info("LOAD start -> MySQL %s/%s", cfg["host"], cfg["database"])
    ensure_database(cfg)
    engine = make_engine(cfg)
    with engine.begin() as conn:
        for name in reversed(LOAD_ORDER):
            conn.execute(text(f"DROP TABLE IF EXISTS {name}"))
        for ddl in DDL:
            conn.execute(text(ddl))
    for name in LOAD_ORDER:
        t0 = time.time()
        tables[name].to_sql(name, engine, if_exists="append", index=False,
                            chunksize=20_000, method="multi")
        log.info("  loaded %-14s %10s rows in %.1fs", name, f"{len(tables[name]):,}", time.time() - t0)
    log.info("LOAD done")
    return engine


# ----------------------------------------------------------------------------
# 6. Validate
# ----------------------------------------------------------------------------
PK = {"dim_date": "date_id", "dim_area": "area_id", "dim_procedure": "procedure_id",
      "dim_project": "project_id", "dim_property": "property_id", "fact_sales": "transaction_id"}


def validate(tables: dict, engine) -> bool:
    log.info("VALIDATE start")
    ok = True

    def check(label, cond):
        nonlocal ok
        ok &= bool(cond)
        log.info("  [%s] %s", "PASS" if cond else "FAIL", label)

    with engine.connect() as conn:
        q = lambda sql: conn.execute(text(sql)).scalar()
        for name, pk in PK.items():
            cnt, dist = conn.execute(text(f"SELECT COUNT(*), COUNT(DISTINCT {pk}) FROM {name}")).one()
            check(f"{name}: rows {cnt:,} == pandas {len(tables[name]):,}, PK unique", cnt == len(tables[name]) == dist)
        for dim, key in [("dim_date", "date_id"), ("dim_area", "area_id"), ("dim_project", "project_id"),
                         ("dim_property", "property_id"), ("dim_procedure", "procedure_id")]:
            orphans = q(f"SELECT COUNT(*) FROM fact_sales f LEFT JOIN {dim} d ON f.{key}=d.{key} WHERE d.{key} IS NULL")
            check(f"no orphan fact rows vs {dim} ({orphans})", orphans == 0)
        total_sql = int(q("SELECT SUM(price_aed) FROM fact_sales"))
        total_pd = int(tables["fact_sales"]["price_aed"].sum())
        check(f"SUM(price_aed) {total_sql:,} == pandas {total_pd:,}", total_sql == total_pd)

    f = tables["fact_sales"].merge(tables["dim_property"], on="property_id")
    resi = f[f["property_type_label"].isin(["Unit", "Villa"]) & (f["usage_label"] == "Residential")]
    log.info("  median residential psf (Unit+Villa, whole window): %.0f AED/sqft", resi["price_psf"].median())
    log.info("VALIDATE %s", "PASSED" if ok else "FAILED")
    return ok


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-load", action="store_true", help="skip MySQL load/validate")
    args = ap.parse_args()
    t0 = time.time()
    try:
        raw = extract()
        profile(raw)
        clean = transform(raw)
        tables = build_star_schema(clean)
        save_csv(tables)
        if not args.no_load:
            engine = load(tables)
            if not validate(tables, engine):
                sys.exit(1)
    except Exception:
        log.exception("PIPELINE FAILED")
        sys.exit(1)
    log.info("PIPELINE finished in %.1fs", time.time() - t0)


if __name__ == "__main__":
    main()
