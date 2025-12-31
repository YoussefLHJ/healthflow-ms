package com.project.scoreapi.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PatientRiskScore {
    private String patientResourceId;
    private Double riskScore;
    private String riskCategory;
    private String modelVersion;
    private LocalDateTime predictionTimestamp;
}

