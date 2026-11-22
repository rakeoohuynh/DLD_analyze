// Build the capstone deck: presentation/DLD_capstone.pptx
// Usage (from presentation/):  npm install   then   node build_deck.js
// Chart numbers come from data.json (export_data.py); ML numbers come from ML.ipynb.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "data.json"), "utf8"));
const OUT = path.join(__dirname, "DLD_capstone.pptx");

// Speaker notes come from script.md: section "## N. ..." holds the bullets for slide N.
const SCRIPT = fs.readFileSync(path.join(__dirname, "script.md"), "utf8").replace(/\r\n/g, "\n");
const NOTES = {};
for (const m of SCRIPT.matchAll(/^## (\d+)\. [^\n]*\n([\s\S]*?)(?=^## |^---|(?![\s\S]))/gm)) NOTES[+m[1]] = m[2].trim();
let noteIndex = 0;
function slideNotes(slide) {
  noteIndex += 1;
  if (!NOTES[noteIndex]) throw new Error(`script.md has no section "## ${noteIndex}."`);
  slide.addNotes(NOTES[noteIndex]);
}

// ---------------------------------------------------------------- palette
const NAVY = "0B2A55", BLUE = "1F5FAD", SKY = "5DA9E9", PALE = "D6E6F7", TINT = "EEF3F9";
const INK = "14233C", MUTED = "5B6B82", LINE = "D9E3EF", ORANGE = "E67E22", WHITE = "FFFFFF";
const HEAD = "Cambria", BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "Dubai Real Estate Sales 2004-2026";
pres.subject = "Capstone Data Analyst";
pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };

const W = 13.333, M = 0.6, CW = W - 2 * M;
const fmt = (n) => String(n).replace(/\B(?=(\d{3})+(?!\d))/g, "."); // Vietnamese thousands separator

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "DARK",
  background: { color: NAVY },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.3, w: CW, h: 1.6, fontFace: HEAD,
        fontSize: 40, bold: true, color: WHITE, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 4.05, w: CW, h: 1.2, fontFace: BODY,
        fontSize: 18, color: PALE, valign: "top", align: "left" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: WHITE },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: CW, h: 0.75, fontFace: HEAD,
        fontSize: 30, bold: true, color: NAVY, valign: "middle", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 1.08, w: CW, h: 0.5, fontFace: BODY,
        fontSize: 16, color: MUTED, valign: "top", align: "left" }, text: "" } },
    { text: { text: "Dubai DLD Sales  |  Capstone Data Analyst", options: { x: M, y: 7.0, w: 6, h: 0.3,
        fontFace: BODY, fontSize: 10, color: MUTED, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontFace: BODY, fontSize: 10, color: MUTED, align: "right" },
});

// ---------------------------------------------------------------- helpers
const shadow = () => ({ type: "outer", color: "8A99AD", blur: 6, offset: 2, angle: 90, opacity: 0.25 });

function card(slide, x, y, w, h, fill = TINT, name = "card") {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill },
    line: { color: fill }, shadow: shadow(), objectName: name });
}

function stat(slide, x, y, w, value, label, color = NAVY, valueSize = 40) {
  slide.addText(value, { x, y, w, h: 0.8, fontFace: HEAD, fontSize: valueSize, bold: true, color, margin: 0,
    isTextBox: true, valign: "bottom" });
  slide.addText(label, { x, y: y + 0.85, w, h: 0.7, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0,
    isTextBox: true, valign: "top" });
}

function badge(slide, x, y, text, fill = BLUE, d = 0.55) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  slide.addText(text, { x, y, w: d, h: d, fontFace: HEAD, fontSize: 16, bold: true, color: WHITE,
    align: "center", valign: "middle", margin: 0, isTextBox: true });
}

function content(section, title, sub) {
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (sub) s.addText(sub, { placeholder: "body" });
  return s;
}

const axis = {
  catAxisLabelColor: MUTED, valAxisLabelColor: MUTED, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "E6ECF3", size: 0.75 },
  catGridLine: { style: "none" }, catAxisLineShow: false, valAxisLineShow: false,
  legendFontFace: "+mn-lt", legendFontSize: 12, legendColor: MUTED, dataLabelFontFace: "+mn-lt",
};

