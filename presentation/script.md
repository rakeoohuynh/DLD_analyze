# Kịch bản thuyết trình: Thị trường nhà đất Dubai 2004–2026

- File slide: `DLD_capstone.pptx` (17 slide). Mỗi mục dưới đây cũng nằm trong phần **Notes** của slide tương ứng.
- Thời gian: khoảng 13 phút, chưa tính phần hỏi đáp.
- Khi trình bày, bật **Presenter View** (Slide Show → Use Presenter View) để nhìn được notes.
- Mỗi gạch đầu dòng là một ý để nói. Không cần đọc thuộc, cứ nói theo cách của mình.

| Phần | Slide | Thời gian |
|---|---|---|
| Mở đầu | 1–2 | ~1 phút 30 |
| Dữ liệu và ETL | 3–6 | ~4 phút |
| Thị trường | 7–12 | ~4 phút 30 |
| Machine Learning | 13–14 | ~2 phút |
| Kết luận | 15–17 | ~1 phút 30 |

---

## 1. Mở đầu (~30 giây)
- Em chào thầy cô và các bạn.
- Đề tài của em là thị trường nhà đất Dubai, dựa trên dữ liệu mua bán đã đăng ký ở Sở Đất đai Dubai (DLD).
- Dữ liệu có khoảng 1,34 triệu giao dịch, từ năm 2004 đến đầu tháng 10/2026.
- Bài gồm 4 phần: dữ liệu và cách làm sạch, thị trường đang diễn biến ra sao, phần Machine Learning, và cuối cùng là đề xuất.

## 2. Tóm tắt (~1 phút)
- Trước khi vào chi tiết, em nói luôn 4 con số chính.
- Năm 2025 có số giao dịch gấp 6,5 lần năm 2020.
- Giá nhà tính trên mỗi foot vuông (sqft) tăng 83% so với năm 2020.
- Gần 2/3 giao dịch là Off-Plan, tức là mua nhà khi dự án còn chưa xây xong.
- Riêng năm 2026: số giao dịch giảm 21% so với cùng kỳ năm trước, nhưng giá vẫn tăng nhẹ 4%.
- Nói gọn lại: mấy năm qua thị trường tăng rất mạnh, và năm nay bắt đầu chậm lại.

## 3. Quy trình dữ liệu (~1 phút)
- Dữ liệu gốc là một file CSV khoảng 1,37 triệu dòng.
- Em viết một file Python, chạy một lệnh là nó tự làm hết: đọc file, làm sạch, chia bảng, đưa vào MySQL, rồi kiểm tra lại.
- Làm sạch xong còn khoảng 1,34 triệu dòng, tức là giữ lại được 97,3%.
- Sau khi đưa vào MySQL, em kiểm tra lại số dòng, các khóa và tổng tiền, tất cả đều khớp với bên Python.
- Từ MySQL, dữ liệu được dùng cho dashboard Power BI và phần Machine Learning.

## 4. Chất lượng dữ liệu (~1 phút)
- Mới nhìn thì dữ liệu khá sạch, nhưng kiểm tra kỹ thì có mấy vấn đề.
- Khoảng 28 nghìn dòng bị nguồn đánh dấu là lỗi, như giá hoặc diện tích vô lý, nên em bỏ.
- Dữ liệu trước 2004 rất ít, nên em chỉ lấy từ 2004 trở đi.
- 23 nghìn dòng năm 2026 bị trống mã thủ tục. Em điền lại được hết, slide sau em nói cách làm.
- Khoảng 118 nghìn dòng giống hệt nhau, chỉ khác mã giao dịch. Em giữ lại, vì đó là chủ đầu tư bán nhiều căn giống nhau trong cùng một ngày, đều là giao dịch thật.
- Tháng 10/2026 mới có 5 ngày dữ liệu. Em đánh dấu để khi vẽ biểu đồ thì bỏ tháng này ra, nếu không sẽ trông như thị trường sụp.

