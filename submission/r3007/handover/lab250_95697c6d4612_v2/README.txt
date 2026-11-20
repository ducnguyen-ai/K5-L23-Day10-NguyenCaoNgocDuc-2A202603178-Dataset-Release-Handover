Release: lab250_95697c6d4612_v2
Parent: lab250_95697c6d4612
Số ảnh: 240
Số nhãn: 1635
Guideline: v1.2 (J01–J04), v1.3 (J05–J10)
QC v1: 19/250 = 7,6%
Kết luận v1: Hold — tỷ lệ lỗi 7,6% vượt ngưỡng 2%.
Kết luận v2: Release — giữ 240 ảnh cho detection và chuyển 10 ảnh sang hàng đợi gán lại.
Ghi chú: Chuyển 000000022396 về split val theo đa số trong cảnh scene_214. Lấy guideline theo job trong jobs.csv. Đã mở 000000020247, ảnh hiện đúng nội dung hai con gấu và khớp nhãn detection, nên giữ ảnh và tính lại SHA-256 trong manifest v2. Ảnh 000000006723 cũng sai hash và đã chuyển đi gán lại vì lỗi class_swap. Mã người gán và người kiểm cho từng ảnh cần gán lại nằm trong rework_queue.csv. Báo đội panoptic về các ảnh vẫn giữ trong lô detection v2: 000000013659, 000000016010, 000000019742, 000000022192, 000000023781.
