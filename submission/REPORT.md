# Báo cáo nhóm <<XX>>

## 1. Số liệu luyện tập
- F1 theo seed (rule / cross_check / overall): <<seed: ... / ... / ...>>
- Số ứng viên trên lô sạch (`--no-faults`): <<...>>; hàng đợi trên seed luyện tập: <<... ảnh>>
- Ngưỡng đã chọn và cách chọn (không dùng `_private`): <<...>>

### Kiểm chứng phần Người 1

Năm kiểm tra file/YOLO chạy trên r3007 tìm6mục lỗi, lô sạch50ảnh tìm0mục lỗi. Bản đề18 đã sửa từ ZIP do học viên cung cấp tìm5mục lỗi thuộc phạm vi Người1. Nguồn số liệu là runs/r3007/rules.json, runs/clean/rules.json và runs/de_an_work/rules.json, được tổng hợp trong person1_status.json. Có8kiểm thử tự tạo đạt. Các số này chưa phải F1 và chưa bao gồm phần metadata/panoptic hay kết luận review ảnh.

## 2. Vì sao báo hết ứng viên làm F1 giảm?
<<Trả lời bằng số của nhóm.>>

## 3. Quyết định và lineage
<<QC v1 a/b, kết luận, vì sao R-021 phải xem lại hoặc train lại.>>

## 4. Hash chứng minh gì, không chứng minh gì?

SHA-256 được tính từ toàn bộ bytes của file và đối chiếu với hash ghi trong manifest. Khi hai hash khác nhau, bytes hiện tại không khớp với giá trị đã được ghi. Cần mở ảnh để xác định nguyên nhân trước khi quyết định cập nhật manifest hoặc chuyển ảnh hỏng vào rework.

Hash khớp xác nhận tính nhất quán giữa file và giá trị tham chiếu, còn chất lượng nhãn cần được kiểm tra bằng luật và xem ảnh. Một file nhãn có thể gán sai lớp, bỏ sót vật hoặc vẽ lệch box nhưng vẫn có hash khớp manifest. Trong bài, hash giúp kiểm tính toàn vẹn file và bảo toàn phiên bản bàn giao.

## 5. Truy vết
<<Tiêu chí tầng a/b, vì sao lấy guideline theo job.>>

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)
<<>>
