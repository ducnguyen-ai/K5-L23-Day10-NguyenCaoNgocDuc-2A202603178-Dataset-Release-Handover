# Báo cáo nhóm <<XX>>

## 1. Số liệu luyện tập
- Seed luyện tập chính: r3007.
- F1 theo seed (rule / cross_check / overall): [CHỜ KẾT QUẢ CHẤM].
- Số ứng viên trên lô sạch (--no-faults): 0.
- Số ứng viên trên lô r3007: 18 ứng viên thuộc 17 ảnh.
- Kết quả review r3007: 10 confirmed, 8 rejected.

**Rà soát của Người 5, ngày 20/11/2026:** đã tái tạo r3007 và lô sạch bằng script chính thức theo START_HERE.md, rồi chạy validator hiện tại. Lô r3007 có 11 lỗi luật và 18 ứng viên/17 ảnh; lô sạch có 0 lỗi luật và 0 ứng viên. Tập lỗi luật r3007 khớp hợp các kết quả Người 1/2 đã lưu. Sau khi nhận commit 3a3c47e của Người 3, đã kiểm chứng submission/person_3/review_log.csv có 18 dòng trên 17 ảnh, gồm 10 confirmed và 8 rejected. Candidates khớp kết quả chạy lại r3007; errors.json có 21 mục, đúng bằng 11 lỗi luật cộng 10 dòng confirmed. Các ghi chú đều đủ 20 ký tự và loại lỗi cuối phù hợp các khả năng của ứng viên, nhưng cả 18 dòng chưa ghi tên người xem. Người 3 cần xác nhận người đã trực tiếp xem và bổ sung tên thật vào note; không tự gán tên thành viên bằng AI. Đây là kiểm tra tính nhất quán file, chưa xác nhận lại nội dung ảnh hoặc F1.

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
Chạy lại validator hiện tại trên r3007 đã xác minh 18 ứng viên thuộc 17 ảnh. Bộ review Người 3 bàn giao tại submission/person_3/review_log.csv có 10 confirmed và 8 rejected; đã đối chiếu số dòng và tính nhất quán với candidates/errors. Còn cần bổ sung tên người thực sự xem vào các ghi chú và hoàn thành phần xem ảnh của từng thành viên; AI không xác nhận thay nội dung ảnh.

Nếu đưa toàn bộ ứng viên vào errors.json mà không review, những trường hợp thực tế không phải lỗi cũng sẽ bị báo sai, làm tăng số false positive (FP). Precision = TP / (TP + FP); F1 là trung bình điều hòa của Precision và Recall. Khi false positive tăng trong khi TP và FN giữ nguyên, Precision giảm và F1 cũng giảm. Vì vậy chỉ đưa các lỗi gán nhãn đã được người trong nhóm xác nhận vào errors.json; lưu cả confirmed và rejected cùng quan sát cụ thể trong review_log.csv.

Giá trị F1 = 0.8 từng được ghi trong bản báo cáo trước; hiện chưa có report.md/metrics.json kèm theo để xác minh. Chưa coi đây là điểm đã được kiểm chứng.

## 3. Quyết định và lineage
<<QC v1 a/b, kết luận, vì sao R-021 phải xem lại hoặc train lại.>>

## 4. Hash chứng minh gì, không chứng minh gì?

SHA-256 được tính từ toàn bộ bytes của file và đối chiếu với hash ghi trong manifest. Khi hai hash khác nhau, bytes hiện tại không khớp với giá trị đã được ghi. Cần mở ảnh để xác định nguyên nhân trước khi quyết định cập nhật manifest hoặc chuyển ảnh hỏng vào rework.

Hash khớp xác nhận tính nhất quán giữa file và giá trị tham chiếu, còn chất lượng nhãn cần được kiểm tra bằng luật và xem ảnh. Một file nhãn có thể gán sai lớp, bỏ sót vật hoặc vẽ lệch box nhưng vẫn có hash khớp manifest. Trong bài, hash giúp kiểm tính toàn vẹn file và bảo toàn phiên bản bàn giao.

## 5. Truy vết

Người phụ trách: **Nguyễn Chí Tài — MHV 2A202603223**. Công cụ `tools/trace_query.py` chỉ đọc delivery được truyền vào và dùng thư viện chuẩn. Ticket xác định scene cần ưu tiên; changelog xác định lớp đổi quy tắc và phiên bản cũ; classes.txt chuyển tên lớp sang mã YOLO. Metadata liên kết ảnh với scene và job; jobs.csv cung cấp guideline cùng mã annotator/reviewer.

- Tầng A: thuộc scene ticket nêu, job dùng guideline cũ, và labels/ có ít nhất một box detection thuộc lớp đổi quy tắc.
- Tầng B: cùng điều kiện về job và box nhưng thuộc scene khác.
- notify: hợp mã annotator và reviewer của các job chứa ảnh ở cả hai tầng, loại trùng.

Phải lấy guideline từ **jobs.csv theo job_id**, vì guideline_version ở từng ảnh có thể bị ghi sai. Trên đề ẩn hiện có, img_0214 ghi v1.2 nhưng job J07 ghi v1.3; công cụ dùng v1.3 của job. Đây là ví dụ thực tế cho lý do không lọc trực tiếp theo guideline trên ảnh. Truy vết xác định phạm vi cần rà lại, không tự chứng minh mọi ảnh được chọn bị lỗi thiếu box.

