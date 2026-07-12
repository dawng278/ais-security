"use client";

import { useParams } from "next/navigation";
import { SecurityConsolePage } from "@/components/SecurityConsole";

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  return <SecurityConsolePage view="incident" incidentId={params.id} />;
}

