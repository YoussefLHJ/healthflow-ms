// lib/hooks/use-patient-score.ts
"use client"

import { useQuery } from "@tanstack/react-query"
import { scoreApi } from "@/lib/api"
import type { ModelRisqueResponse } from "@/lib/types"

export function usePatientScore(patientId: string) {
  return useQuery<ModelRisqueResponse>({
    queryKey: ["patient-score", patientId],
    queryFn: async () => {
      const res = await scoreApi.getPatientScore(patientId) // /api/scores/patient/{id}
      return res.data
    },
    enabled: !!patientId,
    retry: 1,
  })
}
