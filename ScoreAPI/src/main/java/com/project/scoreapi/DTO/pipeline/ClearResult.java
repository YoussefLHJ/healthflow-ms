package com.project.scoreapi.DTO.pipeline;

import lombok.Data;
import java.util.List;

@Data
public class ClearResult {
    private boolean success;
    private String message;
    private List<String> clearedServices;
}