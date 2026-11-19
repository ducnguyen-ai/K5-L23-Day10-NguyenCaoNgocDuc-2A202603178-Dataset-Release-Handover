# Người 2 — Metadata, Panoptic QC và công cụ xem ảnh

## Phạm vi

- Metadata: `scene_leak` (target là `scene_id`) và `guideline_mismatch`
  (target là tên ảnh không có phần mở rộng).
- Panoptic: `invalid_category_id` và `thing_overlap`.
- Công cụ xem ảnh: `tools/view_qc.py`, hiển thị box YOLO và biên segment.
  Dùng `+`/`-` hoặc nút zoom để phóng to vùng cần kiểm tra.

Validator dùng thư viện chuẩn, đọc dữ liệu trong thư mục delivery được truyền
vào và dùng `scripts/pngutil.py` để giải mã mask. Không đọc nhãn nguồn hay dữ
liệu riêng tư.

## Kiểm thử

Chạy các test độc lập của Người 2 từ thư mục gốc repo:

```powershell
python -m unittest discover -s tests -p test_metadata_panoptic.py -v
```

Test tạo delivery nhỏ tạm thời và kiểm tra đủ bốn loại lỗi, guideline được lấy
từ job, bỏ qua pixel nền, và không báo `thing_overlap` cho stuff.
Kết quả xác nhận: 6 test của Người 2 đạt; 8 test hiện có của Người 1 cũng đạt.

## Kết quả đã lưu

Các file seed và clean trong `results/` là đầu ra rules tổng hợp của CLI
(bao gồm cả kiểm tra file/YOLO của Người 1). File `de_an_rules.json` chỉ chứa
bốn loại do Người 2 phụ trách. Số dưới đây chỉ đếm bốn loại do Người 2 phụ trách:

| Lô | guideline_mismatch | scene_leak | invalid_category_id | thing_overlap | Tổng |
|---|---:|---:|---:|---:|---:|
| r3007 | 2 | 1 | 0 | 2 | 5 |
| r3008 | 1 | 1 | 1 | 1 | 4 |
| r3009 | 1 | 1 | 0 | 2 | 4 |
| clean | 0 | 0 | 0 | 0 | 0 |
| de_an (active delivery) | 1 | 1 | 0 | 2 | 4 |

Nguồn: `results/r3007_rules.json`, `results/r3008_rules.json`,
`results/r3009_rules.json`, `results/clean_rules.json` và
`results/de_an_rules.json`. Kết quả de_an được lọc từ lần chạy tích hợp; file
đầy đủ có cả chín lỗi luật nằm ở
`runs/de_an_work/person2_integrated_rules.json`. Các lần chạy lại r3007,
r3008, r3009 và clean cho cùng danh sách phát hiện với kết quả đã chia sẻ. Lô
clean không có phát hiện luật.

Đề ẩn được chạy trên delivery đang hoạt động theo `submission/de_an/input_receipt.json`.
Candidates vẫn ở trạng thái `pending_cross_check_integration` vì chưa có module
Người 3; chưa có kết luận review ảnh và không được xem danh sách luật là kết quả
cuối của đề.

## Chạy validator và viewer

Chạy validator tích hợp từ thư mục gốc; đầu ra đặt ngoài delivery:

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python -X utf8 validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
```

Mở một ảnh trong lô bằng tên hoặc ID:

```powershell
python tools/view_qc.py runs/r3007/delivery
```

Viewer vẽ box YOLO màu đỏ và biên segment màu cyan. Dùng phím `+`/`-`, nút
`Zoom +`, `Zoom -`, hoặc `Reset zoom`; thanh cuộn xuất hiện khi ảnh phóng lớn.
Chưa đánh dấu ảnh là confirmed/rejected chỉ dựa trên kết quả tự động.

## Còn chờ để bàn giao

- Chạy lại CLI trên lô luyện tập và lô sạch cục bộ nếu các delivery còn sẵn;
  kết quả đề ẩn hiện tại không ghi đè `runs/de_an_work/rules.json`.
- Phối hợp Người 3 để nối candidates. Sau đó người được chia ảnh cần ghi kết
  luận và lý do vào `review_log.csv`.
- Bổ sung kết quả đề ẩn cuối sau khi review và tích hợp; không đưa dữ liệu
  delivery/đề ẩn vào Git nếu quy trình nộp yêu cầu loại trừ.
