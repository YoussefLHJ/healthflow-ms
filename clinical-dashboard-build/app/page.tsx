// app/page.tsx
"use client"

import { DashboardNav } from "@/components/dashboard-nav"
import { Overview } from "@/components/overview"
import { useDashboardMetrics } from "@/lib/hooks/use-dashboard-metrics"
import { useHighRiskPatients } from "@/lib/hooks/use-high-risk-patients"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function HomePage() {
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useDashboardMetrics()
  const { data: highRiskPatients, isLoading: patientsLoading, error: patientsError } = useHighRiskPatients()

  const isLoading = metricsLoading || patientsLoading
  const error = metricsError || patientsError

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center space-y-4">
              <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
              <div>
                <h3 className="font-semibold text-lg">Loading Dashboard</h3>
                <p className="text-muted-foreground text-sm">Fetching patient data...</p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error Loading Dashboard</AlertTitle>
            <AlertDescription>
              Failed to load dashboard data. Please check your connection.
              {error instanceof Error && (
                <div className="mt-2 text-sm font-mono bg-destructive/10 p-2 rounded">
                  {error.message}
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {!isLoading && !error && metrics && highRiskPatients && (
          <Overview metrics={metrics} patients={highRiskPatients} />
        )}
      </main>
    </div>
  )
}
