"use client"

import { useQuery } from "@tanstack/react-query"
import type { PipelineStatus } from "../types"

export function usePipelineHealth() {
  console.log("usePipelineHealth called (mocked)")
  return useQuery<PipelineStatus>({
    queryKey: ["pipeline-health"],
    queryFn: async () => {
      // simulate network delay
      await new Promise((r) => setTimeout(r, 300))

      const data: PipelineStatus = {
        allHealthy: true,
        proxyFhirHealthy: true,
        deidHealthy: true,
        featurizerHealthy: true,
        modelRisqueHealthy: true,
      }

      console.log("pipeline health MOCK response", data)
      return data
    },
    refetchInterval: false, // no need to poll when mocked
  })
}
