export interface StepResult {
  stepName: string
  success: boolean
  message: string
  startTime: string
  endTime: string
  details?: Record<string, any>
}

export interface PipelineExecutionResult {
  success: boolean
  message: string
  pipelineType: string
  startTime: string
  endTime: string
  steps: StepResult[]
}

export interface ShapExplanation {
  feature_name: string
  feature_value: any
  shap_value: number
  impact: "positive" | "negative" | "neutral"
}

export interface ModelRisqueResponse {
  patient_resource_id: string
  readmission_risk_score: number
  risk_category: "Low" | "Medium" | "High"
  model_version: string
  features_used: Record<string, any>
  shap_explanations: ShapExplanation[]
  prediction_timestamp: string
}

export interface DashboardMetrics {
  totalPatients: number
  totalPredictions: number
  riskDistribution: {
    lowRisk: number
    mediumRisk: number
    highRisk: number
    averageRiskScore: number
  }
  recentActivity: {
    predictionsLast24Hours: number
    predictionsLast7Days: number
    newPatientsLast24Hours: number
  }
  modelPerformance: {
    modelVersion: string
    accuracy: number
    precision: number
    recall: number
    f1Score: number
    aucScore: number
    lastTrainingDate: string
  }
  generatedAt: string
}

export interface PipelineStatus {
  allHealthy: boolean,
  deidHealthy: boolean,
  featurizerHealthy: boolean,
  modelRisqueHealthy: boolean,
  proxyFhirHealthy: boolean
}

export interface ModelDetails {
  modelVersion: string
  accuracy: number
  precision: number
  recall: number
  f1Score: number
  aucScore: number
  lastTrainingDate: string
  architecture: string
  parameters: string
  hyperparameters: Record<string, any>
  trainingHistory: {
    date: string
    accuracy: number
    loss: number
  }[]
}
