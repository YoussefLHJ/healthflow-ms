package com.project.scoreapi.Controller;

import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/health")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Health", description = "Check health to debug API Gateway")
public class HealthController {
    // Health check endpoint
    @GetMapping()
    public String healthCheck() {
        return "ScoreAPI is running!";
    }
}
