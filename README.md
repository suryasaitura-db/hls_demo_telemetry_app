# HLS Demo Telemetry App

A Databricks application for HLS telemetry data collection, analysis, and executive reporting with AI/BI dashboards and daily refresh capabilities.

## Features

- **Executive Reporting Dashboard**: AI/BI powered dashboards for executive insights
- **Daily Data Refresh**: Automated daily data refresh using Databricks Jobs
- **SQL Serverless**: All queries execute via SQL Serverless warehouse
- **Genie Integration**: Natural language querying capabilities
- **Multi-Workspace Support**: Easy deployment to any Databricks workspace
- **AI-Powered Analytics**: Integrated with Foundation Models for advanced analytics

## Project Structure

```
hls_demo_telemetry_app/
├── src/                      # Application source code
│   ├── app.py               # Main application (to be added)
│   ├── app.yaml             # Databricks App configuration
│   └── requirements.txt     # Python dependencies (to be added)
├── config/                   # Configuration files
│   └── workspace.yaml.template  # Workspace configuration template
├── deployment/               # Deployment scripts
│   ├── setup.sh             # Initial setup script
│   ├── create_schema.sh     # Database schema creation
│   ├── deploy.sh            # App deployment script
│   └── utils.sh             # Utility functions
├── sql/                      # SQL scripts
│   ├── create_tables.sql    # Table DDL
│   ├── sample_data.sql      # Sample data
│   └── queries.sql          # Analytical queries
├── dashboards/               # Dashboard configurations (to be added)
├── docs/                     # Documentation (to be added)
├── .env.template            # Environment variables template
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## Prerequisites

- Databricks workspace access
- Databricks CLI installed: `pip install databricks-cli`
- Python 3.8 or higher
- `jq` installed for JSON processing
- Unity Catalog enabled workspace
- SQL Serverless warehouse
- PAT token with appropriate permissions

## Quick Start - Deploy to Any Workspace

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/hls_demo_telemetry_app.git
cd hls_demo_telemetry_app
```

### Step 2: Configure Your Workspace

Run the interactive setup script:

```bash
./deployment/setup.sh
```

This will:
- Prompt for your workspace details (host, profile, catalog, etc.)
- Fetch available warehouses and endpoints
- Create `config/workspace.yaml` with your settings
- Create `.env` file with your credentials

**Manual Configuration (Alternative):**

If you prefer manual setup:

```bash
# Copy templates
cp config/workspace.yaml.template config/workspace.yaml
cp .env.template .env

# Edit files with your workspace details
nano config/workspace.yaml
nano .env
```

### Step 3: Create Database Schema

```bash
./deployment/create_schema.sh
```

This creates the Unity Catalog schema using SQL Serverless.

### Step 4: Deploy the Application

```bash
./deployment/deploy.sh
```

This will:
- Prepare app.yaml with your workspace settings
- Upload source code to workspace
- Create or update the Databricks App
- Deploy the app
- Display the app URL

### Step 5: Access Your App

The deployment script will output the app URL. Access it to start using the application.

## Deploying to Multiple Workspaces

This project is designed for easy multi-workspace deployment:

### Deploy to DEFAULT Workspace

```bash
# Run setup for DEFAULT workspace
./deployment/setup.sh
# (Select DEFAULT profile when prompted)

# Deploy
./deployment/create_schema.sh
./deployment/deploy.sh
```

### Deploy to Another Workspace (e.g., e2demofieldeng)

```bash
# Create a separate config for the second workspace
cp config/workspace.yaml config/e2demofieldeng_workspace.yaml

# Edit the new config
nano config/e2demofieldeng_workspace.yaml
# Update profile, host, catalog, etc. for e2demofieldeng

# Deploy using the new config
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/create_schema.sh
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/deploy.sh
```

## Configuration Reference

### workspace.yaml

