package com.project.scoreapi.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import io.swagger.v3.oas.models.tags.Tag;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenAPIConfig {

    @Value("${scoreapi.openapi.dev-url:http://localhost:8090}")
    private String devUrl;

    @Value("${scoreapi.openapi.prod-url:https://healthflow-api.com}")
    private String prodUrl;

    @Bean
    public OpenAPI healthFlowOpenAPI() {
        // Development server
        Server devServer = new Server();
        devServer.setUrl(devUrl);
        devServer.setDescription("Development Server");

        // Production server
        Server prodServer = new Server();
        prodServer.setUrl(prodUrl);
        prodServer.setDescription("Production Server");

        // Contact information
        Contact contact = new Contact();
        contact.setName("HealthFlow Team");
        contact.setEmail("[email protected]");
        contact.setUrl("https://healthflow.com");

        // License
        License license = new License()
                .name("Apache 2.0")
                .url("https://www.apache.org/licenses/LICENSE-2.0.html");

        // API Info
        Info info = new Info()
                .title("HealthFlow ScoreAPI - Readmission Risk Prediction")
                .version("1.0.0")
                .description("REST API for managing patient readmission risk scores and orchestrating the ML pipeline. " +
                        "Provides endpoints for:\n" +
                        "- Risk score queries and predictions\n" +
                        "- Pipeline orchestration (ProxyFHIR → DEID → Featurizer → ModelRisque)\n" +
                        "- Data ingestion control for training and hospital data")
                .contact(contact)
                .license(license);

        // API Tags for grouping
        Tag scoresTag = new Tag()
                .name("Risk Scores")
                .description("Endpoints for querying and managing readmission risk scores");

        Tag pipelineTag = new Tag()
                .name("Pipeline Control")
                .description("Endpoints for orchestrating the HealthFlow data pipeline");

        return new OpenAPI()
                .info(info)
                .servers(List.of(devServer, prodServer))
                .tags(List.of(scoresTag, pipelineTag));
    }
}
