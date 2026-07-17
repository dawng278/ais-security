"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SecurityConsolePage } from "@/components/SecurityConsole";
import { studentApi, StudentProfile } from "@/lib/student-api";

export default function PlaygroundPage() {
  const router = useRouter();
  const [student, setStudent] = useState<StudentProfile | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    studentApi
      .me()
      .then((profile) => setStudent(profile))
      .catch(() => router.push("/login"))
      .finally(() => setChecked(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!checked) {
    return <main className="px-4 py-16 text-center text-sm text-gray-500">Đang kiểm tra đăng nhập...</main>;
  }
  if (!student) {
    return null;
  }

  return <SecurityConsolePage view="playground" studentId={student.id} />;
}
