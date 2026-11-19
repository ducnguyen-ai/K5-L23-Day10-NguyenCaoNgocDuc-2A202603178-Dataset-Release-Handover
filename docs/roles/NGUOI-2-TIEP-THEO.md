# Người 2 — Làm tiếp sau khi nhận phần Người 1

## 1. Bạn nhận được gì?

Người 1 là Đức, đã làm năm kiểm tra file/YOLO và điểm chạy `validator/validate.py`. Lệnh chạy, kiểu kết quả và chỗ ghép module đã có trong [validator/README.md](../../validator/README.md).

Kết quả hiện có của riêng Người 1:

| Lô | File chia sẻ | Số mục lỗi |
|---|---|---:|
| Luyện tập3007 | submission/person1/r3007_rules.json | 6 |
| Đề 18 đã sửa | submission/person1/de_an_rules.json | 5 |
| Đối chứng50 ảnh | submission/person1/clean_rules.json | 0 |

Bạn nhận phần kiểm metadata, panoptic và hỗ trợ công cụ xem ảnh. Cả nhóm sẽ dùng kết quả của bạn cùng phần Người 1 để tạo rules.json đầy đủ.

## 2. Lấy code và chuẩn bị đúng lô

Mở terminal tại thư mục gốc repo. Các lệnh Python bên dưới dùng được trong CMD hoặc PowerShell.

```text
git pull origin main
python --version
python -m unittest discover -s tests -p test_file_yolo.py -v
```

Nếu máy đã có code chưa commit, kiểm tra `git status` và lưu phần của bạn trước khi pull. Nếu nhận ZIP qua Zalo, so các file trong gói với repo trước khi ghép vào code đang làm.

Máy chưa có dữ liệu luyện tập thì tải bằng `python scripts/download_public.py`, tạo lần đầu bằng `python scripts/run_lab.py --seeds 3007`. Máy đã có r3007 đang làm tiếp trên lô đó. Máy làm đề ẩn giải nén ZIP `de_an_18.zip` đã sửa do nhóm chuyển vào gốc repo để có thư mục delivery/.

## 3. Viết bốn kiểm tra của bạn

Tạo `validator/metadata_panoptic.py`. Điểm chạy Người 1 hiện gọi hàm sau:

```text
validate(delivery: pathlib.Path) -> list[dict]
```

Hàm trả danh sách lỗi, mỗi lỗi có hai trường type và target. Nếu module bạn đã viết tên khác, gửi Đức tên file/hàm và dạng dữ liệu trả về để sửa adapter khi tích hợp.

| Loại lỗi | Việc kiểm tra | target |
|---|---|---|
| scene_leak | Dùng metadata.json nhóm ảnh theo scene_id, tìm cảnh xuất hiện ở nhiều split | scene_id |
| guideline_mismatch | Lấy job_id của ảnh, đối chiếu guideline ảnh với guideline của job trong jobs.csv | Tên ảnh không có đuôi |
| invalid_category_id | Tìm segment có category_id nằm ngoài danh sách categories của panoptic.json | Tên ảnh không có đuôi |
| thing_overlap | Đếm pixel thật theo segment_id trong mask, so với area khai trong segments_info, phát hiện area khai lớn hơn số pixel thật của segment thing | Tên ảnh không có đuôi |

Ví dụ định dạng để hiểu giao diện, không phải kết quả thật:

```json
[{"type":"guideline_mismatch","target":"ten_anh"},{"type":"scene_leak","target":"scene_x"}]
```

Khi đọc mask, dùng scripts/pngutil.py. Công thức segment_id = R + G*256 + B*65536. ID0 là nền. Phân biệt thing/stuff qua categories và xử lý theo định nghĩa lỗi trong [DELIVERY.md](../DELIVERY.md). Giữ mỗi cặp type/target một lần. Chạy validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn Python và chạy offline.

## 4. Ghép và chạy thử

Nếu dùng đúng tên module/hàm ở trên, validate.py tự gọi phần của bạn. Chạy từ gốc repo:

```text
python validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
```

Kết quả rules.json lúc này gồm năm kiểm tra Người 1 và bốn kiểm tra của bạn. Đối chiếu các loại lỗi thực tế để xác nhận phần metadata/panoptic có chạy.

Nếu còn PENDING về cross_check, báo Người 3 nối phần sinh ứng viên. candidates.json có status pending_cross_check_integration cần chờ module Người 3 trước khi dùng chia ảnh review.

## 5. Kiểm thử trên lô sạch và seed khác

Nếu lô sạch chưa có, tạo một lần:

```text
python scripts/inject_release.py --seed 5 --no-faults --out runs/clean
```

Chạy kiểm tra lô sạch:

```text
python validator/validate.py runs/clean/delivery --out runs/clean/rules.json --candidates runs/clean/candidates.json
```

