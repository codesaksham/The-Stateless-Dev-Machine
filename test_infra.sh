#!/bin/bash

# This script verifies that all infrastructure services are working correctly.
# Run this script with: sudo ./test_infra.sh

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES=("postgres" "mongo" "redis" "rabbitmq" "kafka" "pgadmin" "compass-mongo" "celery" "localstack" "mailpit" "keycloak" "dozzle" "traefik" "opensearch" "portainer" "vault" "sonarqube" "ngrok")

echo "==========================================="
echo "   Infrastructure Health Check Tool        "
echo "==========================================="

# Use 'docker compose' (v2) or 'docker-compose' (v1)
DOCKER_COMPOSE="docker compose"

for service in "${SERVICES[@]}"; do
    echo "[+] Starting $service..."
    cd "$BASE_DIR/$service" || continue
    $DOCKER_COMPOSE up -d --build --force-recreate > /dev/null 2>&1
done

echo "[*] Waiting 20 seconds for initialization..."
sleep 20

echo "--- Container Status ---"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "--- Functional Tests ---"

# 1. Postgres
echo -n "[ ] Postgres Multi-DB: "
docker exec postgres psql -U postgres -d main_db -c "\l" > /tmp/pg_dbs 2>&1
if grep -q "project1" /tmp/pg_dbs && grep -q "project2" /tmp/pg_dbs; then
    echo "OK (project1, project2 found)"
else
    echo "FAILED (Check docker logs postgres)"
fi

# 2. Mongo
echo -n "[ ] Mongo Multi-DB:    "
docker exec mongo mongosh --eval "db.getMongo().getDBNames()" > /tmp/mongo_dbs 2>&1
if grep -q "project1" /tmp/mongo_dbs && grep -q "project2" /tmp/mongo_dbs; then
    echo "OK (project1, project2 found)"
else
    echo "FAILED (Check docker logs mongo)"
fi

# 3. Redis
echo -n "[ ] Redis Sync:        "
if docker exec redis redis-cli -a redis ping 2>/dev/null | grep -q "PONG"; then
    echo "OK"
else
    echo "FAILED"
fi

# 4. RabbitMQ
echo -n "[ ] RabbitMQ Status:   "
if docker exec rabbitmq rabbitmq-diagnostics -q ping > /dev/null 2>&1; then
    echo "OK"
else
    echo "FAILED"
fi

# 5. Kafka
echo -n "[ ] Kafka KRaft:       "
if docker exec kafka kafka-topics.sh --bootstrap-server 127.0.0.1:9092 --list > /dev/null 2>&1; then
    echo "OK"
else
    echo "FAILED"
fi

echo ""
echo "--- Web UI Reachability ---"
check_url() {
    local name=$1
    local url=$2
    echo -n "[ ] $name: "
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|302\|401"; then
        echo "REACHABLE ($url)"
    else
        echo "UNREACHABLE"
    fi
}

check_url "pgAdmin" "http://localhost:15432"
check_url "Compass Web" "http://localhost:17017"
check_url "RabbitMQ Mgmt" "http://localhost:15672"
check_url "Celery Flower" "http://localhost:5555"

echo "==========================================="
