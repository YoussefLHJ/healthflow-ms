package com.project.scoreapi.Controller;

import com.project.scoreapi.DTO.ModelRisqueResponse;
import com.project.scoreapi.Services.RiskScoreService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.*;


// ScoreController.java
@RestController
@RequestMapping("/api/scores")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Risk Scores", description = "Endpoints for patient readmission risk prediction")
public class RiskScoreController {

    private final RiskScoreService riskScoreService;

    @Operation(summary = "Get patient risk score")
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<ModelRisqueResponse> getPatientScore(@PathVariable String patientId) {
        log.info("Fetching risk score for patient: {}", patientId);
        ModelRisqueResponse score = riskScoreService.getPatientScore(patientId);
        return ResponseEntity.ok(score);
    }

    @Operation(summary = "Get all risk scores")
    @GetMapping("/all")
    public ResponseEntity<List<ModelRisqueResponse>> getAllScores(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {

        log.info("Fetching all risk scores (page={}, size={})", page, size);
        List<ModelRisqueResponse> scores = riskScoreService.getAllScores(page, size);
        return ResponseEntity.ok(scores);
    }

    @Operation(summary = "Get high-risk patients")
    @GetMapping("/high-risk")
    public ResponseEntity<List<ModelRisqueResponse>> getHighRiskPatients() {
        log.info("Fetching high-risk patients");
        List<ModelRisqueResponse> scores = riskScoreService.getHighRiskPatients();
        return ResponseEntity.ok(scores);
    }
}

