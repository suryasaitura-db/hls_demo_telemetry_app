#!/bin/bash
# Create all database views for Apps Telemetry
# This script executes all view creation queries from databricks_apps_telemetry_queries.sql

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load utilities
source "$SCRIPT_DIR/utils.sh"

print_header "Creating Database Views for Apps Telemetry"

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

# Read the SQL file and execute each CREATE VIEW statement
SQL_FILE="$PROJECT_ROOT/sql/databricks_apps_telemetry_queries.sql"

if [ ! -f "$SQL_FILE" ]; then
    print_error "SQL file not found: $SQL_FILE"
    exit 1
fi

print_info "Extracting and executing view creation queries..."
print_info "This may take a few minutes..."

# Extract and execute each CREATE OR REPLACE VIEW statement
# Using a temporary approach - execute the entire file line by line

while IFS= read -r line; do
    # Skip empty lines and comments
    if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*--.*$ ]]; then
        continue
    fi

    # Accumulate SQL statement
    sql_statement="$sql_statement$line"$'\n'

    # Check if we have a complete statement (ends with semicolon)
    if [[ "$line" =~ \;[[:space:]]*$ ]]; then
        # Check if this is a CREATE VIEW statement
        if [[ "$sql_statement" =~ CREATE[[:space:]]+OR[[:space:]]+REPLACE[[:space:]]+VIEW ]]; then
            # Extract view name for logging
            view_name=$(echo "$sql_statement" | grep -oP 'CREATE OR REPLACE VIEW \K[^\s]+' || echo "unknown")

            print_info "Creating view: $view_name"

            # Execute the statement
            execute_sql \
                "$sql_statement" \
                "Create view $view_name" \
                "$HOST" \
                "$TOKEN" \
                "$WAREHOUSE_ID"
        fi

        # Reset for next statement
        sql_statement=""
    fi
done < "$SQL_FILE"

echo ""
print_header "View Creation Complete"
echo ""
print_success "All views created successfully in hls_amer_catalog.apps_telemetry"
echo ""
print_info "You can now:"
print_info "  1. Run the Dash dashboard: python src/dash_app.py"
print_info "  2. Create AI/BI dashboard using the views"
echo ""
