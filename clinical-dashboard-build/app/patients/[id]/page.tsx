"use client"

import * as React from "react"
import { DashboardNav } from "@/components/dashboard-nav"
import { PatientDetailView } from "@/components/patient-detail-view"
import { usePatientScore } from "@/lib/hooks/use-patient-score"
import { Loader2, AlertCircle } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { notFound } from "next/navigation"

export default function PatientDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  // Next 15: params is a Promise in client components
  const { id } = React.use(params)

  const { data: patient, isLoading, error } = usePatientScore(id)

  if (isLoading) {
    return (
      <div className="flex h-screen bg-background overflow-hidden">
        <DashboardNav />
        <main className="flex-1 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </main>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen bg-background overflow-hidden">
        <DashboardNav />
        <main className="flex-1 p-8">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error loading patient</AlertTitle>
            <AlertDescription>
              {error instanceof Error
                ? error.message
                : "Unable to load patient details."}
            </AlertDescription>
          </Alert>
        </main>
      </div>
    )
  }

  if (!patient) {
    notFound()
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <PatientDetailView patient={patient} />
      </main>
    </div>
  )
}
