# Bảo mật khi làm việc — lô luyện tập r3007

Người soạn: Nguyễn Chí Tài — MHV 2A202603223.

Lô áp dụng: **r3007**, release bàn giao **lab250_95697c6d4612**, 250 ảnh COCO. Ngày hoàn thành: **20/11/2026**. Các xử lý dưới đây áp dụng cho tình huống bảo mật của đề bài; quyết định QC/phát hành toàn lô do Người 4 ghi riêng từ kết quả kiểm tra thực tế.

Người 5 ghi nhận quan sát trên bản tái lập `lab250_68efac8c866e`. Đã đối chiếu ảnh `000000020992.jpg` của bản bàn giao với SHA-256 trong bằng chứng của Người 5 và xác nhận nội dung tệp trùng khớp.

## 1. Ca USB: hết giờ, muốn chép lô về nhà làm tiếp

Không chép ảnh, nhãn, metadata hoặc gói bàn giao ra USB cá nhân để làm tiếp ở nhà. Với lô r3007, metadata và jobs.csv còn liên kết ảnh với job, người gán và người kiểm; gửi riêng nhãn hoặc ảnh chụp màn hình cũng là đưa dữ liệu ra ngoài phạm vi được cấp quyền. Gửi qua email cá nhân hay nhờ người quen làm hộ không khắc phục được việc chuyển dữ liệu và cấp quyền ngoài quy trình.

Hết giờ, lưu tiến độ trên hệ thống được phê duyệt, ghi việc còn lại và bàn giao cho người phụ trách; đăng xuất hoặc khóa máy. Nếu cần tiếp tục ngoài giờ, xin người phụ trách bố trí máy hoặc kết nối từ xa được tổ chức cho phép, dùng tài khoản cá nhân có phân quyền và nhật ký truy cập. Giữ nguyên v1, chỉ tạo bản xử lý mới khi được giao.

## 2. Năm việc: được hay không

- **Mở job được giao trên máy công ty: được**, khi đăng nhập bằng tài khoản của mình, đúng job được phân quyền và đúng công cụ được tổ chức phê duyệt. Quyền mở job này không cho phép tải hoặc chia sẻ toàn bộ lô.
- **Chụp màn hình gửi người quen: không được.** Ảnh chụp có thể lộ ảnh người thật, nhãn, mã job và thông tin dự án. Muốn hỏi nghiệp vụ, dùng kênh nội bộ và chỉ chia sẻ với người có quyền đối với job đó.
- **Chép lô ra USB cá nhân: không được.** Khó kiểm soát bản sao, việc mất thiết bị và việc thu hồi quyền. Dùng kho hoặc môi trường làm việc đã được phê duyệt.
- **Dán ảnh hoặc nhãn thật của dự án lên chatbot công khai: không được.** Chỉ dùng công cụ AI và dữ liệu đã được tổ chức cho phép, hoặc ví dụ tổng hợp đã duyệt. Riêng bài lab này dùng COCO công khai và RULES.md cho phép hỏi AI khi ghi prompts.md; ngoại lệ đó không áp dụng cho dữ liệu thật của dự án và không thay thế việc thành viên tự xem ảnh.
- **Đưa tài khoản CVAT cho đồng nghiệp: không được.** Dùng chung tài khoản làm mất truy vết ai thao tác và có thể trao quyền vượt nhu cầu. Nhờ quản trị cấp tài khoản riêng, đúng vai trò và job cần làm cho đồng nghiệp.

## 3. Ca khuôn mặt: thấy mặt người rõ trong lô, guideline yêu cầu làm mờ

Khi phát hiện ảnh có khuôn mặt nhìn rõ trái với yêu cầu làm mờ, quyết định là **Hold, báo người phụ trách**. Ghi tên ảnh, release_id, job_id và vị trí khuôn mặt trong kênh nội bộ được phép; báo trưởng nhóm hoặc người phụ trách dữ liệu để điều phối với bộ phận bảo mật theo quy trình của tổ chức. Dừng phát hành bản chưa đáp ứng yêu cầu và hỏi phạm vi ảnh cần rà thêm.

Không tự làm mờ, xóa ảnh hoặc sửa manifest của v1: những thay đổi này làm mất bằng chứng, đổi hash và có thể khiến ảnh, nhãn, manifest cùng lineage không còn khớp. Khi được giao xử lý, làm trên bản mới; người có thẩm quyền kiểm tra lại ảnh, nhãn, hash và quyết định phát hành.

**Ví dụ thật trong lô:** `000000020992.jpg`, thuộc scene_170, job J09. Nguyễn Chí Tài đã trực tiếp mở ảnh gốc trong Preview và xác nhận: người quay mặt về phía bên trái, thấy rõ hai mắt hơn ảnh đối chiếu `000000004395.jpg`, và ảnh được chụp cận mặt hơn. Đây là quan sát của học viên, không suy ra từ box person. Trong tình huống đề bài quy định guideline yêu cầu làm mờ, ảnh này cần được giữ lại làm bằng chứng và chuyển người phụ trách xử lý; trạng thái là **Hold, báo người phụ trách**, chưa phát hành bản chưa đáp ứng yêu cầu.
