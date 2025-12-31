// components/login-form.tsx
"use client"

import type React from "react"
import { useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { useMutation } from "@tanstack/react-query"
import { scoreApi } from "@/lib/api"
import { AxiosError } from "axios"
import { Loader2, AlertCircle } from "lucide-react"

export function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  const loginMutation = useMutation({
    mutationFn: async (credentials: { username: string; password: string }) => {
      const response = await scoreApi.login(credentials.username, credentials.password)
      return response.data
    },
    onSuccess: (data) => {
      if (data.token) {
        localStorage.setItem("healthflow_token", data.token)

        const redirectTo = searchParams.get("redirect") || "/"
        router.replace(redirectTo)
      }
    },
  })

  const getErrorMessage = () => {
    if (!loginMutation.error) return null
    const error = loginMutation.error as AxiosError<any>

    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.error || error.response.data?.detail || error.response.data?.message

      if (status === 400 || status === 401) return message || "Invalid username or password"
      if (status === 404) return "User not found"
      if (message) return message
      return `Login failed with status ${status}`
    } else if (error.request) {
      return "Unable to connect to server. Please check your connection."
    }
    return "An unexpected error occurred. Please try again."
  }

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    loginMutation.mutate({ username, password })
  }

  const errorMessage = getErrorMessage()

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      {errorMessage && (
        <div className="flex items-center gap-2 p-3 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          placeholder="admin"
          type="text"
          autoCapitalize="none"
          autoComplete="username"
          autoCorrect="off"
          required
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          disabled={loginMutation.isPending}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          disabled={loginMutation.isPending}
          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
        />
      </div>

      <button
        type="submit"
        disabled={loginMutation.isPending}
        className="inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium bg-primary text-primary-foreground h-10 w-full"
      >
        {loginMutation.isPending ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Authenticating...
          </>
        ) : (
          "Sign In"
        )}
      </button>
    </form>
  )
}
