# GradingGuard AI — Student Account Security: 5-Minute Live Demo Script

> **Step-by-Step Live Presentation Script for Judges, Reviewers & Stakeholders**
> Scope: Student Account Security feature only — max 2 concurrent devices, secure
> credential handling, session-based auth, CSRF/rate-limit hardening, immediate
> device revocation. Verdict: `STUDENT_ACCOUNT_SECURITY_PRODUCTION_READY: PASS`
> (see `docs/superpowers/plans/2026-07-17-student-account-security.md` and
> `origin/main` commit `bf36728` for full evidence trail).

---

## Live Demo Summary Timeline

| Time | Target UI | Core Focus | Key Thing to Show |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:30** | `/register` | Problem framing | Why student account takeover / shared-account abuse matters |
| **0:30 – 1:30** | `/register` → `/login` | Secure signup + login | bcrypt hash, HttpOnly session cookie, no password/token in response body |
| **1:30 – 2:45** | `/account/devices` (2 browser sessions) | **Core demo: 2-device limit** | 3rd concurrent login is rejected; device list shows exactly 2 |
| **2:45 – 3:30** | `/account/devices` → revoke | Immediate revocation | Revoking a device invalidates its session on the *very next* request, not after TTL |
| **3:30 – 4:15** | `/playground` | Server-side ownership binding | Student cannot spoof another student's identity via request body |
| **4:15 – 5:00** | Closing | Defense-in-depth summary | CSRF Origin check, rate limiting, cookie `Secure` in production |

---

## Recording Setup (Before You Hit Record)

- **Screen resolution**: record at 1920×1080, browser window snapped to
  fill the frame — no OS taskbar/dock visible if possible.
- **Windows needed, opened in advance**:
  1. **Browser A** — normal window, this is "Device 1" / the presenter's
     main camera throughout.
  2. **Browser B** — a *different browser or a separate OS-level profile*
     (not just a new tab/incognito of the same profile), positioned to be
     snapped in side-by-side with Browser A for the 1:30–2:45 segment. This
     is "Device 2".
  3. **Browser C** — a third isolated context (e.g. Firefox if A/B are
     Chrome + Chrome-Incognito), kept minimized until the 3rd-login-attempt
     beat at ~2:15.
  4. **DevTools** docked to the right/bottom of Browser A, Network tab
     open, ready to inspect `/register`, `/login`, `/account/devices/*`
     requests on cue — pre-filter the Network tab to `Fetch/XHR` so
     irrelevant asset requests don't clutter the recording.
- **Font size**: bump browser zoom to 125–150% before recording so cookie
  flags and JSON response bodies are readable on a shared screen/projector.
- **Cursor**: enable a cursor-highlight/click-ping tool (OS accessibility
  setting or a screen-recorder plugin) so viewers can track clicks in
  DevTools panels, which are visually dense.
- **Audio**: record voiceover live if presenting synchronously; otherwise
  record screen first, narrate in a second pass matched to the on-screen
  timestamps below.

---

## Minute-by-Minute Step-by-Step Execution

### 0:00 – 0:30 — Opening & Problem Framing

- **UI Action**: Open `http://localhost:3000/register`.
- **Screen / Recording Direction**:
  - Start on a **full-screen Browser A**, no DevTools open yet — clean,
    uncluttered frame for the opening line.
  - Optionally open on the marketing/landing page (`/`) for 2–3 seconds
    first, then navigate to `/register` as you say "the feature we built to
    close that gap" — the navigation itself should land right as you name
    the feature, so the register form appears on screen exactly when you
    say "Student Account Security."
  - No zoom/highlight needed here — this beat is about the presenter's
    voice, not a UI detail. Keep the shot static.
- **Spoken Script (English)**:
  > *"Hello everyone. GradingGuard AI is a platform where students practice IELTS
  > writing and speaking. Like any account-based product, it faces a simple but
  > costly risk: shared or stolen student credentials. One paid account,
  > logged in on three devices at once, or a leaked password reused by someone
  > else — both quietly break the product's trust model.*
  >
  > *Today's demo is about the feature we built to close that gap: **Student
  > Account Security** — a hard limit of 2 concurrent devices per student,
  > proper credential hashing, and session controls that take effect
  > immediately, not eventually."*
- **Spoken Script (Vietnamese)**:
  > *"Xin chào. GradingGuard AI là nền tảng luyện thi IELTS Writing và
  > Speaking cho học viên. Giống mọi sản phẩm dùng tài khoản, rủi ro lớn nhất
  > là chia sẻ hoặc lộ mật khẩu — một tài khoản trả phí bị đăng nhập trên 3
  > thiết bị cùng lúc.*
  >
  > *Demo hôm nay tập trung vào tính năng Bảo mật Tài khoản Học viên: giới
  > hạn cứng 2 thiết bị đăng nhập đồng thời, hash mật khẩu đúng chuẩn, và các
  > cơ chế session có hiệu lực ngay lập tức."*

