package com.project.scoreapi.DTO.pipeline;

import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Data
public class PipelineExecutionResult {
    private boolean success;
    private String message;
    private String pipelineType;  // "TRAINING" or "HOSPITAL"
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private List<StepResult> steps;
}