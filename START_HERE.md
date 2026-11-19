# Day10 — Bắt đầu với seed 3007

## Dữ liệu trên máy

`data_source/` là kho ảnh COCO và annotation nguồn để script chính thức tạo bài. Kho này có 250 ảnh practice và 50 ảnh calib cùng nhãn detection và panoptic. `data_source/cache/` giữ các gói tải về để tái sử dụng.

`runs/r3007/delivery/` là lô giao cho nhóm kiểm tra. Seed3007 quyết định việc cài lỗi và metadata giả lập, dùng cùng seed và nguồn sẽ tái tạo cùng lô. Mọi thành viên dùng seed3007 cho lô luyện tập chính. Số3007 không tự xác định mã nhóm của lớp.

`runs/clean/delivery/` là lô đối chứng50ảnh khác, tạo bằng seed5 với --no-faults. Dùng để đo cảnh báo tự nhiên và chọn phương pháp ghép box/mask.

Theo RULES.md, validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn và chạy offline. Nguồn COCO và thư mục _private nằm ngoài phạm vi đọc của validator. Dùng script score_findings.py theo cách chính thức để tự đo tổng thể sau khi có kết quả. Review confirmed/rejected cần người trong nhóm xem ảnh.

## Nắm định dạng trước khi viết code

- images/ chứa ảnh JPG.
- labels/ chứa YOLO, mỗi dòng class_id x_center y_center width height, tọa độ chuẩn hóa0–1.
- masks/ và panoptic.json mô tả vùng pixel/segment, gồm các vật thể riêng lẻ và vùng nền. RGB của mask mã hóa segment_id.
- Ghép tên lớp qua classes.txt và categories của panoptic, vì hai hệ dùng ID khác nhau.
- manifest.json dùng để đối chiếu file và SHA256.
- metadata.json liên kết ảnh với scene, split, job, guideline. jobs.csv ghi người gán/kiểm và guideline chuẩn theo job.
- guideline/changelog.md và incoming/ticket.md dùng cho truy vết.
- release.json định danh lô, runs/lineage.jsonl ghi lịch sử. Sự kiện R-021 là lượt train giả lập cho tình huống truy vết của đề.

## Bắt đầu làm bài

Chạy PowerShell từ thư mục repo, Python3.13.7 hiện có đáp ứng yêu cầu. Luồng bắt buộc dùng thư viện chuẩn Python.

1. Đọc submission/TEAM.md, bổ sung mã nhóm, họ tên và MSHV còn thiếu, xác nhận phân công. Mỗi người cấu hình tên/email Git của chính mình.
2. Tuyenda2011 và TranDHoa viết validator/validate.py, Đức chuẩn bị công cụ xem ứng viên. Các phần bàn giao và truy vết chuẩn bị song song.
3. Khi validator có thể chạy, dùng các lệnh sau.

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python -X utf8 validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
```

rules.json là lỗi luật. candidates.json chứa ca nghi sai cần xem ảnh. Chia ảnh cho cả năm người, ghi image,type,verdict,note vào runs/r3007/review_log.csv. Note nêu người xem và điều thấy được. Mọi kết luận phải dựa trên việc xem ảnh.

Sau khi xem và chốt các ca:

```powershell
python -X utf8 scripts/merge_review.py --rules runs/r3007/rules.json --review runs/r3007/review_log.csv --out runs/r3007/errors.json
python -X utf8 scripts/score_findings.py --run runs/r3007
```

Tiếp theo làm theo GUIDE.md Pha3–6 để quyết định, lineage, bàn giao v2, truy vết, bảo mật và đề ẩn. Tạo v2 riêng khi đến Pha4. Trên2% ảnh lỗi thì HOLD v1, tương đương6/250 đã vượt ngưỡng.

## Tái lập trên máy thành viên khác

Sau khi clone repo và có Python3.10+, chạy lần đầu:

```powershell
python -X utf8 scripts/download_public.py
python -X utf8 scripts/run_lab.py --seeds 3007
python -X utf8 scripts/inject_release.py --seed 5 --no-faults --out runs/clean
```

Các lệnh này dành cho máy chưa có lô. Khi đã review, giữ lô đang dùng. Seed thử thêm tạo bằng inject_release.py vào một thư mục mới. runs/ và data_source/ được bỏ qua bởi Git. Sản phẩm cuối xuất sang submission/ theo SUBMISSION.md.

## Kiến thức cần giải thích được

Phân biệt lỗi luật và lỗi gán nhãn. Giải thích vì sao hai nguồn nhãn có thể khác nhau tự nhiên, vì sao báo thừa làm giảm precision/F1, và vì sao hash đúng chỉ xác nhận tính toàn vẹn file. Dùng scene để kiểm rò split, job để kiểm guideline và người chịu trách nhiệm. Hiểu v1, v2, parent và tác động đến lượt train đã dùng dữ liệu.

RUBRIC.md hiện chấm100điểm, không có mục bonus riêng. Bài còn cần code, review ảnh thật, bàn giao, truy vết, báo cáo và đề ẩn để hoàn thành.
