package com.project.scoreapi.DTO;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Schema(description = "Request object for querying risk scores with various filters")
public class ScoreQueryRequest {

    @Schema(description = "Start date for filtering predictions", example = "2025-01-01T00:00:00")
    private LocalDateTime startDate;

    @Schema(description = "End date for filtering predictions", example = "2025-12-31T23:59:59")
    private LocalDateTime endDate;

    @Schema(description = "Filter by risk category", example = "HIGH", allowableValues = {"LOW", "MEDIUM", "HIGH"})
    private String riskCategory;

    @Schema(description = "Minimum risk score threshold", example = "0.7", minimum = "0", maximum = "1")
    private Double minRiskScore;

    @Schema(description = "Maximum number of results to return", example = "100", defaultValue = "100")
    private Integer limit = 100;
}
