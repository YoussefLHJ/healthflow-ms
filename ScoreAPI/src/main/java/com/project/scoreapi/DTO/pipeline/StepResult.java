package com.project.scoreapi.DTO.pipeline;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class StepResult {
    private String stepName;
    private boolean success;
    private String message;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Object details;
}
