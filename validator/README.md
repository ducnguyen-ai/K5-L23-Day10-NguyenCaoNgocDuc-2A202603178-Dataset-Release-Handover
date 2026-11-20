# Validator Day10 — lô luyện tập 3007

## Module và giao diện

| File | Phụ trách | Đầu ra |
|---|---|---|
| file_yolo.py | Đức | Năm lỗi file/YOLO |
| metadata_panoptic.py | Huyền | Bốn lỗi metadata/panoptic |
| cross_check.py | Hòa | Ứng viên đối chiếu cần người xem |
| validate.py | Đức, tích hợp nhóm | Điểm chạy và JSON đầu ra |

Các module kiểm luật xuất validate(delivery: Path) trả danh sách các dict có type và target. Module cross-check xuất generate_candidates(delivery: Path) trả danh sách ứng viên. Validator chỉ đọc lô được truyền vào, dùng thư viện chuẩn và chạy offline.

## Chạy

Từ thư mục gốc repo:

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python -X utf8 validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
```

rules.json có cấu trúc errors chứa các cặp type/target duy nhất. target là tên ảnh không có đuôi, riêng scene_leak dùng scene_id. candidates.json có danh sách candidates và status generated_for_human_review sau khi module cross-check chạy.

Đầu ra đặt ngoài delivery. Điểm chạy ghi JSON qua file tạm và sắp xếp lỗi ổn định. Nếu thiếu module, CLI báo PENDING để người chạy nhận biết việc tích hợp còn thiếu.

## Phạm vi kiểm tra

- File/YOLO gồm missing_image, wrong_hash, invalid_class, bbox_out_of_bounds, duplicate_box.
- Metadata/panoptic gồm scene_leak, guideline_mismatch, invalid_category_id, thing_overlap.
- Cross-check sinh ca cần xem cho class_swap/category_swap, bbox_drift, missing_box, instance_merge. Người xem quyết định nguồn nhãn nào sai.

SHA-256 được tính lại từ bytes. Box vượt biên dùng dung sai chuẩn hóa 1e-6 để xử lý làm tròn. Box trùng cần cùng lớp, chênh kích thước tối đa 0.01 pixel và tâm lệch tối đa 2.01 pixel theo mỗi trục. Các ngưỡng đối chiếu nằm trong cross_check.py và được mô tả trong REPORT.md.

## Review và bàn giao

Xem bằng tools/view_qc.py với đường dẫn candidates. Ghi người xem, verdict và quan sát vào review_log.csv. Chỉ sau khi nhóm chốt mới gộp bằng scripts/merge_review.py. Kết quả chuẩn của lô nằm tại [submission/r3007](../submission/r3007/).

Người 4 quản lý v2/lineage. Người 5 cung cấp tools/trace_query.py và bằng chứng bảo mật. Kết quả và các số liệu kiểm tra được ghi trong [báo cáo](../submission/REPORT.md).

## Kiểm thử

Chạy unittest discover lần lượt với test_file_yolo.py, test_metadata_panoptic.py, test_cross_check.py và test_trace_query.py trong tests/. tests/test_pipeline.py là bộ kiểm gốc của đề, có phần dùng đáp án riêng nên không chạy phần đó trong luồng làm bài của nhóm.
