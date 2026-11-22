"""Regenerate the PBIR report: blue theme, 5 pages x 3-4 charts, 1 tooltip page. Semantic model untouched.

WARNING: deletes and rebuilds DLD_Sales.Report/definition and StaticResources, so any edit made by hand in
Power BI Desktop is lost unless it is also written here. Close Power BI Desktop before running.

Usage (from the capstone folder):  python powerbi/scripts/gen_report.py
"""
import json
import os
import shutil
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = "DLD_Sales.Report"
S = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
V_REPORT, V_PAGE, V_VISUAL = "3.0.0", "2.0.0", "2.4.0"
BASE, CUSTOM = "CY25SU11", "DLD_Blue.json"
TOOLTIP = "tt_market"

for sub in ("definition", "StaticResources"):
    shutil.rmtree(os.path.join(ROOT, RP, sub), ignore_errors=True)


def wjson(rel, obj):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
NAVY, BLUE, SKY, PALE = "#0B2A55", "#1F5FAD", "#5DA9E9", "#D6E6F7"
INK, MUTED, PAGE_BG, LINE = "#14233C", "#5B6B82", "#EEF3F9", "#D9E3EF"


def solid(c):
    return {"solid": {"color": c}}


theme = {
    "name": "DLD Blue",
    "dataColors": [BLUE, SKY, NAVY, "#9CC8F0", "#2E86C1", "#7FA7D6", "#16467F", "#B9D9F5", "#3F7FBF", "#0E3A70"],
    "foreground": INK, "foregroundNeutralSecondary": MUTED, "foregroundNeutralTertiary": "#8A99AD",
    "background": "#FFFFFF", "backgroundLight": "#F5F8FC", "backgroundNeutral": LINE,
    "tableAccent": BLUE, "good": "#1E8E5A", "bad": "#C0392B", "neutral": "#D9A400",
    "maximum": NAVY, "center": SKY, "minimum": PALE,
    "textClasses": {
        "title": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": NAVY},
        "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": INK},
        "callout": {"fontFace": "Segoe UI Semibold", "fontSize": 26, "color": NAVY},
        "header": {"fontFace": "Segoe UI Semibold", "fontSize": 11, "color": NAVY},
    },
    "visualStyles": {
        "*": {"*": {
            "title": [{"show": True, "fontColor": solid(NAVY), "fontSize": 12, "fontFamily": "Segoe UI Semibold"}],
            "background": [{"show": True, "color": solid("#FFFFFF"), "transparency": 0}],
            "border": [{"show": True, "color": solid(LINE), "radius": 10}],
            "dropShadow": [{"show": True, "preset": "BottomRight", "transparency": 85}],
            "padding": [{"top": 10, "bottom": 10, "left": 12, "right": 12}],
            "categoryAxis": [{"showAxisTitle": False, "labelColor": solid(MUTED), "gridlineShow": False}],
            "valueAxis": [{"showAxisTitle": False, "labelColor": solid(MUTED),
                           "gridlineColor": solid("#E6ECF3"), "gridlineStyle": "dotted"}],
            "legend": [{"show": True, "position": "TopRight", "showTitle": False, "labelColor": solid(MUTED)}],
        }},
        "page": {"*": {
            "background": [{"color": solid(PAGE_BG), "transparency": 0}],
            "outspace": [{"color": solid(PAGE_BG), "transparency": 0}],
        }},
        "card": {"*": {
            "categoryLabels": [{"show": False}],
            "labels": [{"color": solid(NAVY), "fontSize": 24, "labelDisplayUnits": 1}],
            "title": [{"fontSize": 10, "fontColor": solid(MUTED), "fontFamily": "Segoe UI"}],
        }},
        "slicer": {"*": {
            "data": [{"mode": "Dropdown"}],
            "header": [{"show": False}],
            "items": [{"fontColor": solid(INK), "background": solid("#FFFFFF"), "textSize": 10}],
            "title": [{"fontSize": 9, "fontColor": solid(MUTED), "fontFamily": "Segoe UI"}],
            "padding": [{"top": 4, "bottom": 4, "left": 10, "right": 10}],
            "dropShadow": [{"show": False}],
        }},
        "textbox": {"*": {
            "background": [{"show": True, "color": solid(NAVY), "transparency": 0}],
            "border": [{"show": False}], "dropShadow": [{"show": False}], "title": [{"show": False}],
            "padding": [{"top": 8, "bottom": 4, "left": 20, "right": 20}],
        }},
        "lineChart": {"*": {"lineStyles": [{"strokeWidth": 3, "showMarker": False}]}},
        "clusteredBarChart": {"*": {"labels": [{"show": True, "color": solid(INK), "fontSize": 9}]}},
        "scatterChart": {"*": {"categoryLabels": [{"show": False}], "bubbles": [{"bubbleSize": -5}]}},
        "tableEx": {"*": {
            "columnHeaders": [{"backColor": solid(NAVY), "fontColor": solid("#FFFFFF"), "fontSize": 10}],
            "values": [{"fontColorPrimary": solid(INK), "backColorPrimary": solid("#FFFFFF"),
                        "fontColorSecondary": solid(INK), "backColorSecondary": solid("#F3F7FC"), "fontSize": 10}],
            "grid": [{"gridVertical": False, "gridHorizontalColor": solid(LINE), "rowPadding": 4}],
            "total": [{"backColor": solid(PALE), "fontColor": solid(NAVY)}],
        }},
    },
}
wjson(f"{RP}/StaticResources/RegisteredResources/{CUSTOM}", theme)
wjson(f"{RP}/StaticResources/SharedResources/BaseThemes/{BASE}.json",
      {"name": BASE, "dataColors": theme["dataColors"], "foreground": INK, "background": "#FFFFFF",
       "tableAccent": BLUE})
