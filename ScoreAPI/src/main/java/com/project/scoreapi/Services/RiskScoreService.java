package com.project.scoreapi.Services;

import com.project.scoreapi.DTO.ModelRisqueResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;

@Service
@RequiredArgsConstructor
@Slf4j
public class RiskScoreService {

    private final WebClient.Builder webClientBuilder;

    @Value("${services.model-risque.url}")
    private String modelRisqueUrl;

    public List<ModelRisqueResponse> getAllScores(int skip, int limit) {
        log.info("Fetching all predictions from ModelRisque (skip={}, limit={})", skip, limit);

        return webClientBuilder.build()
                .get()
                .uri(modelRisqueUrl + "/predictions/all?skip=" + skip + "&limit=" + limit)
                .retrieve()
                .bodyToFlux(ModelRisqueResponse.class)
                .collectList()
                .block();
    }

    public ModelRisqueResponse getPatientScore(String patientId) {
        log.info("Fetching prediction for patient: {}", patientId);

        return webClientBuilder.build()
                .get()
                .uri(modelRisqueUrl + "/predictions/patient/" + patientId)
                .retrieve()
                .bodyToMono(ModelRisqueResponse.class)
                .block();
    }

    public List<ModelRisqueResponse> getHighRiskPatients() {
        log.info("Fetching high-risk patients from ModelRisque");

        return webClientBuilder.build()
                .get()
                .uri(modelRisqueUrl + "/predictions/all?skip=0&limit=1000")
                .retrieve()
                .bodyToFlux(ModelRisqueResponse.class)
                .filter(pred -> "HIGH".equals(pred.getRiskCategory()))
                .collectList()
                .block();
    }
}
