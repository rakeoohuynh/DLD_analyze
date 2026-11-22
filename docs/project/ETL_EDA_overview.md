# Tổng quan quy trình ETL & EDA

> Áp dụng cho capstone: **Dubai DLD Sales Transactions → Python ETL → MySQL → Power BI**
> Mỗi bước gồm: **Mục tiêu**, **Việc cần làm**, **Áp dụng vào dự án**, **Câu hỏi tự kiểm tra**.

---

## Bức tranh toàn cảnh

```
 ┌──────────┐    ┌──────────────────────── ETL (Python) ────────────────────────┐    ┌─────────┐    ┌──────────┐
 │ CSV thô  │ →  │ 0.Chuẩn bị → 1.Extract → 2.Profiling → 3.Transform → 4.Model  │ →  │  MySQL  │ →  │ Power BI │
 └──────────┘    │                                  → 5.Load → 6.Validate      │    └─────────┘    └──────────┘
                 └──────────────────────────────────────────────────────────────┘         │
                                                                                          ↓
                                                                               EDA (Jupyter Notebook)
```

- **ETL** = *Extract – Transform – Load*: lấy dữ liệu thô, làm sạch, biến đổi, rồi đưa vào database.
- **EDA** = *Exploratory Data Analysis*: khám phá dữ liệu **đã sạch** để tìm xu hướng, phân phối, tương quan, insight.

| Phần | Tỷ trọng điểm | Output |
|---|---|---|
| ETL (Python → MySQL) | 25% | Script/notebook ETL + database `dld` có 6 bảng |
| Advanced EDA | 30% | Notebook EDA có biểu đồ + nhận xét |
| Power BI Modeling & DAX | 30% | File `.pbix` |
| Slide insight | 10% | File `.pptx` |
| Thuyết trình & Q&A | 5% | |

---

# PHẦN A — ETL

## Bước 0. Chuẩn bị môi trường

**Mục tiêu:** Có đủ công cụ để code chạy được từ đầu đến cuối.

**Việc cần làm**
- [ ] Tạo virtual environment (`myenv`), cài thư viện trong `requirements.txt`
- [ ] Cài driver MySQL: `pymysql`
- [ ] MySQL Server đang chạy, đã tạo database (`CREATE DATABASE dld;`)
- [ ] File cấu hình kết nối (`utils/config.py`), **không** để lộ mật khẩu khi nộp bài (dùng `.env`)
- [ ] Tạo thư mục `log/` để ghi log pipeline
- [ ] Test kết nối: `test_connection(make_engine(DB_CONFIG))`

**Câu hỏi tự kiểm tra:** Nếu người khác clone project về, họ cần làm gì để chạy được?

---

## Bước 1. Extract — Đọc dữ liệu thô

**Mục tiêu:** Đưa dữ liệu từ file vào DataFrame **với đúng kiểu dữ liệu ngay từ đầu**.

**Việc cần làm**
- Đọc file (`pd.read_csv` / `pd.read_parquet`)
- Chỉ định kiểu dữ liệu: `dtype=`, `parse_dates=` → tránh `DtypeWarning`
- Ghi log: số dòng, số cột đọc được

**Áp dụng vào dự án**
- File: `dld_sales_transactions.csv` (1.372.277 dòng × 20 cột)
- Cột cần ép kiểu: `instance_date` → datetime; `has_parking`, `is_pre_registration` → boolean; `area_id`, `procedure_id`, `rooms_bucket` → số nguyên cho phép null (`Int64`)

**Câu hỏi tự kiểm tra:** Vì sao `area_id` bị pandas đọc thành `float64` dù nó là số nguyên?

---

## Bước 2. Data Profiling — Khám bệnh dữ liệu thô

**Mục tiêu:** Biết dữ liệu **có vấn đề gì** trước khi sửa. (Đây là "EDA mini" trong ETL.)

