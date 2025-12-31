package com.project.scoreapi.Services;

import com.project.scoreapi.DTO.pipeline.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class PipelineOrchestrationService {

    private final WebClient.Builder webClientBuilder;

    @Value("${services.proxy-fhir.url:http://localhost:8001}")
    private String proxyFhirUrl;

    @Value("${services.deid.url:http://localhost:8000}")
    private String deidUrl;

    @Value("${services.featurizer.url:http://localhost:8001}")
    private String featurizerUrl;

    @Value("${services.model-risque.url:http://localhost:8002}")
    private String modelRisqueUrl;

    // ========== FULL PIPELINE EXECUTION ==========

    public PipelineExecutionResult executeTrainingPipeline(boolean clearExisting) {
        PipelineExecutionResult result = new PipelineExecutionResult();
        result.setPipelineType("TRAINING");
        result.setStartTime(LocalDateTime.now());
        result.setSteps(new ArrayList<>());

        try {
            // Step 1: Fetch from ProxyFHIR (training data manifest)
            log.info("📋 Step 1/4: Fetching training data from ProxyFHIR /bulk/manifest");
            StepResult step1 = fetchProxyFHIRData("training");
            result.getSteps().add(step1);

            if (!step1.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at ProxyFHIR step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 2: Ingest to DEID
            log.info("🔒 Step 2/4: Ingesting to DEID service");
            StepResult step2 = ingestToDEID("training", clearExisting);
            result.getSteps().add(step2);

            if (!step2.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at DEID step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 3: Extract features
            log.info("🔬 Step 3/4: Extracting features");
            StepResult step3 = extractFeatures(100);
            result.getSteps().add(step3);

            if (!step3.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at Featurizer step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 4: Train model
            log.info("🤖 Step 4/4: Training prediction model");
            StepResult step4 = trainModel();
            result.getSteps().add(step4);

            if (!step4.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at Model Training step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            result.setSuccess(true);
            result.setMessage("✅ Training pipeline completed successfully");
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("❌ Pipeline execution failed: {}", e.getMessage(), e);
            result.setSuccess(false);
            result.setMessage("Pipeline failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }

    public PipelineExecutionResult executeHospitalPipeline(boolean clearExisting) {
        PipelineExecutionResult result = new PipelineExecutionResult();
        result.setPipelineType("HOSPITAL");
        result.setStartTime(LocalDateTime.now());
        result.setSteps(new ArrayList<>());

        try {
            // Step 1: Fetch from ProxyFHIR (hospital data)
            log.info("🏥 Step 1/4: Fetching hospital data from ProxyFHIR /bulk/hospital/manifest");
            StepResult step1 = fetchProxyFHIRData("hospital");
            result.getSteps().add(step1);

            if (!step1.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at ProxyFHIR step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 2: Ingest to DEID
            log.info("🔒 Step 2/4: Ingesting to DEID service (hospital endpoint)");
            StepResult step2 = ingestToDEID("hospital", clearExisting);
            result.getSteps().add(step2);

            if (!step2.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at DEID step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 3: Extract features
            log.info("🔬 Step 3/4: Extracting features");
            StepResult step3 = extractFeatures(100);
            result.getSteps().add(step3);

            if (!step3.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at Featurizer step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            // Step 4: Generate predictions
            log.info("🎯 Step 4/4: Generating readmission predictions");
            StepResult step4 = modelRisquePrediction(clearExisting, 1000);  // ← Pass limit
            result.getSteps().add(step4);

            if (!step4.isSuccess()) {
                result.setSuccess(false);
                result.setMessage("Pipeline failed at Prediction step");
                result.setEndTime(LocalDateTime.now());
                return result;
            }

            result.setSuccess(true);
            result.setMessage("✅ Hospital pipeline completed successfully with predictions");
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("❌ Pipeline execution failed: {}", e.getMessage(), e);
            result.setSuccess(false);
            result.setMessage("Pipeline failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }



    // ========== INDIVIDUAL STEP EXECUTION ==========

    public StepResult fetchProxyFHIRData(String dataSource) {
        StepResult result = new StepResult();
        result.setStepName("ProxyFHIR Data Fetch");
        result.setStartTime(LocalDateTime.now());

        try {
            // Choose endpoint based on data source
            String endpoint = dataSource.equalsIgnoreCase("hospital")
                    ? "/bulk/hospital/manifest"
                    : "/bulk/manifest";

            log.info("Calling ProxyFHIR: {}{}", proxyFhirUrl, endpoint);

            Map<String, Object> response = webClientBuilder.build()
                    .get()
                    .uri(proxyFhirUrl + endpoint)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            result.setSuccess(true);
            result.setMessage("Successfully fetched " + dataSource + " data from ProxyFHIR");
            result.setDetails(response);
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("Failed to fetch from ProxyFHIR: {}", e.getMessage());
            result.setSuccess(false);
            result.setMessage("ProxyFHIR fetch failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }

    public StepResult ingestToDEID(String dataSource, boolean clearExisting) {
        StepResult result = new StepResult();
        result.setStepName("DEID Ingestion");
        result.setStartTime(LocalDateTime.now());

        try {
            // Choose endpoint based on data source
            String endpoint = dataSource.equalsIgnoreCase("hospital")
                    ? "/deid/ingest-hospital?clear_existing=" + clearExisting
                    : "/deid/ingest?clear_existing=" + clearExisting;

            log.info("Calling DEID: {}{}", deidUrl, endpoint);

            DEIDIngestionResult response = webClientBuilder.build()
                    .post()
                    .uri(deidUrl + endpoint)
                    .retrieve()
                    .bodyToMono(DEIDIngestionResult.class)
                    .block();

            result.setSuccess("success".equalsIgnoreCase(response.getStatus()));
            result.setMessage(response.getMessage());
            result.setDetails(Map.of(
                    "files_processed", response.getFilesProcessed(),
                    "patients_created", response.getPatientsCreated(),
                    "encounters_created", response.getEncountersCreated(),
                    "conditions_created", response.getConditionsCreated(),
                    "observations_created", response.getObservationsCreated(),
                    "medication_requests_created", response.getMedicationRequestsCreated()
            ));
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("Failed to ingest to DEID: {}", e.getMessage());
            result.setSuccess(false);
            result.setMessage("DEID ingestion failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }

    public StepResult extractFeatures(int batchSize) {
        StepResult result = new StepResult();
        result.setStepName("Feature Extraction");
        result.setStartTime(LocalDateTime.now());

        try {
            log.info("Calling Featurizer: {}/features/all", featurizerUrl);

            Map<String, Object> response = webClientBuilder.build()
                    .post()
                    .uri(featurizerUrl + "/features/all?force_refresh=true&limit=" + batchSize)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            result.setSuccess(true);
            result.setMessage("Features extracted successfully");
            result.setDetails(response);
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("Failed to extract features: {}", e.getMessage());
            result.setSuccess(false);
            result.setMessage("Feature extraction failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }

    public StepResult modelRisquePrediction(boolean clearExisting, int limit) {
        StepResult result = new StepResult();
        result.setStepName("Model Risque Predictions");
        result.setStartTime(LocalDateTime.now());

        try {
            // Clear existing predictions if requested
            if (clearExisting) {
                log.info("Clearing existing predictions from ModelRisque");
                try {
                    webClientBuilder.build()
                            .delete()
                            .uri(modelRisqueUrl + "/predictions/clear")
                            .retrieve()
                            .bodyToMono(Void.class)
                            .block();
                    log.info("Successfully cleared existing predictions");
                } catch (Exception e) {
                    log.warn("Failed to clear predictions: {}", e.getMessage());
                }
            }

            // Call ModelRisque to generate predictions from Featurizer data
            log.info("Calling ModelRisque to generate predictions from Featurizer (limit={})", limit);

            Map<String, Object> response = webClientBuilder.build()
                    .post()
                    .uri(modelRisqueUrl + "/prediction/data?skip_cache=false&limit=" + limit)
                    .contentType(org.springframework.http.MediaType.APPLICATION_JSON)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            // Parse response to count successes/failures
            int successCount = 0;
            int failureCount = 0;

            if (response != null) {
                for (Map.Entry<String, Object> entry : response.entrySet()) {
                    if (entry.getValue() instanceof Map) {
                        Map<String, Object> pred = (Map<String, Object>) entry.getValue();
                        if (pred.containsKey("error")) {
                            failureCount++;
                            log.warn("Prediction failed for {}: {}", entry.getKey(), pred.get("error"));
                        } else {
                            successCount++;
                        }
                    }
                }
            }

            result.setSuccess(successCount > 0);
            result.setMessage(String.format(
                    "Predictions completed: %d successful, %d failed",
                    successCount, failureCount
            ));
            result.setDetails(Map.of(
                    "predictions_successful", successCount,
                    "predictions_failed", failureCount,
                    "limit", limit,
                    "cleared_existing", clearExisting
            ));
            result.setEndTime(LocalDateTime.now());

            log.info("✅ Model predictions complete: {} successful, {} failed", successCount, failureCount);

        } catch (Exception e) {
            log.error("Failed to generate predictions: {}", e.getMessage(), e);
            result.setSuccess(false);
            result.setMessage("Prediction generation failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }


    public StepResult trainModel() {
        StepResult result = new StepResult();
        result.setStepName("Model Training");
        result.setStartTime(LocalDateTime.now());

        try {
            log.info("Calling ModelRisque: {}/train", modelRisqueUrl);

            Map<String, Object> response = webClientBuilder.build()
                    .post()
                    .uri(modelRisqueUrl + "/train")
                    .bodyValue(Map.of(
                            "test_size", 0.2,
                            "random_state", 42
                    ))
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();

            result.setSuccess(true);
            result.setMessage("Model trained successfully");
            result.setDetails(response);
            result.setEndTime(LocalDateTime.now());

        } catch (Exception e) {
            log.error("Failed to train model: {}", e.getMessage());
            result.setSuccess(false);
            result.setMessage("Model training failed: " + e.getMessage());
            result.setEndTime(LocalDateTime.now());
        }

        return result;
    }

    public PipelineStatus getCurrentStatus() {
        PipelineStatus status = new PipelineStatus();
        status.setTimestamp(LocalDateTime.now());

        try {
            // Check DEID service
            Map<String, Object> deidStats = webClientBuilder.build()
                    .get()
                    .uri(deidUrl + "/deid/patients?limit=1")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .onErrorReturn(Map.of())
                    .block();

            status.setDeidHealthy(deidStats != null && !deidStats.isEmpty());

            // Check Featurizer service (placeholder - adjust based on actual endpoint)
            status.setFeaturizerHealthy(true);

            // Check Model service (placeholder - adjust based on actual endpoint)
            status.setModelHealthy(true);

            status.setAllServicesHealthy(
                    status.isDeidHealthy() &&
                            status.isFeaturizerHealthy() &&
                            status.isModelHealthy()
            );

        } catch (Exception e) {
            log.error("Failed to get pipeline status: {}", e.getMessage());
            status.setAllServicesHealthy(false);
        }

        return status;
    }


    public ClearResult clearAllData() {
        ClearResult result = new ClearResult();
        List<String> clearedServices = new ArrayList<>();

        try {
            // Clear DEID database
            webClientBuilder.build()
                    .delete()
                    .uri(deidUrl + "/deid/clear-database")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            clearedServices.add("DEID");

            // Clear Featurizer database
            webClientBuilder.build()
                    .delete()
                    .uri(featurizerUrl + "/features/patient/prune")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            clearedServices.add("Featurizer");

            // Clear ModelRisque database
            webClientBuilder.build()
                    .delete()
                    .uri(modelRisqueUrl + "/model/clear-database")
                    .retrieve()
                    .bodyToMono(Void.class)
                    .block();
            clearedServices.add("ModelRisque");

            result.setSuccess(true);
            result.setMessage("All data cleared successfully");
            result.setClearedServices(clearedServices);

        } catch (Exception e) {
            log.error("Failed to clear data: {}", e.getMessage());
            result.setSuccess(false);
            result.setMessage("Clear failed: " + e.getMessage());
            result.setClearedServices(clearedServices);
        }

        return result;
    }



    public PipelineHealthStatus checkServicesHealth() {
        PipelineHealthStatus health = new PipelineHealthStatus();

        try {
            // Check ProxyFHIR
            webClientBuilder.build().get().uri(proxyFhirUrl + "/api/health").retrieve().bodyToMono(String.class).block();
            health.setProxyFhirHealthy(true);
        } catch (Exception e) {
            health.setProxyFhirHealthy(false);
        }

        try {
            // Check DEID
            webClientBuilder.build().get().uri(deidUrl + "/").retrieve().bodyToMono(String.class).block();
            health.setDeidHealthy(true);
        } catch (Exception e) {
            health.setDeidHealthy(false);
        }

        try {
            // Check Featurizer
            webClientBuilder.build().get().uri(featurizerUrl + "/").retrieve().bodyToMono(String.class).block();
            health.setFeaturizerHealthy(true);
        } catch (Exception e) {
            health.setFeaturizerHealthy(false);
        }

        try {
            // Check ModelRisque
            webClientBuilder.build().get().uri(modelRisqueUrl + "/").retrieve().bodyToMono(String.class).block();
            health.setModelRisqueHealthy(true);
        } catch (Exception e) {
            health.setModelRisqueHealthy(false);
        }

        health.setAllHealthy(
                health.isProxyFhirHealthy() &&
                        health.isDeidHealthy() &&
                        health.isFeaturizerHealthy() &&
                        health.isModelRisqueHealthy()
        );

        return health;
    }


}
