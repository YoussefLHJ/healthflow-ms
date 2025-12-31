"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Calendar, User, Activity, Brain, AlertCircle, TrendingUp, TrendingDown, Minus } from "lucide-react"
import Link from "next/link"
import type { ModelRisqueResponse, ShapExplanation } from "@/lib/types"
import { Progress } from "@/components/ui/progress"

interface PatientDetailViewProps {
  patient: ModelRisqueResponse
}

export function PatientDetailView({ patient }: PatientDetailViewProps) {
  const getRiskColor = (category: string) => {
    switch (category) {
      case "High":
        return "text-red-600 bg-red-50 border-red-200"
      case "Medium":
        return "text-amber-600 bg-amber-50 border-amber-200"
      case "Low":
        return "text-green-600 bg-green-50 border-green-200"
      default:
        return "text-slate-600 bg-slate-50 border-slate-200"
    }
  }

  const getImpactIcon = (impact: ShapExplanation["impact"]) => {
    switch (impact) {
      case "positive":
        return <TrendingUp className="h-4 w-4 text-red-500" />
      case "negative":
        return <TrendingDown className="h-4 w-4 text-green-500" />
      default:
        return <Minus className="h-4 w-4 text-slate-400" />
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link href="/patients">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Patient Analysis</h1>
            <p className="text-muted-foreground">Detailed risk assessment and model explanations</p>
          </div>
        </div>
        <Badge className={`px-3 py-1 text-sm font-medium border ${getRiskColor(patient.risk_category)}`}>
          {patient.risk_category} Risk
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Core Info */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <User className="h-4 w-4 text-blue-500" />
              Identity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{patient.patient_resource_id}</div>
            <p className="text-xs text-muted-foreground mt-1">Resource ID</p>
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Model Version</span>
                <span className="font-mono">{patient.model_version}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Prediction Date</span>
                <span>{new Date(patient.prediction_timestamp).toLocaleDateString()}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Risk Score */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-blue-500" />
              Risk Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(patient.readmission_risk_score * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground mt-1">Readmission Probability</p>
            <div className="mt-4">
              <Progress
                value={patient.readmission_risk_score * 100}
                className={`h-2 ${patient.risk_category === "High" ? "bg-red-100" : "bg-slate-100"}`}
              />
            </div>
          </CardContent>
        </Card>

        {/* Prediction Meta */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Calendar className="h-4 w-4 text-blue-500" />
              Last Prediction
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Date(patient.prediction_timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Eastern Standard Time</p>
            <div className="mt-4 flex items-center gap-2 text-sm text-green-600 font-medium">
              <Activity className="h-4 w-4" />
              Pipeline Healthy
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* SHAP Explanations */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-500" />
              Clinical Interpretability (SHAP)
            </CardTitle>
            <CardDescription>
              Factors contributing to the risk score. Positive values increase risk, negative values decrease risk.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {patient.shap_explanations.map((explanation, index) => (
                <div key={index} className="space-y-1.5">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{explanation.feature_name}</span>
                    <div className="flex items-center gap-1.5 font-mono text-xs">
                      {getImpactIcon(explanation.impact)}
                      {explanation.shap_value > 0 ? "+" : ""}
                      {explanation.shap_value.toFixed(3)}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden flex">
                      <div
                        className={`h-full ${explanation.impact === "positive" ? "bg-red-400" : "bg-green-400"}`}
                        style={{
                          width: `${Math.abs(explanation.shap_value * 100)}%`,
                          marginLeft:
                            explanation.impact === "positive"
                              ? "50%"
                              : `${50 - Math.abs(explanation.shap_value * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-[10px] text-muted-foreground italic">
                    Feature Value: {String(explanation.feature_value)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Feature Context */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-blue-500" />
              Key Features
            </CardTitle>
            <CardDescription>Raw data values extracted from ProxyFHIR for this prediction.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {Object.entries(patient.features_used).map(([key, value]) => (
                <div key={key} className="p-3 border rounded-lg bg-slate-50/50">
                  <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">
                    {key.replace(/_/g, " ")}
                  </div>
                  <div className="text-lg font-bold mt-1">
                    {typeof value === "number" ? value.toLocaleString() : String(value)}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 p-4 bg-blue-50 border border-blue-100 rounded-lg">
              <h4 className="text-sm font-semibold text-blue-900 flex items-center gap-2 mb-2">
                <Brain className="h-4 w-4" />
                Model Inference Note
              </h4>
              <p className="text-xs text-blue-700 leading-relaxed">
                This prediction was generated using the {patient.model_version} ensemble model. The primary drivers for
                the {patient.risk_category.toLowerCase()} risk category are related to historical admissions and chronic
                condition count.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
