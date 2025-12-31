// lib/config.ts
export const config = {
  // API Gateway - Single entry point for all services
  gateway: {
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8888',
    timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'),
  },
  
  // Gateway Routes (all through port 8888)
  routes: {
    scoreApi: '/api',           // http://localhost:8888/api/**
    proxyFhir: '/proxyFHIR',    // http://localhost:8888/proxyFHIR/**
    deid: '/deid',              // http://localhost:8888/deid/**
    featurizer: '/featurizer',  // http://localhost:8888/featurizer/**
    modelRisque: '/model',      // http://localhost:8888/model/**
    auditFairness: "/audit-fairness", // new
  },
  
  // Direct service URLs (for monitoring dashboards only)
  services: {
    proxyFhir: process.env.NEXT_PUBLIC_PROXY_FHIR_DIRECT,
    deid: process.env.NEXT_PUBLIC_DEID_DIRECT,
    featurizer: process.env.NEXT_PUBLIC_FEATURIZER_DIRECT,
    modelRisque: process.env.NEXT_PUBLIC_MODEL_RISQUE_DIRECT,
    scoreApi: process.env.NEXT_PUBLIC_SCORE_API_DIRECT,
  },
  
  auth: {
    storageKey: process.env.NEXT_PUBLIC_JWT_STORAGE_KEY || 'healthflow_token',
    refreshInterval: parseInt(process.env.NEXT_PUBLIC_JWT_REFRESH_INTERVAL || '3600000'),
  },
  
  features: {
    enableRegistration: process.env.NEXT_PUBLIC_ENABLE_REGISTRATION === 'true',
    enablePipelineControl: process.env.NEXT_PUBLIC_ENABLE_PIPELINE_CONTROL === 'true',
    debugMode: process.env.NEXT_PUBLIC_ENABLE_DEBUG_MODE === 'true',
    showServiceMonitoring: process.env.NEXT_PUBLIC_SHOW_SERVICE_MONITORING === 'true',
  },
  
  pagination: {
    defaultPageSize: parseInt(process.env.NEXT_PUBLIC_DEFAULT_PAGE_SIZE || '20'),
    maxPageSize: parseInt(process.env.NEXT_PUBLIC_MAX_PAGE_SIZE || '100'),
  },
  
  polling: {
    pipelineStatusInterval: parseInt(process.env.NEXT_PUBLIC_PIPELINE_STATUS_POLL_INTERVAL || '5000'),
    metricsRefreshInterval: parseInt(process.env.NEXT_PUBLIC_METRICS_REFRESH_INTERVAL || '30000'),
  },
  
  ui: {
    appName: process.env.NEXT_PUBLIC_APP_NAME || 'HealthFlow',
    appVersion: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
    theme: process.env.NEXT_PUBLIC_THEME || 'light',
  },
  
  charts: {
    animationDuration: parseInt(process.env.NEXT_PUBLIC_CHART_ANIMATION_DURATION || '750'),
    enableAnimations: process.env.NEXT_PUBLIC_ENABLE_CHART_ANIMATIONS === 'true',
  },
  
  logging: {
    level: process.env.NEXT_PUBLIC_LOG_LEVEL || 'info',
  },
} as const;
