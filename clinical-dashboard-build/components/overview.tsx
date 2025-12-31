// components/overview.tsx
"use client"

import type { DashboardMetrics, ModelRisqueResponse } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, BrainCircuit, AlertTriangle, TrendingUp, Clock } from "lucide-react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts"
import { PatientRiskTable } from "./patient-risk-table"

interface OverviewProps {
  metrics: DashboardMetrics
  patients: ModelRisqueResponse[]
}

export function Overview({ metrics, patients }: OverviewProps) {
  // Chart colors
  const COLORS = {
    lowRisk: "#22c55e",      // Green
    mediumRisk: "#f59e0b",   // Orange
    highRisk: "#ef4444",     // Red
    chart1: "#3b82f6",       // Blue
    chart2: "#8b5cf6",       // Purple
    chart3: "#ec4899",       // Pink
    chart4: "#10b981",       // Emerald
  }

  const distributionData = [
    { name: "Low Risk", value: metrics.riskDistribution.lowRisk, color: COLORS.lowRisk },
    { name: "Medium Risk", value: metrics.riskDistribution.mediumRisk, color: COLORS.mediumRisk },
    { name: "High Risk", value: metrics.riskDistribution.highRisk, color: COLORS.highRisk },
  ]

  const performanceData = [
    { name: "Accuracy", value: metrics.modelPerformance.accuracy * 100, color: COLORS.chart1 },
    { name: "Precision", value: metrics.modelPerformance.precision * 100, color: COLORS.chart2 },
    { name: "Recall", value: metrics.modelPerformance.recall * 100, color: COLORS.chart3 },
    { name: "F1 Score", value: metrics.modelPerformance.f1Score * 100, color: COLORS.chart4 },
  ]

  // Format last training date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="rounded-lg border bg-background p-2 shadow-sm">
          <div className="grid gap-2">
            <div className="flex flex-col">
              <span className="text-[0.70rem] uppercase text-muted-foreground">
                {payload[0].name}
              </span>
              <span className="font-bold text-foreground">
                {typeof payload[0].value === 'number' 
                  ? payload[0].value.toFixed(1) 
                  : payload[0].value}
                %
              </span>
            </div>
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Clinical Dashboard</h1>
        <p className="text-muted-foreground">HealthFlow ScoreAPI – Readmission Risk Prediction Overview</p>
      </div>

      {/* Metric Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Total Patients</CardTitle>
            <Users className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics.totalPatients.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              +{metrics.recentActivity.newPatientsLast24Hours} in last 24h
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Risk Score Avg</CardTitle>
            <TrendingUp className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics.riskDistribution.averageRiskScore * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">Overall population mean</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">High Risk Alerts</CardTitle>
            <AlertTriangle className="w-4 h-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">
              {metrics.riskDistribution.highRisk}
            </div>
            <p className="text-xs text-muted-foreground">Require immediate review</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Model Accuracy</CardTitle>
            <BrainCircuit className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(metrics.modelPerformance.accuracy * 100).toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {metrics.modelPerformance.modelVersion} • Trained {formatDate(metrics.modelPerformance.lastTrainingDate)}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Risk Distribution Chart */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
            <CardDescription>Patient population by risk category</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {distributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex justify-center gap-4 mt-4">
              {distributionData.map((d) => (
                <div key={d.name} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: d.color }} />
                  <span className="text-xs font-medium">{d.name}: {d.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Model Performance Chart */}
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Model Performance Metrics</CardTitle>
            <CardDescription>Key performance indicators for {metrics.modelPerformance.modelVersion}</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={performanceData}>
                <CartesianGrid 
                  strokeDasharray="3 3" 
                  vertical={false} 
                  stroke="rgba(0,0,0,0.1)" 
                />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false}
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  domain={[0, 100]}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(0,0,0,0.05)" }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {performanceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Patient Risk Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>High Risk Patients</CardTitle>
            <CardDescription>
              {patients.length > 0 
                ? `Showing ${Math.min(patients.length, 10)} of ${patients.length} high-risk patients`
                : "No high-risk patients at this time"
              }
            </CardDescription>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <Clock className="w-3 h-3" />
            Last Updated: {new Date(metrics.generatedAt).toLocaleTimeString()}
          </div>
        </CardHeader>
        <CardContent>
          {patients.length > 0 ? (
            <PatientRiskTable patients={patients.slice(0, 10)} />
          ) : (
            <div className="flex items-center justify-center h-32 text-muted-foreground">
              <p>No high-risk patient data available</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
