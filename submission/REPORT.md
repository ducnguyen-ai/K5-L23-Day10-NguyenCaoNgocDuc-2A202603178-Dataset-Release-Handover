# Báo cáo nhóm <<XX>>

## 1. Số liệu luyện tập
- Seed luyện tập chính: r3007.
- F1 theo seed (rule / cross_check / overall): [CHỜ KẾT QUẢ CHẤM].
- Số ứng viên trên lô sạch (--no-faults): 0.
- Số ứng viên trên lô r3007: 18 ứng viên thuộc 17 ảnh.
- Kết quả review r3007: 10 confirmed, 8 rejected.

### Kiểm chứng phần Người 1

Năm kiểm tra file/YOLO chạy trên r3007 tìm6mục lỗi, lô sạch50ảnh tìm0mục lỗi. Bản đề18 đã sửa từ ZIP do học viên cung cấp tìm5mục lỗi thuộc phạm vi Người1. Nguồn số liệu là runs/r3007/rules.json, runs/clean/rules.json và runs/de_an_work/rules.json, được tổng hợp trong person1_status.json. Có8kiểm thử tự tạo đạt. Các số này chưa phải F1 và chưa bao gồm phần metadata/panoptic hay kết luận review ảnh.

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
<<QC v1 a/b, kết luận, vì sao R-021 phải xem lại hoặc train lại.>>

## 4. Hash chứng minh gì, không chứng minh gì?

SHA-256 được tính từ toàn bộ bytes của file và đối chiếu với hash ghi trong manifest. Khi hai hash khác nhau, bytes hiện tại không khớp với giá trị đã được ghi. Cần mở ảnh để xác định nguyên nhân trước khi quyết định cập nhật manifest hoặc chuyển ảnh hỏng vào rework.

Hash khớp xác nhận tính nhất quán giữa file và giá trị tham chiếu, còn chất lượng nhãn cần được kiểm tra bằng luật và xem ảnh. Một file nhãn có thể gán sai lớp, bỏ sót vật hoặc vẽ lệch box nhưng vẫn có hash khớp manifest. Trong bài, hash giúp kiểm tính toàn vẹn file và bảo toàn phiên bản bàn giao.

## 5. Truy vết
<<Tiêu chí tầng a/b, vì sao lấy guideline theo job.>>

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
<<>>
