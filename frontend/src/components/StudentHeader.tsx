"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { studentApi } from "@/lib/student-api";

export function StudentHeader({ email }: { email: string }) {
  const router = useRouter();

  async function handleLogout() {
    await studentApi.logout();
    router.push("/login");
  }

  return (
    <div className="flex items-center justify-between border-b px-4 py-3 text-sm">
      <span>{email}</span>
      <div className="flex items-center gap-4">
        <Link href="/account/devices" className="text-blue-600 hover:underline">
          Thiết bị của tôi
        </Link>
        <button onClick={handleLogout} className="text-red-600 hover:underline">
          Đăng xuất
        </button>
      </div>
    </div>
  );
}
