# Kịch bản thuyết trình: Thị trường BĐS Dubai 2004–2026

- **File slide:** `DLD_capstone.pptx` (16 slide). Lời thoại bên dưới cũng nằm trong phần *Notes* của từng slide.
- **Thời lượng dự kiến:** khoảng 12 phút, cộng thêm phần Q&A.
- **Mẹo:** dùng chế độ **Presenter View** trong PowerPoint (Slide Show → Use Presenter View) để nhìn thấy notes khi trình bày.

| Phần | Slide | Thời gian |
|---|---|---|
| Mở đầu | 1–2 | ~1 phút 30 |
| Dữ liệu và ETL | 3–5 | ~3 phút |
| Insight thị trường | 6–11 | ~4 phút 30 |
| Machine Learning | 12–13 | ~2 phút |
| Kết luận | 14–16 | ~1 phút 30 |

---

## 1. Tiêu đề (~30 giây)
Chào thầy cô và các bạn. Đề tài của em là phân tích thị trường bất động sản Dubai, dựa trên toàn bộ giao dịch mua bán đã đăng ký với Dubai Land Department từ 2004 đến tháng 10 năm 2026, khoảng 1,34 triệu giao dịch sau khi làm sạch. Em sẽ đi qua 4 phần: dữ liệu và quy trình ETL, các insight chính về thị trường, phần Machine Learning, và cuối cùng là đề xuất.

## 2. Tóm tắt (~1 phút)
Nếu chỉ nhớ một slide thì đây là slide đó. Thứ nhất, số giao dịch năm 2025 gấp khoảng 6,5 lần năm 2020. Thứ hai, giá mỗi foot vuông của nhà ở tăng 83% từ đáy năm 2020. Thứ ba, gần 2/3 giao dịch là Off-Plan, tức mua dự án chưa xây xong. Và thứ tư, năm 2026 số giao dịch giảm 21% so với cùng kỳ, trong khi giá vẫn tăng khoảng 4%: lượng mua giảm nhưng giá chưa giảm. Các phần sau sẽ giải thích từng con số.

## 3. Quy trình dữ liệu (~1 phút)
Dữ liệu là file CSV 1,37 triệu dòng. Em viết pipeline bằng Python, chạy một lệnh là xong cả 6 bước. Sau khi làm sạch còn 1.335.396 giao dịch, tức giữ được 97,3% dữ liệu gốc. Dữ liệu được load vào MySQL theo mô hình star schema, sau đó kiểm tra lại: số dòng khớp, khóa chính không trùng, không có khóa mồ côi và tổng giá trị khớp với pandas. Từ MySQL, dữ liệu đi tiếp sang Power BI và notebook Machine Learning.

## 4. Chất lượng dữ liệu (~1 phút)
Nhìn qua thì dữ liệu khá sạch, nhưng khi kiểm tra kỹ em thấy một số vấn đề. Đáng chú ý nhất là 23 nghìn dòng năm 2026 thiếu mã thủ tục. Em phát hiện số ở giữa của `transaction_id` chính là mã thủ tục, khớp 100% trên các dòng có đủ dữ liệu, nên khôi phục được toàn bộ thay vì gán Unknown. Có khoảng 118 nghìn dòng giống hệt nhau chỉ khác mã giao dịch; em giữ lại vì đó là các đợt chủ đầu tư bán nhiều căn cùng mẫu, cùng ngày, cùng giá. Cuối cùng, em gắn cờ tháng và năm chưa đủ dữ liệu để biểu đồ xu hướng không bị giảm giả.

## 5. Star schema (~1 phút)
Từ một bảng phẳng 20 cột, em tách thành star schema: bảng `fact_sales` chứa số đo là giá, diện tích, giá mỗi sqft, và 5 bảng dimension. `dim_date` là lịch liên tục, có cờ đánh dấu tháng và năm chưa đủ dữ liệu. `dim_property` là junk dimension gom loại BĐS, số phòng, mục đích sử dụng và chỗ đậu xe thành 140 tổ hợp. Mọi quan hệ là nhiều-một, một chiều. Sau khi load, em kiểm tra không có dòng fact nào trỏ tới khóa không tồn tại.

## 6. Số giao dịch bùng nổ (~45 giây)
Biểu đồ cho thấy hai chu kỳ. Chu kỳ đầu là 2008–2009, trước khủng hoảng tài chính, sau đó thị trường giảm mạnh và đi ngang đến 2020. Chu kỳ thứ hai bắt đầu sau Covid: từ 32 nghìn giao dịch năm 2020 lên 210 nghìn năm 2025, gấp 6,5 lần, với tổng giá trị 589 tỷ AED. Phần màu xanh đậm là Off-Plan, và nó chính là động lực tăng trưởng chính.

