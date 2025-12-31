package com.project.scoreapi.DTO.pipeline;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.List;

@Data
public class DEIDIngestionResult {
    private String status;
    private String message;

    @JsonProperty("files_processed")
    private List<String> filesProcessed;

    @JsonProperty("patients_created")
    private Integer patientsCreated;

    @JsonProperty("encounters_created")
    private Integer encountersCreated;

    @JsonProperty("conditions_created")
    private Integer conditionsCreated;

    @JsonProperty("observations_created")
    private Integer observationsCreated;

    @JsonProperty("medication_requests_created")
    private Integer medicationRequestsCreated;

    @JsonProperty("procedures_created")
    private Integer proceduresCreated;

    @JsonProperty("diagnostic_reports_created")
    private Integer diagnosticReportsCreated;
}