**Đề ẩn:** release `lab250_278031cc6eb2`, khớp input_receipt.json. Ticket nêu scene_290 và scene_635; changelog đổi lớp car (YOLO 2), từ v1.2 sang v1.3. Trong 250 ảnh, 75 ảnh thuộc job v1.2; 6 ảnh còn box car được chọn: tier_a = img_0074, img_0236; tier_b = img_0135, img_0146, img_0188, img_0209. Các job liên quan là J02 và J03; notify = A02, A04, Q02. Kết quả ở `submission/de_an/trace.json`; bằng chứng scene/job/dòng nhãn và SHA-256 đầu vào ở `submission/person5/de_an_trace_evidence.json`.

**Luyện tập r3007:** đã tái lập theo START_HERE.md bằng script chính thức do bản repo nhận được không kèm runs/ và data_source/. Release mới là `lab250_68efac8c866e`. Ticket nêu scene_197 và scene_309; lớp đổi quy tắc là bottle (YOLO 39), guideline cũ v1.2. Trong 250 ảnh có 100 ảnh thuộc job cũ, 6 ảnh còn box bottle: tier_a = 000000002685, 000000009590; tier_b = 000000005193, 000000006471, 000000007574, 000000008021. Các job liên quan là J02, J03, J04; notify = A02, A04, A05, Q01, Q03. Kết quả ở runs/r3007/trace.json, bản nộp ở submission/r3007/trace.json; bằng chứng ở submission/person5/r3007_trace_evidence.json. Phép lọc độc lập cho cùng kết quả; snapshot SHA-256 trước/sau kiểm tra xác nhận nguyên vẹn 758 file trong delivery r3007. Không dùng kết quả đề ẩn thay cho lô luyện tập.

## 6. Bug hoặc điểm chưa rõ trong lab (nếu có)

Rà soát bản repo nhận được, chưa kết luận có bug trong script chính thức:

- Báo cáo còn thiếu QC v1, quyết định phát hành và tác động R-021 ở mục 3; Người 4 cần điền từ errors.json và lineage thật.
- Đã nhận bộ luyện tập Người 3 tại submission/person_3/ từ commit 3a3c47e. Số review 10 confirmed/8 rejected và phép gộp 21 lỗi đã kiểm chứng bằng file thật; 18 ghi chú còn thiếu tên người xem. F1 0.8 vẫn chưa có file kết quả chấm để đối chiếu; không suy ra F1 từ số ứng viên hoặc số confirmed. Sau khi hoàn thiện thông tin review, tích hợp file vào runs/r3007/ rồi xuất đúng submission/r3007/ theo SUBMISSION.md.
- candidates.json của đề ẩn ban đầu có trạng thái pending_cross_check_integration. Chạy lại validator hiện có trên đúng delivery đã sinh 13 bản ghi ứng viên thuộc 12 ảnh; đã cập nhật hàng đợi chính thức, lưu bản trước đó và kết quả kiểm luật trong submission/person5/. Hai bản ghi instance_merge ở img_0213 phải được xem cùng ảnh và chốt một kết luận cho cặp ảnh/loại lỗi. Bốn ứng viên bất đồng lớp có possible_types gồm class_swap và category_swap; cần người xem xác định nguồn nhãn sai.
- Chưa có review_log.csv và errors.json cuối cùng cho đề ẩn. Người 3 cần phân công người xem và gộp kết quả thật với 9 lỗi luật được validator hiện tại tìm thấy. Bản worksheet trong submission/person5/ không phải log đã review.
- README.md và TEAM.md còn mã nhóm chưa điền; một số thông tin thành viên chưa đủ. Bản tải mã nguồn ban đầu không có .git. Đã nối lại lịch sử origin/main và làm phần Người 5 trên nhánh person5-nguyen-chi-tai, dùng tên Nguyễn Chí Tài và email chitain26@gmail.com do học viên cung cấp; kiểm tra lịch sử commit của các thành viên còn lại trên repo nhóm.
- Phát hiện lỗi tích hợp trong tools/view_qc.py ở bản a489650: __init__ dùng biến top chưa khai báo; open_image dùng index chưa khai báo; render gọi Image.open(image_path) dù biến thực là path và còn gọi các hàm không tồn tại. Đã khôi phục nguyên bản viewer đầy đủ từ commit 4ae5598 của thành viên trong nhóm. Kiểm tra mở 13 ứng viên đề ẩn, chế độ nhập ảnh, zoom và crop bằng Python hệ thống có Tkinter cùng Pillow 11.3.0 đã đạt; đây là kiểm tra công cụ, không phải kết luận review ảnh.
- Lần chạy check_handover.py trên r3007 hiện có H1 PASS, H2/H3/H4 FAIL do thiếu errors.json cuối, review_log.csv và các phần của v2. Script dừng ở H4, chưa đánh giá H16/H17. Chi tiết lưu ở submission/person5/handover_check.txt; cần Người 3/4 hoàn thiện dữ liệu trước khi kiểm lại toàn bộ.
