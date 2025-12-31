package com.project.proxyfhir.repository;

import com.project.proxyfhir.model.FhirResource;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface FhirResourceRepository extends JpaRepository<FhirResource, Long> {
    List<FhirResource> findByResourceType(String resourceType);
    Optional<FhirResource> findByResourceTypeAndResourceId(String resourceType, String resourceId);
}
