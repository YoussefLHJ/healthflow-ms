package com.project.scoreapi.Controller;

import com.project.scoreapi.DTO.pipeline.*;
import com.project.scoreapi.Services.PipelineOrchestrationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/pipeline")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
public class PipelineController {

    private final PipelineOrchestrationService pipelineService;

    /**
     * Execute full training pipeline: ProxyFHIR → DEID → Featurizer → ModelRisque (train)
     */
    @PostMapping("/run/training")
    public ResponseEntity<PipelineExecutionResult> runTrainingPipeline(
            @RequestParam(defaultValue = "false") boolean clearExisting) {
        log.info("Starting TRAINING data pipeline (clear_existing={})", clearExisting);

        PipelineExecutionResult result = pipelineService.executeTrainingPipeline(clearExisting);

        return ResponseEntity.ok(result);
    }

    /**
     * Execute hospital pipeline: ProxyFHIR (hospital) → DEID → Featurizer
     */
    @PostMapping("/run/hospital")
    public ResponseEntity<PipelineExecutionResult> runHospitalPipeline(
            @RequestParam(defaultValue = "false") boolean clearExisting) {
        log.info("Starting HOSPITAL data pipeline (clear_existing={})", clearExisting);

        PipelineExecutionResult result = pipelineService.executeHospitalPipeline(clearExisting);

        return ResponseEntity.ok(result);
    }

    /**
     * Execute single step: Fetch from ProxyFHIR
     */
    @PostMapping("/steps/predictHospital")
    public ResponseEntity<StepResult> fetchForHospitalPrediction(
            @RequestParam(defaultValue = "false") boolean clearExisting,
            @RequestParam(defaultValue = "100") int numberOfPatients) {
        log.info("Fetching data from ProxyFHIR for hospital prediction (clear={})", clearExisting);
        StepResult result = pipelineService.modelRisquePrediction(clearExisting, numberOfPatients);
        return ResponseEntity.ok(result);
    }


    @PostMapping("/steps/proxyfhir")
    public ResponseEntity<StepResult> fetchFromProxyFHIR(
            @RequestParam String dataSource) {  // "training" or "hospital"
        log.info("Fetching data from ProxyFHIR: {}", dataSource);

        StepResult result = pipelineService.fetchProxyFHIRData(dataSource);

        return ResponseEntity.ok(result);
    }

    /**
     * Execute single step: Ingest to DEID
     */
    @PostMapping("/steps/deid")
    public ResponseEntity<StepResult> ingestToDEID(
            @RequestParam String dataSource,
            @RequestParam(defaultValue = "false") boolean clearExisting) {
        log.info("Ingesting to DEID: {} (clear={})", dataSource, clearExisting);

        StepResult result = pipelineService.ingestToDEID(dataSource, clearExisting);

        return ResponseEntity.ok(result);
    }

    /**
     * Execute single step: Extract features
     */
    @PostMapping("/steps/featurizer")
    public ResponseEntity<StepResult> extractFeatures(
            @RequestParam(defaultValue = "100") int batchSize) {
        log.info("Extracting features (batch_size={})", batchSize);

        StepResult result = pipelineService.extractFeatures(batchSize);

        return ResponseEntity.ok(result);
    }

    /**
     * Execute single step: Train model
     */
    @PostMapping("/steps/model-train")
    public ResponseEntity<StepResult> trainModel() {
        log.info("Training readmission prediction model");

        StepResult result = pipelineService.trainModel();

        return ResponseEntity.ok(result);
    }

    /**
     * Get current pipeline status
     */
    @GetMapping("/status")
    public ResponseEntity<PipelineStatus> getPipelineStatus() {
        PipelineStatus status = pipelineService.getCurrentStatus();
        return ResponseEntity.ok(status);
    }

    /**
     * Clear all data from pipeline services
     */
    @DeleteMapping("/clear-all")
    public ResponseEntity<ClearResult> clearAllData() {
        log.warn("Clearing ALL data from pipeline");

        ClearResult result = pipelineService.clearAllData();

        return ResponseEntity.ok(result);
    }

    /**
     * Health check for pipeline endpoints
     */
    @GetMapping("/health")
    public ResponseEntity<PipelineHealthStatus> checkHealth() {
        PipelineHealthStatus health = pipelineService.checkServicesHealth();
        return ResponseEntity.ok(health);
    }
}

