"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Database, Shield } from "lucide-react"

export function SettingsView() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your HealthFlow API configuration and preferences</p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              <CardTitle>API Configuration</CardTitle>
            </div>
            <CardDescription>Configure connection strings for clinical data sources</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="fhir-url">FHIR Server URL</Label>
              <Input id="fhir-url" placeholder="https://fhir-server.institutional.edu/v4" />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="api-key">Service API Key</Label>
              <Input id="api-key" type="password" placeholder="••••••••••••••••" />
            </div>
            <Button className="w-fit">Save Connectivity Settings</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-primary" />
              <CardTitle>Security & Compliance</CardTitle>
            </div>
            <CardDescription>Manage data de-identification and privacy protocols</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>HIPAA Mode</Label>
                <p className="text-xs text-muted-foreground">Enforce strict data obfuscation in UI</p>
              </div>
              <Switch checked />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Audit Logging</Label>
                <p className="text-xs text-muted-foreground">Keep detailed logs of all model queries</p>
              </div>
              <Switch checked />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
