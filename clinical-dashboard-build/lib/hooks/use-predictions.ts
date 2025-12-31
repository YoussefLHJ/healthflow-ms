// lib/hooks/use-predictions.ts
"use client"

import { useQuery } from '@tanstack/react-query'
import { scoreApi } from '@/lib/api'
import type { ModelRisqueResponse } from '@/lib/types'

export function usePredictions(limit = 100) {
  return useQuery<ModelRisqueResponse[]>({
    queryKey: ['predictions', limit],
    queryFn: async () => {
      const response = await scoreApi.getAllScores(0, limit)
      return response.data
    },
    refetchInterval: 60000,
    retry: 2,
  })
}