## 5. Khôi phục mã thủ tục (~1 phút)
- Mã giao dịch có dạng 1-11-2025-19755, gồm 4 phần.
- Em để ý phần thứ hai trông giống mã thủ tục.
- Bảng bên trái là 3 giao dịch thật: mã 11 là bán, 102 là bán Off-Plan, 41 là bán trễ hạn. Phần thứ hai của mã giao dịch trùng đúng với mã thủ tục.
- Em kiểm tra trên toàn bộ 1,32 triệu dòng có đủ dữ liệu thì trùng 100%, không sai dòng nào.
- Bảng bên phải là các dòng năm 2026 bị trống. Phần thứ hai của chúng đều là 11, nên em điền là "Sell".
- Nhờ vậy không có dòng nào phải để "Unknown".
- Cách đọc mã này là em tự rút ra từ dữ liệu, nguồn không có tài liệu ghi rõ.

## 6. Star schema (~1 phút)
- Dữ liệu gốc là một bảng lớn 20 cột. Em tách ra thành 6 bảng theo kiểu star schema.
- Ở giữa là bảng fact_sales: mỗi dòng là một giao dịch, gồm giá, diện tích và giá/sqft.
- Xung quanh là 5 bảng mô tả: ngày, khu vực, dự án, loại nhà và thủ tục.
- Bảng loại nhà gom loại bất động sản, số phòng, mục đích sử dụng và chỗ đậu xe lại, chỉ còn 140 dòng.
- Tách như vậy giúp Power BI chạy nhanh hơn và viết công thức DAX gọn hơn.

## 7. Số giao dịch (~45 giây)
- Biểu đồ có hai lần tăng mạnh.
- Lần thứ nhất là 2008–2009. Sau khủng hoảng tài chính thì rớt mạnh và đi ngang tới năm 2020.
- Lần thứ hai là sau Covid: từ 32 nghìn giao dịch năm 2020 lên 210 nghìn năm 2025.
- Năm 2025, tổng giá trị giao dịch là 589 tỷ AED.
- Phần màu xanh đậm là Off-Plan, và đây là phần tăng nhiều nhất.

## 8. Giá nhà (~45 giây)
- Em đo giá bằng giá trên mỗi sqft, và chỉ tính căn hộ, villa dùng để ở.
- Em không tính đất hay văn phòng, vì cách định giá của chúng khác hẳn.
- Từ 2014 tới 2021, giá gần như đứng yên quanh 1.000 AED/sqft.
- Từ 2022 giá tăng mạnh: riêng năm 2022 tăng 26%, tới 2025 đạt 1.686 AED/sqft.
- Em dùng trung vị (median) chứ không dùng trung bình, vì vài căn siêu đắt kéo trung bình lên gần gấp đôi.

## 9. Năm 2026 (~45 giây)
- Em so cùng giai đoạn từ 1/1 đến 5/10 của hai năm.
- Số giao dịch năm 2026 giảm 21% so với 2025.
- Nhưng giá vẫn tăng 4%.
- Nghĩa là người mua đã chậm lại, nhưng người bán chưa chịu giảm giá. Thường đây là dấu hiệu thị trường bắt đầu hạ nhiệt.
- Em so cùng giai đoạn vì dữ liệu 2026 chỉ có tới ngày 5/10.
- Một số giao dịch gần đây có thể chưa kịp đăng ký, nên mức giảm thật có thể ít hơn 21%.

## 10. Off-Plan (~45 giây)
- Off-Plan là mua nhà khi dự án chưa xây xong.
- Tỷ lệ này tăng từ 39% năm 2021 lên gần 63% năm 2025.
- Giá Off-Plan cao hơn nhà đã xây xong khoảng 33% mỗi sqft, vì nhà mới, khu mới, lại được trả góp theo tiến độ.
- Khu bán Off-Plan nhiều nhất là Jumeirah Village Circle.
- Rủi ro là thị trường dựa nhiều vào Off-Plan. Nếu người mua chậm lại như năm 2026 thì các dự án sẽ bị ảnh hưởng trước.

