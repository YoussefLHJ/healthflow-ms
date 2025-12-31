package com.project.scoreapi.DTO.pipeline;
import lombok.Data;

@Data
public class PipelineHealthStatus {
    private boolean allHealthy;
    private boolean proxyFhirHealthy;
    private boolean deidHealthy;
    private boolean featurizerHealthy;
    private boolean modelRisqueHealthy;
}