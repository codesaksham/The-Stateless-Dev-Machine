# Local Development Infrastructure

This repository contains Docker Compose configurations for running essential infrastructure services locally. It provides an isolated, containerized environment for dependent services required during application development.

## Included Services

This infrastructure stack includes the following services, each housed in its respective directory:

- **PostgreSQL**: Relational database (`postgres/`)
- **pgAdmin**: Web-based administration tool for PostgreSQL (`pgadmin/`)
- **MongoDB**: NoSQL database (`mongo/`)
- **MongoDB Compass**: Graphical overview of MongoDB data (`compass-mongo/`)
- **Redis**: In-memory data structure store, used as a database, cache, and message broker (`redis/`)
- **RabbitMQ**: Message broker (`rabbitmq/`)
- **Kafka**: Distributed event streaming platform (`kafka/`)
- **Celery**: Distributed task queue (`celery/`)
- **MinIO**: High-performance, S3-compatible object storage (`minio/`)
- **LocalStack**: AWS Cloud mock (`localstack/`)
- **MailPit**: Email testing and SMTP mock (`mailpit/`)
- **Keycloak**: Identity and Access Management (`keycloak/`)
- **Dozzle**: Real-time web-based Docker log viewer (`dozzle/`)
- **Traefik**: Modern reverse proxy and load balancer (`traefik/`)
- **OpenSearch**: Search and analytics engine (`opensearch/`)
- **Portainer**: Graphical container management (`portainer/`)
- **SigNoz**: Open-source Observability and tracing (`signoz/`)
- **SonarQube**: Continuous inspection of code quality and security (`sonarqube/`)
- **Vault**: Secrets and identity management (`vault/`)
- **Ngrok**: Ingress to local applications (`ngrok/`)
- **Hoppscotch**: API development ecosystem (`postwoman-hoppscotch/`)
- **Dashy**: Centralized dashboard for all services (`dashy/`)
- **Gitea**: Lightweight self-hosted Git service with CI/CD (`gitea/`)
- **Locust**: Python-based performance testing (`locust/`)
- **Pyroscope**: Continuous profiling for Python applications (`pyroscope/`)
- **Redpanda Console**: Modern UI for Kafka topics and clusters (`redpanda-console/`)
- **Semaphore**: Modern UI for Ansible automation (`semaphore/`)
- **Trivy**: Vulnerability scanner for containers and dependencies (`trivy/`)
- **DefectDojo**: Vulnerability management and security dashboard (`defectdojo/`)
- **Private Meeting Chatroom**: Real-time WebSocket chat application (`private-meeting-chatroom/`)

## Usage

You can start and manage the services using the provided bash scripts (`infra.sh` or `test_infra.sh`) or manually via Docker Compose within each directory.

Navigate to the directory of the service you want to run:

```bash
cd postgres
docker-compose up -d
```

Make sure Docker and Docker Compose are installed and running on your system before bringing up the services.
