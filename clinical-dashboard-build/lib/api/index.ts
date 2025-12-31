// lib/api/index.ts
import apiClient from './client';
import { config } from '@/lib/config';

// ===========================================
// ScoreAPI - Single Source of Truth
// ===========================================
export const scoreApi = {
  // Authentication
  login: (username: string, password: string) =>
    apiClient.post(`${config.routes.scoreApi}/auth/login`, { username, password }),
  
  register: (data: any) =>
    apiClient.post(`${config.routes.scoreApi}/auth/register`, data),
  
  getCurrentUser: () =>
    apiClient.get(`${config.routes.scoreApi}/auth/me`),

  // Dashboard Metrics
  getDashboardMetrics: () =>
    apiClient.get(`${config.routes.scoreApi}/dashboard/metrics`),

  // Risk Scores
  getAllScores: (skip = 0, limit = 20) =>
    apiClient.get(`${config.routes.scoreApi}/scores/all`, { params: { skip, limit } }),
  
  getHighRiskPatients: () =>
    apiClient.get(`${config.routes.scoreApi}/scores/high-risk`),
  
  getPatientScore: (patientId: string) =>
    apiClient.get(`${config.routes.scoreApi}/scores/patient/${patientId}`),

  // Pipeline Control
  runHospitalPipeline: (clearExisting = false) =>
    apiClient.post(`${config.routes.scoreApi}/pipeline/run/hospital`, null, {
      params: { clearExisting },
    }),
  
  runTrainingPipeline: (clearExisting = false) =>
    apiClient.post(`${config.routes.scoreApi}/pipeline/run/training`, null, {
      params: { clearExisting },
    }),
  
  getPipelineHealth: () =>
    apiClient.get(`${config.routes.scoreApi}/pipeline/health`),
  
  clearAllData: () =>
    apiClient.delete(`${config.routes.scoreApi}/pipeline/clear-all`),

  // Audit Fairness
  getFairnessLatest: () =>
    apiClient.get(
      `${config.routes.auditFairness}/api/v1/fairness/latest`,
    ),

  runFairnessFromScoreApi: () =>
    apiClient.post(
      `${config.routes.auditFairness}/api/v1/fairness/audit-from-scoreapi`,
    ),
};