// ================================================================ 1. Title
pres.addSection({ title: "Mở đầu" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Mở đầu" });
s.addText("Thị trường bất động sản Dubai 2004–2026", { placeholder: "title" });
s.addText("Phân tích 1,34 triệu giao dịch mua bán đăng ký tại Dubai Land Department\nPython ETL · MySQL · Power BI · Machine Learning",
  { placeholder: "body" });
slideNotes(s);

// ================================================================ 2. Executive summary
s = content("Mở đầu", "Tóm tắt: thị trường bùng nổ, nhưng 2026 bắt đầu chững lại",
  "Bốn con số quan trọng nhất của bài phân tích");
const kpis = [
  [`×${((D.tx_offplan.at(-1) + D.tx_ready.at(-1)) / (D.tx_offplan[13] + D.tx_ready[13])).toFixed(1).replace(".", ",")}`,
    "số giao dịch năm 2025 so với 2020 (32 nghìn → 210 nghìn)", BLUE],
  [`+${Math.round((D.psf.at(-1) / D.psf[13] - 1) * 100)}%`, "giá/sqft nhà ở từ đáy 2020 đến 2025", BLUE],
  [`${D.offplan_share.at(-1).toString().replace(".", ",")}%`, "giao dịch năm 2025 là Off-Plan (mua trước khi xây xong)", BLUE],
  [`${Math.round((D.ytd.n26 / D.ytd.n25 - 1) * 100)}%`, "số giao dịch 2026 so với cùng kỳ 2025, dù giá vẫn tăng nhẹ", ORANGE],
];
const kw = (CW - 3 * 0.3) / 4;
kpis.forEach(([v, l, c], i) => {
  const x = M + i * (kw + 0.3);
  card(s, x, 1.95, kw, 2.6, TINT, `kpi_${i}`);
  stat(s, x + 0.3, 2.35, kw - 0.6, v, l, c, 48);
});
s.addText("Thị trường đang chuyển từ giai đoạn tăng nóng sang chọn lọc: vị trí và loại sản phẩm quyết định giá nhiều hơn chu kỳ chung.",
  { x: M, y: 5.0, w: CW, h: 0.8, fontFace: BODY, fontSize: 18, italic: true, color: INK, margin: 0, isTextBox: true });
slideNotes(s);

// ================================================================ 3. Pipeline
pres.addSection({ title: "Dữ liệu và ETL" });
s = content("Dữ liệu và ETL", "Quy trình dữ liệu: từ CSV thô đến dashboard và mô hình",
  "Một lệnh python etl.py chạy toàn bộ: extract → profile → transform → star schema → load → validate");
const steps = [
  ["CSV thô", "1.372.277 dòng\n20 cột, 239 MB"],
  ["Python ETL", "pandas: làm sạch,\nchuẩn hóa, tách bảng"],
  ["MySQL", "database dld\n6 bảng, có khóa"],
  ["Power BI", "5 trang dashboard\n+ trang tooltip"],
  ["ML notebook", "định giá và\nphân cụm khu vực"],
];
const sw = 2.05, gap = (CW - 5 * sw) / 4;
steps.forEach(([t, d], i) => {
  const x = M + i * (sw + gap);
  card(s, x, 2.0, sw, 2.0, i === 2 ? NAVY : TINT, `step_${i}`);
  s.addText(t, { x: x + 0.2, y: 2.2, w: sw - 0.4, h: 0.5, fontFace: HEAD, fontSize: 18, bold: true,
    color: i === 2 ? WHITE : NAVY, margin: 0, isTextBox: true });
  s.addText(d, { x: x + 0.2, y: 2.8, w: sw - 0.4, h: 1.0, fontFace: BODY, fontSize: 14,
    color: i === 2 ? PALE : MUTED, margin: 0, isTextBox: true });
  if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + sw + gap / 2 - 0.17, y: 2.85, w: 0.34, h: 0.3,
    fill: { color: SKY }, line: { color: SKY } });
});
const pst = [
  [fmt(D.totals.clean), "giao dịch sạch được giữ lại"],
  [`${(D.totals.clean / D.totals.raw * 100).toFixed(1).replace(".", ",")}%`, "dữ liệu gốc còn lại sau lọc"],
  ["11/11", "bước kiểm tra sau khi load đều đạt"],
];
pst.forEach(([v, l], i) => stat(s, M + i * (CW / 3), 4.6, CW / 3 - 0.4, v, l, BLUE, 36));
slideNotes(s);

// ================================================================ 4. Data quality
s = content("Dữ liệu và ETL", "Dữ liệu “trông sạch” nhưng có 5 vấn đề cần xử lý",
  "Mỗi vấn đề được xử lý có lý do, không xóa dòng một cách im lặng");
