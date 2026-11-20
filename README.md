# Day 10 Lab — Nhóm 18

**Seed luyện tập: 3007.** Nhóm thực hiện kiểm tra chất lượng, bàn giao dataset v2 và truy vết trên lô luyện tập.

## Thành viên và phân công

| Vai trò | Họ và tên | MSHV | GitHub | Phần chính |
|---|---|---|---|---|
| Người 1 | Nguyễn Cao Ngọc Đức | 2A202603178 | ducnguyen-ai | File/YOLO, tích hợp validator, điều phối |
| Người 2 | Vũ Thị Thu Huyền | 2A202603115 | thuhuyen126 | Metadata/panoptic, hỗ trợ xem ảnh |
| Người 3 | Trần Đức Hòa | 2A202603181 | TranDHoa | Cross-check, review và tổng hợp lỗi |
| Người 4 | Đặng Anh Tuyền | 2A202603039 | tuyenda2011 | QC, bàn giao v2 và lineage |
| Người 5 | Nguyễn Chí Tài | 2A202603223 | nguyen-chi-tai-2005 | Truy vết và bảo mật |

## Bài nộp

- [Báo cáo Nhóm 18](submission/REPORT.md).
- [Thông tin nhóm](submission/TEAM.md).
- [Nhật ký sử dụng AI](submission/prompts.md).
- [Lineage](submission/lineage.jsonl).
- [Kết quả và gói bàn giao r3007](submission/r3007/).

```text
submission/
  TEAM.md
  REPORT.md
  prompts.md
  lineage.jsonl
  r3007/
    errors.json
    candidates.json
    review_log.csv
    trace.json
    security.md
    handover/
      lab250_95697c6d4612_v2/
      lab250_95697c6d4612_v2.sha256
```

Phạm vi bài nộp hiện tại là luyện tập 3007 theo yêu cầu của nhóm ngày 20/11/2026. Thư mục r3007 có cấu hình .gitattributes để giữ nguyên bytes của gói bàn giao khi checkout trên các hệ điều hành.

## Kết quả

| Mục | Kết quả |
|---|---|
| Review | 18 ứng viên trên17 ảnh,10 confirmed và8 rejected |
| F1 tự đo, làm tròn | Lỗi luật 1,0; lỗi gán nhãn 0,6; tổng 0,8 |
| QC v1 | 19/250 =7,6%, HOLD |
| Bàn giao v2 | 240 ảnh,1.635 nhãn,10 ảnh rework |
| Kiểm thử | 23 test tự tạo đạt, H1–H17 đạt 17 PASS và 0 FAIL |
| Truy vết | Tầng A 2 ảnh, tầng B 4 ảnh, notify 5 mã người |

Ghi chú review còn cần bổ sung đúng tên người thực sự đã xem từng ảnh.

## Chạy lại

Python 3.10+ cho validator. Viewer cần Tkinter và Pillow. Máy đã có lô thì giữ delivery hiện tại, xem [GUIDE](GUIDE.md) để tạo dữ liệu trên máy mới.

```powershell
python -X utf8 validator/validate.py runs/r3007/delivery --out runs/r3007/rules.json --candidates runs/r3007/candidates.json
python tools/view_qc.py runs/r3007/delivery --candidates submission/r3007/candidates.json
python tools/trace_query.py runs/r3007/delivery --out runs/r3007/trace.json
```

Để kiểm gói đã nộp, chép errors.json, candidates.json, review_log.csv, trace.json, security.md và handover/ từ submission/r3007 sang runs/r3007, chép submission/lineage.jsonl sang runs/lineage.jsonl. Giữ nguyên delivery, sau đó chạy:

```powershell
python scripts/check_handover.py --run runs/r3007
```

validator/, tools/ và tests/ chứa code triển khai và kiểm thử của nhóm. scripts/, templates/, examples/ và các tài liệu GUIDE, RULES, RUBRIC, SUBMISSION, CHECKPOINTS là tài nguyên đề gốc để tái lập và đối chiếu.

## Kiến thức cần nắm

Mỗi thành viên cần giải thích được lỗi luật/lỗi nhãn, precision/recall/F1, tính toàn vẹn SHA-256, version/parent của dataset, rework và truy vết theo job/guideline. Rubric gốc chấm100 điểm, không có mục bonus riêng.
