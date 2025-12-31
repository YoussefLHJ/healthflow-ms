"use client"

import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { LayoutDashboard, Users, Activity, Settings, Database, BrainCircuit, LogOut, Scale } from "lucide-react"
import { logout } from "@/lib/auth"

const navItems = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Patients", href: "/patients", icon: Users },
  { name: "Pipeline", href: "/pipeline", icon: Database },
  { name: "Model Specs", href: "/model", icon: BrainCircuit },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Audit Fairness", href: "/audit", icon: Scale },
]

export function DashboardNav() {
  const pathname = usePathname()
  const router = useRouter()

  return (
    <nav className="flex flex-col h-full bg-card border-r w-64 p-4 gap-2">
      <div className="flex items-center gap-2 px-2 mb-8">
        <Activity className="h-6 w-6 text-primary" />
        <span className="font-bold text-xl tracking-tight">HealthFlow</span>
      </div>

      <div className="flex-1 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                pathname === item.href
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              <span className="text-sm font-medium">{item.name}</span>
            </Link>
          )
        })}
      </div>

      <div className="pt-4 border-t">
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2 w-full text-sm font-medium text-muted-foreground hover:text-destructive transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </nav>
  )
}