const hdr = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontFace: BODY, fontSize: 14 } });
const cell = (t, o = {}) => ({ text: t, options: { fontFace: BODY, fontSize: 13, color: INK, ...o } });
const rows = [
  [hdr("Vấn đề"), hdr("Quy mô"), hdr("Cách xử lý")],
  [cell("Dòng bị gắn cờ chất lượng (giá, diện tích vô lý, outlier)"), cell("28.495 dòng"), cell("Loại bỏ, dùng cờ quality_flags có sẵn của nguồn")],
  [cell("Dữ liệu trước 2004 quá thưa"), cell("8.386 dòng"), cell("Giới hạn khung phân tích 2004 – 05/10/2026")],
  [cell("Mã thủ tục trống, toàn bộ ở năm 2026"), cell("23.324 dòng"), cell("Khôi phục từ transaction_id (khớp 100%)", { bold: true, color: BLUE })],
  [cell("Tên dự án, tòa nhà lệch chữ hoa/thường; thiếu tên"), cell("~400 nghìn ô trống"), cell("Gộp cách viết phổ biến nhất; ô trống → “Unknown”")],
  [cell("Dòng giống hệt nhau, chỉ khác mã giao dịch"), cell("~118 nghìn dòng"), cell("Giữ lại: chủ đầu tư bán nhiều căn cùng mẫu; ghi chú khi phân tích")],
  [cell("Tháng 10/2026 và năm 2026 chưa đủ dữ liệu"), cell("1 tháng, 1 năm"), cell("Cờ is_complete_month/year để lọc khi tính xu hướng")],
];
s.addTable(rows, { x: M, y: 1.85, w: CW, colW: [5.0, 2.0, CW - 7.0], border: { type: "solid", color: LINE, pt: 0.75 },
  fill: { color: WHITE }, rowH: 0.62, valign: "middle", margin: [0.06, 0.12, 0.06, 0.12] });
slideNotes(s);

// ================================================================ 4b. Recovering procedure_id (real examples)
s = content("Dữ liệu và ETL", "Khôi phục mã thủ tục: transaction_id chứa sẵn đáp án",
  "Ví dụ thật từ dataset · phần thứ hai của transaction_id chính là procedure_id");
// Anatomy of one real id: 1-11-2025-19755
const parts = [["1", "tiền tố", MUTED], ["11", "mã thủ tục", ORANGE], ["2025", "năm", MUTED], ["19755", "số thứ tự", MUTED]];
const pw = [1.0, 1.4, 1.7, 2.1], pg = 0.45;
let px = (W - (pw.reduce((a, b) => a + b) + pg * 3)) / 2;
card(s, M, 1.75, CW, 1.75, TINT, "anatomy");
parts.forEach(([t, l, c], i) => {
  s.addText(t, { x: px, y: 1.9, w: pw[i], h: 0.85, fontFace: HEAD, fontSize: 40, bold: true, align: "center",
    color: i === 1 ? ORANGE : NAVY, margin: 0, isTextBox: true, valign: "middle" });
  s.addText(l, { x: px, y: 2.8, w: pw[i], h: 0.4, fontFace: BODY, fontSize: 14, align: "center",
    color: c, bold: i === 1, margin: 0, isTextBox: true });
  if (i < 3) s.addText("–", { x: px + pw[i], y: 1.9, w: pg, h: 0.85, fontFace: HEAD, fontSize: 36, color: MUTED,
    align: "center", valign: "middle", margin: 0, isTextBox: true });
  px += pw[i] + pg;
});
const idRuns = (id) => {
  const [a, b, ...rest] = id.split("-");
  return [{ text: `${a}-`, options: {} }, { text: b, options: { bold: true, color: ORANGE } }, { text: `-${rest.join("-")}`, options: {} }];
};
const th = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontFace: BODY, fontSize: 13 } });
const td = (t, o = {}) => ({ text: t, options: { fontFace: BODY, fontSize: 13, color: INK, ...o } });
const tw = (CW - 0.4) / 2;
s.addText("Dòng có đủ dữ liệu: phần giữa luôn trùng procedure_id", { x: M, y: 3.7, w: tw, h: 0.4, fontFace: BODY,
  fontSize: 14, bold: true, color: NAVY, margin: 0, isTextBox: true });
s.addTable([
  [th("transaction_id"), th("procedure_id"), th("Thủ tục")],
  [td(idRuns("1-11-2025-19755")), td("11"), td("Sell")],
  [td(idRuns("1-102-2025-41486")), td("102"), td("Sell - Pre registration")],
  [td(idRuns("1-41-2025-16781")), td("41"), td("Delayed Sell")],
], { x: M, y: 4.15, w: tw, colW: [2.3, 1.3, tw - 3.6], rowH: 0.42, border: { type: "solid", color: LINE, pt: 0.75 },
  fill: { color: WHITE }, valign: "middle", margin: [0.04, 0.1, 0.04, 0.1] });
