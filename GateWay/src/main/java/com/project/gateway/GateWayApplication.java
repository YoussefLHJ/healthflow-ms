// GateWayApplication.java
package com.project.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.gateway.route.RouteLocator;
import org.springframework.cloud.gateway.route.builder.RouteLocatorBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;


@SpringBootApplication
public class GateWayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GateWayApplication.class, args);
    }

    @Bean
    public CorsWebFilter corsWebFilter() {
        CorsConfiguration corsConfig = new CorsConfiguration();

        // Allowed origins
        corsConfig.setAllowedOrigins(Arrays.asList(
                "http://localhost:3000",
                "http://127.0.0.1:3000"
        ));

        // Allow credentials
        corsConfig.setAllowCredentials(true);

        // Allow methods
        corsConfig.setAllowedMethods(Arrays.asList(
                "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"
        ));

        // Allow all headers
        corsConfig.setAllowedHeaders(List.of("*"));

        // Expose headers
        corsConfig.setExposedHeaders(Arrays.asList(
                "Authorization",
                "Content-Type",
                "X-Requested-With"
        ));

        // Cache preflight
        corsConfig.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }


    @Bean
    public RouteLocator routes(RouteLocatorBuilder builder) {
        return builder.routes()
                // ProxyFHIR Service - FHIR Resource Proxy
                .route("proxyfhir-service", r -> r.path("/proxyFHIR/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://PROXYFHIR"))

                // DeID Service - De-identification of sensitive data
                .route("deid-service", r -> r.path("/deid/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://DEID-SERVICE"))

                // Featurizer Service - Feature extraction from FHIR data
                .route("featurizer-service", r -> r.path("/featurizer/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://FEATURIZER-SERVICE"))

                // Model Risque - Risk prediction ML model
                .route("model-risque", r -> r.path("/model/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://MODEL-RISQUE"))

                // ScoreAPI - Risk scoring and management (no stripPrefix - keep /api paths)
                .route("score-api", r -> r.path("/api/**")
                        .uri("lb://SCORE-API"))
                // Audit Fairness service (FastAPI)
                .route("audit-fairness", r -> r.path("/audit-fairness/**")
                        .filters(f -> f.stripPrefix(1))
                        .uri("lb://AUDIT-FAIRNESS"))

                .build();

    }
}
