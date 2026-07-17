# Thiết kế: Bảo mật tài khoản học viên (giới hạn thiết bị + bảo vệ dữ liệu)

**Ngày**: 2026-07-17
**Trạng thái**: Đã duyệt thiết kế, chưa implement

## Bối cảnh

Dự án GradingGuard AI hiện tập trung vào chống prompt injection khi AI chấm bài luyện tập IELTS. Toàn bộ hệ thống hiện có (`backend/app/operational/auth.py`, `backend/app/api/security_v1.py`) là RBAC nội bộ dành cho **operator bảo mật** (viewer/analyst/policy_manager/security_admin/integration_service) — token tự ký HMAC, không lưu DB, không track thiết bị/session. Không có bất kỳ khái niệm "học viên đăng nhập" nào trong hệ thống: không có bảng `users`/`students`, không có trang login/register ở frontend, `/playground` gọi thẳng API chấm bài bằng token operator.

Chủ dự án quyết định đổi trọng tâm sản phẩm sang: bảo mật tài khoản học viên, cụ thể là **giới hạn mỗi học viên tối đa 2 thiết bị đăng nhập đồng thời**, và bảo vệ dữ liệu học viên (mật khẩu, bài làm, PII). Thời hạn: vài ngày trước khi nộp/demo.

## Ràng buộc & quyết định đã chốt

- **Không đụng** vào `operational/auth.py`, `security_v1.py`, engine firewall (`backend/app/firewall/`) — giữ nguyên để không phá vỡ phần chấm điểm đang hoạt động.
- Đăng nhập bằng **email + mật khẩu**.
- 1 lần đăng nhập = 1 session/thiết bị (không dùng device fingerprinting).
- Vượt quá 2 thiết bị → **từ chối đăng nhập thiết bị thứ 3**, không tự động đăng xuất thiết bị cũ.
- Học viên có trang **"Thiết bị của tôi"** để xem và tự thu hồi session từ xa.
- Bài làm & kết quả học tập: tái dùng `/playground` hiện có, gắn kết quả với `student_id` thay vì ẩn danh.
- PII (tên, email, sđt): lưu plaintext trong SQLite local, **không mã hóa at-rest** — điểm mấu chốt là không bao giờ trả password/token qua response hay ghi vào log.
- Mật khẩu: hash bằng bcrypt, không lưu plaintext.
- Token: access token ngắn hạn (JWT, ~15–30 phút) + refresh token dài hạn (~7 ngày), cả hai lưu qua **httpOnly cookie** (chống XSS đọc token qua JavaScript).
- Hệ thống học viên **tách hoàn toàn** khỏi hệ thống operator — bảng riêng, router riêng, middleware riêng.

## Kiến trúc

- Backend: module mới `backend/app/student_auth/` song song với `backend/app/operational/`, dùng lại SQLite raw (`sqlite3` chuẩn, không thêm ORM) đã có trong `operational/database.py`, tự thêm 2 bảng mới qua cơ chế migration `SCHEMA_SQL` đã tồn tại.
- Router mới `backend/app/api/student_auth_v1.py`, prefix `/api/student`.
- Frontend: thêm `/login`, `/register`, `/account/devices`; sửa `/playground` để yêu cầu đăng nhập và hiển thị lịch sử bài làm.

## Schema database

### Bảng `students`
```sql
id              TEXT PRIMARY KEY   -- uuid
email           TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL      -- bcrypt
full_name       TEXT
phone           TEXT
created_at      TEXT NOT NULL
```

### Bảng `student_sessions`
```sql
id                  TEXT PRIMARY KEY   -- uuid, đại diện cho 1 refresh token/thiết bị
student_id          TEXT NOT NULL REFERENCES students(id)
refresh_token_hash  TEXT NOT NULL      -- hash refresh token, không lưu plaintext
user_agent          TEXT               -- hiển thị "Chrome trên Windows" ở trang quản lý thiết bị
ip_address          TEXT
created_at          TEXT NOT NULL
last_seen_at        TEXT NOT NULL
expires_at          TEXT NOT NULL      -- created_at + 7 ngày
revoked_at          TEXT               -- NULL nếu còn hoạt động
```