## 11. Mùa cao điểm (~30 giây)
- Thị trường có mùa cao điểm và thấp điểm khá rõ.
- Tháng 10 nhiều giao dịch nhất, cao hơn trung bình 13%. Quý 4 nói chung đều đông.
- Tháng 1 và tháng 2 vắng nhất, thấp hơn trung bình 11–16%.
- Với công ty môi giới hay chủ đầu tư, nên mở bán và chạy quảng cáo mạnh vào cuối năm.

## 12. Khu vực (~45 giây)
- Khu nhiều giao dịch nhất là Al Barsha South Fourth, chính là khu người ta hay gọi là Jumeirah Village Circle, với hơn 43 nghìn giao dịch từ 2024.
- Các khu đứng đầu chủ yếu là khu căn hộ giá vừa phải.
- Khu tăng giá nhanh nhất lại là khu ven như Al Hebiah, gần gấp 3 trong 3 năm.
- Palm Jumeirah, khu sang nhất, thì giá gần như không tăng.
- Ở phần Machine Learning, em sẽ chia các khu này thành nhóm cho rõ hơn.

## 13. Mô hình đoán giá (~1 phút 15)
- Mục tiêu là đoán giá/sqft hợp lý của một căn nhà, dựa trên khu vực, loại căn, diện tích, số phòng và tình hình thị trường lúc đó.
- Em cho mô hình học dữ liệu 2012–2024, rồi kiểm tra trên năm 2025 mà nó chưa thấy. Làm vậy mới giống dự đoán thật.
- Em không đưa giá bán vào làm dữ liệu đầu vào, vì như vậy là cho mô hình nhìn trước đáp án.
- Kết quả: với LightGBM, một nửa số căn bị đoán lệch dưới 13%. Nếu chỉ đoán bằng giá chung của thị trường thì con số này là 25%.
- Vị trí quyết định khoảng 65% giá nhà.
- Có một điều thú vị: thêm tên dự án vào lại làm mô hình kém đi, vì 43% giao dịch năm 2025 nằm ở dự án mới mà mô hình chưa từng thấy.

## 14. Chia nhóm khu vực (~1 phút)
- Em dùng K-Means chia 49 khu vực thành nhóm, dựa trên 5 thông tin: mức giá, tốc độ tăng giá, số giao dịch, tỷ lệ Off-Plan và diện tích căn.
- Em chọn 4 nhóm, vì các chỉ số đánh giá cho các số nhóm khác nhau gần như ngang nhau, mà 4 nhóm thì dễ giải thích nhất.
- Nhóm Emerging hot spots: giá vừa, tăng nhanh nhất, gấp khoảng 2,5 lần trong 3 năm.
- Nhóm Prime: giá cao nhất nhưng tăng chậm nhất.
- Nhóm Mass-market: đông người mua bán nhất.
- Nhóm cuối: khu villa, nhà lớn đã xây xong.
- Kết quả được lưu vào MySQL để dùng tiếp trong Power BI.

## 15. Đề xuất (~45 giây)
- Muốn đầu tư để ăn tăng giá thì nhìn vào nhóm Emerging hot spots. Nhưng phải theo dõi dự án có giao nhà đúng hạn không, vì nhóm này phần lớn là Off-Plan.
- Mua để ở hoặc cho thuê thì chọn nhóm Mass-market, vì dễ bán lại.
- Muốn giữ tài sản lâu dài thì chọn nhóm Prime.
- Có thể dùng mô hình đoán giá để kiểm tra nhanh giá chào bán: lệch hơn khoảng 13% so với giá mô hình thì nên xem kỹ lại.

## 16. Hạn chế (~30 giây)
- Dữ liệu không có view, tầng, chất lượng nhà hay tên chủ đầu tư, nên mô hình đoán chưa tốt với nhà siêu sang.
- Dữ liệu không có giá thuê, nên chưa tính được lợi nhuận cho thuê.
- Hướng làm tiếp: thêm dữ liệu thuê nhà, cho ETL tự chạy hàng tháng, và đưa các nhóm khu vực vào dashboard.

## 17. Cảm ơn (~15 giây)
- Em cảm ơn thầy cô và các bạn đã lắng nghe.
- Code, dashboard và notebook em để trên GitHub.
- Em xin nhận câu hỏi ạ.

