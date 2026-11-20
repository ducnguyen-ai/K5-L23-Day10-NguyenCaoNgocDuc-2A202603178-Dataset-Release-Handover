# Báo cáo Nhóm 18 — Day 10

Nhóm 18 thực hiện kiểm tra và bàn giao lô luyện tập seed 3007. Thông tin thành viên và phân công được ghi tại TEAM.md.

## 1. Số liệu luyện tập
- Seed luyện tập chính: r3007.
- F1 tự đo trên r3007 (lỗi luật / lỗi gán nhãn / tổng): 1,0 / 0,6 / 0,8. Kết quả làm tròn từ `scripts/score_findings.py`.
- Số ứng viên trên lô sạch (--no-faults): 0.
- Số ứng viên trên lô r3007: 18 ứng viên thuộc 17 ảnh.
- Kết quả review r3007: 10 confirmed, 8 rejected.

### Kiểm chứng phần Người 1

Năm kiểm tra file/YOLO trên r3007 tìm 6 mục lỗi, lô đối chứng 50 ảnh tìm 0 mục lỗi. Phần tích hợp có 11 lỗi luật. Gộp các lỗi luật với 10 kết luận confirmed tạo 21 mục trong r3007/errors.json. Kết luận review được lưu tại r3007/review_log.csv. Sau tích hợp, 23 test tự tạo đạt và bộ kiểm bàn giao H1–H17 đạt 17 PASS, 0 FAIL.

### Phương pháp đối chiếu YOLO và Panoptic

Hệ thống chuyển bounding box YOLO từ tọa độ chuẩn hóa sang tọa độ pixel, sau đó đối chiếu với các panoptic segment loại thing.
Việc so sánh lớp dựa trên tên class thay vì category ID, vì hai hệ nhãn YOLO và Panoptic sử dụng hệ thống ID khác nhau.
Sử dụng pixel mask, tỷ lệ độ phủ và bounding box để tạo ứng viên cho năm loại lỗi: class_swap, category_swap, bbox_drift, missing_box và instance_merge.

### Ngưỡng sử dụng

- MIN_SEGMENT_PIXELS = 64.
- MATCH_SEGMENT_COVERAGE = 0.45.
- DRIFT_SEGMENT_COVERAGE = 0.80.
- MERGE_BOX_COVERAGE = 0.50.

Các ngưỡng được kiểm tra bằng lô sạch và lô luyện tập, không sử dụng dữ liệu _private hoặc nhãn nguồn để quyết định kết luận của từng ảnh.

## 2. Vì sao báo hết ứng viên làm F1 giảm?
Trên lô r3007, công cụ cross-check sinh ra 18 ứng viên nghi vấn. Sau khi xem ảnh và đối chiếu bounding box YOLO với panoptic mask, nhóm đưa ra 10 kết luận confirmed và 8 kết luận rejected. Các ứng viên bị rejected chủ yếu liên quan đến hiện tượng bounding box chồng lấn tự nhiên, vật thể đứng sát nhau, segment có phạm vi lớn hoặc hình dạng đối tượng khó phân biệt. Nếu đưa toàn bộ 18 ứng viên vào errors.json mà không review, những trường hợp thực tế không phải lỗi cũng sẽ bị báo sai, làm tăng số false positive (FP). Precision được tính theo công thức: Precision = TP / (TP + FP) F1 là trung bình điều hòa của Precision và Recall. Vì vậy, khi số false positive tăng, Precision có thể giảm, kéo theo F1 giảm ngay cả khi Recall không thay đổi. Nhóm chỉ đưa các kết luận confirmed vào errors.json; các ứng viên rejected được giữ lại trong review_log.csv để làm bằng chứng quá trình kiểm tra. F1 thực tế sau khi gộp: 0.8

## 3. Quyết định và lineage
- **QC v1:** 19/250 = 7,6%. Có 21 mục lỗi trong `errors.json`. Bộ kiểm đếm mỗi ảnh hoặc cảnh một lần, nên có 19 mục tiêu lỗi.
- **Kết luận v1:** `HOLD` vì tỷ lệ lỗi vượt 2%. `R-021` đã train trên lô `lab250_95697c6d4612` và cần xem lại hoặc train lại.
- **Bàn giao v2:** `lab250_95697c6d4612_v2` có 240 ảnh, 1.635 nhãn và 10 ảnh chuyển sang hàng đợi gán lại. Bộ kiểm xác nhận v1 nguyên vẹn và v2 đạt H1–H17 trên lô r3007 tái lập bằng script chính thức.

## 4. Hash chứng minh gì, không chứng minh gì?

SHA-256 được tính từ toàn bộ bytes của file và đối chiếu với hash ghi trong manifest. Khi hai hash khác nhau, bytes hiện tại không khớp với giá trị đã được ghi. Cần mở ảnh để xác định nguyên nhân trước khi quyết định cập nhật manifest hoặc chuyển ảnh hỏng vào rework.

Hash khớp xác nhận tính nhất quán giữa file và giá trị tham chiếu, còn chất lượng nhãn cần được kiểm tra bằng luật và xem ảnh. Một file nhãn có thể gán sai lớp, bỏ sót vật hoặc vẽ lệch box nhưng vẫn có hash khớp manifest. Trong bài, hash giúp kiểm tính toàn vẹn file và bảo toàn phiên bản bàn giao.

## 5. Truy vết
Nguyễn Chí Tài phụ trách truy vết và bảo mật. Với r3007, ticket nêu `scene_197` và `scene_309`. Lọc ảnh có box YOLO lớp `bottle` (mã 39) và job dùng guideline v1.2. Ảnh trong các cảnh ticket thuộc tầng A, ảnh ở các cảnh khác thuộc tầng B. Lấy guideline theo `job_id` trong `jobs.csv` vì trường phiên bản ở từng ảnh có thể bị ghi sai.

Kết quả trong `submission/r3007/trace.json` gồm 2 ảnh ở tầng A, 4 ảnh ở tầng B và 5 mã người gán hoặc kiểm trong `notify`. Cả ba mục có F1 tự đo làm tròn là 1,0. Ảnh bảo mật `000000020992.jpg` khớp SHA-256 với ảnh Người 5 đã trực tiếp xem.

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
- Bản tái lập của Người 5 có mã `lab250_68efac8c866e`. Trên máy bàn giao Windows, hai file JSON dùng để tính mã lô có dấu xuống dòng CRLF và cho mã `lab250_95697c6d4612`. Thay CRLF bằng LF trong bộ nhớ cho đúng mã của Người 5. `trace.json` và bằng chứng ảnh bảo mật đã được đối chiếu trên bản bàn giao Windows.
- Log review do Người 3 chuyển có 18 dòng, gồm 10 xác nhận và 8 bác bỏ. Nhóm cần bổ sung tên thực tế vào ghi chú từng lượt xem để đáp ứng yêu cầu ghi người xem.

## 7. Tích hợp và tình trạng cuối

Đã tích hợp tools/trace_query.py, tests/test_trace_query.py và bản sửa tools/view_qc.py từ nhánh Nguyễn Chí Tài. Giải quyết xung đột bằng bộ r3007 trên main đã đạt kiểm tra bàn giao. Truy vết chạy lại trên delivery Windows hiện tại khớp trace.json đã nộp, hash ảnh bảo mật khớp bằng chứng học viên.

Kết quả chuẩn nằm trong r3007/. Phần submission giữ các file theo cấu trúc nộp của đề cho lô luyện tập. Mục cần bổ sung là tên người xem thực tế trong 18 dòng review.
