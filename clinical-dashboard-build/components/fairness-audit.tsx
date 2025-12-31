"use client"

import type { FairnessAnalysis } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Scale, CheckCircle2 } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function FairnessAudit({ analysis }: { analysis: FairnessAnalysis[] }) {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Fairness Audit</h1>
          <p className="text-muted-foreground">EvidentAI Compliance - Algorithmic Bias & Equity Analysis</p>
        </div>
        <div className="bg-primary/10 text-primary px-4 py-2 rounded-full flex items-center gap-2 text-sm font-semibold border border-primary/20">
          <Scale className="w-4 h-4" />
          Bias Guard Active
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-chart-1/5 border-chart-1/20">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Disparate Impact</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0.98</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <CheckCircle2 className="w-3 h-3 text-chart-1" /> Within acceptable range (0.8 - 1.25)
            </p>
          </CardContent>
        </Card>
        {/* ... similar summary cards ... */}
      </div>

      <Tabs defaultValue={analysis[0].attribute} className="space-y-4">
        <TabsList>
          {analysis.map((item) => (
            <TabsTrigger key={item.attribute} value={item.attribute}>
              {item.attribute}
            </TabsTrigger>
          ))}
        </TabsList>
        {analysis.map((item) => (
          <TabsContent key={item.attribute} value={item.attribute} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Disparate Impact Ratio</CardTitle>
                  <CardDescription>Relative selection rates across {item.attribute} groups</CardDescription>
                </CardHeader>
                <CardContent className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={item.metrics} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="var(--muted)" />
                      <XAxis type="number" domain={[0, 1.5]} />
                      <YAxis dataKey="group" type="category" axisLine={false} tickLine={false} width={80} />
                      <Tooltip />
                      <ReferenceLine x={1.0} stroke="var(--primary)" strokeDasharray="3 3" />
                      <ReferenceLine
                        x={0.8}
                        stroke="var(--destructive)"
                        strokeDasharray="3 3"
                        label={{ position: "top", value: "Min", fill: "var(--destructive)", fontSize: 10 }}
                      />
                      <Bar dataKey="disparateImpact" fill="var(--chart-4)" radius={[0, 4, 4, 0]} barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Error Rate Parity</CardTitle>
                  <CardDescription>False positive and negative rate balance</CardDescription>
                </CardHeader>
                <CardContent className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={item.metrics}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted)" />
                      <XAxis dataKey="group" axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 1]} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="equalOpportunity" name="Equal Opp." fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                      <Bar
                        dataKey="statisticalParity"
                        name="Stat. Parity"
                        fill="var(--chart-2)"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