s.addText("Dòng năm 2026 bị trống: suy ra từ phần giữa", { x: M + tw + 0.4, y: 3.7, w: tw, h: 0.4, fontFace: BODY,
  fontSize: 14, bold: true, color: NAVY, margin: 0, isTextBox: true });
s.addTable([
  [th("transaction_id"), th("procedure_id gốc"), th("Sau khôi phục")],
  [td(idRuns("1-11-2026-11120")), td("(trống)", { color: MUTED, italic: true }), td("11 · Sell", { bold: true, color: BLUE })],
  [td(idRuns("1-11-2026-11990")), td("(trống)", { color: MUTED, italic: true }), td("11 · Sell", { bold: true, color: BLUE })],
  [td(idRuns("1-11-2026-21059")), td("(trống)", { color: MUTED, italic: true }), td("11 · Sell", { bold: true, color: BLUE })],
], { x: M + tw + 0.4, y: 4.15, w: tw, colW: [2.3, 1.7, tw - 4.0], rowH: 0.42, border: { type: "solid", color: LINE, pt: 0.75 },
  fill: { color: WHITE }, valign: "middle", margin: [0.04, 0.1, 0.04, 0.1] });
[["1.320.458", "dòng kiểm chứng, khớp 100%"], ["23.324", "dòng 2026 khôi phục thành Sell"],
 ["0", "dòng phải gán “Unknown”"]].forEach(([v, l], i) => {
  const x = M + i * (CW / 3);
  s.addText([{ text: `${v}  `, options: { fontFace: HEAD, fontSize: 22, bold: true, color: i === 1 ? ORANGE : NAVY } },
    { text: l, options: { fontFace: BODY, fontSize: 13, color: MUTED } }],
    { x, y: 6.05, w: CW / 3 - 0.2, h: 0.7, margin: 0, valign: "middle", isTextBox: true });
});
slideNotes(s);

// ================================================================ 5. Star schema
s = content("Dữ liệu và ETL", "Mô hình star schema: 1 bảng fact và 5 bảng dimension",
  "Tách bảng phẳng 20 cột thành mô hình quan hệ để Power BI lọc nhanh và DAX gọn");
const cx = W / 2 - 1.6, cy = 3.35;
card(s, cx, cy, 3.2, 1.9, NAVY, "fact");
s.addText([{ text: "fact_sales", options: { bold: true, fontSize: 20, fontFace: HEAD, color: WHITE, breakLine: true } },
  { text: `${fmt(D.totals.clean)} dòng`, options: { fontSize: 14, color: PALE, breakLine: true } },
  { text: "price_aed · area_sqm · price_psf", options: { fontSize: 13, color: PALE } }],
  { x: cx + 0.2, y: cy + 0.15, w: 2.8, h: 1.6, fontFace: BODY, margin: 0, valign: "middle", align: "center", isTextBox: true });
const dims = [
  ["dim_date", "8.310 ngày · năm, quý, tháng,\ncờ tháng/năm đủ dữ liệu", M + 0.2, 1.85],
  ["dim_area", "197 khu vực của DLD", W - M - 3.4, 1.85],
  ["dim_project", "10.028 dự án / tòa nhà", M + 0.2, 5.25],
  ["dim_property", "140 tổ hợp: loại, số phòng,\nmục đích, chỗ đậu xe", W - M - 3.4, 5.25],
  ["dim_procedure", "18 thủ tục · Off-Plan / Ready", W / 2 - 1.6, 5.6],
];
dims.forEach(([n, d, x, y]) => {
  card(s, x, y, 3.2, 1.1, TINT, n);
  s.addText([{ text: n, options: { bold: true, fontSize: 16, fontFace: HEAD, color: NAVY, breakLine: true } },
    { text: d, options: { fontSize: 12, color: MUTED } }],
    { x: x + 0.2, y: y + 0.08, w: 2.8, h: 0.95, fontFace: BODY, margin: 0, valign: "middle", isTextBox: true });
});
[[M + 3.4, 2.4, cx, cy + 0.4], [W - M - 3.4, 2.4, cx + 3.2, cy + 0.4], [M + 3.4, 5.8, cx, cy + 1.6],
 [W - M - 3.4, 5.8, cx + 3.2, cy + 1.6], [W / 2, 5.6, W / 2, cy + 1.9]].forEach(([x1, y1, x2, y2]) => {
  s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001,
    h: Math.abs(y2 - y1) || 0.001, flipH: (x2 < x1) !== (y2 < y1), line: { color: SKY, width: 1.5 } });
});
slideNotes(s);

