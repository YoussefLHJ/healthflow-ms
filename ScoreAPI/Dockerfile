# ==== Build stage ====
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /app

# Copy pom and sources
COPY pom.xml .
COPY src ./src

# Build the jar (skip tests for faster local builds; remove -DskipTests in CI)
RUN mvn clean package -DskipTests

# ==== Run stage ====
FROM eclipse-temurin:21-jre-jammy

WORKDIR /app

# Copy the built jar
COPY --from=build /app/target/*.jar app.jar

# Expose HTTP port
EXPOSE 8080

# JVM options can be tuned via JAVA_OPTS
ENV JAVA_OPTS=""

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
