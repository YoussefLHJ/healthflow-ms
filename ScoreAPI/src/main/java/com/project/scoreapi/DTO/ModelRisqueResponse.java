package com.project.scoreapi.DTO;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class ModelRisqueResponse {
    @JsonProperty("patient_resource_id")
    private String patientResourceId;

    @JsonProperty("readmission_risk_score")
    private Double readmissionRiskScore;

    @JsonProperty("risk_category")
    private String riskCategory;

    @JsonProperty("model_version")
    private String modelVersion;

    @JsonProperty("features_used")
    private Map<String, Object> featuresUsed;

    // Fix: Change from Object to List<ShapExplanation>
    @JsonProperty("shap_explanations")
    private List<ShapExplanation> shapExplanations;

    @JsonProperty("prediction_timestamp")
    private LocalDateTime predictionTimestamp;
}
