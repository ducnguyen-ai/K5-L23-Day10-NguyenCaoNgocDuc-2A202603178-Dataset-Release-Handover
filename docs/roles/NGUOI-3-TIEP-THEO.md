# Người 3 — Làm tiếp sau khi nhận phần Người 1

## 1. Bạn nhận gì và cần chờ phần nào?

Đức đã bàn giao code năm kiểm tra file/YOLO và điểm chạy validator/validate.py. Kết quả riêng Người 1 trên r3007 có6 mục lỗi, đề 18 đã sửa có5 mục lỗi. Bản chia sẻ nằm tại submission/person1/.

Người 2 bổ sung bốn kiểm tra metadata/panoptic. Bạn phụ trách đối chiếu nhãn, sinh ứng viên, chia ảnh cho cả nhóm xem, tổng hợp kết luận và chốt errors.json. Người 4 nhận bộ kết quả của bạn để rà soát tiếp.

rules.json cuối phải gồm đủ lỗi luật đã tích hợp. Hàng đợi review sinh từ code của bạn. Kết quả hiện có của Người 1 là đầu vào để ghép.

## 2. Lấy code và kiểm tra đường dẫn

Mở terminal ở gốc repo:

```text
git pull origin main
python --version
```

Kiểm tra và lưu code của bạn trước khi pull nếu đang có thay đổi chưa commit. Nếu nhận ZIP qua Zalo, đối chiếu file trước khi ghép.

Luyện tập dùng runs/r3007/delivery/. Lô đối chứng dùng runs/clean/delivery/. Đề ẩn dùng delivery/ ở gốc, giải nén từ ZIP de_an_18.zip đã sửa mà nhóm được cung cấp. Chạy các lệnh ở các mục sau trên đúng lô đang làm.

## 3. Viết phần đối chiếu

Tạo validator/cross_check.py. Giao diện điểm chạy Người 1 đang chuẩn bị:

```text
generate_candidates(delivery: pathlib.Path) -> list[dict]
```

Hàm trả danh sách ứng viên. validate.py bọc danh sách đó trong khóa candidates và ghi file --candidates. Nếu đã viết module/hàm tên khác, gửi Đức để ghép adapter.

Thực hiện lần lượt:

1. Đọc classes.txt, labels/, masks/ và panoptic.json trong delivery.
2. Đổi box YOLO sang pixel bằng kích thước của từng ảnh.
3. Ghép tên lớp detection với tên categories của panoptic. Hai hệ dùng ID khác nhau nên đối chiếu qua tên.
4. Tìm segment thing và box cùng vị trí. Dùng cả pixel mask, độ phủ và bbox để đánh giá ca nghi lệch hoặc gộp vật.
5. Sinh ứng viên cho năm loại dưới đây.

| Loại | Dấu hiệu cần đưa ra xem |
|---|---|
| class_swap | Detection có thể sai lớp so với vật và mask |
| category_swap | Panoptic có thể sai lớp so với vật và box |
| bbox_drift | Box lệch khỏi vùng vật trong mask |
| missing_box | Segment thing đáng kể chưa có box phù hợp |
| instance_merge | Một segment có thể chứa hai vật cùng lớp |

Khi hai nguồn bất đồng lớp, cần người xem ảnh xác định bên nào sai. Có thể lưu một ca bất đồng cùng hai khả năng để người review chọn đúng loại. Khi ghi kết luận, dùng đúng class_swap hoặc category_swap đã xác nhận.

Bạn cùng Người 2 chốt định dạng từng ứng viên để công cụ xem đọc được. Đề xuất gồm image/target, type hoặc loại nghi vấn, box_index/segment_id, vị trí và evidence. Tên trường chi tiết là giao diện nhóm tự thống nhất. Điểm chạy hiện chỉ yêu cầu hàm trả danh sách và bọc vào khóa candidates.

Giữ validator dùng thư viện chuẩn và chạy offline. Công cụ xem ảnh có thể dùng Pillow riêng.

## 4. Chọn phương pháp ghép bằng lô sạch

Nếu máy chưa có dữ liệu luyện tập, tải bằng script download_public.py rồi tạo r3007 một lần theo GUIDE. Lô sạch chưa có thì tạo:

```text
python scripts/inject_release.py --seed 5 --no-faults --out runs/clean
```

Khi đã có module của bạn, chạy:

```text
python validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
python validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
```

Kiểm tra CLI đã gọi đúng module. Status pending_cross_check_integration nghĩa là chưa có kết quả đối chiếu. Khi sinh ứng viên thành công, status là generated_for_human_review.

Lô sạch có thể vẫn có ứng viên do khác biệt tự nhiên giữa nhãn detection và panoptic. Ghi số ứng viên và số ảnh riêng biệt, cùng ngưỡng ghép/độ phủ và cách xử lý crowd hoặc vật bị che. Chọn hàng đợi đủ khả năng xem hết. Ghi cách chọn vào REPORT.md.

Dùng score_findings.py để tự đo kết quả tổng hợp theo rules. Việc thay đổi một phần danh sách rồi xem điểm nhằm dò ảnh nào là đáp án bị cấm. Bằng chứng confirmed/rejected phải đến từ xem ảnh.

## 5. Chia ảnh cho cả năm người

