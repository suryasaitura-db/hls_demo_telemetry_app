#!/bin/bash
# Create database schema using SQL Serverless
# This script will be populated with actual table DDL after requirements are provided

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load utilities
source "$SCRIPT_DIR/utils.sh"

print_header "Creating Database Schema"

# Load configuration
CONFIG_FILE="$PROJECT_ROOT/config/workspace.yaml"
load_config "$CONFIG_FILE"

# Extract configuration values
PROFILE=$(get_yaml_value "$CONFIG_FILE" "profile")
HOST=$(get_yaml_value "$CONFIG_FILE" "host")
CATALOG=$(get_yaml_value "$CONFIG_FILE" "catalog")
SCHEMA=$(get_yaml_value "$CONFIG_FILE" "schema")
WAREHOUSE_ID=$(get_yaml_value "$CONFIG_FILE" "warehouse_id")

# Load token from .env
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

TOKEN=$DATABRICKS_TOKEN

print_info "Target: ${CATALOG}.${SCHEMA}"
print_info "Warehouse: ${WAREHOUSE_ID}"

# Create schema
print_info "Creating schema if not exists..."
execute_sql \
    "CREATE SCHEMA IF NOT EXISTS ${CATALOG}.${SCHEMA}" \
    "Create schema" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

print_success "Schema ${CATALOG}.${SCHEMA} is ready"

echo ""
print_info "Schema creation complete!"
print_info "Table definitions will be added after project requirements are finalized"
echo ""
