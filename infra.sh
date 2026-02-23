#!/bin/bash

# Usage: ./infra.sh [start|stop|restart] [all|service_name1 service_name2 ...]

ACTION=$1
shift
TARGETS="$@"

# Function to print usage
usage() {
    echo "Usage: $0 [start|stop|restart] [all|service1 service2 ...]"
    echo "Examples:"
    echo "  $0 start all"
    echo "  $0 stop postgres redis"
    echo "  $0 restart mongo"
    exit 1
}

# validate action
if [[ "$ACTION" != "start" && "$ACTION" != "stop" && "$ACTION" != "restart" ]]; then
    echo "Invalid action: '$ACTION'. Must be one of: start, stop, restart."
    usage
fi

# validate targets
if [ -z "$TARGETS" ]; then
    echo "Error: No target specified."
    usage
fi

# Resolve targets
if [[ "$TARGETS" == "all" ]]; then
    # Find all directories that contain a docker-compose file
    # We look for docker-compose.yml or docker-compose.yaml in immediate subdirectories
    TARGETS=$(find . -maxdepth 2 \( -name "docker-compose.yml" -o -name "docker-compose.yaml" \) -exec dirname {} \; | sort | uniq | sed 's|^\./||')
    echo "Managing ALL services: $TARGETS"
    echo "---------------------------------------------------"
fi

# Function to execute docker compose command
run_compose() {
    local service=$1
    local action=$2
    
    # Check if directory exists
    if [ ! -d "$service" ]; then
        echo "⚠️  Warning: Directory '$service' not found. Skipping."
        return
    fi
    
    # Find compose file
    local compose_file=""
    if [ -f "$service/docker-compose.yml" ]; then
        compose_file="$service/docker-compose.yml"
    elif [ -f "$service/docker-compose.yaml" ]; then
        compose_file="$service/docker-compose.yaml"
    else
        echo "⚠️  Warning: No docker-compose.y[a]ml found in '$service'. Skipping."
        return
    fi
    
    echo "🚀 [$action] $service..."
    
    case $action in
        start)
            sudo docker compose -f "$compose_file" up -d --build --force-recreate
            ;;
        stop)
            sudo docker compose -f "$compose_file" down
            ;;
        restart)
            sudo docker compose -f "$compose_file" down
            sudo docker compose -f "$compose_file" up -d --build --force-recreate
            ;;
    esac
}

# Main loop
for service in $TARGETS; do
    if [[ "$service" != "." ]]; then  # Ignore current directory if picked up by find
        run_compose "$service" "$ACTION"
    fi
done

echo "---------------------------------------------------"
echo "✅ Operation '$ACTION' completed."
