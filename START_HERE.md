# Day10 — Chạy và kiểm tra lô 3007

## Phạm vi và dữ liệu

Nhóm tập trung lô luyện tập 3007 theo yêu cầu của học viên ngày 20/11/2026. Mã nhóm cần xác nhận trong TEAM.md.

data_source/ chứa kho COCO nguồn để script chính thức tạo lô. runs/r3007/delivery/ là đầu vào của validator. runs/clean/delivery/ có50 ảnh đối chứng để đo cảnh báo tự nhiên. Validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn và chạy offline theo RULES.md.

## Tạo dữ liệu trên máy mới

Chạy từ thư mục gốc repo, Python3.10+:

```powershell
python -X utf8 scripts/download_public.py
python -X utf8 scripts/run_lab.py --seeds 3007
python -X utf8 scripts/inject_release.py --seed 5 --no-faults --out runs/clean
```

Các lệnh tạo lô dùng cho máy chưa có lô. Giữ nguyên delivery khi đã làm. Seed thử thêm dùng inject_release.py vào thư mục mới.

## Khôi phục bộ bài đã nộp vào runs

Sau khi tạo dữ liệu, chép errors.json, candidates.json, review_log.csv, trace.json, security.md và thư mục handover/ từ submission/r3007/ sang runs/r3007/. Chép submission/lineage.jsonl sang runs/lineage.jsonl. Không chép đè delivery/.

```powershell
Copy-Item submission/r3007/errors.json,submission/r3007/candidates.json,submission/r3007/review_log.csv,submission/r3007/trace.json,submission/r3007/security.md -Destination runs/r3007
Copy-Item submission/r3007/handover -Destination runs/r3007 -Recurse
Copy-Item submission/lineage.jsonl -Destination runs/lineage.jsonl
python scripts/check_handover.py --run runs/r3007
```

## Chạy validator và xem ứng viên

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python tools/view_qc.py runs/r3007/delivery --candidates runs/r3007/candidates.json
```

Viewer hiển thị box YOLO, viền segment, bằng chứng ứng viên, zoom và crop. Người xem xác nhận/bác bỏ bằng việc nhìn ảnh và ghi image,type,verdict,note vào review_log.csv. Note cần tên người xem và quan sát cụ thể. Các kết luận đã có được giữ tại submission/r3007/review_log.csv, tên người xem còn cần bổ sung từ xác nhận thực tế.

## Gộp review và truy vết

Chỉ chạy gộp khi log đã được nhóm chốt:

```powershell
python scripts/merge_review.py --rules runs/r3007/rules.json --review runs/r3007/review_log.csv --out runs/r3007/errors.json
python tools/trace_query.py runs/r3007/delivery --out runs/r3007/trace.json --evidence submission/verification/r3007_trace_current.json
```

Người 4 cập nhật gói v2 khi kết quả QC thay đổi, chạy pack_release.py sau khi chốt và chạy check_handover.py. Bản hiện có240 ảnh, 1.635 nhãn và10 ảnh rework. QC v1 dùng19 mục tiêu riêng biệt/250 ảnh =7,6%. Giữ nguyên nhãn v1, chuyển ảnh lỗi detection sang rework và xử lý metadata theo GUIDE.

## Kiểm thử và bài nộp

Chạy các test tự tạo dưới đây. tests/test_pipeline.py là bộ kiểm gốc có nhánh dùng đáp án riêng, đọc RULES trước khi chọn bài test phù hợp.

```powershell
python -m unittest discover -s tests -p test_file_yolo.py -v
python -m unittest discover -s tests -p test_metadata_panoptic.py -v
python -m unittest discover -s tests -p test_cross_check.py -v
python -m unittest discover -s tests -p test_trace_query.py -v
```

Khi bộ làm việc đã hoàn chỉnh, dùng export_submission.py để xuất lại và kiểm Git trước khi push. Giữ code và sản phẩm nộp, loại runs/, data_source/, ZIP và secret theo rules. Mỗi người có ít nhất 2 commit có nội dung và giải thích được phần mình làm.

## Kiến thức và câu hỏi tự kiểm

- Lỗi luật có thể kiểm bằng cấu trúc và file, lỗi gán nhãn cần đối chiếu nguồn và xem ảnh. Tại sao hai nguồn có thể lệch tự nhiên?
- Báo thừa làm giảm precision và có thể giảm F1. Vì sao18 ứng viên không tự thành18lỗi?
- SHA-256 xác nhận bytes so với hash đã ghi. File có hash khớp nhưng nhãn sai lớp sẽ được phát hiện ở bước nào?
- V2 liên kết parent với v1. Vì sao sửa dataset không tự sửa lượt train đã dùng v1?
- Truy vết dùng guideline theo job. Vì sao trường guideline của ảnh có thể là nguồn sai?
- Review và kiểm hình thức có phạm vi khác nhau. Ai đã xem từng ảnh và quan sát được gì?

RUBRIC gốc không có mục bonus riêng. Cần hiểu kết quả thật của nhóm để trình bày và vấn đáp.
