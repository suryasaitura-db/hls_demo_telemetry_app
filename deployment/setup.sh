#!/bin/bash
# Initial setup script for HLS Demo Telemetry App
# This script prepares the configuration files for deployment

set -e

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load utilities
source "$SCRIPT_DIR/utils.sh"

print_header "HLS Demo Telemetry App - Initial Setup"

# Check if workspace.yaml exists
if [ -f "$PROJECT_ROOT/config/workspace.yaml" ]; then
    print_warning "workspace.yaml already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Setup cancelled"
        exit 0
    fi
fi

# Interactive setup
echo ""
print_info "Let's configure your workspace settings"
echo ""

# Get workspace details
read -p "Workspace name (e.g., DEFAULT or e2demofieldeng): " WORKSPACE_NAME
read -p "Databricks profile name from ~/.databrickscfg: " PROFILE_NAME
read -p "Workspace host (e.g., https://your-workspace.cloud.databricks.com): " WORKSPACE_HOST
read -p "Unity Catalog name: " CATALOG_NAME
read -p "Schema name [telemetry]: " SCHEMA_NAME
SCHEMA_NAME=${SCHEMA_NAME:-telemetry}
read -p "Your email for workspace path: " USER_EMAIL

echo ""
print_info "Fetching available resources from workspace..."

# Verify connection
check_databricks_cli
verify_workspace "$PROFILE_NAME"

# Get warehouse ID
print_info "Fetching available SQL warehouses..."
unset DATABRICKS_HOST DATABRICKS_TOKEN
WAREHOUSES=$(databricks --profile "$PROFILE_NAME" warehouses list --output json 2>/dev/null || echo "[]")

if [ "$WAREHOUSES" != "[]" ]; then
    echo "Available warehouses:"
    echo "$WAREHOUSES" | python3 -c "
import sys, json
warehouses = json.load(sys.stdin)
for w in warehouses.get('warehouses', []):
    print(f\"  - {w['name']} (ID: {w['id']})\")
"
    echo ""
fi

read -p "SQL Warehouse ID: " WAREHOUSE_ID

# Get serving endpoint
print_info "Fetching available serving endpoints..."
ENDPOINTS=$(databricks --profile "$PROFILE_NAME" serving-endpoints list --output json 2>/dev/null || echo "[]")

if [ "$ENDPOINTS" != "[]" ]; then
    echo "Available endpoints:"
    echo "$ENDPOINTS" | python3 -c "
import sys, json
endpoints = json.load(sys.stdin)
for e in endpoints.get('endpoints', []):
    print(f\"  - {e['name']}\")
" 2>/dev/null || echo "  (Unable to parse endpoints)"
    echo ""
fi

read -p "Serving endpoint name: " SERVING_ENDPOINT

# Create workspace.yaml
print_info "Creating workspace.yaml..."

cat > "$PROJECT_ROOT/config/workspace.yaml" <<EOF
# Workspace Configuration
# Generated on $(date)

workspace:
  name: "$WORKSPACE_NAME"
  host: "$WORKSPACE_HOST"
  profile: "$PROFILE_NAME"

  catalog: "$CATALOG_NAME"
  schema: "$SCHEMA_NAME"

  warehouse_id: "$WAREHOUSE_ID"
  serving_endpoint: "$SERVING_ENDPOINT"

  workspace_path: "/Users/${USER_EMAIL}/databricks_apps/hls-demo-telemetry-app"

app:
  name: "hls-demo-telemetry-app"
  description: "HLS Demo Telemetry Application for Executive Reporting"
  compute_size: "MEDIUM"

  dashboard_id: ""
  genie_space_id: ""

  refresh_schedule: "0 0 * * *"

  data_refresh_job_id: ""
  aggregation_job_id: ""

features:
  enable_dashboard: true
  enable_genie: true
  enable_scheduled_refresh: true
  enable_executive_reports: true
EOF

print_success "workspace.yaml created successfully"

# Create .env file
print_info "Creating .env file..."

read -p "Databricks PAT token: " -s DATABRICKS_TOKEN
echo ""

cat > "$PROJECT_ROOT/.env" <<EOF
# Environment Variables
# Generated on $(date)

DATABRICKS_HOST=$WORKSPACE_HOST
DATABRICKS_TOKEN=$DATABRICKS_TOKEN

DATABRICKS_WAREHOUSE_ID=$WAREHOUSE_ID
ANALYTICS_CATALOG=$CATALOG_NAME
ANALYTICS_SCHEMA=$SCHEMA_NAME
SERVING_ENDPOINT=$SERVING_ENDPOINT

APP_NAME=hls-demo-telemetry-app
DASHBOARD_URL=
GENIE_SPACE_ID=

LOG_LEVEL=INFO
EOF

print_success ".env file created successfully"

echo ""
print_header "Setup Complete!"
echo ""
print_success "Configuration files created:"
print_info "  - config/workspace.yaml"
print_info "  - .env"
echo ""
print_info "Next steps:"
print_info "  1. Review config/workspace.yaml"
print_info "  2. Run: ./deployment/create_schema.sh to create database schema"
print_info "  3. Run: ./deployment/deploy.sh to deploy the app"
echo ""
