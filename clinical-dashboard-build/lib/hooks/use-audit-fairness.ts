// lib/hooks/use-audit-fairness.ts
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { fairnessApi } from "@/lib/api/fairnessApi"

export function useAuditFairness() {
  const queryClient = useQueryClient()

  const query = useQuery({
    queryKey: ["audit-fairness-latest"],
    queryFn: async () => {
      try {
        const res = await fairnessApi.getFairnessLatest()
        return res.data.snapshot
      } catch (err: any) {
        if (err?.response?.status === 404) {
          await fairnessApi.runFairnessFromScoreApi()
          const res2 = await fairnessApi.getFairnessLatest()
          return res2.data.snapshot
        }
        throw err
      }
    },
  })

  const recalculate = async () => {
    await fairnessApi.runFairnessFromScoreApi()
    await queryClient.invalidateQueries({ queryKey: ["audit-fairness-latest"] })
  }

  return { ...query, recalculate }
}
