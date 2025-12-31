// lib/hooks/use-all-scores.ts
"use client"

import { useQuery } from '@tanstack/react-query'
import { scoreApi } from '@/lib/api'
import type { ModelRisqueResponse } from '@/lib/types'

export function useAllScores(skip = 0, limit = 100) {
  return useQuery<ModelRisqueResponse[]>({
    queryKey: ['all-scores', skip, limit],
    queryFn: async () => {
      const response = await scoreApi.getAllScores(skip, limit)
      return response.data
    },
    refetchInterval: 60000,
    retry: 2,
  })
}