// ================================================================ 6. Volume boom
pres.addSection({ title: "Insight thị trường" });
s = content("Insight thị trường", "Số giao dịch tăng gấp 6,5 lần chỉ trong 5 năm",
  "Giao dịch mua bán mỗi năm, chia theo Off-Plan và Ready (2007–2025, các năm trọn vẹn)");
s.addChart(pres.charts.BAR, [
  { name: "Off-Plan", labels: D.years.map(String), values: D.tx_offplan },
  { name: "Ready", labels: D.years.map(String), values: D.tx_ready },
], { x: M, y: 1.7, w: 8.6, h: 5.1, barDir: "col", barGrouping: "stacked", chartColors: [BLUE, SKY], showLegend: true,
  legendPos: "t", valAxisLabelFormatCode: "#,##0", ...axis });
card(s, 9.6, 1.9, 3.13, 4.7, TINT, "callouts");
stat(s, 9.9, 2.1, 2.6, "210.438", "giao dịch năm 2025, cao nhất lịch sử", NAVY, 34);
stat(s, 9.9, 3.6, 2.6, "589 tỷ", "AED tổng giá trị giao dịch năm 2025", NAVY, 34);
stat(s, 9.9, 5.0, 2.6, "2009", "lần đầu Off-Plan xuất hiện, rồi sụp cùng khủng hoảng", MUTED, 28);
slideNotes(s);

// ================================================================ 7. Price
s = content("Insight thị trường", "Giá nhà ở tăng 83% từ đáy năm 2020",
  "Median giá/sqft nhà ở (căn hộ và villa, mục đích Residential), AED");
s.addChart(pres.charts.LINE, [{ name: "Median PSF", labels: D.years.map(String), values: D.psf }],
  { x: M, y: 1.7, w: 8.6, h: 5.1, chartColors: [BLUE], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 6,
    showLegend: false, valAxisLabelFormatCode: "#,##0", ...axis });
card(s, 9.6, 1.9, 3.13, 4.7, TINT, "callouts");
stat(s, 9.9, 2.1, 2.6, `${fmt(D.psf.at(-1))}`, "AED/sqft năm 2025, đỉnh mới", NAVY, 34);
stat(s, 9.9, 3.6, 2.6, "+26%", "năm 2022, mức tăng mạnh nhất trong 1 năm", NAVY, 34);
stat(s, 9.9, 5.0, 2.6, "Median", "dùng thay trung bình vì giá lệch phải mạnh", MUTED, 28);
slideNotes(s);

// ================================================================ 8. 2026 slowdown
s = content("Insight thị trường", "2026: lượng mua giảm, nhưng giá chưa giảm",
  "So sánh cùng kỳ 1/1 – 5/10 của năm 2026 với năm 2025");
const dn = Math.round((D.ytd.n26 / D.ytd.n25 - 1) * 100), dp = Math.round((D.ytd.psf26 / D.ytd.psf25 - 1) * 100);
card(s, M, 1.9, 5.8, 2.6, TINT, "volume");
stat(s, M + 0.4, 2.2, 5.0, `${dn}%`, `số giao dịch: ${fmt(D.ytd.n25)} → ${fmt(D.ytd.n26)}`, ORANGE, 66);
card(s, M + 6.3, 1.9, 5.8, 2.6, TINT, "price");
stat(s, M + 6.7, 2.2, 5.0, `+${dp}%`, `median giá/sqft nhà ở: ${fmt(D.ytd.psf25)} → ${fmt(D.ytd.psf26)} AED`, BLUE, 66);
s.addText([
  { text: "Ý nghĩa: ", options: { bold: true, color: NAVY } },
  { text: "người mua bắt đầu thận trọng, nhưng người bán chưa giảm giá. Đây thường là tín hiệu đầu tiên của giai đoạn hạ nhiệt.", options: { breakLine: true } },
  { text: "Lưu ý: ", options: { bold: true, color: NAVY } },
  { text: "các tháng gần nhất có thể chưa đăng ký đủ, nên mức giảm thực tế có thể nhỏ hơn." },
], { x: M, y: 4.9, w: CW, h: 1.2, fontFace: BODY, fontSize: 16, color: INK, margin: 0, paraSpaceAfter: 6, isTextBox: true });
slideNotes(s);

// ================================================================ 9. Off-plan
const opYears = D.years.slice(2), opShare = D.offplan_share.slice(2);
s = content("Insight thị trường", "Off-Plan dẫn dắt thị trường và được bán giá cao hơn",
  "Tỷ lệ giao dịch Off-Plan trên tổng số giao dịch mỗi năm (%)");
