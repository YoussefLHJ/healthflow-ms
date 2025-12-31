// lib/hooks/use-auth-check.ts
"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"

export function useAuthCheck() {
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("healthflow_token")
        : null

    console.log("AUTH CHECK (no redirect)", { pathname, token })

    // Just update flags, no routing at all
    setIsAuthenticated(true)
    setIsLoading(false)
  }, [pathname])

  return { isAuthenticated, isLoading }
}