**Việc cần làm**
| Kiểm tra | Lệnh pandas |
|---|---|
| Kích thước, kiểu dữ liệu | `df.shape`, `df.info()` |
| Giá trị thiếu | `df.isnull().sum()` |
| Trùng lặp | `df.duplicated().sum()`, `df['transaction_id'].is_unique` |
| Thống kê số | `df.describe()` |
| Giá trị phân loại | `df['cột'].value_counts(dropna=False)` |
| Khoảng thời gian | `df['instance_date'].min()/.max()`, đếm theo năm |
| Ngoại lai | boxplot, so sánh mean vs median |

**Áp dụng vào dự án — những gì đã phát hiện**
| Vấn đề | Số dòng |
|---|---|
| `area_id` / `area_name_en` trống | 128 |
| `project_name` / `master_project_name` / `building_name` trống | ~284k / ~243k / ~398k |
| `property_sub_type` trống | ~198k |
| `rooms_bucket` trống | ~280k |
| `has_parking` trống | ~39k |
| `procedure_id` / `procedure_name_en` trống | 23.764 |
| `quality_flags ≠ 0` (dòng lỗi) | 28.495 |
| Dữ liệu trước 2004 thưa; 2026 chỉ đến 05/10 | |
| Mean giá 2,76tr ≫ median 1,36tr → lệch phải, nhiều outlier | |

**Câu hỏi tự kiểm tra:** Với mỗi vấn đề, bạn sẽ **xóa dòng, điền giá trị, hay giữ nguyên**? Vì sao?

---

## Bước 3. Transform — Làm sạch & biến đổi

**Mục tiêu:** Dữ liệu sạch, nhất quán, đúng kiểu, sẵn sàng để phân tích.

### 3.1 Lọc dòng (Filter)
- Giữ `quality_flags == 0` (loại giá/diện tích vô lý, outlier, ngày sai)
- Giới hạn khoảng thời gian phân tích *(cần chốt: từ năm ___ đến ___)*

### 3.2 Xử lý giá trị thiếu (Missing values)
> **Nguyên tắc:** thiếu **thông tin mô tả** → gán `"Unknown"` / mã `0`; thiếu **số đo** (giá, diện tích) → loại dòng.

| Cột | Cách xử lý |
|---|---|
| `area_id`, `area_name_en` | `0` / `"Unknown"` |
| `procedure_id`, `procedure_name_en` | `0` / `"Unknown"` (reg_type vẫn là `Ready`) |
| 3 cột dự án | `"Unknown"` |
| `property_sub_type`, `has_parking` | `"Unknown"` |
| `rooms_bucket` | giữ null + thêm cột chữ `rooms_label` (`Studio`, `1 BR`…`5+ BR`, `Unknown`) |

### 3.3 Chuẩn hóa (Standardize)
- Kiểu dữ liệu đúng (ngày, số nguyên, chữ, boolean)
- Text: bỏ khoảng trắng thừa (`.str.strip()`), thống nhất hoa/thường cho tên dự án/tòa nhà
- Tên cột: chữ thường, `snake_case`

### 3.4 Xử lý ngoại lai (Outliers)
- Đã có sẵn `PSF_OUTLIER` trong `quality_flags` (P1–P99 theo năm × loại BĐS × loại đăng ký)
- Tự kiểm chứng lại bằng **IQR / boxplot** để chứng minh hiểu phương pháp

### 3.5 Loại bỏ cột thừa
- `is_pre_registration` (trùng `reg_type_label`), `quality_flags` (sau khi lọc chỉ còn 0)

### 3.6 Tạo cột mới (Feature engineering)
- `date_id` = `YYYYMMDD` (số nguyên) từ `instance_date`
- `rooms_label`
- (tuỳ chọn) `price_psf` tính lại để kiểm chứng: `price_aed / (area_sqm × 10.7639)`

**Câu hỏi tự kiểm tra:** Sau transform, còn bao nhiêu dòng? Mất bao nhiêu % so với ban đầu? Có giải thích được từng dòng bị mất không?

---

## Bước 4. Data Modeling — Tách thành Star Schema