s.addChart(pres.charts.LINE, [{ name: "Off-Plan share", labels: opYears.map(String), values: opShare }],
  { x: M, y: 1.7, w: 8.6, h: 5.1, chartColors: [BLUE], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 6,
    showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 80, valAxisLabelFormatCode: "0", ...axis });
card(s, 9.6, 1.9, 3.13, 4.7, TINT, "callouts");
stat(s, 9.9, 2.1, 2.6, "62,6%", "giao dịch năm 2025 là Off-Plan (2021: 39%)", NAVY, 34);
stat(s, 9.9, 3.6, 2.6, "+33%", "giá/sqft Off-Plan cao hơn Ready năm 2025", ORANGE, 34);
stat(s, 9.9, 5.0, 2.6, "JVC", "master project nhiều giao dịch Off-Plan nhất từ 2024", MUTED, 28);
slideNotes(s);

// ================================================================ 10. Seasonality
const months = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11", "T12"];
s = content("Insight thị trường", "Mùa vụ: cuối năm sôi động, tháng 1 trầm nhất",
  "Số giao dịch trung bình của mỗi tháng so với mức trung bình năm (%), các năm trọn vẹn 2004–2025");
s.addChart(pres.charts.BAR, [{ name: "So với trung bình", labels: months, values: D.season.map((v) => Math.round(v)) }],
  { x: M, y: 1.7, w: 8.6, h: 5.1, barDir: "col", chartColors: [BLUE],
    showLegend: false, showValue: true, dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 11,
    dataLabelFormatCode: "+0;-0;0", valAxisLabelFormatCode: "+0;-0;0", ...axis });
card(s, 9.6, 1.9, 3.13, 4.7, TINT, "callouts");
stat(s, 9.9, 2.1, 2.6, "+13%", "tháng 10, tháng cao điểm", NAVY, 34);
stat(s, 9.9, 3.6, 2.6, "−16%", "tháng 1, thấp nhất năm", BLUE, 34);
stat(s, 9.9, 5.0, 2.6, "Q4", "nên tập trung ngân sách marketing", MUTED, 28);
slideNotes(s);

// ================================================================ 11. Areas
s = content("Insight thị trường", "Khu đại chúng dẫn đầu về số giao dịch",
  "Top 8 khu vực theo số giao dịch 2024 – 05/10/2026 (tên khu theo bản đồ địa chính của DLD)");
s.addChart(pres.charts.BAR, [{ name: "Giao dịch", labels: D.top_areas.names.slice().reverse(), values: D.top_areas.values.slice().reverse() }],
  { x: M, y: 1.7, w: 8.6, h: 5.1, barDir: "bar", chartColors: [BLUE], showLegend: false, showValue: true,
    dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 11, dataLabelFormatCode: "#,##0",
    valAxisLabelFormatCode: "#,##0", ...axis });
card(s, 9.6, 1.9, 3.13, 4.7, TINT, "callouts");
stat(s, 9.9, 2.1, 2.6, "43.465", "giao dịch tại Al Barsha South Fourth (thường gọi là JVC)", NAVY, 34);
stat(s, 9.9, 3.6, 2.6, "+190%", "khu tăng giá nhanh nhất 2022→2025 (Al Hebiah First)", ORANGE, 34);
stat(s, 9.9, 5.0, 2.6, "−5%", "Palm Jumeirah: khu sang nhất gần như đi ngang", MUTED, 28);
slideNotes(s);

// ================================================================ 12. ML pricing
pres.addSection({ title: "Machine Learning" });
s = content("Machine Learning", "Mô hình định giá: sai số trung vị 13% trên dữ liệu năm 2025",
  "Dự đoán giá/sqft nhà ở · train 2012–2024 · test 2025 (dữ liệu mô hình chưa từng thấy)");
s.addChart(pres.charts.BAR, [{ name: "Sai số trung vị (%)", labels: ["Naive (giá thị trường)", "Ridge", "LightGBM"], values: [25.0, 15.1, 13.4] }],
  { x: M, y: 1.75, w: 5.9, h: 4.9, barDir: "col", chartColors: [SKY, SKY, NAVY], showLegend: false, showValue: true,
    dataLabelPosition: "outEnd", dataLabelColor: INK, dataLabelFontSize: 14, dataLabelFormatCode: "0.0",
    valAxisHidden: true, valGridLine: { style: "none" }, showTitle: true, title: "Sai số trung vị (%), càng thấp càng tốt",
    titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: MUTED, catAxisLabelColor: MUTED, catAxisLabelFontSize: 12,
    catAxisLabelFontFace: "+mn-lt", catGridLine: { style: "none" }, catAxisLineShow: false, dataLabelFontFace: "+mn-lt" });
