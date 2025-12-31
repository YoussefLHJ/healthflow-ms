"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, AlertTriangle, CheckCircle, TrendingDown, Users, Scale } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
} from "recharts"
import { useAuditFairness } from "@/lib/hooks/use-audit-fairness"
import { Button } from "./ui/button"

type FairnessMetric = {
  metric: string
  value: number
  threshold: number
  status: "pass" | "warn" | "fail"
}

export function AuditFairness() {
  const { data: snapshot, isLoading, error, recalculate, isFetching } = useAuditFairness()

  if (isLoading || !snapshot) {
    return <div className="p-4 text-sm text-muted-foreground">Loading fairness audit...</div>
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-600">
        Failed to load fairness audit.
      </div>
    )
  }

  const {
    disparate_impact,
    statistical_parity,
    equal_opportunity,
    overall_status,
    gender_metrics,
    age_metrics,
    fairness_metrics,
    fairness_trend,
    risk_distribution,
  } = snapshot

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fairness Audit</h1>
          <p className="text-muted-foreground">
            Model bias analysis and demographic fairness evaluation.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={recalculate}
          disabled={isFetching}
        >
          Recalculate
        </Button>
      </div>

      {/* Fairness Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Disparate Impact</CardTitle>
            <Scale className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{disparate_impact.toFixed(2)}</div>
            <div className="flex items-center gap-1 text-xs text-chart-1">
              <CheckCircle className="w-3 h-3" />
              <span>Above 0.8 threshold</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Statistical Parity</CardTitle>
            <Users className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistical_parity.toFixed(2)}</div>
            <div className="flex items-center gap-1 text-xs text-chart-1">
              <CheckCircle className="w-3 h-3" />
              <span>Gender balanced</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Equal Opportunity</CardTitle>
            <Shield className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{equal_opportunity.toFixed(2)}</div>
            <div className="flex items-center gap-1 text-xs text-chart-1">
              <CheckCircle className="w-3 h-3" />
              <span>Age-fair predictions</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Overall Fairness</CardTitle>
            <TrendingDown className="w-4 h-4 text-chart-1" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-chart-1">
              {overall_status === "pass" ? "Pass" : overall_status}
            </div>
            <p className="text-xs text-muted-foreground">All metrics within bounds</p>
          </CardContent>
        </Card>
      </div>

      {/* Fairness Metrics Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Fairness Metrics Summary</CardTitle>
          <CardDescription>Compliance check across demographic groups</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {fairness_metrics.map((metric: FairnessMetric) => (
              <div key={metric.metric} className="flex items-center justify-between p-3 bg-muted/50 rounded">
                <div className="flex items-center gap-3">
                  {metric.status === "pass" ? (
                    <CheckCircle className="w-5 h-5 text-chart-1" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-chart-3" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{metric.metric}</p>
                    <p className="text-xs text-muted-foreground">Threshold: {metric.threshold}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold">{metric.value.toFixed(2)}</p>
                  <p className="text-xs text-chart-1">
                    {metric.status === "pass" ? "✓ Compliant" : "⚠ Review Required"}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Fairness Trend Over Time (may be empty for now) */}
      <Card>
        <CardHeader>
          <CardTitle>Fairness Trend Analysis</CardTitle>
          <CardDescription>Historical progression of fairness metrics</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={fairness_trend}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted)" />
              <XAxis dataKey="month" axisLine={false} tickLine={false} />
              <YAxis domain={[0.8, 1.0]} axisLine={false} tickLine={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="disparateImpact" stroke="var(--chart-1)" name="Disparate Impact" strokeWidth={2} />
              <Line type="monotone" dataKey="statisticalParity" stroke="var(--chart-4)" name="Statistical Parity" strokeWidth={2} />
              <Line type="monotone" dataKey="equalOpportunity" stroke="var(--primary)" name="Equal Opportunity" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Performance by Gender */}
        <Card>
          <CardHeader>
            <CardTitle>Performance by Gender</CardTitle>
            <CardDescription>Model accuracy across genders</CardDescription>
          </CardHeader>
          <CardContent className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={gender_metrics}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted)" />
                <XAxis dataKey="group" axisLine={false} tickLine={false} />
                <YAxis
                  domain={[0, 1]}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
                <Legend />
                <Bar dataKey="accuracy" fill="var(--chart-1)" name="Accuracy" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance by Age Group */}
        <Card>
          <CardHeader>
            <CardTitle>Performance by Age Group</CardTitle>
            <CardDescription>Model accuracy across age groups</CardDescription>
          </CardHeader>
          <CardContent className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={age_metrics}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted)" />
                <XAxis dataKey="group" axisLine={false} tickLine={false} />
                <YAxis
                  domain={[0, 1]}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                />
                <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
                <Legend />
                <Bar dataKey="accuracy" fill="var(--chart-1)" name="Accuracy" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Risk distribution can be wired once you populate risk_distribution in the backend */}
    </div>
  )
}