ver = {"visual": V_VISUAL, "report": V_REPORT, "page": V_PAGE}
wjson(f"{RP}/definition/version.json", {"$schema": f"{S}/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
wjson(f"{RP}/definition/report.json", {
    "$schema": f"{S}/report/{V_REPORT}/schema.json",
    "themeCollection": {
        "baseTheme": {"name": BASE, "reportVersionAtImport": ver, "type": "SharedResources"},
        "customTheme": {"name": CUSTOM, "reportVersionAtImport": ver, "type": "RegisteredResources"}},
    "resourcePackages": [
        {"name": "SharedResources", "type": "SharedResources",
         "items": [{"name": BASE, "path": f"BaseThemes/{BASE}.json", "type": "BaseTheme"}]},
        {"name": "RegisteredResources", "type": "RegisteredResources",
         "items": [{"name": CUSTOM, "path": CUSTOM, "type": "CustomTheme"}]}],
})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def col(e, p):
    return {"Column": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}


def mea(p, e="fact_sales"):
    return {"Measure": {"Expression": {"SourceRef": {"Entity": e}}, "Property": p}}


def proj(field, display=None):
    k = "Column" if "Column" in field else "Measure"
    e, p = field[k]["Expression"]["SourceRef"]["Entity"], field[k]["Property"]
    out = {"field": field, "queryRef": f"{e}.{p}", "nativeQueryRef": p}
    if display:
        out["displayName"] = display
    return out


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def f_in(entity, prop, value_literal, name):
    return {"name": name, "field": col(entity, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "d", "Entity": entity, "Type": 0}],
                       "Where": [{"Condition": {"In": {
                           "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}},
                                                       "Property": prop}}],
                           "Values": [[{"Literal": {"Value": value_literal}}]]}}}]}}


def f_top(measure, n, name):
    """Visual-level filter: measure <= n (used with rank measures for Top N)."""
    return {"name": name, "field": mea(measure), "type": "Advanced",
            "filter": {"Version": 2, "From": [{"Name": "f", "Entity": "fact_sales", "Type": 0}],
                       "Where": [{"Condition": {"Comparison": {
                           "ComparisonKind": 4,
                           "Left": {"Measure": {"Expression": {"SourceRef": {"Source": "f"}}, "Property": measure}},
                           "Right": {"Literal": {"Value": f"{n}L"}}}}}]}}


FULL_YEAR = f_in("dim_date", "is_complete_year", "1L", "complete_year")
FULL_MONTH = f_in("dim_date", "is_complete_month", "1L", "complete_month")


