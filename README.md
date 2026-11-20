# Day 10 Lab — Luyện tập 3007

Nhóm làm bài bàn giao dataset và truy vết. Phạm vi hiện tại là lô luyện tập seed **3007**, theo yêu cầu của học viên ngày 20/11/2026. Mã nhóm đang chờ xác nhận.

## Kết quả hiện có

| Mục | Kết quả |
|---|---|
| Validator | 9 loại lỗi luật và đối chiếu detection với panoptic |
| Hàng đợi luyện tập | 18 ứng viên trên17 ảnh |
| Review đã ghi | 10 confirmed, 8 rejected |
| QC v1 | 19 mục tiêu lỗi/250 ảnh =7,6%, HOLD |
| Bàn giao v2 | 240 ảnh, 1.635 nhãn, 10 ảnh chuyển rework |
| Kiểm thử sau tích hợp | 23 test đạt, H1–H17 đạt 17 PASS và 0 FAIL |
| Truy vết | Tầng A 2 ảnh, tầng B 4 ảnh, thông báo 5 mã người |

Ghi chú review cần bổ sung đúng tên người đã xem. Bằng chứng xác nhận cá nhân hiện được giữ trong verification/review_assignments.json.

## Đọc bài và xem kết quả

- [Hướng dẫn chạy trên máy](START_HERE.md).
- [Thông tin và phân công nhóm](submission/TEAM.md).
- [Báo cáo](submission/REPORT.md).
- [Bộ bàn giao r3007](submission/r3007/).
- [Kiểm chứng và bằng chứng](submission/verification/README.md).
- [Giao diện validator](validator/README.md).

## Cấu trúc repo

```text
validator/                # Kiểm file/YOLO, metadata/panoptic, cross-check và CLI
 tools/                   # Viewer box/mask và truy vết ticket
 tests/                   # Kiểm thử tự tạo và kiểm thử gốc của đề
 scripts/                 # Công cụ chính thức của giảng viên
 docs/                    # Định dạng lô và hướng dẫn vai trò
 submission/
   TEAM.md, REPORT.md, prompts.md, lineage.jsonl
   r3007/                 # Kết quả chuẩn dùng bàn giao
   verification/          # Bằng chứng, log kiểm tra và kết quả các lô thử
```

Các thư mục data_source/ và runs/ được tạo trên máy khi chạy, được Git bỏ qua.

## Chạy nhanh

Máy đã có r3007 thì dùng lô hiện tại. Máy mới tải dữ liệu, tạo seed 3007 theo [START_HERE.md](START_HERE.md).

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python tools/view_qc.py runs/r3007/delivery --candidates submission/r3007/candidates.json
python tools/trace_query.py runs/r3007/delivery --out runs/r3007/trace.json --evidence submission/verification/r3007_trace_current.json
python scripts/check_handover.py --run runs/r3007
```

Validator dùng thư viện chuẩn Python. Viewer cần Tkinter và Pillow.

## Tài liệu đề và kiến thức

Giữ [GUIDE](GUIDE.md), [RULES](RULES.md), [RUBRIC](RUBRIC.md), [SUBMISSION](SUBMISSION.md), [CHECKPOINTS](CHECKPOINTS.md) và tài nguyên gốc trong docs/assets để đối chiếu yêu cầu lớp. Rubric gốc chấm100 điểm và không có mục bonus riêng.

Sau bài, mỗi thành viên cần giải thích được lỗi luật/lỗi nhãn, precision/recall/F1, ý nghĩa SHA-256, version và parent của dataset, cách đưa ảnh vào rework, và truy vết theo job/guideline. Xem ví dụ và câu hỏi tự kiểm trong START_HERE.md.