const imp = [["Khu vực", 49], ["Xu hướng thị trường", 17], ["Master project", 16], ["Diện tích", 9], ["Off-Plan / Ready", 5]];
s.addText("Yếu tố quyết định giá (mức quan trọng, %)", { x: 7.0, y: 1.8, w: 5.7, h: 0.4, fontFace: BODY, fontSize: 14,
  color: MUTED, margin: 0, isTextBox: true });
imp.forEach(([n, v], i) => {
  const y = 2.35 + i * 0.55;
  s.addText(n, { x: 7.0, y, w: 2.2, h: 0.4, fontFace: BODY, fontSize: 14, color: INK, margin: 0, valign: "middle", isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 9.3, y: y + 0.08, w: 2.8 * v / 49, h: 0.26, rectRadius: 0.05,
    fill: { color: i < 1 ? NAVY : BLUE }, line: { color: i < 1 ? NAVY : BLUE } });
  s.addText(`${v}%`, { x: 9.3 + 2.8 * v / 49 + 0.1, y, w: 0.7, h: 0.4, fontFace: BODY, fontSize: 14, bold: true, color: INK,
    margin: 0, valign: "middle", isTextBox: true });
});
s.addText([
  { text: "R² = 0,64 · 37% căn dự đoán trong ±10%", options: { bold: true, color: NAVY, breakLine: true } },
  { text: "Thêm tên dự án làm mô hình kém đi: 43% giao dịch 2025 thuộc dự án mới (cold start)", options: { breakLine: true } },
  { text: "Không có view, tầng, thương hiệu → không dùng cho phân khúc siêu sang" },
], { x: 7.0, y: 5.25, w: 5.7, h: 1.5, fontFace: BODY, fontSize: 14, color: INK, margin: 0, paraSpaceAfter: 6, isTextBox: true });
slideNotes(s);

// ================================================================ 13. Clusters
s = content("Machine Learning", "Phân cụm K-Means: 4 nhóm khu vực với hành vi giá khác nhau",
  "49 khu vực có ≥ 100 giao dịch nhà ở trong cả 2022 và 2025 · 5 đặc trưng đã chuẩn hóa");
