"""Add insight/ranking measures to fact_sales.tmdl. Safe to re-run: existing measures are skipped.

Close Power BI Desktop before running.
Usage (from the capstone folder):  python powerbi/scripts/add_measures.py
"""
import os
import sys
import uuid

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "DLD_Sales.SemanticModel", "definition", "tables", "fact_sales.tmdl")
text = open(path, encoding="utf-8").read().replace("\r\n", "\n")

AREA = "dim_area[area_name_en]"
MP = "dim_project[master_project_name]"
NEW = [
    ("Avg Monthly Transactions", "AVERAGEX(VALUES(dim_date[year]), [Transactions])", "#,0", "1 Volume"),
    ("Median PSF Off-Plan",
     'CALCULATE([Median PSF Residential], KEEPFILTERS(dim_procedure[reg_type_label] = "Off-Plan"))', "#,0", "2 Price"),
    ("Median PSF Ready",
     'CALCULATE([Median PSF Residential], KEEPFILTERS(dim_procedure[reg_type_label] = "Ready"))', "#,0", "2 Price"),
    ("Off-Plan PSF Premium %", "DIVIDE([Median PSF Off-Plan] - [Median PSF Ready], [Median PSF Ready])",
     "+0.0%;-0.0%;0.0%", "2 Price"),
    ("PSF Growth 2022-2025 %",
     "VAR p0 = CALCULATE([Median PSF Residential], REMOVEFILTERS(dim_date), dim_date[year] = 2022) "
     "VAR p1 = CALCULATE([Median PSF Residential], REMOVEFILTERS(dim_date), dim_date[year] = 2025) "
     "VAR n0 = CALCULATE([Residential Transactions], REMOVEFILTERS(dim_date), dim_date[year] = 2022) "
     "VAR n1 = CALCULATE([Residential Transactions], REMOVEFILTERS(dim_date), dim_date[year] = 2025) "
     "RETURN IF(n0 >= 300 && n1 >= 300, DIVIDE(p1 - p0, p0))", "+0.0%;-0.0%;0.0%", "4 YoY"),
    ("Area Rank Volume",
     f"IF(ISINSCOPE({AREA}), RANKX(ALLSELECTED({AREA}), [Transactions], , DESC))", "0", "5 Ranking"),
    ("Area Rank PSF",
     f"IF(ISINSCOPE({AREA}) && [Residential Transactions] >= 300, "
     f"RANKX(FILTER(ALLSELECTED({AREA}), [Residential Transactions] >= 300), [Median PSF Residential], , DESC))",
     "0", "5 Ranking"),
    ("Area Rank PSF Growth",
     f"IF(ISINSCOPE({AREA}) && NOT ISBLANK([PSF Growth 2022-2025 %]), "
     f"RANKX(FILTER(ALLSELECTED({AREA}), NOT ISBLANK([PSF Growth 2022-2025 %])), [PSF Growth 2022-2025 %], , DESC))",
     "0", "5 Ranking"),
    ("Project Rank Off-Plan",
     f'IF(ISINSCOPE({MP}) && SELECTEDVALUE({MP}) <> "Unknown", '
     f'RANKX(FILTER(ALLSELECTED({MP}), {MP} <> "Unknown"), [Off-Plan Transactions], , DESC))', "0", "5 Ranking"),
]

block = ""
added = []
for name, dax, fmt, folder in NEW:
    if f"measure '{name}'" in text:
        continue
    block += (f"\tmeasure '{name}' = {dax}\n\t\tformatString: {fmt}\n\t\tdisplayFolder: {folder}\n"
              f"\t\tlineageTag: {uuid.uuid4()}\n\n")
    added.append(name)
i = text.index("\tcolumn ")
text = text[:i] + block + text[i:]
with open(path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write(text)
print("added:", added)
