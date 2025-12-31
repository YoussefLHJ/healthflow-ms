// lib/hooks/use-dashboard-metrics.ts
"use client"

import { useQuery } from "@tanstack/react-query"
import { scoreApi } from "@/lib/api"
import type { DashboardMetrics } from "@/lib/types"

export function useDashboardMetrics() {
  return useQuery<DashboardMetrics>({
    queryKey: ["dashboard-metrics"],
    queryFn: async () => {
      const response = await scoreApi.getDashboardMetrics()
      return response.data
    },
    refetchInterval: 30000,
    staleTime: 25000,
  })
}