---

### 0:30 – 1:30 — Secure Signup & Login

- **UI Action**:
  1. Register a new student: `demo.student@example.com` / a password.
  2. Point out: no plaintext password ever appears in the network response
     (open DevTools → Network → inspect the `/register` and `/login`
     response bodies — only `student_id`/`email` come back, never the hash
     or the token in the JSON body).
  3. Point out the session cookie in DevTools → Application → Cookies:
     `HttpOnly`, `SameSite=Lax`, `Secure` (when served over HTTPS in
     production).
- **Screen / Recording Direction**:
  - Fill the register form on camera at normal typing speed (don't
    paste-in silently — the audience should see the fields being typed).
  - After clicking **Đăng ký**, open DevTools (`F12`) and dock it to the
    **bottom** of the window (more horizontal room to read JSON) —
    Network tab, click the `/register` request, select the **Response**
    sub-tab. Cursor-highlight the JSON body and pause 2 seconds on it
    silently so the "no password field" point lands visually before you
    say it.
  - Cut/switch to the **Application → Cookies** panel next. Highlight the
    row for the session cookie, specifically the `HttpOnly` and `Secure`
    columns — zoom in (browser zoom or a recording-tool zoom box) on just
    that row so the flags are legible.
  - Then repeat the same flow quickly for `/login` (this can be sped up
    2× in post-production since it's visually repetitive) before moving
    to the next segment.
- **Spoken Script (English)**:
  > *"Passwords are hashed with bcrypt before they ever touch the database —
  > the raw password is never stored. The session token itself is
  > HttpOnly, so client-side JavaScript, including anything injected via
  > XSS, cannot read or exfiltrate it. It's Secure-flagged in production, so
  > it's never sent over plain HTTP."*
- **Spoken Script (Vietnamese)**:
  > *"Mật khẩu được hash bằng bcrypt trước khi lưu — không bao giờ lưu bản
  > rõ. Token phiên đăng nhập là HttpOnly, JavaScript phía client, kể cả mã
  > độc chèn qua XSS, không thể đọc được. Cờ Secure được bật ở môi trường
  > production nên cookie không bao giờ đi qua HTTP thường."*

---

### 1:30 – 2:45 — Core Demo: 2-Device Limit

- **UI Action**:
  1. Open a **second browser** (or a private/incognito window) and log in
     as the **same student** (`demo.student@example.com`). Now 2 active
     sessions exist.
  2. Visit `/account/devices` in either window — show the device list: 2
     entries, each with `user_agent` / last-seen time, no raw tokens
     displayed.
  3. Open a **third browser context** and attempt to log in as the same
     student again.
  4. Point out the rejection: the 3rd login attempt is refused because the
     student already has 2 active sessions — nudge the audience to notice
     this is enforced **server-side**, not a UI-only restriction.
- **Screen / Recording Direction**: *(this is the hero shot of the whole
  video — give it the most screen real estate and the least camera-cutting)*
  - Snap **Browser A** and **Browser B** side-by-side, each at ~50% screen
    width, both logged in and sitting on `/account/devices`. This
    side-by-side split should already be visible for a beat *before* you
    start talking, so viewers register "two separate windows, two separate
    browsers" before the explanation starts.
  - Both windows on `/account/devices` should visibly show **2 entries**
    in the device list at this point — briefly cursor-circle the count
    ("2 devices") on one of the two windows.
  - Cut to **Browser C** (bring it to foreground, full screen) already
    sitting on `/login` with the same email pre-filled. Type the password
    live and click **Đăng nhập** on camera — do not pre-trigger this
    off-screen, the rejection response needs to visibly happen live.
  - The instant the error appears, **freeze/hold the frame for 2–3
    seconds** on the rejection message (or zoom in on the error banner) —
    this is the single most important visual beat in the whole demo and
    should not be rushed past.
  - Cut back to the side-by-side A/B view to close the segment, reinforcing
    "still just 2, exactly as before."
- **Spoken Script (English)**:
  > *"Here's the core of the feature. I'm logged in as this student on two
  > separate devices already. Watch what happens when I try a third login
  > with the same credentials — it's rejected. Not because the UI hides a
  > button, but because the backend atomically counts active sessions and
  > refuses to issue a third one.*
  >
  > *That word 'atomically' matters: if two login requests for the same
  > student arrive at the exact same millisecond, a naive check-then-insert
  > implementation can let both through and blow past the limit. We
  > verified this under real concurrent load with threading tests — zero
  > failures across 40 runs after the fix."*
- **Spoken Script (Vietnamese)**:
  > *"Đây là phần lõi của tính năng. Tôi đã đăng nhập tài khoản này trên 2
  > thiết bị. Khi thử đăng nhập lần thứ 3 bằng đúng tài khoản đó — hệ thống
  > từ chối. Đây không phải giới hạn ở giao diện, mà backend đếm số phiên
  > đang hoạt động một cách atomically và từ chối cấp phiên thứ 3.*
  >
  > *Từ 'atomically' ở đây quan trọng: nếu 2 yêu cầu đăng nhập của cùng một
  > học viên đến cùng lúc, cách kiểm tra ngây thơ (đếm rồi mới ghi) có thể
  > để lọt cả hai và vượt giới hạn. Chúng tôi đã kiểm chứng dưới tải đồng
  > thời thật bằng threading test — 0 lỗi sau 40 lần chạy."*

---

### 2:45 – 3:30 — Immediate Device Revocation

- **UI Action**:
  1. From device A's `/account/devices` page, click **Revoke** on device
     B's session.
  2. Switch to device B's browser window and refresh **any** page (e.g.
     `/playground` or `/account/devices`) — show it immediately bounces to
     `/login`, without waiting for the token to expire.