---

## Chuẩn bị hỏi đáp

**Sao dùng trung vị mà không dùng trung bình?**
- Giá bị kéo lệch bởi vài giao dịch cực lớn, ví dụ một tòa nhà bán 1,86 tỷ AED.
- Giá trung bình khoảng 2,76 triệu AED, gần gấp đôi trung vị 1,36 triệu.
- Trung vị cho thấy một giao dịch bình thường tốt hơn.

**Sao chỉ tính giá/sqft cho căn hộ và villa để ở?**
- Đất tính theo diện tích lô, nên giá mỗi sqft rẻ hơn rất nhiều.
- Bán cả tòa nhà là bán sỉ. Cửa hàng, văn phòng thì có cách định giá khác.
- Gộp chung vào sẽ làm con số sai. Nguồn dữ liệu cũng hướng dẫn lọc như vậy.

**Sao không xóa 118 nghìn dòng trùng?**
- Mỗi dòng có mã giao dịch riêng.
- Xem kỹ thì đó là chủ đầu tư bán nhiều căn giống nhau trong cùng một ngày, ví dụ 60 căn studio cùng dự án, cùng diện tích, cùng giá.
- Đó là giao dịch thật, xóa đi thì đếm thiếu.

**Chạy lại ETL có bị nhân đôi dữ liệu không?**
- Không. Mỗi lần chạy, chương trình xóa 6 bảng cũ và tạo lại từ đầu, rồi kiểm tra số dòng khớp.

**Mô hình có bị "nhìn trộm đáp án" không?**
- Không dùng giá bán làm đầu vào, vì giá/sqft được tính từ giá bán.
- Thông tin thị trường lấy của tháng trước, tức là đã biết trước khi giao dịch xảy ra.
- Mô hình được kiểm tra trên năm 2025, năm nó chưa từng học.

**R² = 0,64 có thấp không?**
- Với giá nhà mà chỉ biết vị trí, diện tích và loại căn thì đây là mức hợp lý.
- Phần còn lại phụ thuộc vào view, tầng, hướng, chất lượng nhà, những thứ dữ liệu không có.
- So với cách đoán đơn giản bằng giá chung thì mức lệch giảm gần một nửa, từ 25% xuống 13%.

**Sao chọn 4 nhóm?**
- Điểm Silhouette của các lựa chọn từ 3 đến 8 nhóm gần như bằng nhau (0,27–0,30), không có lựa chọn nào nổi bật.
- Biểu đồ Elbow gãy ở khoảng 3–4 nhóm.
- Em chọn 4 vì nhóm nào cũng có ý nghĩa rõ ràng và dễ trình bày.

**Sao năm 2026 có thể giảm ít hơn 21%?**
- Có giao dịch được đăng ký trễ. Dữ liệu chỉ chụp tới ngày 5/10/2026, nên mấy tháng gần đây có thể còn được bổ sung thêm.

**Làm sao biết phần giữa của mã giao dịch là mã thủ tục?**
- Không có tài liệu nào ghi, em tự kiểm tra trên dữ liệu.
- Trên 1.320.458 dòng có đủ cả hai cột, phần thứ hai của mã giao dịch trùng mã thủ tục ở 100% dòng.
- Vì vậy dùng nó để điền 23.324 dòng bị trống là an toàn (slide 5).

**Al Barsha South Fourth là khu nào?**
- Đó là tên chính thức trên bản đồ địa chính của DLD.
- Người Dubai hay gọi khu này là Jumeirah Village Circle (JVC).

**Cờ "tháng đủ dữ liệu" nghĩa là gì?**
- Tháng đó nằm trọn trong khoảng thời gian của dữ liệu. Chỉ tháng 10/2026 bị cắt ngang nên mới bị đánh dấu là chưa đủ.
- Thứ Bảy và Chủ nhật luôn không có giao dịch, vì Sở Đất đai nghỉ. Đó là chuyện bình thường, không phải thiếu dữ liệu.
