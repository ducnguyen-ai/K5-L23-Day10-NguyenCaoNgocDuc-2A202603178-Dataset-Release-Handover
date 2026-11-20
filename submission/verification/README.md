# Kiểm chứng lô luyện tập 3007

## Kết quả luật

| File | Phạm vi |
|---|---|
| rules/person1_r3007.json | Năm kiểm tra Người 1 trên r3007,6 mục lỗi |
| rules/person1_clean.json | Năm kiểm tra Người 1 trên lô đối chứng,0 mục lỗi |
| rules/integrated_r3007.json | Chín kiểm tra luật trên r3007,11 mục lỗi |
| rules/integrated_r3008.json | Kết quả lô thử bổ sung của Người 2 |
| rules/integrated_r3009.json | Kết quả lô thử bổ sung của Người 2 |
| rules/integrated_clean.json | Chín kiểm tra trên lô đối chứng,0 mục lỗi |
| clean_candidates.json | Hàng đợi đối chiếu lô sạch từ lần chạy đã bàn giao |
| person1_status.json | Phạm vi và kiểm thử phần Người 1 |

## Truy vết và review

- r3007_trace_current.json là bằng chứng truy vết chạy lại trên delivery Windows hiện tại. Kết quả khớp ../r3007/trace.json.
- r3007_trace_original_tai.json giữ bằng chứng gốc của Tài. Khác mã release do xuống dòng như REPORT.md đã ghi, nên đối chiếu bản current khi dùng trên máy Windows.
- security_face_observation.json giữ quan sát trực tiếp của Tài và SHA-256 ảnh ví dụ. Hash đã được đối chiếu với ảnh nguồn r3007 hiện tại.
- review_assignments.json giữ phân công gợi ý và trạng thái xác nhận cá nhân. Tên người trong review_log.csv chỉ bổ sung sau khi biết ai thực sự đã xem và ghi kết luận.
- review_queue_tai.json là phạm vi ảnh riêng đã chuẩn bị cho Tài.

## Kiểm tra sau tích hợp

- unit_tests.txt ghi kết quả các test tự tạo của validator và truy vết.
- handover_check.txt ghi đầu ra bộ kiểm chính thức H1–H17.
- score_report.md và score_findings.txt giữ kết quả tự đo aggregate bằng script chính thức.

Các file log được tạo trực tiếp từ lệnh chạy. Kết quả chuẩn để bàn giao nằm trong ../r3007/ và ../lineage.jsonl. Các bản trùng đã được dọn khỏi cây bài nộp. Bản khôi phục local nằm trong runs/cleanup_archive_20261120, được Git bỏ qua.
