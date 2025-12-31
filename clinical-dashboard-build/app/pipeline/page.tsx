// app/pipeline/page.tsx
"use client"

import { useState } from "react"
import { DashboardNav } from "@/components/dashboard-nav"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Play,
  RotateCcw,
  Database,
  ShieldCheck,
  Cpu,
  CheckCircle2,
  Loader2,
  Trash2,
} from "lucide-react"
import { scoreApi } from "@/lib/api"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import { usePipelineHealth } from "@/lib/hooks/use-pipeline-health"

export default function PipelinePage() {
  const [isRunning, setIsRunning] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data: status, isLoading, error, refetch } = usePipelineHealth()

  const runPipeline = async (type: "training" | "hospital") => {
    try {
      setIsRunning(true)
      setActionError(null)

      if (type === "hospital") {
        await scoreApi.runHospitalPipeline(false)
      } else {
        await scoreApi.runTrainingPipeline(false)
      }

      await refetch()
    } catch (e: any) {
      setActionError(e?.message || "Failed to trigger pipeline.")
    } finally {
      setIsRunning(false)
    }
  }

  const handleClearAll = async () => {
    try {
      setIsRunning(true)
      setActionError(null)
      await scoreApi.clearAllData()
      await refetch()
    } catch (e: any) {
      setActionError(e?.message || "Failed to clear data.")
    } finally {
      setIsRunning(false)
    }
  }

  const steps = [
    { name: "ProxyFHIR Ingestion", id: "fhir", icon: Database, status: status?.allHealthy ?? true },
    { name: "De-identification (DEID)", id: "deid", icon: ShieldCheck, status: status?.deidHealthy ?? false },
    { name: "Featurizer Engine", id: "feat", icon: Cpu, status: status?.featurizerHealthy ?? false },
    { name: "ModelRisque Inference", id: "model", icon: CheckCircle2, status: status?.modelRisqueHealthy ?? false },
  ]

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="space-y-8 max-w-5xl">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Pipeline Control</h1>
            <p className="text-muted-foreground">
              Orchestrate the ML pipeline and monitor system health.
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error loading pipeline status</AlertTitle>
              <AlertDescription>
                {error instanceof Error ? error.message : "Unable to load pipeline status."}
              </AlertDescription>
            </Alert>
          )}

          {actionError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Pipeline action failed</AlertTitle>
              <AlertDescription>{actionError}</AlertDescription>
            </Alert>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>System Health</CardTitle>
                <CardDescription>Real-time status of pipeline microservices</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoading && (
                  <div className="flex items-center justify-center py-6">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  </div>
                )}
                {!isLoading &&
                  steps.map((step) => (
                    <div key={step.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-muted rounded-full">
                          <step.icon className="w-4 h-4 text-primary" />
                        </div>
                        <span className="text-sm font-medium">{step.name}</span>
                      </div>
                      {step.status ? (
                        <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200">
                          Operational
                        </Badge>
                      ) : (
                        <Badge variant="destructive">Critical Error</Badge>
                      )}
                    </div>
                  ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Control Panel</CardTitle>
                <CardDescription>Trigger automated pipeline executions</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-muted/50 rounded-lg border border-dashed flex flex-col items-center justify-center text-center space-y-4">
                  <div className="p-3 bg-card rounded-full shadow-sm">
                    {isRunning ? (
                      <Loader2 className="w-8 h-8 text-primary animate-spin" />
                    ) : (
                      <Play className="w-8 h-8 text-primary" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold">Execute Prediction Pipeline</h3>
                    <p className="text-xs text-muted-foreground px-4">
                      Fetch new data from FHIR, de-identify, featurize, and run readmission risk inference.
                    </p>
                  </div>
                  <div className="flex gap-2 w-full">
                    <Button
                      className="flex-1"
                      onClick={() => runPipeline("hospital")}
                      disabled={isRunning}
                    >
                      Run Hospital Pipeline
                    </Button>
                    <Button
                      variant="outline"
                      className="flex-1 bg-transparent"
                      onClick={() => runPipeline("training")}
                      disabled={isRunning}
                    >
                      Train Model
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    className="gap-2"
                    onClick={() => refetch()}
                    disabled={isLoading}
                  >
                    <RotateCcw className="w-4 h-4" />
                    Refresh Status
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-2 text-destructive hover:bg-destructive/10 bg-transparent"
                    onClick={handleClearAll}
                    disabled={isRunning}
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear All Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* You can later replace the static logs with a real /api/logs endpoint if you add one */}
        </div>
      </main>
    </div>
  )
}
