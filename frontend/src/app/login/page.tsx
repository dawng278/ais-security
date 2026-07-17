"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { studentApi, StudentRequestError } from "@/lib/student-api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await studentApi.login({ email, password });
      router.push("/playground");
    } catch (err) {
      if (err instanceof StudentRequestError && err.code === "DEVICE_LIMIT_EXCEEDED") {
        setError("Bạn đã đăng nhập tối đa 2 thiết bị. Vui lòng đăng xuất một thiết bị khác trước.");
      } else if (err instanceof StudentRequestError) {
        setError(err.message);
      } else {
        setError("Đăng nhập thất bại, vui lòng thử lại.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold">Đăng nhập</h1>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Mật khẩu
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-blue-600 px-4 py-2 font-semibold text-white disabled:opacity-50"
        >
          {submitting ? "Đang xử lý..." : "Đăng nhập"}
        </button>
      </form>
    </main>
  );
}
