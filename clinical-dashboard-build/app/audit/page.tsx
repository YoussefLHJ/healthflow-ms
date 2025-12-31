import { DashboardNav } from "@/components/dashboard-nav"
import { AuditFairness } from "@/components/audit-fairness"

export default function AuditPage() {
  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <DashboardNav />
      <main className="flex-1 overflow-y-auto p-8">
        <AuditFairness />
      </main>
    </div>
  )
}
