package com.project.scoreapi.DTO;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

@Data
public class DashboardMetrics {
    private int totalPatients;
    private int totalPredictions;
    private RiskDistribution riskDistribution;
    private RecentActivity recentActivity;
    private ModelPerformance modelPerformance;
    private LocalDateTime generatedAt;

    @Data
    public static class RiskDistribution {
        private int lowRisk;
        private int mediumRisk;
        private int highRisk;
        private double averageRiskScore;
    }

    @Data
    public static class RecentActivity {
        private int predictionsLast24Hours;
        private int predictionsLast7Days;
        private int newPatientsLast24Hours;
    }

    @Data
    public static class ModelPerformance {
        private String modelVersion;
        private double accuracy;
        private double precision;
        private double recall;
        private double f1Score;
        private double aucScore;
        private LocalDateTime lastTrainingDate;
    }
}
