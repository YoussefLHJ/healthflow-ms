// lib/auth.ts
export function logout() {
  localStorage.removeItem("healthflow_token")
  window.location.href = "/login"
}
