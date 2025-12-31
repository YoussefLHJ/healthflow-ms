// app/model/page.tsx
"use client"

import { DashboardNav } from "@/components/dashboard-nav"
import { ModelSpecs } from "@/components/model-specs"
import { useDashboardMetrics } from "@/lib/hooks/use-dashboard-metrics"
import type { ModelDetails, DashboardMetrics } from "@/lib/types"

export default function ModelPage() {
  const { data, isLoading, error } = useDashboardMetrics()

  if (isLoading || !data) {
    return (
      <div className="flex h-screen bg-background overflow-hidden">
        <DashboardNav />
        <main className="flex-1 flex items-center justify-center">
          Loading...
        </main>
      </div>
    )
  }

  const metrics = data as unknown as DashboardMetrics

  const model: ModelDetails = {
    modelVersion: metrics.modelPerformance.modelVersion,
    accuracy: metrics.modelPerformance.accuracy,
    precision: metrics.modelPerformance.precision,
    recall: metrics.modelPerformance.recall,
    f1Score: metrics.modelPerformance.f1Score,
    aucScore: metrics.modelPerformance.aucScore,
    lastTrainingDate: metrics.modelPerformance.lastTrainingDate,
    // placeholders / defaults
    architecture: "Placeholder architecture",
    parameters: "N/A",
    hyperparameters: {},          // important: not undefined
    trainingHistory: [],          // important: not undefined
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <ModelSpecs model={model} />
      </main>
    </div>
  )
}
