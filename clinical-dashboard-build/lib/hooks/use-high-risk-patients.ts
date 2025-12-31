// lib/hooks/use-high-risk-patients.ts
"use client"

import { useQuery } from '@tanstack/react-query'
import { scoreApi } from '@/lib/api'
import type { ModelRisqueResponse } from '@/lib/types'

export function useHighRiskPatients() {
  return useQuery<ModelRisqueResponse[]>({
    queryKey: ['high-risk-patients'],
    queryFn: async () => {
      const response = await scoreApi.getHighRiskPatients()
      return response.data
    },
    refetchInterval: 60000, // Refresh every minute
  })
}
