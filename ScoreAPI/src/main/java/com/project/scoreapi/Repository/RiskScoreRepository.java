package com.project.scoreapi.Repository;

import com.project.scoreapi.models.RiskScore;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface RiskScoreRepository extends JpaRepository<RiskScore, Long> {

    Optional<RiskScore> findFirstByPatientResourceIdOrderByPredictionTimestampDesc(String patientResourceId);

    List<RiskScore> findByRiskCategoryOrderByRiskScoreDesc(String riskCategory);

    List<RiskScore> findByPredictionTimestampBetween(LocalDateTime start, LocalDateTime end);

    @Query("SELECT COUNT(r) FROM RiskScore r WHERE r.riskCategory = :category")
    Long countByRiskCategory(String category);

    List<RiskScore> findByRiskCategory(String high);

    // NEW: Count recent predictions
    int countByPredictionTimestampAfter(LocalDateTime timestamp);

    // NEW: Average risk score
    @Query("SELECT AVG(r.riskScore) FROM RiskScore r")
    Double averageRiskScore();
}