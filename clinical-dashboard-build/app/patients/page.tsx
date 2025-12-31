// app/patients/page.tsx
"use client"

import { DashboardNav } from "@/components/dashboard-nav"
import { PatientDirectory } from "@/components/patient-directory"
import { useAllScores } from "@/lib/hooks/use-all-scores"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function PatientsPage() {
  const { data: patients, isLoading, error } = useAllScores(0, 100)

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Patient Directory</h1>
            <p className="text-muted-foreground">
              Manage and monitor readmission risks across your patient population.
            </p>
          </div>

          {isLoading && (
            <div className="flex items-center justify-center h-40">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error loading patients</AlertTitle>
              <AlertDescription>
                Failed to load patient directory.
                {error instanceof Error && (
                  <div className="mt-2 text-xs font-mono bg-destructive/10 p-2 rounded">
                    {error.message}
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {!isLoading && !error && patients && (
            <PatientDirectory patients={patients} />
          )}
        </div>
      </main>
    </div>
  )
}