def build_visual(name, i, v):
    x, y, w, h = v["pos"]
    vis = {"$schema": f"{S}/visualContainer/{V_VISUAL}/schema.json", "name": name,
           "position": {"x": round(x, 1), "y": round(y, 1), "z": i * 1000, "width": round(w, 1),
                        "height": round(h, 1), "tabOrder": i * 1000}}
    if v["type"] == "textbox":
        paras = [{"textRuns": [{"value": v["text"], "textStyle": {
            "fontFamily": "Segoe UI Semibold", "fontSize": v.get("size", "18pt"), "color": "#FFFFFF"}}]}]
        if v.get("sub"):
            paras.append({"textRuns": [{"value": v["sub"], "textStyle": {
                "fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#BFD6F2"}}]})
        vis["visual"] = {"visualType": "textbox", "objects": {"general": [{"properties": {"paragraphs": paras}}]},
                         "drillFilterOtherVisuals": True}
        return vis
    body = {"visualType": v["type"],
            "query": {"queryState": {role: {"projections": [proj(*f) if isinstance(f, tuple) else proj(f)
                                                            for f in fields]}
                                     for role, fields in v["roles"].items()}},
            "drillFilterOtherVisuals": True}
    if "sort" in v:
        f, d = v["sort"]
        body["query"]["sortDefinition"] = {"sort": [{"field": f, "direction": d}], "isDefaultSort": False}
    vco = {}
    if "title" in v:
        vco["title"] = [{"properties": {"show": lit("true"),
                                        "text": lit("'" + v["title"].replace("'", "''") + "'")}}]
        if "title_size" in v:
            vco["title"][0]["properties"]["fontSize"] = lit(f"{v['title_size']}D")
    if v.get("tooltip"):
        vco["visualTooltip"] = [{"properties": {"show": lit("true"), "type": lit("'Canvas'"),
                                                "section": lit(f"'{TOOLTIP}'")}}]
    if vco:
        body["visualContainerObjects"] = vco
    if "objects" in v:
        body["objects"] = v["objects"]
    vis["visual"] = body
    if v.get("filters"):
        vis["filterConfig"] = {"filters": v["filters"]}
    return vis


pages = []
W, H = 1280, 720
M, G = 20, 16
HEADER_H = 72
SLICER_Y, SLICER_H = HEADER_H + 10, 56
TOP = SLICER_Y + SLICER_H + 12          # first content row
CW = W - 2 * M                          # content width
HALF = (CW - G) / 2
THIRD = (CW - 2 * G) / 3


def slicers():
    w = 220
    specs = [(col("dim_date", "year"), "Year"),
             (col("dim_procedure", "reg_type_label"), "Registration type"),
             (col("dim_property", "property_type_label"), "Property type"),
             (col("dim_area", "area_name_en"), "Area")]
    return [{"type": "slicer", "pos": (M + i * (w + G), SLICER_Y, w, SLICER_H), "roles": {"Values": [f]}, "title": t}
            for i, (f, t) in enumerate(specs)]


def page(name, display, subtitle, visuals):
    pages.append(name)
    wjson(f"{RP}/definition/pages/{name}/page.json", {
        "$schema": f"{S}/page/{V_PAGE}/schema.json", "name": name, "displayName": display,
        "displayOption": "FitToPage", "height": H, "width": W})
    header = [{"type": "textbox", "pos": (0, 0, W, HEADER_H),
               "text": f"Dubai Real Estate Sales  |  {display}", "sub": subtitle}]
    for i, v in enumerate(header + slicers() + visuals):
        vname = f"{name}_v{i:02d}"
        wjson(f"{RP}/definition/pages/{name}/visuals/{vname}/visual.json", build_visual(vname, i, v))


def grid2x2():
    h = (H - TOP - M - G) / 2
    return [(M, TOP, HALF, h), (M + HALF + G, TOP, HALF, h),
            (M, TOP + h + G, HALF, h), (M + HALF + G, TOP + h + G, HALF, h)]


YEAR, MONTH = col("dim_date", "year"), col("dim_date", "year_month_label")
REG = col("dim_procedure", "reg_type_label")
AREA = col("dim_area", "area_name_en")

# 1. Overview: KPI row + 3 charts --------------------------------------------
kpi_h = 88
kw = (CW - 3 * G) / 4
kpis = [{"type": "card", "pos": (M + i * (kw + G), TOP, kw, kpi_h), "roles": {"Values": [mea(m)]}, "title": t}
        for i, (m, t) in enumerate([
            ("Transactions", "Transactions"), ("Total Value AED bn", "Total value (AED bn)"),
            ("Median PSF Residential", "Median price per sqft, residential (AED)"),
            ("Off-Plan Share", "Off-plan share of transactions")])]