- **Screen / Recording Direction**:
  - Keep the same side-by-side A/B layout from the previous segment —
    continuity matters here, don't re-establish the windows from scratch.
  - On Browser A, cursor-highlight device B's row in the list for a beat
    before clicking **Revoke**, so viewers can tell which entry is about
    to be removed.
  - Click **Revoke** on camera, then immediately (same shot, no cut) pan
    focus to Browser B and trigger the refresh/navigation there — the
    cause → effect needs to read as *one continuous action*, not two
    separate clips, or the "immediately" claim loses its visual proof.
  - Hold on Browser B's redirect to `/login` for 1–2 seconds before
    cutting away.
- **Spoken Script (English)**:
  > *"Revoking a device isn't just a database flag that gets checked next
  > time someone refreshes a long-lived token. Every authenticated request
  > now does a live session lookup — so the moment I revoke device B from
  > device A, device B's very next request is rejected, even if its access
  > token hasn't technically expired yet. That closes a real gap: without
  > this, a stolen session token would keep working for its full lifetime
  > even after the student revokes it."*
- **Spoken Script (Vietnamese)**:
  > *"Thu hồi thiết bị không chỉ là đánh dấu trong database rồi chờ token
  > hết hạn mới có hiệu lực. Mỗi request đã xác thực đều tra cứu session
  > trong DB theo thời gian thực — nên ngay khi thiết bị A thu hồi thiết bị
  > B, request tiếp theo của B bị từ chối lập tức, dù access token về mặt
  > kỹ thuật chưa hết hạn. Đây là lỗ hổng thật đã được vá: nếu không, token
  > bị đánh cắp vẫn dùng được tới hết thời hạn dù học viên đã thu hồi."*

---

### 3:30 – 4:15 — Server-Side Ownership Binding

- **UI Action**: Open `/playground`, submit an analysis request as the
  logged-in student. Open DevTools → Network → inspect the outgoing
  `/api/v1/students/analyze` request body — point out there is **no**
  `student_id` or `pseudonymous_user_id` field in the payload at all.
- **Screen / Recording Direction**:
  - Drop back to a single full-screen window (Browser A) — this segment is
    about one request's payload, not multi-device comparison, so the
    side-by-side split from the previous two segments should end here.
  - Use one of the pre-loaded **Playground sample essays** (the injection
    sample) rather than typing a long essay live — click the sample
    button, then click **Analyze with Phase 4 gateway** on camera.
  - While the request is in flight, switch to DevTools Network tab,
    click the `/analyze` request, and select the **Payload/Request**
    sub-tab (not Response this time). Cursor-scroll through the JSON body
    slowly enough for viewers to read every field name and visually
    confirm the absence of `student_id`.
  - Optional stronger visual: briefly show the `StudentAnalyzeRequest`
    schema source (`backend/app/api/student_auth_v1.py`) in an editor
    window side-by-side with the DevTools payload, to make "the schema
    forbids it" and "the actual request proves it" land together.
- **Spoken Script (English)**:
  > *"One subtle but serious class of bug in account systems is trusting the
  > client to say who it is. Our `/analyze` endpoint's request schema
  > deliberately has no field for the caller to assert their own identity —
  > it's rejected outright if one is present. The student's identity is
  > bound entirely server-side, extracted from the verified session cookie.
  > That means Student A can never make a request that gets attributed to
  > Student B, no matter what they put in the request body."*
