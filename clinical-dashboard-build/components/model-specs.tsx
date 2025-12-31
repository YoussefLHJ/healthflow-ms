"use client"

import type { ModelDetails } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BrainCircuit, Cpu, History } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

export function ModelSpecs({ model }: { model: ModelDetails }) {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Model Specifications</h1>
        <p className="text-muted-foreground">Technical details and performance history for {model.modelVersion}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Architecture</CardTitle>
            <Cpu className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{model.architecture}</div>
            <p className="text-xs text-muted-foreground">{model.parameters} parameters</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Last Training</CardTitle>
            <History className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{new Date(model.lastTrainingDate).toLocaleDateString()}</div>
            <p className="text-xs text-muted-foreground">Successfully deployed to production</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Active Version</CardTitle>
            <BrainCircuit className="w-4 h-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{model.modelVersion}</div>
            <p className="text-xs text-muted-foreground">Optimized for low latency inference</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Hyperparameters</CardTitle>
            <CardDescription>Configuration used during the last training cycle</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(model.hyperparameters).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between border-b pb-2 last:border-0">
                  <span className="text-sm font-medium text-muted-foreground">{key}</span>
                  <code className="bg-muted px-2 py-0.5 rounded text-xs">{value}</code>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Training Progress</CardTitle>
            <CardDescription>Accuracy and loss trends over time</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={model.trainingHistory}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--muted)" />
                <XAxis dataKey="date" axisLine={false} tickLine={false} tickFormatter={(val) => val.split("-")[2]} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="accuracy" stroke="var(--primary)" strokeWidth={2} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="loss" stroke="var(--destructive)" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
