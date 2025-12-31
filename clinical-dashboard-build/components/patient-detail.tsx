"use client"

import type { ModelRisqueResponse } from "@/lib/types"
import { ArrowLeft, Activity, Calendar, User, TrendingUp, AlertTriangle } from "lucide-react"
import Link from "next/link"

interface PatientDetailProps {
  patient: ModelRisqueResponse
}

export function PatientDetail({ patient }: PatientDetailProps) {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <Link
        href="/patients"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Directory
      </Link>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{patient.patient_resource_id}</h1>
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                patient.risk_category === "High"
                  ? "bg-red-100 text-red-700"
                  : patient.risk_category === "Medium"
                    ? "bg-amber-100 text-amber-700"
                    : "bg-green-100 text-green-700"
              }`}
            >
              {patient.risk_category} Risk
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <User className="h-4 w-4" />
              <span>Age: {patient.features_used.age}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="h-4 w-4" />
              <span>Last Prediction: {new Date(patient.prediction_timestamp).toLocaleDateString()}</span>
            </div>
          </div>
        </div>

        <div className="bg-card border rounded-lg p-4 flex items-center gap-6">
          <div className="text-center">
            <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider mb-1">Risk Score</p>
            <p className="text-2xl font-bold">{Math.round(patient.readmission_risk_score * 100)}%</p>
          </div>
          <div className="w-px h-10 bg-border" />
          <div className="text-center">
            <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider mb-1">Model Version</p>
            <p className="text-sm font-medium">{patient.model_version}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">SHAP Explanation</h2>
            </div>
            <div className="bg-card border rounded-xl overflow-hidden">
              <div className="p-6 space-y-6">
                <p className="text-sm text-muted-foreground">
                  SHAP values represent the contribution of each feature to the final prediction. Positive values
                  increase risk, while negative values decrease it.
                </p>
                <div className="space-y-4">
                  {patient.shap_explanations.map((shap, i) => (
                    <div key={i} className="space-y-1.5">
                      <div className="flex justify-between text-sm">
                        <span className="font-medium">{shap.feature_name}</span>
                        <span className={shap.impact === "positive" ? "text-red-500" : "text-green-500"}>
                          {shap.impact === "positive" ? "+" : ""}
                          {shap.shap_value.toFixed(2)}
                        </span>
                      </div>
                      <div className="relative h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`absolute h-full rounded-full transition-all ${
                            shap.impact === "positive" ? "bg-red-400" : "bg-green-400"
                          }`}
                          style={{
                            width: `${Math.abs(shap.shap_value) * 100}%`,
                            left: shap.impact === "positive" ? "50%" : "auto",
                            right: shap.impact === "negative" ? "50%" : "auto",
                          }}
                        />
                        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-border -translate-x-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">Features Used</h2>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
              {Object.entries(patient.features_used).map(([key, value]) => (
                <div key={key} className="bg-card border rounded-lg p-4">
                  <p className="text-xs text-muted-foreground uppercase font-semibold mb-1">{key.replace("_", " ")}</p>
                  <p className="text-lg font-bold">{value}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="space-y-8">
          <section className="space-y-4">
            <h2 className="text-xl font-semibold">Clinical Alerts</h2>
            <div className="space-y-3">
              {patient.readmission_risk_score > 0.7 && (
                <div className="flex gap-3 p-4 rounded-lg bg-red-50 border border-red-200 text-red-800">
                  <AlertTriangle className="h-5 w-5 shrink-0" />
                  <div className="text-sm">
                    <p className="font-bold">Critical Risk Level</p>
                    <p className="opacity-90">Consider immediate intervention and enhanced discharge planning.</p>
                  </div>
                </div>
              )}
              <div className="flex gap-3 p-4 rounded-lg bg-blue-50 border border-blue-200 text-blue-800">
                <Activity className="h-5 w-5 shrink-0" />
                <div className="text-sm">
                  <p className="font-bold">Follow-up Recommended</p>
                  <p className="opacity-90">Schedule post-discharge call within 48 hours.</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}
