#!/bin/bash
# Deploy HLS Demo Telemetry App to Databricks workspace

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load utilities
source "$SCRIPT_DIR/utils.sh"

print_header "Deploying HLS Demo Telemetry App"

# Load configuration
CONFIG_FILE="$PROJECT_ROOT/config/workspace.yaml"
load_config "$CONFIG_FILE"

# Extract configuration values
PROFILE=$(get_yaml_value "$CONFIG_FILE" "profile")
CATALOG=$(get_yaml_value "$CONFIG_FILE" "catalog")
SCHEMA=$(get_yaml_value "$CONFIG_FILE" "schema")
WAREHOUSE_ID=$(get_yaml_value "$CONFIG_FILE" "warehouse_id")
SERVING_ENDPOINT=$(get_yaml_value "$CONFIG_FILE" "serving_endpoint")
WORKSPACE_PATH=$(get_yaml_value "$CONFIG_FILE" "workspace_path")
APP_NAME=$(get_yaml_value "$CONFIG_FILE" "name")

print_info "Deploying to workspace using profile: $PROFILE"
print_info "Target path: $WORKSPACE_PATH"

# Verify workspace connection
check_databricks_cli
verify_workspace "$PROFILE"

# Step 1: Prepare app.yaml with actual values
print_info "Preparing app.yaml with workspace configuration..."

TEMP_APP_YAML="$PROJECT_ROOT/src/app_deployed.yaml"
replace_placeholders \
    "$PROJECT_ROOT/src/app.yaml" \
    "$CATALOG" \
    "$SCHEMA" \
    "$WAREHOUSE_ID" \
    "$SERVING_ENDPOINT" > "$TEMP_APP_YAML"

print_success "app.yaml prepared"

# Step 2: Upload source code to workspace
print_info "Uploading source code to workspace..."

cd "$PROJECT_ROOT/src"
unset DATABRICKS_HOST DATABRICKS_TOKEN
databricks --profile "$PROFILE" workspace import-dir ./ "$WORKSPACE_PATH" --overwrite

print_success "Source code uploaded"

# Step 3: Upload the prepared app.yaml
print_info "Uploading app.yaml..."

databricks --profile "$PROFILE" workspace import-dir ./ "$WORKSPACE_PATH" --overwrite

# Clean up temp file
rm -f "$TEMP_APP_YAML"

print_success "app.yaml uploaded"

# Step 4: Create or update the app
print_info "Checking if app exists..."

APP_EXISTS=$(databricks --profile "$PROFILE" apps get "$APP_NAME" --output json 2>/dev/null || echo "null")

if [ "$APP_EXISTS" = "null" ]; then
    print_info "Creating new app..."

    databricks --profile "$PROFILE" apps create --json "{
        \"name\": \"$APP_NAME\",
        \"description\": \"HLS Demo Telemetry Application for Executive Reporting\",
        \"source_code_path\": \"$WORKSPACE_PATH\"
    }"

    print_success "App created successfully"
else
    print_info "App already exists, will deploy update"
fi

# Step 5: Deploy the app
print_info "Deploying app..."

databricks --profile "$PROFILE" apps deploy "$APP_NAME" \
    --source-code-path "$WORKSPACE_PATH" \
    --mode SNAPSHOT

print_success "Deployment initiated"

# Step 6: Wait and check status
print_info "Waiting for app to start (30 seconds)..."
sleep 30

APP_STATUS=$(databricks --profile "$PROFILE" apps get "$APP_NAME" --output json)

STATE=$(echo "$APP_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('app_status', {}).get('state', 'UNKNOWN'))")
URL=$(echo "$APP_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('url', 'N/A'))")

echo ""
print_header "Deployment Summary"
echo ""
print_info "App Name: $APP_NAME"
print_info "App State: $STATE"
print_info "App URL: $URL"
echo ""

if [ "$STATE" = "RUNNING" ]; then
    print_success "App is running successfully!"
    echo ""
    print_info "Access your app at: $URL"
elif [ "$STATE" = "CRASHED" ] || [ "$STATE" = "FAILED" ]; then
    print_error "App deployment failed"
    print_info "Check logs with: databricks apps get $APP_NAME"
else
    print_warning "App is in state: $STATE"
    print_info "Check status with: databricks apps get $APP_NAME"
fi

echo ""