Nhóm ứng viên theo tên ảnh. Chia gần đều số ảnh và cân nhắc ảnh đông vật để cân bằng việc xem. Mỗi ảnh có một người phụ trách chính, các ca trong cùng ảnh đi cùng người đó.

Gửi cho từng người tên ảnh, những ca nghi vấn, vị trí file ảnh/nhãn/mask và cách mở công cụ xem. Cùng Người 2 thử mở được ít nhất một ca trước khi chia cả hàng đợi. Bạn cũng tự xem phần ảnh của mình.

## 6. Thu kết luận review

File luyện tập là runs/r3007/review_log.csv. File đề ẩn là submission/de_an/review_log.csv. Giữ đúng header:

```csv
image,type,verdict,note
```

- image là tên ảnh không có đuôi, đúng với target.
- type là một trong năm lỗi gán nhãn ở mục 3.
- verdict là confirmed hoặc rejected.
- note có tên người xem và điều quan sát cụ thể. Với confirmed đề ẩn, ghi chú tối thiểu20 ký tự và có nội dung riêng của ca đó.

Confirmed là kết luận người xem đã xác nhận lỗi. Rejected cần lý do như khác biệt do che khuất hoặc crowd. Khi nhiều người gửi kết luận mâu thuẫn cho cùng ảnh/loại, mở ảnh và chốt một kết luận trước khi gộp.

Các lỗi luật được lấy từ rules.json. Các dòng confirmed đưa vào merge_review.py phải là lỗi gán nhãn, vì script kiểm tra trường type của các dòng này.

## 7. Chốt kết quả luyện tập

Xác nhận Người 2 và Đức đã ghép đầy đủ lỗi luật, rồi chạy:

```text
python scripts/merge_review.py --rules runs/r3007/rules.json --review runs/r3007/review_log.csv --out runs/r3007/errors.json
python scripts/score_findings.py --run runs/r3007
```

Báo cáo ghi F1 thật theo nhóm lỗi, số ứng viên lô sạch/luyện tập, ngưỡng đã dùng và lý do báo hết ứng viên có thể làm F1 giảm. Ghi nguồn file và mẫu số. Chuyển errors.json đã chốt cho Người 4.

## 8. Làm đề ẩn

Khi code đã ghép, Đức hoặc bạn chạy trên delivery/:

```text
python validator/validate.py delivery --out runs/de_an_work/rules.json --candidates submission/de_an/candidates.json
```

Kiểm candidates đã được sinh, chia ảnh cho cả năm người, thu review vào submission/de_an/review_log.csv. Sau khi chốt các kết luận:

```text
python scripts/merge_review.py --rules runs/de_an_work/rules.json --review submission/de_an/review_log.csv --out submission/de_an/errors.json
```

Gửi Người 4 ba file candidates.json, review_log.csv và errors.json. Báo Đức phần đã xong, phần còn cần rà, thời điểm có thể tập hợp bài. Nhóm còn cần trace.json do người phụ trách truy vết hoàn thành trước khi nộp đủ đề ẩn.

## 9. Bạn bàn giao những gì?

- cross_check.py hoặc module thực tế kèm hàm cần gọi.
- candidates.json của các lô đã chạy, phương pháp/ngưỡng và số ứng viên đo được.
- Cách chia ảnh, review_log.csv do người thật xem.
- errors.json đã gộp và số liệu báo cáo luyện tập.
- Hướng dẫn công cụ xem ảnh dùng cùng Người 2.

Đề yêu cầu mỗi thành viên ít nhất hai commit có nội dung. Có thể chia thành commit logic đối chiếu và commit review/số liệu đã xác minh. Giữ file đề và scripts gốc theo rules, chép sản phẩm luyện tập sang submission theo SUBMISSION.md khi nộp. Tránh đưa dữ liệu runs, data_source, delivery, ZIP và secret vào commit.

## 10. Hoàn thành khi nào?

Module được CLI gọi thành công, ứng viên của lô sạch/luyện tập đã đo, cả nhóm đã xem các ảnh được chia, review_log được kiểm tra, errors.json đã gộp và chuyển Người 4. Bạn phải giải thích được vì sao một ca được confirmed/rejected và vì sao precision/F1 có thể giảm khi báo thừa.

Nguồn nhiệm vụ là NGUOI-3.md do học viên cung cấp. Xem [RULES.md](../../RULES.md), [GUIDE.md](../../GUIDE.md), [mẫu review](../../templates/review_log.csv), [RUBRIC.md](../../RUBRIC.md).

## Quy tắc bắt buộc khi thực hiện

- Validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn Python và chạy offline.
- Không đọc _private hoặc nhãn COCO nguồn trong data_source, không dùng --dev-truth hay --truth-dir.
- Các dòng confirmed/rejected cần người trong nhóm xem ảnh và ghi tên người xem. AI được hỗ trợ code, prompt và cách kiểm lại ghi vào submission/prompts.md.
- Giữ delivery v1 và scripts của đề. Khi có bug thật, ghi rõ trong REPORT.md và báo giảng viên.
- Mọi con số lấy từ kết quả chạy thật. Điểm chấm dùng để tự đo phương pháp, việc dò đáp án qua thay đổi từng phần danh sách bị cấm theo RULES.md.