- **Spoken Script (Vietnamese)**:
  > *"Một lỗi tinh vi nhưng nghiêm trọng trong hệ thống tài khoản là tin
  > tưởng client tự khai danh tính. Schema của endpoint `/analyze` cố tình
  > không có field để client tự khai `student_id` — nếu client cố gửi field
  > đó, request bị từ chối ngay. Danh tính học viên được gắn hoàn toàn ở
  > phía server, lấy từ session cookie đã xác thực. Học viên A không bao
  > giờ có thể khiến request của mình bị gán nhầm cho học viên B."*

---

### 4:15 – 5:00 — Closing: Defense-in-Depth Summary

- **UI Action**: No specific UI — verbal summary, optionally show
  `README.md` §15 (Limitations) to demonstrate the team documents honest
  boundaries rather than overclaiming.
- **Screen / Recording Direction**:
  - Scroll to and hold on `README.md` §15 "Limitations" in an editor or
    GitHub's rendered view — let the two documented limitation bullets
    (rate limiting, CSRF) be legible on screen while narrating them, don't
    just talk over a blank/unrelated frame.
  - Optional closing shot: a simple static title card listing the 7 gate
    names with a checkmark next to each (Backend regression ✓, Frontend
    type-check/lint/build ✓, Browser lifecycle ✓, Production cookie ✓,
    Fresh deploy smoke test ✓, origin/main commit ✓, README parity ✓) —
    reinforces the "independently verified" claim visually instead of only
    verbally.
  - End on the project name/logo or landing page (`/`), not on a DevTools
    panel — close the video on a clean, recognizable frame.
- **Spoken Script (English)**:
  > *"To summarize the layers behind this feature: bcrypt password hashing,
  > HttpOnly/Secure session cookies, a hard 2-device limit enforced
  > atomically at the database level, Origin/Referer-based CSRF defense on
  > every state-changing route, SQLite-backed rate limiting on login and
  > registration to blunt credential-stuffing and brute force, and
  > immediate server-side revocation instead of waiting out a token's TTL.*
  >
  > *This went through 7 independent release-acceptance gates — full
  > backend regression, frontend type-check and production build, a real
  > browser lifecycle test, production-ENV cookie verification, a fresh
  > clone smoke test, commit verification against `origin/main`, and a
  > line-by-line README accuracy check. All seven passed. Thank you."*
- **Spoken Script (Vietnamese)**:
  > *"Tóm lại các lớp bảo vệ: hash mật khẩu bằng bcrypt, cookie phiên
  > HttpOnly/Secure, giới hạn cứng 2 thiết bị được thực thi atomically ở
  > tầng database, phòng thủ CSRF dựa trên Origin/Referer cho mọi route làm
  > thay đổi dữ liệu, rate limiting cho đăng nhập/đăng ký để chặn tấn công
  > dò mật khẩu hàng loạt, và thu hồi phiên có hiệu lực ngay lập tức thay vì
  > chờ token hết hạn.*
  >
  > *Tính năng đã qua 7 cổng chấp nhận release độc lập: hồi quy backend đầy
  > đủ, type-check và production build frontend, kiểm thử vòng đời trên
  > trình duyệt thật, xác minh cookie ở môi trường production, smoke test
  > trên bản clone hoàn toàn mới, xác minh commit trên origin/main, và đối
  > chiếu README với hành vi thực tế từng dòng. Cả 7 đều đạt. Xin cảm ơn."*

---

## Emergency Fallback & Q&A Cheat Sheet

### If the 3rd-device login rejection doesn't visibly trigger:
> Check that all 3 browser contexts are fully isolated (separate browser
> profiles or one regular + two incognito windows in **different**
> browsers) — cookies shared across tabs of the same profile will just
> reuse session 1 or 2 instead of attempting a genuine 3rd login.

### If asked "why 2 devices and not device fingerprinting?":
> *"Device fingerprinting is fragile and easy to spoof or accidentally
> trigger false positives on (browser updates, VPNs). A session-count limit
> is simpler, cannot be bypassed by changing headers, and gives students a
> transparent, self-serve way to manage their own devices."*

### If asked "what happens to the 3rd device's existing UX?":
> *"They get a clear 'device limit reached' response and are pointed to
> `/account/devices` to revoke an old session themselves — no silent
> failure, no support ticket required."*

### If asked about production readiness / what's still a known limitation:
> *"Two things are explicitly documented, not hidden: rate limiting is a
> single-instance SQLite fixed-window counter, not a distributed limiter —
> fine for one server, would need a shared store like Redis for horizontal
> scaling. And CSRF defense is Origin/Referer validation, a strong
> baseline, but not a cryptographic per-request token. Both are called out
> in README §15 exactly as implemented — see `docs/superpowers/plans/2026-07-17-student-account-security.md`
> for the full audit trail."*

### If the backend/frontend crashes mid-demo:
> Fall back to the pre-recorded browser lifecycle evidence from Gate 3/5
> (register → login → 2-device limit → revoke → analyze), captured during
> the release-acceptance audit, and narrate over the recording instead.
