# Bàn giao Người 5 — Nguyễn Chí Tài

MHV: **2A202603223**. Email commit: **chitain26@gmail.com**. Ngày làm: **20/11/2026**.

## Phạm vi và file

- Truy vết đề ẩn đã chốt tại [../de_an/trace.json](../de_an/trace.json), kèm [bằng chứng](de_an_trace_evidence.json). Đúng release `lab250_278031cc6eb2` trong input_receipt.json.
- Công cụ dùng lại: [../../tools/trace_query.py](../../tools/trace_query.py). Không nhúng đáp án seed; chỉ đọc delivery được truyền vào, dùng thư viện chuẩn, từ chối ghi đầu ra vào v1.
- Truy vết luyện tập có [bằng chứng r3007](r3007_trace_evidence.json): release lab250_68efac8c866e, bottle (YOLO 39), job v1.2, ticket scene_197/scene_309. Tầng A có 2 ảnh, tầng B có 4 ảnh; notify A02, A04, A05, Q01, Q03. Đã xuất [trace.json](../r3007/trace.json) và [security.md](../r3007/security.md) bằng script chính thức. Lô r3007 được tái tạo theo START_HERE.md từ COCO công khai, không lấy dữ liệu đề ẩn thay cho practice.
- TEAM.md đã bổ sung tên và mã học viên; REPORT.md có tiêu chí truy vết, kết quả hai lô và các điểm chưa đủ bằng chứng; prompts.md ghi hỗ trợ AI, lỗi giả định manifest và cách kiểm lại.

## Chạy lại truy vết

Chạy từ thư mục repo bằng Python 3.10+; trên máy này dùng python3.11:

```sh
python3.11 tools/trace_query.py runs/r3007/delivery --out runs/r3007/trace.json --evidence submission/person5/r3007_trace_evidence.json
python3.11 tools/trace_query.py ../delivery --out submission/de_an/trace.json --evidence submission/person5/de_an_trace_evidence.json
```

Trong bản làm việc này, delivery đề ẩn nằm ở thư mục cha repo, nên lệnh dùng ../delivery. Khi nhóm đặt delivery trong repo như GUIDE.md, thay bằng delivery. Công cụ cho phép --scenes, --class-name và --old-guideline nếu ticket/changelog khác mẫu; không tự đoán khi không xác định duy nhất được tiêu chí.

## Hàng đợi review đề ẩn

Validator hiện có sinh **13 bản ghi ứng viên thuộc 12 ảnh**, gồm 4 class_swap, 7 instance_merge, 1 missing_box và 1 bbox_drift. Hai instance_merge cùng img_0213 được xem chung; worksheet có 12 cặp ảnh/loại lỗi, không có verdict. Bốn ca bất đồng lớp có possible_types gồm class_swap/category_swap; người xem cần xác định detection sai hay panoptic sai và ghi loại lỗi cuối cùng phù hợp.

- [de_an_candidates_before_person5.json](de_an_candidates_before_person5.json): bản trước, chỉ có trạng thái pending_cross_check_integration, giữ để đối chiếu.
- [de_an_candidates_generated.json](de_an_candidates_generated.json): kết quả chạy thật; giống candidates.json đã cập nhật ở submission/de_an/.
- [de_an_rules.json](de_an_rules.json): 9 lỗi luật do validator hiện tại tìm thấy, chưa ghép lỗi gán nhãn.
- [de_an_review_queue.csv](de_an_review_queue.csv): worksheet trống cho Người 3 chia người xem. Không dùng làm review_log.csv đã hoàn thành.

## Bảo mật đã chốt

[security.md](../r3007/security.md) đủ ca USB, năm việc được/không và ca khuôn mặt; kết luận **Hold, báo người phụ trách** trong tình huống guideline yêu cầu làm mờ. Nguyễn Chí Tài trực tiếp xem hai ảnh trong Preview và chọn **000000020992.jpg** vì ảnh chụp cận mặt, người quay sang trái và thấy hai mắt rõ hơn ảnh đối chiếu. Lời xác nhận, release/job/scene và SHA-256 ảnh được lưu ở [security_face_observation.json](security_face_observation.json). Đây là ví dụ bảo mật do người thật xác nhận, không phải verdict lỗi gán nhãn trong review_log.csv.

## Công cụ xem ảnh