**Mục tiêu:** Từ 1 bảng phẳng → 1 Fact + nhiều Dimension (đáp ứng yêu cầu "đa bảng, mô hình quan hệ").

```
                         dim_date (liên tục, pd.date_range)
                                |
dim_area ———————————— fact_sales ———————————— dim_project (~10k dòng)
                       transaction_id (PK)
                       date_id, area_id, project_id,
                       property_id, procedure_id (FK)
                       price_aed, area_sqm, price_psf
                          |                 |
                 dim_property (~141)   dim_procedure (~19)
```

| Bảng | Khóa chính | Cách tạo |
|---|---|---|
| `dim_date` | `date_id` | `pd.date_range(start, end, freq='D')` → year, quarter, month, month_name, weekday_num, weekday_name |
| `dim_area` | `area_id` | `drop_duplicates()` trên (area_id, area_name_en) + dòng `0 = Unknown` |
| `dim_project` | `project_id` (tự tạo) | `drop_duplicates()` trên 3 cột dự án → đánh số; `0 = Unknown` |
| `dim_property` | `property_id` (tự tạo) | `drop_duplicates()` trên 5 cột loại BĐS → đánh số (junk dimension) |
| `dim_procedure` | `procedure_id` | `drop_duplicates()` trên (id, name, reg_type) + dòng `0 = Unknown` |
| `fact_sales` | `transaction_id` | `merge()` bảng sạch với các dim để lấy khóa tự tạo, chỉ giữ khóa + số đo |

**Kỹ thuật chính:** `drop_duplicates()`, `reset_index()`, `merge(how='left')`

**Câu hỏi tự kiểm tra:** Sau khi `merge`, số dòng của fact có **thay đổi** không? Nếu tăng lên thì vì sao (gợi ý: khóa dim bị trùng)?

---

## Bước 5. Load — Đưa vào MySQL

**Mục tiêu:** 6 bảng nằm trong database, có khóa chính/khóa ngoại đúng.

**Việc cần làm**
- Kết nối bằng SQLAlchemy + pymysql
- Load **dim trước, fact sau** (vì fact tham chiếu dim)
- `df.to_sql(name, engine, if_exists='replace' | 'append', index=False, chunksize=...)`
- Bảng lớn (fact ~1,3tr dòng) → dùng `chunksize` (ví dụ 10.000–50.000)
- (Nâng cao) Tạo bảng trước bằng SQL `CREATE TABLE` với `PRIMARY KEY`, `FOREIGN KEY`, kiểu dữ liệu chuẩn → rồi `append`

**Câu hỏi tự kiểm tra:** Nếu chạy pipeline **2 lần**, dữ liệu có bị nhân đôi không? `replace` và `append` khác nhau thế nào?

---

## Bước 6. Validate — Kiểm tra sau khi load

**Mục tiêu:** Chứng minh dữ liệu trong MySQL **đúng và đủ**.

| Kiểm tra | Cách làm |
|---|---|
| Số dòng khớp | `SELECT COUNT(*)` từng bảng = `len(df)` trong Python |
| Không có khóa mồ côi | `LEFT JOIN` fact với dim, đếm dòng dim bị NULL → phải = 0 |
| Khóa chính không trùng | `COUNT(*)` vs `COUNT(DISTINCT pk)` |
| Tổng giá trị khớp | `SUM(price_aed)` trong MySQL = trong pandas |
| Median psf hợp lý | So với con số tham chiếu trong `DATA_DICTIONARY.md` |

---

## Bước 7. Đóng gói pipeline (tự động hóa)

**Mục tiêu:** Đạt tiêu chí "code script tự động mượt mà".

- Gom thành các hàm `extract()`, `transform()`, `build_star_schema()`, `load()`, `validate()`
- Hàm `main()` gọi lần lượt; chạy 1 lệnh là xong: `python etl.py`
- Ghi **log** mỗi bước (số dòng trước/sau, thời gian chạy)
- `try/except` để báo lỗi rõ ràng

---

