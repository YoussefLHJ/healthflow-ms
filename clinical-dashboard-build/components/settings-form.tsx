"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Database, Bell, Shield, User, Server, Save } from "lucide-react"

export function SettingsForm() {
  const [settings, setSettings] = useState({
    apiUrl: "https://api.healthflow.io/v2",
    fhirEndpoint: "https://fhir.healthflow.io",
    modelVersion: "v2.1.0",
    autoRetrain: true,
    notificationsEnabled: true,
    highRiskThreshold: 0.7,
    mediumRiskThreshold: 0.4,
    userName: "Admin User",
    userEmail: "admin.user@healthflow.io",
    institution: "Hospital Network",
    dataRetentionDays: 365,
  })

  const handleSave = () => {
    console.log("[v0] Settings saved:", settings)
    alert("Settings saved successfully!")
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage system configuration and API settings</p>
      </div>

      {/* User Profile */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="w-5 h-5 text-muted-foreground" />
            <CardTitle>User Profile</CardTitle>
          </div>
          <CardDescription>Your personal information and account details</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="userName">Full Name</Label>
              <Input
                id="userName"
                value={settings.userName}
                onChange={(e) => setSettings({ ...settings, userName: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="userEmail">Email Address</Label>
              <Input
                id="userEmail"
                type="email"
                value={settings.userEmail}
                onChange={(e) => setSettings({ ...settings, userEmail: e.target.value })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="institution">Institution</Label>
            <Input
              id="institution"
              value={settings.institution}
              onChange={(e) => setSettings({ ...settings, institution: e.target.value })}
            />
          </div>
        </CardContent>
      </Card>

      {/* API Configuration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="w-5 h-5 text-muted-foreground" />
            <CardTitle>API Configuration</CardTitle>
          </div>
          <CardDescription>Configure API endpoints and data sources</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="apiUrl">HealthFlow API URL</Label>
            <Input
              id="apiUrl"
              value={settings.apiUrl}
              onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
              placeholder="https://api.healthflow.io/v2"
            />
            <p className="text-xs text-muted-foreground">Base URL for the HealthFlow ScoreAPI</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="fhirEndpoint">FHIR Endpoint</Label>
            <Input
              id="fhirEndpoint"
              value={settings.fhirEndpoint}
              onChange={(e) => setSettings({ ...settings, fhirEndpoint: e.target.value })}
              placeholder="https://fhir.healthflow.io"
            />
            <p className="text-xs text-muted-foreground">FHIR server for patient data retrieval</p>
          </div>
        </CardContent>
      </Card>

      {/* Model Configuration */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-muted-foreground" />
            <CardTitle>Model Configuration</CardTitle>
          </div>
          <CardDescription>Manage model versions and risk thresholds</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="modelVersion">Active Model Version</Label>
            <Input
              id="modelVersion"
              value={settings.modelVersion}
              onChange={(e) => setSettings({ ...settings, modelVersion: e.target.value })}
            />
            <p className="text-xs text-muted-foreground">Current production model in use</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="highRisk">High Risk Threshold</Label>
              <Input
                id="highRisk"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.highRiskThreshold}
                onChange={(e) => setSettings({ ...settings, highRiskThreshold: Number.parseFloat(e.target.value) })}
              />
              <p className="text-xs text-muted-foreground">Scores above this trigger alerts</p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="mediumRisk">Medium Risk Threshold</Label>
              <Input
                id="mediumRisk"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.mediumRiskThreshold}
                onChange={(e) => setSettings({ ...settings, mediumRiskThreshold: Number.parseFloat(e.target.value) })}
              />
              <p className="text-xs text-muted-foreground">Scores above this are medium risk</p>
            </div>
          </div>
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded">
            <div>
              <p className="text-sm font-medium">Automatic Model Retraining</p>
              <p className="text-xs text-muted-foreground">Enable weekly model retraining with new data</p>
            </div>
            <Switch
              checked={settings.autoRetrain}
              onCheckedChange={(checked) => setSettings({ ...settings, autoRetrain: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-muted-foreground" />
            <CardTitle>Notifications</CardTitle>
          </div>
          <CardDescription>Configure alert preferences and notification settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded">
            <div>
              <p className="text-sm font-medium">Enable Notifications</p>
              <p className="text-xs text-muted-foreground">Receive alerts for high-risk patient predictions</p>
            </div>
            <Switch
              checked={settings.notificationsEnabled}
              onCheckedChange={(checked) => setSettings({ ...settings, notificationsEnabled: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Data Retention */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-muted-foreground" />
            <CardTitle>Data Retention & Privacy</CardTitle>
          </div>
          <CardDescription>Manage data retention policies and privacy settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="retention">Data Retention Period (Days)</Label>
            <Input
              id="retention"
              type="number"
              value={settings.dataRetentionDays}
              onChange={(e) => setSettings({ ...settings, dataRetentionDays: Number.parseInt(e.target.value) })}
            />
            <p className="text-xs text-muted-foreground">Prediction data older than this will be archived</p>
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} size="lg" className="gap-2">
          <Save className="w-4 h-4" />
          Save Settings
        </Button>
      </div>
    </div>
  )
}
