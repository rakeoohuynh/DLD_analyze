# Phân tích thị trường bất động sản Dubai (DLD Sales 2004–2026)

Capstone Data Analyst: phân tích **1,34 triệu giao dịch mua bán bất động sản** đã đăng ký tại Dubai Land Department (DLD), từ năm 2004 đến 05/10/2026.

```
CSV thô ──► Python ETL ──► MySQL (star schema) ──► Power BI dashboard
                                   │
                                   └──► Notebook Machine Learning ──► Slide thuyết trình
```

## Kết quả chính

| | |
|---|---|
| **×6,5** | Số giao dịch năm 2025 (210 nghìn) so với năm 2020 (32 nghìn) |
| **+83%** | Median giá/sqft nhà ở, từ đáy năm 2020 đến 2025 (1.686 AED) |
| **62,6%** | Tỷ lệ giao dịch Off-Plan năm 2025; giá/sqft cao hơn Ready khoảng 33% |
| **−21%** | Số giao dịch 2026 so với cùng kỳ 2025, trong khi giá vẫn tăng 4% |
| **13,4%** | Sai số trung vị của mô hình định giá LightGBM trên dữ liệu năm 2025 |
| **4 cụm** | Nhóm khu vực theo K-Means: Prime, Emerging hot spots, Mass-market, Ready larger homes |

Chi tiết xem trong [slide thuyết trình](presentation/DLD_capstone.pptx) và [kịch bản](presentation/script.md).

## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| [`etl.py`](etl.py) | Pipeline ETL: extract → profile → transform → star schema → load MySQL → validate |
| [`utils/`](utils/) | Cấu hình và hàm kết nối MySQL |
| [`ML.ipynb`](ML.ipynb) | Mô hình định giá (Ridge, LightGBM) và phân cụm khu vực (K-Means) |
| [`powerbi/`](powerbi/) | Project Power BI (PBIP): semantic model TMDL, report 5 trang và trang tooltip |
| [`powerbi/scripts/`](powerbi/scripts/) | Script sinh lại report và thêm measure DAX |
| [`presentation/`](presentation/) | Slide PowerPoint, kịch bản thuyết trình, script sinh slide |
| [`docs/project/`](docs/project/) | Đề bài và kế hoạch ETL/EDA |
| [`docs/dataset/`](docs/dataset/) | Mô tả bộ dữ liệu gốc, data dictionary, giấy phép |
| `data/` | Dữ liệu thô và đã xử lý (không đưa lên GitHub, xem bên dưới) |

## Mô hình dữ liệu

Database MySQL `dld` gồm 1 bảng fact và 5 bảng dimension, quan hệ nhiều-một:

| Bảng | Số dòng | Nội dung |
|---|---|---|
| `fact_sales` | 1.335.396 | Giá (AED), diện tích (m²), giá/sqft và các khóa ngoại |
| `dim_date` | 8.310 | Lịch liên tục, có cờ tháng/năm chưa đủ dữ liệu |
| `dim_area` | 197 | Khu vực theo địa chính DLD |
| `dim_project` | 10.028 | Dự án, master project, tòa nhà |
| `dim_property` | 140 | Loại BĐS, mục đích sử dụng, số phòng, chỗ đậu xe |
| `dim_procedure` | 18 | Thủ tục DLD, Off-Plan / Ready |

Notebook ML ghi thêm bảng `area_cluster` (nhãn cụm của 49 khu vực).

**Làm sạch dữ liệu:** giữ 97,3% dữ liệu gốc. Loại các dòng bị gắn cờ chất lượng và dữ liệu trước 2004; khôi phục mã thủ tục bị thiếu của năm 2026 từ `transaction_id`; gộp các tên dự án chỉ khác chữ hoa/thường. Chi tiết trong [`etl.py`](etl.py) và slide 4–5.

## Cách chạy

### 1. Cài đặt môi trường

Yêu cầu: Python 3.12+, MySQL 8, Power BI Desktop (bản hỗ trợ PBIP), Node.js (chỉ cần nếu muốn sinh lại slide).

```powershell
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

Sửa thông tin kết nối MySQL trong [`utils/config.py`](utils/config.py). Database `dld` sẽ được tự tạo khi chạy ETL.

### 2. Tải dữ liệu

File gốc `dld_sales_transactions.csv` (~239 MB) vượt giới hạn 100 MB của GitHub nên không có trong repo. Tải từ [dubairealestatedata.com/sources](https://www.dubairealestatedata.com/sources) và đặt vào `data/raw/`.

### 3. Chạy ETL

```powershell
python etl.py
```

Script làm sạch dữ liệu, load 6 bảng vào MySQL, ghi bản CSV vào `data/processed/` và kiểm tra lại số dòng, khóa và tổng giá trị. Mất khoảng 2,5 phút; log ghi trong `log/`. Chạy lại không làm nhân đôi dữ liệu vì các bảng được tạo lại mỗi lần. Dùng `python etl.py --no-load` để chỉ xuất CSV mà không load MySQL.

### 4. Mở dashboard Power BI

Mở [`powerbi/DLD_Sales.pbip`](powerbi/DLD_Sales.pbip) trong Power BI Desktop rồi bấm **Refresh**. Mặc định report đọc từ MySQL. Để đọc từ CSV, đổi tham số `SourceMode` thành `CSV` và `DataFolder` thành đường dẫn tới `data/processed/` trên máy bạn (Transform data → Edit parameters).

### 5. Chạy notebook Machine Learning

Mở [`ML.ipynb`](ML.ipynb) và chạy toàn bộ (khoảng 2 phút). Notebook đọc dữ liệu từ MySQL nên cần chạy ETL trước.

### 6. Sinh lại slide (tùy chọn)

```powershell
python presentation\export_data.py
cd presentation
npm install
node build_deck.js
```

Lưu ý: script sẽ ghi đè `DLD_capstone.pptx`. Các số liệu ML trên slide 13–14 được ghi cố định theo kết quả của `ML.ipynb`.

## Nguồn dữ liệu

Dubai Real Estate Data ([dubairealestatedata.com](https://www.dubairealestatedata.com)), dựa trên dữ liệu mở của Dubai Land Department. Giấy phép **CC BY 4.0**. Xem [`docs/dataset/README.md`](docs/dataset/README.md) và [`docs/dataset/LICENSE.md`](docs/dataset/LICENSE.md).

Dự án phục vụ mục đích học tập, không phải tư vấn đầu tư.
