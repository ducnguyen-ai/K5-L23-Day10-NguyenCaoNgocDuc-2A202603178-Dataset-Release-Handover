# Validator Day10 — bàn giao Người 1

## Phần đã có

Người 1 là Nguyễn Cao Ngọc Đức. `file_yolo.py` cung cấp `validate(delivery: Path) -> list[dict]`, gồm missing_image, wrong_hash, invalid_class, bbox_out_of_bounds và duplicate_box.

SHA-256 được tính lại trên bytes của file ảnh/nhãn/mask có khai hash trong manifest. Box kiểm theo tọa độ chuẩn hóa với dung sai1e-6 để xử lý làm tròn6chữ số. Box trùng cần cùng lớp, kích thước lệch tối đa0.01pixel và tâm lệch tối đa2.01pixel theo mỗi trục. Kích thước ảnh đọc từ mục images của panoptic.json trong delivery. Các ngưỡng này được kiểm bằng dữ liệu tự tạo và lô sạch, cần nhóm giải thích khi vấn đáp.

`validate.py` là điểm chạy chung, xuất lỗi duy nhất theo cặp type/target, sắp xếp ổn định và ghi JSON qua file tạm. Tất cả đầu ra đặt ngoài delivery.

## Lệnh bàn giao cho Người 2 và Người 3

Từ thư mục gốc repo:

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python -X utf8 validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
```

Đề ẩn được thay bằng ZIP đã sửa `de_an_18.zip` mà học viên cung cấp. Lệnh theo nhiệm vụ mới:

```powershell
python -X utf8 validator/validate.py delivery --out runs/de_an_work/rules.json --candidates submission/de_an/candidates.json
```

`rules.json` chứa dạng sau, tên ảnh không có đuôi:

```json
{"errors": [{"type": "missing_image", "target": "ten_anh"}]}
```

Scene leak khi tích hợp có target là scene_id theo đề. Người 3 gộp rules.json với các dòng confirmed sau khi nhóm xem ảnh, bằng scripts/merge_review.py. File errors.json cuối chỉ được chốt sau phần tích hợp và review.

## Giao diện tích hợp đề xuất

Hai tên module/hàm sau được Người 1 chuẩn bị để ghép code. Đây là đề xuất kỹ thuật, chưa có xác nhận của Người 2/3. Nếu hai bạn đã dùng tên khác thì sửa adapter trong validate.py để gọi code được bàn giao.

- `validator/metadata_panoptic.py` xuất `validate(delivery: Path) -> list[dict]`. Mỗi mục có type và target. Điểm chạy chung gọi hàm rồi gộp với lỗi file/YOLO.
- `validator/cross_check.py` xuất `generate_candidates(delivery: Path) -> list[dict]`. Điểm chạy chung bọc danh sách trong khóa candidates. Người làm công cụ review thống nhất các trường type, target/image, vị trí box/segment và evidence với người sinh ứng viên.
- Các module nhận đúng đường dẫn delivery và chỉ đọc dữ liệu bên trong. Dùng thư viện chuẩn Python, chạy offline.
- Khi thiếu module, CLI in PENDING. File candidates có status=pending_cross_check_integration là chỗ chờ tích hợp, chưa phải hàng đợi review đã sinh. Danh sách rỗng ở trạng thái này chưa được dùng để kết luận không có lỗi gán nhãn.

## Kiểm chứng phần Người 1

```powershell
python -m unittest discover -s tests -p test_file_yolo.py -v
```

Có8kiểm thử dữ liệu tự tạo, bao gồm sai hash, thiếu ảnh, lớp sai, box tràn nhẹ, tọa độ không hữu hạn, box trùng và cặp vật chồng nhau tự nhiên. Kết quả thực tế lưu trong submission/person1_status.json. Lô sạch có0lỗi thuộc5kiểm tra Người1. Phần F1 tổng, kiểm metadata/panoptic và review ảnh còn chờ các thành viên phụ trách.

## Điều phối tiếp theo

1. Người 2 thử lệnh r3007, bàn giao module kiểm tra của mình và chỉ rõ hàm cần gọi.
2. Người 3 bàn giao phần sinh ứng viên hoặc tên hàm đang dùng, sau đó chia ảnh review cho cả nhóm.
3. Đức ghép các module qua điểm chạy chung, chạy lại và chuyển đúng rules.json/candidates.json cho Người 3.
4. Sau khi Người 3 chốt errors.json, chuyển kết quả cho Người 4 kiểm tra theo phân công mới.

Các thành viên tự ghi người xem và bằng chứng ảnh khi confirmed/rejected. Phần hướng dẫn này chưa ghi nhận ai đã hoàn thành review.

## File kết quả đã chia sẻ trên GitHub

- [Kết quả Người1 trên r3007](../submission/person1/r3007_rules.json).
- [Kết quả Người1 trên đề18 đã sửa](../submission/person1/de_an_rules.json).
- [Kết quả Người1 trên lô sạch](../submission/person1/clean_rules.json).

Các bản này sao chép đúng kết quả của năm kiểm tra Người1 để thành viên tải về và tích hợp. Người3 cần nhận thêm lỗi metadata/panoptic và kết luận review trước khi chốt errors.json của nhóm. Các thư mục runs và delivery được giữ trên máy làm việc theo rules của đề.