## 7. Giá nhà ở (~45 giây)
Về giá, em dùng median giá mỗi foot vuông và chỉ tính căn hộ, villa để ở, đúng theo hướng dẫn của nguồn dữ liệu, vì đất và văn phòng định giá theo logic khác. Giá đi ngang khoảng 1.000 AED suốt 2014–2021, sau đó tăng mạnh: +26% riêng năm 2022 và đạt 1.686 AED năm 2025, cao hơn đáy năm 2020 khoảng 83%. Em dùng median chứ không dùng trung bình vì giá lệch phải: giá trung bình cao gấp đôi median.

## 8. Năm 2026 chững lại (~45 giây)
Đây là insight em thấy đáng chú ý nhất. So cùng kỳ từ 1/1 đến 5/10, số giao dịch năm 2026 giảm 21%, nhưng giá vẫn tăng 4%. Tức là người mua đã chậm lại nhưng người bán chưa giảm giá. Em so cùng kỳ chứ không so cả năm, vì dữ liệu 2026 chỉ đến ngày 5/10. Cũng cần thận trọng: các giao dịch gần đây có thể chưa được đăng ký hết, nên mức giảm có thể nhỏ hơn con số này.

## 9. Off-Plan (~45 giây)
Off-Plan là mua căn hộ khi dự án chưa xây xong. Tỷ lệ này tăng từ 39% năm 2021 lên gần 63% năm 2025. Đáng chú ý là giá mỗi sqft của Off-Plan cao hơn Ready khoảng 33%, vì dự án mới, vị trí mới và có kế hoạch thanh toán linh hoạt. Dẫn đầu là Jumeirah Village Circle. Thị trường phụ thuộc nhiều vào Off-Plan cũng là một rủi ro nếu nhu cầu chững lại như năm 2026.

## 10. Mùa vụ (~30 giây)
Ngoài xu hướng dài hạn, thị trường có tính mùa vụ khá rõ. Tháng 10 cao hơn trung bình 13%, quý 4 nhìn chung sôi động. Tháng 1 và tháng 2 trầm nhất, thấp hơn 11–16%. Với một công ty môi giới hay chủ đầu tư, đây là gợi ý về thời điểm tung dự án và đẩy ngân sách marketing.

## 11. Khu vực (~45 giây)
Khu nhiều giao dịch nhất là Al Barsha South Fourth, chính là khu mà người Dubai quen gọi là Jumeirah Village Circle, với hơn 43 nghìn giao dịch từ 2024. Các khu dẫn đầu chủ yếu là khu căn hộ tầm trung. Trong khi đó, khu tăng giá mạnh nhất là các khu vùng ven như Al Hebiah, gần gấp 3 lần trong 3 năm, còn Palm Jumeirah, khu cao cấp nhất, lại gần như đi ngang. Phần Machine Learning sẽ hệ thống hóa nhận xét này.

## 12. Mô hình định giá (~1 phút 15)
Hướng ML thứ nhất là mô hình định giá. Em dự đoán giá mỗi sqft từ khu vực, loại căn, diện tích, số phòng và xu hướng thị trường. Em chia train/test theo thời gian: học trên 2012–2024, kiểm tra trên 2025, vì định giá thực tế là dự đoán tương lai. Để tránh rò rỉ dữ liệu, em không dùng giá bán làm biến đầu vào, còn xu hướng thị trường lấy theo median của tháng trước. LightGBM tốt nhất với sai số trung vị 13,4%, so với 25% nếu chỉ đoán bằng giá thị trường. Vị trí quyết định khoảng 65% giá. Một phát hiện thú vị: thêm tên dự án lại làm mô hình kém đi, vì 43% giao dịch năm 2025 thuộc dự án mới mà mô hình chưa từng thấy.

## 13. Phân cụm khu vực (~1 phút)
Hướng ML thứ hai là phân cụm khu vực bằng K-Means, dựa trên 5 đặc trưng: mức giá, tốc độ tăng giá, số giao dịch, tỷ lệ Off-Plan và diện tích căn điển hình. Em chọn 4 cụm dựa trên Elbow và Silhouette, và vì 4 nhóm dễ diễn giải. Nhóm Emerging hot spots có giá vừa phải nhưng tăng gần 2,5 lần trong 3 năm. Nhóm Prime giá cao nhất nhưng tăng chậm nhất. Nhóm Mass-market là nơi có nhiều giao dịch nhất. Nhóm cuối là các khu villa, nhà lớn đã hoàn thiện. Kết quả phân cụm được ghi vào bảng `area_cluster` trong MySQL để dùng tiếp trong Power BI.

