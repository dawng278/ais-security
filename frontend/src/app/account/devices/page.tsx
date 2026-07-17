"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { studentApi, StudentDevice, StudentRequestError } from "@/lib/student-api";

export default function DevicesPage() {
  const router = useRouter();
  const [devices, setDevices] = useState<StudentDevice[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const res = await studentApi.devices();
      setDevices(res.devices);
    } catch (err) {
      if (err instanceof StudentRequestError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError("Không tải được danh sách thiết bị.");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleRevoke(sessionId: string) {
    await studentApi.revokeDevice(sessionId);
    await load();
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-16">
      <h1 className="text-2xl font-bold">Thiết bị của tôi</h1>
      <p className="mt-2 text-sm text-gray-600">Bạn có thể đăng nhập tối đa 2 thiết bị cùng lúc.</p>
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      <ul className="mt-6 flex flex-col gap-3">
        {devices?.map((device) => (
          <li key={device.id} className="flex items-center justify-between rounded border px-4 py-3">
            <div>
              <p className="font-medium">{device.user_agent ?? "Thiết bị không xác định"}</p>
              <p className="text-xs text-gray-500">
                IP {device.ip_address ?? "?"} · Hoạt động lần cuối {new Date(device.last_seen_at).toLocaleString("vi-VN")}
              </p>
            </div>
            <button
              onClick={() => handleRevoke(device.id)}
              className="rounded border border-red-500 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
            >
              Đăng xuất
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
