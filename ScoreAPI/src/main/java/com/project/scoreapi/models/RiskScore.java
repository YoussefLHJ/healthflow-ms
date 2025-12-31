package com.project.scoreapi.models;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Entity
@Table(name = "risk_scores", indexes = {
        @Index(name = "idx_patient_resource_id", columnList = "patient_resource_id"),
        @Index(name = "idx_prediction_timestamp", columnList = "prediction_timestamp"),
        @Index(name = "idx_risk_category", columnList = "risk_category")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RiskScore {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "patient_resource_id", nullable = false)
    private String patientResourceId;

    @Column(name = "risk_score", nullable = false)
    private Double riskScore;

    @Column(name = "risk_category", nullable = false)
    private String riskCategory;

    @Column(name = "model_version", nullable = false)
    private String modelVersion;

    @Column(name = "prediction_timestamp", nullable = false)
    private LocalDateTime predictionTimestamp;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "features_used", columnDefinition = "jsonb")
    private Map<String, Object> featuresUsed;

    // Changed to List (generic) - Hibernate will store as JSON
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "shap_explanations", columnDefinition = "jsonb")
    private List<Map<String, Object>> shapExplanations;  // ← Changed from List<ShapExplanation>

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