## 14. Đề xuất (~45 giây)
Từ các phân tích trên, em đưa ra 4 đề xuất theo mục tiêu. Nhà đầu tư muốn tăng trưởng nên nhìn vào nhóm Emerging hot spots, nhưng cần theo dõi tiến độ bàn giao vì nhóm này phụ thuộc Off-Plan, trong bối cảnh năm 2026 số giao dịch đang giảm. Người mua để ở hoặc cho thuê nên chọn Mass-market hubs vì dễ bán lại. Nhóm Prime phù hợp giữ tài sản. Và mô hình định giá có thể dùng như công cụ kiểm tra nhanh giá chào bán.

## 15. Hạn chế và hướng phát triển (~30 giây)
Bài phân tích vẫn có hạn chế. Dữ liệu không có view, tầng hay thương hiệu chủ đầu tư, nên mô hình định giá chưa chính xác ở phân khúc cao cấp. Chưa có giá thuê nên chưa tính được lợi suất cho thuê, một chỉ số nhà đầu tư rất quan tâm. Hướng tiếp theo là bổ sung dữ liệu thuê, tự động hóa ETL hàng tháng và đưa nhãn cụm vào dashboard.

## 16. Cảm ơn (~15 giây)
Em xin cảm ơn thầy cô và các bạn đã lắng nghe. Toàn bộ mã nguồn ETL, dashboard Power BI và notebook ML đều có trên GitHub. Em rất mong nhận được câu hỏi và góp ý.

---

## Chuẩn bị Q&A

**Vì sao dùng median chứ không dùng trung bình?**
Giá lệch phải mạnh: trung bình giá giao dịch khoảng 2,76 triệu AED, gần gấp đôi median 1,36 triệu. Vài giao dịch cực lớn (một tòa nhà 1,86 tỷ AED) kéo trung bình lên, nên median phản ánh giao dịch điển hình tốt hơn.

**Vì sao chỉ tính giá/sqft cho căn hộ và villa để ở?**
Đất định giá theo diện tích lô (rẻ hơn nhiều lần mỗi sqft), cả tòa nhà là giao dịch bán sỉ, còn shop và văn phòng có logic giá khác. Gộp vào sẽ làm median sai. Nguồn dữ liệu cũng khuyến nghị đúng cách lọc này.

**Vì sao không xóa 118 nghìn dòng trùng?**
Các dòng có mã giao dịch khác nhau. Khi xem kỹ, đó là các đợt chủ đầu tư bán nhiều căn cùng mẫu trong cùng ngày, ví dụ 60 căn studio cùng dự án, cùng diện tích, cùng giá. Đây là giao dịch thật, xóa đi sẽ làm sai số lượng.

**Chạy lại pipeline có bị nhân đôi dữ liệu không?**
Không. Mỗi lần chạy, script xóa và tạo lại 6 bảng rồi mới load, sau đó kiểm tra số dòng khớp với pandas.

**Mô hình có bị rò rỉ dữ liệu (data leakage) không?**
Không dùng `price_aed` (vì `price_psf` tính từ giá). Xu hướng thị trường lấy từ tháng trước, là thông tin đã có trước giao dịch. Train/test chia theo thời gian, test trên năm 2025 mà mô hình chưa thấy.

**R² = 0,64 có thấp không?**
Với giá BĐS chỉ có vị trí, diện tích, loại căn thì đây là mức hợp lý. Phần còn lại phụ thuộc view, tầng, hướng, chất lượng, thương hiệu, những thứ dữ liệu không có. Sai số trung vị 13% thấp hơn gần một nửa so với mốc Naive (25%).

**Vì sao chọn k = 4?**
Silhouette gần bằng nhau trong khoảng k = 3–8 (0,27–0,30), không có k nào vượt trội. Elbow gãy quanh 3–4. Chọn 4 vì mỗi nhóm có ý nghĩa kinh doanh rõ ràng và dễ trình bày.

**Vì sao năm 2026 có thể giảm ít hơn con số -21%?**
Giao dịch có thể được đăng ký trễ, và dữ liệu là bản chụp tại ngày 5/10/2026. Các tháng gần nhất có thể còn được bổ sung khi nguồn cập nhật.

**Al Barsha South Fourth là khu nào?**
Đó là tên địa chính chính thức của DLD. Người Dubai quen gọi khu này là Jumeirah Village Circle (JVC).