cy = TOP + kpi_h + G
ch = H - cy - M
page("overview", "Overview", "Registered sale transactions, Dubai Land Department, 2004 to 5 Oct 2026", kpis + [
    {"type": "clusteredColumnChart", "pos": (M, cy, THIRD, ch),
     "roles": {"Category": [YEAR], "Y": [mea("Transactions")], "Series": [REG]},
     "title": "Transactions per year (complete years)", "filters": [FULL_YEAR], "tooltip": True},
    {"type": "clusteredColumnChart", "pos": (M + THIRD + G, cy, THIRD, ch),
     "roles": {"Category": [YEAR], "Y": [mea("Total Value AED bn")]},
     "title": "Total value per year, AED bn (complete years)", "filters": [FULL_YEAR], "tooltip": True},
    {"type": "lineChart", "pos": (M + 2 * (THIRD + G), cy, THIRD, ch),
     "roles": {"Category": [YEAR], "Y": [mea("Median PSF Residential")]},
     "title": "Median residential price per sqft (AED)", "tooltip": True},
])

# 2. Market trend: 2x2 --------------------------------------------------------
g = grid2x2()
page("trend", "Market trend", "Monthly momentum, seasonality and year-over-year change", [
    {"type": "lineChart", "pos": g[0],
     "roles": {"Category": [MONTH], "Y": [mea("Transactions")], "Series": [REG]},
     "title": "Monthly transactions (complete months)", "filters": [FULL_MONTH], "tooltip": True},
    {"type": "lineChart", "pos": g[1],
     "roles": {"Category": [MONTH], "Y": [mea("Median PSF Residential")]},
     "title": "Monthly median residential price per sqft (AED)", "filters": [FULL_MONTH], "tooltip": True},
    {"type": "clusteredColumnChart", "pos": g[2],
     "roles": {"Category": [col("dim_date", "month_name")], "Y": [mea("Avg Monthly Transactions")]},
     "sort": (col("dim_date", "month_name"), "Ascending"),
     "title": "Seasonality: average transactions per calendar month (complete years)", "filters": [FULL_YEAR]},
    {"type": "tableEx", "pos": g[3],
     "roles": {"Values": [(YEAR, "Year"), (mea("Transactions"), "Transactions"),
                          (mea("Transactions YoY %"), "YoY"), (mea("Total Value AED bn"), "AED bn"),
                          (mea("Median PSF Residential"), "Median PSF"), (mea("Median PSF YoY %"), "PSF YoY")]},
     "sort": (YEAR, "Descending"),
     "title": "Year over year (2026 = 1 Jan to 5 Oct vs same period 2025)"},
])

# 3. Off-Plan vs Ready: 2x2 ---------------------------------------------------
page("offplan", "Off-Plan vs Ready", "Pre-construction sales versus completed property", [
    {"type": "lineChart", "pos": g[0],
     "roles": {"Category": [YEAR], "Y": [mea("Off-Plan Share")]},
     "title": "Off-plan share of transactions by year", "tooltip": True},
    {"type": "lineChart", "pos": g[1],
     "roles": {"Category": [YEAR], "Y": [mea("Median PSF Residential")], "Series": [REG]},
     "title": "Median residential price per sqft: Off-Plan vs Ready (AED)", "tooltip": True},
    {"type": "clusteredBarChart", "pos": g[2],
     "roles": {"Category": [col("dim_project", "master_project_name")], "Y": [mea("Off-Plan Transactions")]},
     "sort": (mea("Off-Plan Transactions"), "Descending"),
     "title": "Top 10 master projects by off-plan transactions",
     "filters": [f_top("Project Rank Off-Plan", 10, "top10_project")], "tooltip": True},
    {"type": "clusteredBarChart", "pos": g[3],
     "roles": {"Category": [col("dim_procedure", "procedure_name_en")], "Y": [mea("Transactions")]},
     "sort": (mea("Transactions"), "Descending"),
     "title": "Transactions by DLD procedure"},
])