```yaml
workspace:
  name: "DEFAULT"                                    # Workspace name
  host: "https://your-workspace.cloud.databricks.com"  # Workspace URL
  profile: "DEFAULT"                                 # Profile from ~/.databrickscfg
  catalog: "your_catalog"                           # Unity Catalog name
  schema: "telemetry"                               # Schema name
  warehouse_id: "your-warehouse-id"                 # SQL Warehouse ID
  serving_endpoint: "databricks-claude-sonnet-4-5"  # AI serving endpoint
  workspace_path: "/Users/your@email.com/databricks_apps/hls-demo-telemetry-app"

app:
  name: "hls-demo-telemetry-app"
  description: "HLS Demo Telemetry Application"
  compute_size: "MEDIUM"                            # SMALL, MEDIUM, or LARGE
  dashboard_id: ""                                  # Add after creating dashboard
  genie_space_id: ""                                # Add after creating Genie space
  refresh_schedule: "0 0 * * *"                     # Cron: daily at midnight
  data_refresh_job_id: ""                           # Add after creating job
  aggregation_job_id: ""                            # Add after creating job

features:
  enable_dashboard: true
  enable_genie: true
  enable_scheduled_refresh: true
  enable_executive_reports: true
```

## Databricks CLI Setup

Ensure your `~/.databrickscfg` has the correct profile:

```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi_your_token_here
```

## Development Workflow

1. **Make Changes**: Edit files in `src/`
2. **Test Locally**: (Testing framework to be added)
3. **Deploy**: Run `./deployment/deploy.sh`
4. **Verify**: Check app status and logs

## Daily Refresh Setup

After initial deployment, set up daily refresh:

1. Create Databricks Job for data refresh
2. Update `data_refresh_job_id` in workspace.yaml
3. Redeploy with `./deployment/deploy.sh`

## AI/BI Dashboard Setup

1. Create dashboard in Databricks
2. Note the dashboard ID from URL
3. Update `dashboard_id` in workspace.yaml
4. Update `DASHBOARD_URL` in src/app.yaml
5. Redeploy

## Genie Space Setup

1. Create Genie space in Databricks
2. Add all telemetry tables
3. Note the space ID from URL
4. Update `genie_space_id` in workspace.yaml
5. Redeploy

## Useful Commands

```bash
# Check app status
databricks --profile DEFAULT apps get hls-demo-telemetry-app

# View app logs
databricks --profile DEFAULT apps get hls-demo-telemetry-app | jq '.active_deployment.status'

# List tables
databricks --profile DEFAULT tables list your_catalog telemetry

# Delete app (if needed)
databricks --profile DEFAULT apps delete hls-demo-telemetry-app

# Redeploy
./deployment/deploy.sh
```

## Troubleshooting

### App Crashes After Deployment

Check the deployment status:
```bash
databricks --profile DEFAULT apps get hls-demo-telemetry-app --output json
```

Common issues:
- Invalid DASHBOARD_URL: Set to empty string if dashboard not created yet
- Missing serving endpoint: Verify endpoint exists
- Warehouse not available: Check warehouse ID

### Configuration Not Loading

Ensure:
- `config/workspace.yaml` exists (not the .template file)
- `.env` file exists with valid token
- Profile name matches your ~/.databrickscfg

### SQL Execution Fails

Verify:
- SQL Warehouse is running
- Warehouse ID is correct
- Catalog and schema exist
- Permissions are set correctly

## Security

- Never commit `.env` or `config/workspace.yaml` to git
- Use Databricks secrets for production deployments
- Rotate PAT tokens regularly
- Follow least-privilege principles

## Project Status

This project template is ready for development. The following components will be added based on detailed requirements:

- [ ] Application source code (app.py)
- [ ] Database table schemas
- [ ] Sample data
- [ ] Analytical queries
- [ ] Dashboard configurations
- [ ] Databricks Jobs
- [ ] Testing framework
- [ ] Additional documentation

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Databricks Apps documentation
3. Contact: suryasai.turaga@databricks.com

## License

Databricks Internal Use

---

**Ready to Build**: The project structure is ready. Provide your detailed requirements to populate the application logic, database schemas, and dashboards.
