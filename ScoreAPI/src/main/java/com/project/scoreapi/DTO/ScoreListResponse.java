package com.project.scoreapi.DTO;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ScoreListResponse {
    private Integer totalCount;
    private List<PatientRiskScore> scores;
}