# 4. Areas: 2x2 ---------------------------------------------------------------
page("areas", "Areas", "Where the market trades, what it costs and where prices rise fastest", [
    {"type": "clusteredBarChart", "pos": g[0],
     "roles": {"Category": [AREA], "Y": [mea("Transactions")]}, "sort": (mea("Transactions"), "Descending"),
     "title": "Top 15 areas by transactions", "filters": [f_top("Area Rank Volume", 15, "top15_volume")],
     "tooltip": True},
    {"type": "clusteredBarChart", "pos": g[1],
     "roles": {"Category": [AREA], "Y": [mea("Median PSF Residential")]},
     "sort": (mea("Median PSF Residential"), "Descending"),
     "title": "Top 15 most expensive areas, median PSF (min 300 residential sales)",
     "filters": [f_top("Area Rank PSF", 15, "top15_psf")], "tooltip": True},
    {"type": "clusteredBarChart", "pos": g[2],
     "roles": {"Category": [AREA], "Y": [mea("PSF Growth 2022-2025 %")]},
     "sort": (mea("PSF Growth 2022-2025 %"), "Descending"),
     "title": "Top 15 areas by median PSF growth, 2022 to 2025",
     "filters": [f_top("Area Rank PSF Growth", 15, "top15_growth")], "tooltip": True},
    {"type": "scatterChart", "pos": g[3],
     "roles": {"Category": [AREA], "X": [mea("Transactions")], "Y": [mea("Median PSF Residential")]},
     "title": "Volume vs price per area (each dot = one area)", "tooltip": True},
])

# 5. Property: 2x2 ------------------------------------------------------------
ROOMS = col("dim_property", "rooms_label")
page("property", "Property", "How property type, bedrooms and parking relate to price", [
    {"type": "clusteredColumnChart", "pos": g[0],
     "roles": {"Category": [ROOMS], "Y": [mea("Median PSF Residential")]}, "sort": (ROOMS, "Ascending"),
     "title": "Median residential price per sqft by bedrooms (AED)", "tooltip": True},
    {"type": "clusteredColumnChart", "pos": g[1],
     "roles": {"Category": [ROOMS], "Y": [mea("Residential Transactions")]}, "sort": (ROOMS, "Ascending"),
     "title": "Residential transactions by bedrooms", "tooltip": True},
    {"type": "hundredPercentStackedColumnChart", "pos": g[2],
     "roles": {"Category": [YEAR], "Y": [mea("Transactions")], "Series": [col("dim_property", "property_type_label")]},
     "title": "Property type mix by year", "tooltip": True},
    {"type": "clusteredBarChart", "pos": g[3],
     "roles": {"Category": [col("dim_property", "parking_label")], "Y": [mea("Median PSF Residential")]},
     "title": "Median residential price per sqft by parking (AED)", "tooltip": True},
])

# 6. Tooltip page -------------------------------------------------------------
TW, TH = 420, 270
small = {"labels": [{"properties": {"fontSize": lit("16D")}}]}
cw3 = (TW - 2 * 10 - 2 * 8) / 3
tt_visuals = [
    {"type": "textbox", "pos": (0, 0, TW, 36), "text": "Market snapshot", "size": "12pt"},
] + [
    {"type": "card", "pos": (10 + i * (cw3 + 8), 44, cw3, 70), "roles": {"Values": [mea(m)]}, "title": t,
     "title_size": 8, "objects": small}
    for i, (m, t) in enumerate([("Transactions", "Transactions"), ("Median PSF Residential", "Median PSF (AED)"),
                                ("Off-Plan Share", "Off-plan share")])
] + [
    {"type": "clusteredBarChart", "pos": (10, 122, TW - 20, TH - 132),
     "roles": {"Category": [col("dim_property", "property_type_label")], "Y": [mea("Transactions")]},
     "sort": (mea("Transactions"), "Descending"), "title": "Transactions by property type"},
]
wjson(f"{RP}/definition/pages/{TOOLTIP}/page.json", {
    "$schema": f"{S}/page/{V_PAGE}/schema.json", "name": TOOLTIP, "displayName": "Tooltip - market snapshot",
    "displayOption": "ActualSize", "height": TH, "width": TW, "type": "Tooltip",
    "visibility": "HiddenInViewMode", "pageBinding": {"name": "tt_market_binding", "type": "Tooltip"}})
for i, v in enumerate(tt_visuals):
    vname = f"{TOOLTIP}_v{i:02d}"
    wjson(f"{RP}/definition/pages/{TOOLTIP}/visuals/{vname}/visual.json", build_visual(vname, i, v))

wjson(f"{RP}/definition/pages/pages.json", {"$schema": f"{S}/pagesMetadata/1.0.0/schema.json",
                                            "pageOrder": pages + [TOOLTIP], "activePageName": pages[0]})
print("report regenerated:", ", ".join(pages + [TOOLTIP]))