Mục tiêu là 0 lỗi luật trên lô sạch. Nếu có cảnh báo, kiểm tra cách đọc metadata, tên trường, diện tích pixel hoặc định nghĩa lỗi. Ghi lỗi thật đã sửa và cách kiểm lại vào prompts.md nếu có AI hỗ trợ.

CP1 yêu cầu thử trên ít nhất hai seed luyện tập. Seed chính là3007. Có thể dùng3008 làm seed thử bổ sung, tạo vào thư mục mới khi chưa có:

```text
python scripts/inject_release.py --seed 3008 --out runs/r3008
python validator/validate.py runs/r3008/delivery --out runs/r3008/rules.json --candidates runs/r3008/candidates.json
```

Dùng inject_release.py cho seed thêm để giữ lineage của lô chính. Sau khi có kết quả errors.json luyện tập đúng phạm vi, nhóm dùng score_findings.py để tự đo tổng hợp. Không suy F1 từ số mục lỗi đã tìm được.

Ghi lại tên lô, số lỗi theo loại, số ứng viên khi đã ghép cross_check và câu lệnh. Các con số cần lấy từ lần chạy thật.

## 6. Cùng Người 3 chuẩn bị xem ảnh

Thống nhất dữ liệu ứng viên với Người 3 trước khi nối công cụ xem. Công cụ cần mở theo tên ảnh, hiện box YOLO, mask hoặc viền segment, và phóng to vùng nghi lỗi. Pillow được phép dùng trong công cụ xem riêng. Validator vẫn dùng thư viện chuẩn.

Trang Người 1 đã làm chỉ phục vụ xem box file/YOLO. Phần hỗ trợ xem mask và các ứng viên đối chiếu do bạn cùng Người 3 hoàn thiện.

## 7. Chạy phần bạn trên đề ẩn

Sau khi ghép đủ module, dùng đúng thư mục delivery/ ở gốc:

```text
python validator/validate.py delivery --out runs/de_an_work/rules.json --candidates submission/de_an/candidates.json
```

Báo Đức và Người 3 phần metadata/panoptic đã ghép, vị trí file và các cảnh báo còn tồn tại. Khi Người 3 chia ảnh, xem ảnh của mình và gửi kết luận cùng lý do, tên người xem. Người 3 tổng hợp review_log.csv.

## 8. Bạn bàn giao những gì?

- Module metadata_panoptic.py, hoặc tên module/hàm thực tế để Đức ghép.
- Kiểm thử hoặc cách tái hiện bốn loại lỗi bạn phụ trách.
- Kết quả chạy r3007, seed thử thêm, lô sạch và đề ẩn khi đã được chạy.
- Hướng dẫn công cụ xem ảnh/mask dùng cùng Người 3.
- Các dòng review do chính bạn xem.

Khi báo nhóm, ghi rõ commit, lệnh chạy, đường dẫn kết quả và phần còn chờ. Đề yêu cầu mỗi thành viên ít nhất hai commit có nội dung. Có thể chia thành commit kiểm metadata/panoptic và commit kiểm thử/công cụ xem ảnh.

Các file code và sản phẩm nộp đặt theo cấu trúc repo. runs/, data_source/, delivery/, ZIP và secret được bỏ qua theo rules. Kết quả cần chia sẻ trên Git thì sao chép vào khu vực submission phù hợp, ghi rõ phạm vi và lô nguồn.

## 9. Hoàn thành khi nào?

Bốn kiểm tra đã được gọi từ CLI chung, lô sạch0 lỗi luật, đã thử ít nhất hai seed, đã giao code/kết quả và đã xem phần ảnh được chia. Nhóm phải giải thích được cách phát hiện scene leak, chọn guideline theo job, đổi RGB thành segment_id và so area với số pixel.

Nguồn nhiệm vụ là NGUOI-2.md do học viên cung cấp. Quy tắc chung xem [RULES.md](../../RULES.md), các pha xem [GUIDE.md](../../GUIDE.md).

## Quy tắc bắt buộc khi thực hiện

- Validator chỉ đọc delivery được truyền vào, dùng thư viện chuẩn Python và chạy offline.
- Không đọc _private hoặc nhãn COCO nguồn trong data_source, không dùng --dev-truth hay --truth-dir.
- Các dòng confirmed/rejected cần người trong nhóm xem ảnh và ghi tên người xem. AI được hỗ trợ code, prompt và cách kiểm lại ghi vào submission/prompts.md.
- Giữ delivery v1 và scripts của đề. Khi có bug thật, ghi rõ trong REPORT.md và báo giảng viên.
- Mọi con số lấy từ kết quả chạy thật. Điểm chấm dùng để tự đo phương pháp, việc dò đáp án qua thay đổi từng phần danh sách bị cấm theo RULES.md.
