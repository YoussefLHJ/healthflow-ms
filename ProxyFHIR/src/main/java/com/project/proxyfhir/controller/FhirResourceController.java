package com.project.proxyfhir.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.proxyfhir.model.FhirResource;
import com.project.proxyfhir.repository.FhirResourceRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/ressources")
public class FhirResourceController {

    @Autowired
    private FhirResourceRepository repository;

    private final ObjectMapper mapper = new ObjectMapper();

    /**
     * POST /proxyFHIR - Ingest a FHIR Bundle or single resource (keeps existing behaviour)
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> ingestBundle(@RequestBody String fhirJson) {
        try {
            // Parse and save the FHIR resource/bundle
            FhirResource resource = new FhirResource();
            resource.setResourceType("Bundle"); // You can parse resourceType from JSON if desired
            resource.setResourceId("auto-" + System.currentTimeMillis());
            resource.setData(fhirJson);
            resource.setLastUpdated(LocalDateTime.now());

            repository.save(resource);

            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                "status", "success",
                "message", "FHIR resource ingested",
                "resourceId", resource.getResourceId(),
                "timestamp", resource.getLastUpdated()
            ));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of(
                "status", "error",
                "message", e.getMessage()
            ));
        }
    }

    /**
     * GET /proxyFHIR - List all FHIR resources
     */
    @GetMapping
    public ResponseEntity<List<FhirResource>> listResources() {
        List<FhirResource> resources = repository.findAll();
        return ResponseEntity.ok(resources);
    }

    /**
     * GET /proxyFHIR/{id} - Get a specific FHIR resource by DB ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getResource(@PathVariable Long id) {
        Optional<FhirResource> resource = repository.findById(id);
        if (resource.isPresent()) {
            return ResponseEntity.ok(resource.get());
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
            "error", "Resource not found",
            "id", id
        ));
    }

    /**
     * GET /proxyFHIR/type/{resourceType} - Get all resources of a specific type
     */
    @GetMapping("/type/{resourceType}")
    public ResponseEntity<List<FhirResource>> getResourcesByType(@PathVariable String resourceType) {
        List<FhirResource> resources = repository.findByResourceType(resourceType);
        return ResponseEntity.ok(resources);
    }

    /**
     * GET /proxyFHIR/type/{resourceType}/{resourceId} - Get resource by FHIR type and resource id
     */
    @GetMapping("/type/{resourceType}/{resourceId}")
    public ResponseEntity<?> getResourceByTypeAndId(@PathVariable String resourceType, @PathVariable String resourceId) {
        Optional<FhirResource> resource = repository.findByResourceTypeAndResourceId(resourceType, resourceId);
        if (resource.isPresent()) {
            // try to return parsed JSON content where possible
            try {
                JsonNode node = mapper.readTree(resource.get().getContent());
                return ResponseEntity.ok(node);
            } catch (Exception e) {
                return ResponseEntity.ok(Map.of("content", resource.get().getContent()));
            }
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
            "error", "Resource not found",
            "resourceType", resourceType,
            "resourceId", resourceId
        ));
    }

    /**
     * POST /proxyFHIR/type/{resourceType} - Create or update a resource of given type
     * Body should contain the resource JSON. If 'id' present inside JSON, it will be used as resourceId.
     */
    @PostMapping("/type/{resourceType}")
    public ResponseEntity<?> createOrUpdateResource(@PathVariable String resourceType, @RequestBody JsonNode body) {
        try {
            String resourceId = null;
            if (body.has("id")) resourceId = body.get("id").asText();
            String content = body.toString();

            if (resourceId != null) {
                Optional<FhirResource> existing = repository.findByResourceTypeAndResourceId(resourceType, resourceId);
                if (existing.isPresent()) {
                    FhirResource r = existing.get();
                    r.setContent(content);
                    r.setLastUpdated(LocalDateTime.now());
                    repository.save(r);
                    return ResponseEntity.ok(Map.of("status", "updated", "resourceType", resourceType, "resourceId", resourceId));
                }
            }

            // create new
            FhirResource r = new FhirResource(resourceType, resourceId, content);
            repository.save(r);
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of("status", "created", "resourceType", resourceType, "resourceId", r.getResourceId()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * DELETE /fhir/{id} - Delete a FHIR resource
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteResource(@PathVariable Long id) {
        if (repository.existsById(id)) {
            repository.deleteById(id);
            return ResponseEntity.ok(Map.of(
                "status", "success",
                "message", "Resource deleted",
                "id", id
            ));
        }
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of(
            "status", "error",
            "message", "Resource not found",
            "id", id
        ));
    }

    /**
     * GET /fhir/health - Simple health check
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        long count = repository.count();
        return ResponseEntity.ok(Map.of(
            "status", "UP",
            "service", "FHIR Proxy",
            "totalResources", count,
            "timestamp", LocalDateTime.now()
        ));
    }
}