Đã khôi phục nguyên bản tools/view_qc.py từ commit **4ae5598** của nhóm do bản merge a489650 bị lỗi biến/hàm chưa khai báo. Viewer có danh sách ứng viên, evidence, chuyển ảnh, zoom và crop; không ghi kết luận thay người xem.

Trên máy có Python kèm Tkinter và Pillow, chạy:

```sh
python tools/view_qc.py ../delivery --candidates submission/de_an/candidates.json
```

Trên máy Mac hiện tại, Python 3.11 không có Tkinter; đã kiểm bằng /usr/bin/python3 có Tkinter và cài Pillow 11.3.0 riêng vào /tmp/lab10-person5-viewer-deps. Trong phiên hiện tại có thể mở bằng:

```sh
PYTHONPATH=/tmp/lab10-person5-viewer-deps /usr/bin/python3 tools/view_qc.py ../delivery --candidates submission/de_an/candidates.json
```

Thư mục /tmp có thể bị dọn; đây là môi trường kiểm công cụ, không phải dependency của validator. Sau khi kiểm các phần mềm trong môi trường phù hợp, mỗi thành viên vẫn phải trực tiếp xem ảnh và tự ghi quan sát.

## Kiểm chứng và việc nhóm còn phải làm

Đã chạy 29 test trước khi tải dữ liệu: **26 đạt, 3 bỏ qua** vì chưa có dữ liệu, không có test thất bại. Trong đó có 8 test mới cho truy vết: guideline theo job dù metadata sai, mã lớp chính xác, loại trùng ảnh/người, bảo toàn đầu vào, thiếu job/nhãn phải báo lỗi, chặn đường dẫn thoát delivery, release sai và changelog mơ hồ. Các test pipeline dùng ground truth không được chạy sau khi tải dữ liệu. Đã đối chiếu truy vết đề ẩn bằng phép lọc độc lập. GUI smoke check đã mở được 13 ứng viên, ảnh nhập tay, zoom và crop; không tạo confirmed/rejected.

Người 3 còn cần bàn giao review_log.csv có người xem và errors.json cuối cùng cho cả hai lô. Người 4 còn cần quyết định/QC, HOLD v1 nếu vượt ngưỡng, đánh giá R-021, v2 và lineage thật; sau đó mới chạy kiểm bàn giao đầy đủ. Người 1 cần xác nhận mã nhóm, thông tin thành viên, tích hợp và nộp bài theo lớp. Không có kết quả F1 mới trong phần Người 5 vì chưa có kết luận review cuối.

Đã chạy lại validator trên practice/clean: **11 lỗi luật và 18 ứng viên/17 ảnh** ở r3007, **0 lỗi luật/0 ứng viên** ở clean; kết quả thật được lưu dưới tên r3007_*.json và clean_*.json trong thư mục này. Worksheet luyện tập [r3007_review_queue.csv](r3007_review_queue.csv) còn trống, chờ Người 3 phân công người xem. Tập lỗi luật của cả practice và đề ẩn đều khớp hợp các kết quả Người 1/2 đã lưu. Snapshot trước/sau xác nhận 758 file v1 practice giữ nguyên.

[verification.json](verification.json) ghi các kết quả kiểm. [handover_check.txt](handover_check.txt) là lần chạy kiểm bàn giao hiện tại: H1 đạt; H2/H3/H4 chưa đạt vì còn thiếu errors.json cuối, review của người thật và v2. Script dừng ở H4 nên chưa chạy tới H16/H17; không tuyên bố bộ bàn giao nhóm đã đạt.

## Git và cách nhận phần việc

Đã nối lại lịch sử repo gốc, làm trên nhánh person5-nguyen-chi-tai, giữ các commit cũ của nhóm. Các commit phần Người 5 dùng đúng tên/email do học viên cung cấp. Chưa push hoặc nộp LMS; Người 1 cần tích hợp bài của các thành viên trước khi xuất bản cuối.

Từ thư mục cha repo, file Nguoi5_NguyenChiTai_2A202603223.patch chứa các commit phần Người 5 sau khi hoàn tất. Người tích hợp có thể xem patch trước rồi dùng git am trên nhánh làm việc sạch của cùng repo; không cần chép runs/, data_source/ hoặc delivery đề ẩn vào Git.
