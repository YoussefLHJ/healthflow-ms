package com.project.scoreapi.DTO;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ShapExplanation {

    @JsonProperty("feature_name")
    private String featureName;

    @JsonProperty("feature_value")
    private Object featureValue;

    @JsonProperty("shap_value")
    private Double shapValue;

    @JsonProperty("impact")
    private String impact;  // "increases_risk" or "decreases_risk"
}


