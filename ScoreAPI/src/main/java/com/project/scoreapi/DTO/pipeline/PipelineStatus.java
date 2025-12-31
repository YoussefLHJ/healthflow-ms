package com.project.scoreapi.DTO.pipeline;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class PipelineStatus {
    private boolean allServicesHealthy;
    private boolean deidHealthy;
    private boolean featurizerHealthy;
    private boolean modelHealthy;
    private LocalDateTime timestamp;
}
