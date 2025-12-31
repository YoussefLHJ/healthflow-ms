// lib/api/fairnessApi.ts
import axios from "axios"

const fairnessClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_AUDIT_FAIRNESS_DIRECT, // http://localhost:8100
  withCredentials: true, // only if you use cookies/auth
})

export const fairnessApi = {
  getFairnessLatest: () =>
    fairnessClient.get("/api/v1/fairness/latest"),

  runFairnessFromScoreApi: () =>
    fairnessClient.post("/api/v1/fairness/audit-from-scoreapi"),
}
