package com.project.proxyfhir.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
@RequestMapping("/bulk")
public class FhirExportController {

    // Use a container-friendly default: the synthea sample folder is mounted at /synthea
    @Value("${synthea.files.dir:/synthea-sample/${NUM_PATIENTS:100}-patients}")
    private String filesDir;

    // Hospital FHIR data directory
    @Value("${fhir.hospital.dir:/synthea-sample/FHIR-patients}")
    private String hospitalFhirDir;

    /**
     * Endpoint to get hospital FHIR data manifest
     * Simulates a real hospital FHIR server bulk export
     */
    @GetMapping("/hospital/manifest")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> hospitalManifest() throws IOException {
        Path dir = Paths.get(hospitalFhirDir);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            Map<String, Object> m = new HashMap<>();
            m.put("error", "Hospital FHIR directory not found: " + hospitalFhirDir);
            return ResponseEntity.badRequest().body(m);
        }

        List<String> files = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.ndjson")) {
            for (Path p : ds) {
                // Exclude log files
                if (!p.getFileName().toString().equals("log.ndjson")) {
                    files.add(p.getFileName().toString());
                }
            }
        }

        List<Map<String, String>> items = files.stream().map(f -> {
            Map<String, String> it = new HashMap<>();
            it.put("fileName", f);
            it.put("url", "/bulk/hospital/files/" + f);
            it.put("resourceType", f.split("\\.")[0]); // Extract resource type from filename
            return it;
        }).collect(Collectors.toList());

        Map<String, Object> out = new HashMap<>();
        out.put("exportId", "hospital-fhir-export");
        out.put("exportType", "hospital");
        out.put("transactionTime", java.time.Instant.now().toString());
        out.put("files", items);
        out.put("totalFiles", items.size());
        return ResponseEntity.ok(out);
    }

    /**
     * Get a specific file from hospital FHIR data
     */
    @GetMapping("/hospital/files/{filename:.+}")
    public ResponseEntity<StreamingResponseBody> getHospitalFile(@PathVariable String filename) throws IOException {
        Path dir = Paths.get(hospitalFhirDir);
        Path file = dir.resolve(filename).normalize();
        if (!file.startsWith(dir) || !Files.exists(file)) {
            return ResponseEntity.notFound().build();
        }

        StreamingResponseBody body = outputStream -> {
            try (InputStream in = Files.newInputStream(file)) {
                byte[] buffer = new byte[8192];
                int len;
                while ((len = in.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, len);
                }
            }
        };

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "application/fhir+ndjson; charset=utf-8")
                .header("X-FHIR-Source", "hospital-system")
                .body(body);
    }

    /**
     * Get all resources of a specific type from hospital FHIR data
     */
    @GetMapping("/hospital/resource/{resourceType}")
    public ResponseEntity<StreamingResponseBody> getHospitalResourceType(@PathVariable String resourceType) throws IOException {
        Path dir = Paths.get(hospitalFhirDir);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            return ResponseEntity.notFound().build();
        }

        List<Path> matches = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, resourceType + "*.ndjson")) {
            for (Path p : ds) matches.add(p);
        }

        if (matches.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        StreamingResponseBody body = outputStream -> {
            byte[] buffer = new byte[8192];
            for (Path p : matches) {
                try (InputStream in = Files.newInputStream(p)) {
                    int len;
                    while ((len = in.read(buffer)) != -1) {
                        outputStream.write(buffer, 0, len);
                    }
                }
            }
        };

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "application/fhir+ndjson; charset=utf-8")
                .header("X-FHIR-Source", "hospital-system")
                .header("X-Resource-Type", resourceType)
                .body(body);
    }

    /**
     * Get all hospital FHIR data in one stream
     */
    @GetMapping("/hospital/all")
    public ResponseEntity<StreamingResponseBody> getAllHospitalData() throws IOException {
        Path dir = Paths.get(hospitalFhirDir);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            return ResponseEntity.notFound().build();
        }

        List<Path> allFiles = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.ndjson")) {
            for (Path p : ds) {
                // Exclude log files
                if (!p.getFileName().toString().equals("log.ndjson")) {
                    allFiles.add(p);
                }
            }
        }

        if (allFiles.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        StreamingResponseBody body = outputStream -> {
            byte[] buffer = new byte[8192];
            for (Path p : allFiles) {
                try (InputStream in = Files.newInputStream(p)) {
                    int len;
                    while ((len = in.read(buffer)) != -1) {
                        outputStream.write(buffer, 0, len);
                    }
                }
            }
        };

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "application/fhir+ndjson; charset=utf-8")
                .header("X-FHIR-Source", "hospital-system")
                .header("X-Export-Type", "complete")
                .body(body);
    }

    @GetMapping("/manifest")
    @ResponseBody
    public ResponseEntity<Map<String, Object>> manifest() throws IOException {
        Path dir = Paths.get(filesDir);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) {
            Map<String, Object> m = new HashMap<>();
            m.put("error", "files directory not found: " + filesDir);
            return ResponseEntity.badRequest().body(m);
        }

        List<String> files = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.ndjson")) {
            for (Path p : ds) files.add(p.getFileName().toString());
        }

        List<Map<String, String>> items = files.stream().map(f -> {
            Map<String, String> it = new HashMap<>();
            it.put("fileName", f);
            it.put("url", "/bulk/files/" + f);
            return it;
        }).collect(Collectors.toList());

        Map<String, Object> out = new HashMap<>();
        out.put("exportId", "synthea-export");
        out.put("files", items);
        return ResponseEntity.ok(out);
    }

    @GetMapping("/files/{filename:.+}")
    public ResponseEntity<StreamingResponseBody> getFile(@PathVariable String filename) throws IOException {
        Path dir = Paths.get(filesDir);
        Path file = dir.resolve(filename).normalize();
        if (!file.startsWith(dir) || !Files.exists(file)) {
            return ResponseEntity.notFound().build();
        }

        StreamingResponseBody body = outputStream -> {
            try (InputStream in = Files.newInputStream(file)) {
                byte[] buffer = new byte[8192];
                int len;
                while ((len = in.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, len);
                }
            }
        };

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "application/fhir+ndjson; charset=utf-8")
                .body(body);
    }

    @GetMapping("/resource/{resourceType}")
    public ResponseEntity<StreamingResponseBody> getResourceType(@PathVariable String resourceType) throws IOException {
        Path dir = Paths.get(filesDir);
        if (!Files.exists(dir) || !Files.isDirectory(dir)) return ResponseEntity.notFound().build();

        List<Path> matches = new ArrayList<>();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, resourceType + "*.ndjson")) {
            for (Path p : ds) matches.add(p);
        }

        if (matches.isEmpty()) return ResponseEntity.notFound().build();

        StreamingResponseBody body = outputStream -> {
            byte[] buffer = new byte[8192];
            for (Path p : matches) {
                try (InputStream in = Files.newInputStream(p)) {
                    int len;
                    while ((len = in.read(buffer)) != -1) {
                        outputStream.write(buffer, 0, len);
                    }
                }
            }
        };

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_TYPE, "application/fhir+ndjson; charset=utf-8")
                .body(body);
    }
}
