package com.project.scoreapi;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.Bean;
import org.springframework.web.reactive.function.client.WebClient;

@SpringBootApplication
@EnableDiscoveryClient
public class ScoreApiApplication {

    public static void main(String[] args) {
        SpringApplication.run(ScoreApiApplication.class, args);
    }
    @Bean
    public WebClient.Builder webClientBuilder() {
        return WebClient.builder();
    }

}
