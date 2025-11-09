#!/bin/bash
# Utility functions for deployment scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Load workspace configuration
load_config() {
    local config_file=$1

    if [ ! -f "$config_file" ]; then
        print_error "Configuration file not found: $config_file"
        print_info "Please copy config/workspace.yaml.template to $config_file and fill in your details"
        exit 1
    fi

    print_success "Configuration loaded from $config_file"
}

# Parse YAML (simple key-value extraction)
get_yaml_value() {
    local file=$1
    local key=$2
    grep "^  $key:" "$file" | sed 's/.*: "\(.*\)"/\1/' | tr -d '"'
}

# Execute SQL via Serverless
execute_sql() {
    local sql=$1
    local description=$2
    local host=$3
    local token=$4
    local warehouse_id=$5

    print_info "Executing: $description"

    response=$(curl -s -X POST "${host}/api/2.0/sql/statements/" \
        -H "Authorization: Bearer ${token}" \
        -H "Content-Type: application/json" \
        -d "{
            \"warehouse_id\": \"${warehouse_id}\",
            \"statement\": $(echo "$sql" | jq -Rs .),
            \"wait_timeout\": \"50s\"
        }")

    status=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', {}).get('state', 'UNKNOWN'))" 2>/dev/null || echo "ERROR")

    if [ "$status" = "SUCCEEDED" ]; then
        print_success "$description - SUCCESS"
        return 0
    else
        print_error "$description - FAILED"
        echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', {}).get('error', {}))" 2>/dev/null
        return 1
    fi
}

# Check if databricks CLI is installed
check_databricks_cli() {
    if ! command -v databricks &> /dev/null; then
        print_error "Databricks CLI not found"
        print_info "Install with: pip install databricks-cli"
        exit 1
    fi
    print_success "Databricks CLI found"
}

# Verify workspace connection
verify_workspace() {
    local profile=$1

    print_info "Verifying connection to workspace using profile: $profile"

    if unset DATABRICKS_HOST DATABRICKS_TOKEN && databricks --profile "$profile" workspace list / --output json > /dev/null 2>&1; then
        print_success "Successfully connected to workspace"
        return 0
    else
        print_error "Failed to connect to workspace"
        print_info "Please check your ~/.databrickscfg file and profile name"
        exit 1
    fi
}

# Replace placeholders in file
replace_placeholders() {
    local file=$1
    local catalog=$2
    local schema=$3
    local warehouse_id=$4
    local serving_endpoint=$5

    sed -e "s/{{CATALOG}}/$catalog/g" \
        -e "s/{{SCHEMA}}/$schema/g" \
        -e "s/{{WAREHOUSE_ID}}/$warehouse_id/g" \
        -e "s/{{SERVING_ENDPOINT}}/$serving_endpoint/g" \
        "$file"
}
