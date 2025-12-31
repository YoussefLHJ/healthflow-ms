import { DashboardNav } from "@/components/dashboard-nav"
import { SettingsForm } from "@/components/settings-form"

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <SettingsForm />
      </main>
    </div>
  )
}
