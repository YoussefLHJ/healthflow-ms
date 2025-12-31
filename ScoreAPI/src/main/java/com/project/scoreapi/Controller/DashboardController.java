package com.project.scoreapi.Controller;


import com.project.scoreapi.DTO.DashboardMetrics;
import com.project.scoreapi.Services.DashboardService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Dashboard", description = "Dashboard metrics and analytics")
public class DashboardController {

    private final DashboardService dashboardService;

    @Operation(
            summary = "Get dashboard metrics",
            description = "Retrieve comprehensive metrics for dashboard: patient counts, risk distribution, recent activity, and model performance"
    )
    @GetMapping("/metrics")
    public ResponseEntity<DashboardMetrics> getDashboardMetrics() {
        log.info("📊 Fetching dashboard metrics");
        DashboardMetrics metrics = dashboardService.getDashboardMetrics();
        return ResponseEntity.ok(metrics);
    }
}