# PHẦN B — EDA (Advanced, Jupyter Notebook)

> Làm trên dữ liệu **đã sạch** (đọc lại từ MySQL hoặc từ DataFrame sau transform).

## Bước 1. Đặt câu hỏi kinh doanh trước
EDA không phải vẽ biểu đồ cho đẹp — mỗi biểu đồ phải trả lời 1 câu hỏi. Ví dụ:
- Thị trường tăng/giảm thế nào theo thời gian? (số giao dịch, tổng giá trị, median psf)
- Off-Plan vs Ready khác nhau ra sao?
- Khu vực nào đắt nhất / tăng giá nhanh nhất?
- Số phòng, diện tích, parking ảnh hưởng giá thế nào?

## Bước 2. Phân tích đơn biến (Univariate) — Phân phối
| Việc | Công cụ |
|---|---|
| Thống kê mô tả | `.describe()`, mean vs median |
| Hình dạng phân phối | histogram, KDE; `skew()` → lệch phải/trái/chuẩn |
| Ngoại lai | **boxplot**, IQR (Q1 − 1.5·IQR, Q3 + 1.5·IQR) |
| Biến phân loại | `value_counts()`, bar chart |
| Biến đổi log | `np.log(price)` để phân phối bớt lệch |

## Bước 3. Phân tích theo thời gian (Trend)
- Line chart theo tháng/năm: số giao dịch, tổng giá trị, median psf
- Tính **YoY / MoM %** bằng pandas (`pct_change`)
- Tách Off-Plan vs Ready; nhận diện các giai đoạn (trước/sau Covid…)

## Bước 4. Phân tích hai biến (Bivariate)
| Cặp biến | Biểu đồ |
|---|---|
| Số ↔ Số (diện tích ↔ giá) | scatter plot |
| Phân loại ↔ Số (loại BĐS ↔ psf) | boxplot / violin theo nhóm |
| Phân loại ↔ Phân loại (usage ↔ reg_type) | crosstab, stacked bar |

## Bước 5. Phân tích đa biến & tương quan
- **Heatmap** ma trận tương quan (`df.corr()`, `sns.heatmap`)
- Chọn biến số: `price_aed`, `area_sqm`, `price_psf`, `rooms_bucket`, `has_parking`, năm, `is_offplan`…
- Phân biệt **Pearson** (tuyến tính) vs **Spearman** (thứ hạng, hợp với dữ liệu lệch)
- Nhớ: **tương quan ≠ nhân quả**

## Bước 6. Trích xuất insight
- Mỗi biểu đồ → 1–2 câu nhận xét có số liệu ("Median psf khu X tăng 35% YoY…")
- Bổ sung góc nhìn Power BI khó làm (phân phối, tương quan, kiểm định)
- Gom thành 3–5 insight chính phục vụ slide

## Bước 7 (Bonus). Machine Learning
- Linear Regression dự báo giá / psf → đọc **R²**, MAE
- K-Means phân cụm khu vực theo giá & tăng trưởng
- Logistic Regression / Decision Tree phân loại Off-Plan vs Ready → Accuracy, Precision, Recall
- Kết thúc bằng **1 đề xuất kinh doanh**

---

## Checklist tiến độ

| # | Bước | Trạng thái |
|---|---|---|
| A0 | Chuẩn bị môi trường | 🟡 thiếu `pymysql`, thư mục `log/` |
| A1 | Extract | 🟡 đã đọc CSV, chưa ép kiểu |
| A2 | Profiling | 🟡 đã `info()`, `isnull()` |
| A3 | Transform | ⬜ |
| A4 | Star Schema | ✅ đã thiết kế, ⬜ chưa code |
| A5 | Load | ⬜ |
| A6 | Validate | ⬜ |
| A7 | Đóng gói pipeline | ⬜ |
| B1–B7 | EDA | ⬜ |

**Quyết định còn chờ chốt:** khoảng năm phân tích · chỉ số thay "lợi nhuận" · đối tượng & câu hỏi kinh doanh.