Giới hạn 2 thiết bị = đếm `WHERE student_id = ? AND revoked_at IS NULL AND expires_at > now()`. Nếu ≥ 2 → từ chối tạo session mới ở bước login.

### Bài làm học viên
Tái dùng bảng `security_decisions` đã tồn tại (có sẵn cột `pseudonymous_user_id`, hiện đang optional/ẩn danh). Khi học viên đã đăng nhập gọi API chấm bài, backend điền `student_id` thật vào cột này thay vì để trống. Không cần bảng mới.

## API endpoints

Router `backend/app/api/student_auth_v1.py`:

| Endpoint | Method | Mô tả |
|---|---|---|
| `/api/student/register` | POST | email + password + full_name (+ phone tùy chọn) → tạo student, hash password bcrypt |
| `/api/student/login` | POST | email + password → verify; nếu ≥2 session sống, trả lỗi rõ ràng (không tạo session); ngược lại tạo `student_sessions` row, set access + refresh token qua httpOnly cookie |
| `/api/student/refresh` | POST | dùng refresh cookie → kiểm tra session chưa revoke/hết hạn → cấp access token mới, cập nhật `last_seen_at` |
| `/api/student/logout` | POST | revoke session hiện tại (theo refresh token trong cookie) |
| `/api/student/devices` | GET | liệt kê session đang sống của học viên hiện tại |
| `/api/student/devices/{session_id}/revoke` | POST | học viên tự thu hồi 1 thiết bị khác từ xa |
| `/api/student/submissions` | GET | lịch sử bài làm, join `security_decisions` theo `pseudonymous_user_id = student_id` |

Middleware `require_student` (song song với `require_actor` bên operator) đọc access token từ cookie, verify chữ ký + hạn dùng, gắn `student_id` vào request context. API `/analyze` hiện có (được `/playground` gọi) được bọc thêm: nếu có student đăng nhập hợp lệ, tự động điền `pseudonymous_user_id` = student_id thật.

## Frontend

- **`/register`**: form email, mật khẩu (tối thiểu 8 ký tự, validate client-side), họ tên, sđt tùy chọn. Submit → `POST /api/student/register` → chuyển sang `/login`.
- **`/login`**: form email + mật khẩu → `POST /api/student/login`. Nếu lỗi "đã đủ 2 thiết bị", hiển thị thông báo rõ ràng hướng dẫn học viên xử lý (chi tiết UX message chốt ở bước viết plan).
- **`/account/devices`** ("Thiết bị của tôi"): danh sách session đang sống (trình duyệt, IP, lần hoạt động cuối), nút đăng xuất từng thiết bị (trừ thiết bị hiện tại).
- **`/playground` (sửa)**: thêm guard đầu trang — chưa đăng nhập thì redirect `/login`. Giữ nguyên toàn bộ UI/logic phân tích hiện có. Thêm khối "Lịch sử bài làm của tôi" gọi `GET /api/student/submissions`.
- Component header nhỏ hiển thị email học viên + nút đăng xuất, xuất hiện trên các trang học viên (không hiện ở `/login`, `/register`).

## Ngoài phạm vi (out of scope) cho lần này

- Mã hóa PII at-rest (AES) — có thể làm sau nếu còn thời gian, không phải MVP.
- Device fingerprinting thật (browser/device ID) — dùng session-based counting thay thế.
- Reset mật khẩu qua email, xác thực email khi đăng ký.
- Bất kỳ thay đổi nào tới `operational/auth.py`, `security_v1.py`, hoặc engine firewall.
- Rate limiting riêng cho endpoint login/register (có thể tái dùng `operational/rate_limit.py` nếu còn thời gian, nhưng không bắt buộc cho MVP).

## Kiểm thử

- Unit test cho: hash/verify password, tạo/verify JWT, logic đếm & từ chối session thứ 3.
- Integration test: đăng ký → đăng nhập 2 lần (2 "thiết bị" khác nhau) → đăng nhập lần 3 phải bị từ chối → đăng xuất 1 thiết bị → đăng nhập lần 3 phải thành công.
- Kiểm tra không có password/token nào lộ ra trong response JSON hoặc log (grep log sau khi chạy integration test).
