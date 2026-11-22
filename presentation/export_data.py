"""Export the numbers used by the deck charts to presentation/data.json.

Reads the processed star schema CSVs written by etl.py.
Usage (from the capstone folder):  myenv\\Scripts\\python.exe presentation\\export_data.py
"""
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "data", "processed")

f = pd.read_csv(os.path.join(P, "fact_sales.csv"))
d = pd.read_csv(os.path.join(P, "dim_date.csv"))
a = pd.read_csv(os.path.join(P, "dim_area.csv"))
pr = pd.read_csv(os.path.join(P, "dim_property.csv"))
pc = pd.read_csv(os.path.join(P, "dim_procedure.csv"))
x = f.merge(d, on="date_id").merge(a, on="area_id").merge(pr, on="property_id").merge(pc, on="procedure_id")
resi = x[x.property_type_label.isin(["Unit", "Villa"]) & (x.usage_label == "Residential")]

years = list(range(2007, 2026))  # complete years with meaningful volume
in_years = x[x.year.isin(years)]
by_year = in_years.groupby("year")


def per_year(frame):
    return [int(v) for v in frame.groupby("year").size().reindex(years, fill_value=0)]


out = {
    "years": years,
    "tx_offplan": per_year(in_years[in_years.reg_type_label == "Off-Plan"]),
    "tx_ready": per_year(in_years[in_years.reg_type_label == "Ready"]),
    "psf": [round(float(v)) for v in resi[resi.year.isin(years)].groupby("year").price_psf.median()],
    "offplan_share": [round(float(v) * 100, 1) for v in by_year.reg_type_label.apply(lambda s: (s == "Off-Plan").mean())],
    "value_bn": [round(float(v) / 1e9, 1) for v in by_year.price_aed.sum()],
}

complete = x[x.is_complete_year == 1]
monthly = complete.groupby(["year", "month"]).size().groupby("month").mean()
out["season"] = [round(float(v), 2) for v in (monthly / monthly.mean() * 100 - 100)]

top = x[x.year >= 2024].groupby("area_name_en").size().nlargest(8)
out["top_areas"] = {"names": list(top.index), "values": [int(v) for v in top.values]}


def ytd(frame, year):
    return frame[(frame.year == year) & (frame.full_date <= f"{year}-10-05")]


out["ytd"] = {"n26": len(ytd(x, 2026)), "n25": len(ytd(x, 2025)),
              "psf26": round(float(ytd(resi, 2026).price_psf.median())),
              "psf25": round(float(ytd(resi, 2025).price_psf.median()))}
out["totals"] = {"raw": 1372277, "clean": len(f), "value_bn": round(f.price_aed.sum() / 1e9, 1),
                 "areas": int(x.area_id.nunique())}

with open(os.path.join(HERE, "data.json"), "w") as fh:
    json.dump(out, fh, indent=1)
print("wrote presentation/data.json")
