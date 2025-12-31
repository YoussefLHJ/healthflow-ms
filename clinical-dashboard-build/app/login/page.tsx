// app/login/page.tsx
"use client"

import { useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { LoginForm } from "@/components/login-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
  const token = localStorage.getItem("healthflow_token")

  if (token) {
    console.log("Token found, redirecting...")
    const redirectTo = searchParams.get("redirect") || "/"
    router.push(redirectTo)
    return
  }

  console.log("No token found, staying on login page.")
}, [router, searchParams])

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">HealthFlow Login</CardTitle>
          <CardDescription>Enter your credentials to access the dashboard</CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  )
}
