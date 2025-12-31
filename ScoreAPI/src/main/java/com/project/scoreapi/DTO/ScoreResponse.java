package com.project.scoreapi.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class ScoreResponse {
    // Database ID (internal only, not from ModelRisque)
    private Long id;

    @JsonProperty("patient_resource_id")
    private String patientResourceId;

    @JsonProperty("readmission_risk_score")
    private Double readmissionRiskScore;

    @JsonProperty("risk_category")
    private String riskCategory;

    @JsonProperty("model_version")
    private String modelVersion;

    @JsonProperty("prediction_timestamp")
    private LocalDateTime predictionTimestamp;

    @JsonProperty("features_used")
    private Map<String, Object> featuresUsed;

    @JsonProperty("shap_explanations")
    private List<ShapExplanation> shapExplanations;
}


