#!/bin/bash
# Test SQL queries for HLS Demo Telemetry App
# Verifies all queries work correctly with SQL Serverless

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load utilities
source "$SCRIPT_DIR/utils.sh"

print_header "Testing SQL Queries for Apps Telemetry"

# Configuration - Load from workspace.yaml or environment
CONFIG_FILE="${CONFIG_FILE:-$PROJECT_ROOT/config/workspace.yaml}"

if [ -f "$CONFIG_FILE" ]; then
    HOST=$(get_yaml_value "$CONFIG_FILE" "host")
    WAREHOUSE_ID=$(get_yaml_value "$CONFIG_FILE" "warehouse_id")

    # Load token from .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
        TOKEN=$DATABRICKS_TOKEN
    else
        print_error ".env file not found. Please create it with DATABRICKS_TOKEN"
        exit 1
    fi
else
    print_error "Configuration file not found: $CONFIG_FILE"
    print_info "Please run ./deployment/setup.sh first"
    exit 1
fi

# Test 1: Check access to system.access.audit
print_info "Test 1: Verifying access to system.access.audit table"
execute_sql \
    "SELECT COUNT(*) as total_records FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY" \
    "Check audit table access" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 2: Create schema if not exists
print_info "Test 2: Creating apps_telemetry schema"
execute_sql \
    "CREATE SCHEMA IF NOT EXISTS hls_amer_catalog.apps_telemetry COMMENT 'Schema for Databricks Apps telemetry and analytics'" \
    "Create schema" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 3: Test KPI Summary Query
print_info "Test 3: Testing KPI Summary query"
execute_sql \
    "SELECT COUNT(DISTINCT user_identity.email) AS total_unique_users, COUNT(DISTINCT request_params.app_id) AS total_unique_apps, COUNT(*) AS total_interactions FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '30' DAY AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')" \
    "KPI Summary" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 4: Test DAU Trend Query
print_info "Test 4: Testing DAU Trend query"
execute_sql \
    "SELECT DATE(event_time) AS activity_date, COUNT(DISTINCT user_identity.email) AS daily_active_users, COUNT(*) AS total_clicks FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp') GROUP BY DATE(event_time) ORDER BY activity_date DESC LIMIT 5" \
    "DAU Trend" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 5: Test Top Apps Query
print_info "Test 5: Testing Top Apps query"
execute_sql \
    "SELECT COALESCE(request_params.app_name, 'Unknown App') AS app_name, COUNT(*) AS click_count, COUNT(DISTINCT user_identity.email) AS unique_users FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp') GROUP BY request_params.app_name ORDER BY click_count DESC LIMIT 5" \
    "Top Apps" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 6: Test Error Rate Query
print_info "Test 6: Testing Error Rate query"
execute_sql \
    "SELECT COUNT(*) AS total_requests, SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) AS failed_requests, ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percentage FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY" \
    "Error Rate" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

# Test 7: Test Usage Heatmap Query
print_info "Test 7: Testing Usage Heatmap query"
execute_sql \
    "SELECT DAYOFWEEK(event_time) AS day_of_week, HOUR(event_time) AS hour_of_day, COUNT(*) AS click_count FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '7' DAY AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp') GROUP BY DAYOFWEEK(event_time), HOUR(event_time) ORDER BY day_of_week, hour_of_day LIMIT 10" \
    "Usage Heatmap" \
    "$HOST" \
    "$TOKEN" \
    "$WAREHOUSE_ID"

echo ""
print_header "SQL Query Testing Complete"
echo ""
print_success "All queries executed successfully!"
print_info "Ready to proceed with view creation and dashboard deployment"
echo ""