const clusters = [
  ["Emerging hot spots", "6 khu", "~1.580", "+147%", "Giá vừa, tăng nhanh nhất, 71% Off-Plan", "Madinat Al Mataar, Al Hebiah", ORANGE],
  ["Prime established", "14 khu", "~2.730", "+35%", "Giá cao nhất, tăng chậm nhất", "Business Bay, Marsa Dubai", NAVY],
  ["Mass-market hubs", "21 khu", "~1.420", "+52%", "Nhiều giao dịch nhất, căn nhỏ ~69 m²", "JVC, Wadi Al Safa 5", BLUE],
  ["Ready, larger homes", "8 khu", "~1.410", "+65%", "Chỉ 10% Off-Plan, căn lớn ~163 m²", "Al Thanyah Third, Jabal Ali", "2E86C1"],
];
const cw4 = (CW - 3 * 0.3) / 4;
clusters.forEach(([n, k, psf, g, desc, ex, col], i) => {
  const x = M + i * (cw4 + 0.3), y = 1.85;
  card(s, x, y, cw4, 4.4, TINT, `cluster_${i}`);
  badge(s, x + 0.3, y + 0.3, String(i + 1), col);
  s.addText(n, { x: x + 0.3, y: y + 0.95, w: cw4 - 0.6, h: 0.5, fontFace: HEAD, fontSize: 17, bold: true, color: NAVY,
    margin: 0, isTextBox: true });
  s.addText(k, { x: x + 0.3, y: y + 1.42, w: cw4 - 0.6, h: 0.3, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  s.addText(g, { x: x + 0.3, y: y + 1.8, w: cw4 - 0.6, h: 0.7, fontFace: HEAD, fontSize: 34, bold: true, color: col,
    margin: 0, isTextBox: true });
  s.addText(`tăng giá 2022→2025 · ${psf} AED/sqft`, { x: x + 0.3, y: y + 2.5, w: cw4 - 0.6, h: 0.5, fontFace: BODY,
    fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  s.addText([{ text: desc, options: { breakLine: true } }, { text: ex, options: { italic: true, color: MUTED } }],
    { x: x + 0.3, y: y + 3.1, w: cw4 - 0.6, h: 1.6, fontFace: BODY, fontSize: 14, color: INK, margin: 0,
      paraSpaceAfter: 6, valign: "top", isTextBox: true });
});
slideNotes(s);

// ================================================================ 14. Recommendations
pres.addSection({ title: "Kết luận" });
s = content("Kết luận", "Đề xuất: chọn nhóm khu vực theo mục tiêu đầu tư",
  "Kết hợp insight thị trường với kết quả phân cụm và mô hình định giá");
const recs = [
  ["Tìm tăng trưởng", "Emerging hot spots: giá vào thấp hơn Prime ~40% nhưng tăng gấp 4 lần. Theo dõi tiến độ bàn giao vì phụ thuộc Off-Plan.", ORANGE],
  ["Ở hoặc cho thuê", "Mass-market hubs: thanh khoản cao nhất, giá vừa phải, dễ bán lại.", BLUE],
  ["Giữ tài sản", "Prime established: giá cao và ổn định, phù hợp nắm giữ dài hạn hơn là lướt sóng.", NAVY],
  ["Kiểm tra giá chào", "Dùng mô hình định giá: lệch hơn ±13% so với giá mô hình thì cần xem kỹ; huấn luyện lại mỗi quý.", "2E86C1"],
];
recs.forEach(([t, d, col], i) => {
  const y = 1.9 + i * 1.2;
  card(s, M, y, CW, 1.0, TINT, `rec_${i}`);
  badge(s, M + 0.25, y + 0.22, String(i + 1), col);
  s.addText(t, { x: M + 1.05, y: y + 0.1, w: 2.6, h: 0.8, fontFace: HEAD, fontSize: 18, bold: true, color: NAVY,
    margin: 0, valign: "middle", isTextBox: true });
  s.addText(d, { x: M + 3.7, y: y + 0.1, w: CW - 3.9, h: 0.8, fontFace: BODY, fontSize: 15, color: INK, margin: 0,
    valign: "middle", isTextBox: true });
});
slideNotes(s);

// ================================================================ 15. Limitations
s = content("Kết luận", "Hạn chế và hướng phát triển", "Những gì dữ liệu chưa trả lời được và bước tiếp theo");
const lim = [
  ["Hạn chế", ["Không có view, tầng, chất lượng, thương hiệu chủ đầu tư", "Không có giá thuê → chưa tính được lợi suất cho thuê",
    "Dữ liệu 2026 có thể chưa đăng ký đủ ở các tháng gần nhất", "Tên khu theo địa chính DLD, khác tên thương mại quen dùng"]],
  ["Hướng phát triển", ["Bổ sung dữ liệu cho thuê để tính rental yield theo khu", "Tự động chạy ETL hàng tháng khi nguồn cập nhật",
    "Đưa nhãn cụm khu vực vào Power BI để lọc và tô màu", "Dự báo số giao dịch theo tháng (time series)"]],
];
lim.forEach(([t, items], i) => {
  const x = M + i * (CW / 2 + 0.15), w = CW / 2 - 0.15;
  card(s, x, 1.85, w, 4.2, i ? TINT : WHITE, `lim_${i}`);
  s.addText(t, { x: x + 0.35, y: 2.05, w: w - 0.7, h: 0.5, fontFace: HEAD, fontSize: 20, bold: true, color: NAVY,
    margin: 0, isTextBox: true });
  s.addText(items.map((it, j) => ({ text: it, options: { bullet: true, breakLine: j < items.length - 1 } })),
    { x: x + 0.35, y: 2.7, w: w - 0.7, h: 3.7, fontFace: BODY, fontSize: 16, color: INK, paraSpaceAfter: 12,
      valign: "top", isTextBox: true });
});
slideNotes(s);

// ================================================================ 16. Closing
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Kết luận" });
s.addText("Cảm ơn thầy cô và các bạn", { placeholder: "title" });
s.addText("Hỏi đáp\nMã nguồn: github.com/rakeoohuynh/DLD_analyze", { placeholder: "body" });
slideNotes(s);

// Write without ZIP folder entries (they break opening the deck from OneDrive/SharePoint).
(async () => {
  const JSZip = require("jszip");
  const src = await JSZip.loadAsync(await pres.write({ outputType: "nodebuffer" }));
  const zip = new JSZip(); // copy files only; zip.remove(folder) would also delete the folder's files
  for (const [name, entry] of Object.entries(src.files)) {
    if (!entry.dir) zip.file(name, await entry.async("nodebuffer"), { createFolders: false });
  }
  fs.writeFileSync(OUT, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("wrote", OUT);
})();
