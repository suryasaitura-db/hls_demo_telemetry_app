# Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the HLS Demo Telemetry App to any Databricks workspace.

## Prerequisites Checklist

Before starting deployment, ensure you have:

- [ ] Databricks workspace access with admin permissions
- [ ] Unity Catalog enabled
- [ ] SQL Serverless warehouse created
- [ ] Databricks CLI installed (`pip install databricks-cli`)
- [ ] Python 3.8+ installed
- [ ] `jq` command-line tool installed
- [ ] PAT token generated with appropriate scopes
- [ ] Git installed

## Step-by-Step Deployment

### 1. Get the Code

```bash
# Clone the repository
git clone https://github.com/your-username/hls_demo_telemetry_app.git
cd hls_demo_telemetry_app
```

### 2. Configure Databricks CLI

Add your workspace to `~/.databrickscfg`:

```bash
databricks configure --token
```

Enter:
- Databricks host: `https://your-workspace.cloud.databricks.com`
- Token: Your PAT token

Verify connection:
```bash
databricks workspace list /
```

### 3. Run Setup Script

```bash
./deployment/setup.sh
```

The script will prompt for:
- Workspace name (e.g., DEFAULT)
- Profile name from ~/.databrickscfg
- Workspace host URL
- Catalog name
- Schema name (default: telemetry)
- Your email address
- SQL Warehouse ID
- Serving endpoint name
- PAT token

### 4. Review Configuration

Check the generated files:

```bash
# Review workspace config
cat config/workspace.yaml

# Verify environment variables (be careful with tokens!)
cat .env
```

### 5. Create Database Schema

```bash
./deployment/create_schema.sh
```

This will:
- Connect to your workspace
- Create the catalog.schema if not exists
- Verify SQL Serverless connection

### 6. Deploy Application

```bash
./deployment/deploy.sh
```

This will:
1. Prepare app.yaml with your settings
2. Upload source code to workspace
3. Create Databricks App
4. Deploy the app
5. Wait for startup
6. Display app URL and status

### 7. Verify Deployment

```bash
databricks --profile YOUR_PROFILE apps get hls-demo-telemetry-app
```

Check that:
- App state is "RUNNING"
- URL is accessible
- No errors in status message

### 8. Access the Application

Visit the URL provided by the deployment script:
```
https://hls-demo-telemetry-app-XXXXX.cloud.databricksapps.com
```

## Deploying to Multiple Workspaces

### Scenario: Deploy to DEFAULT and e2demofieldeng

#### Deploy to DEFAULT Workspace

```bash
# Setup for DEFAULT
./deployment/setup.sh
# Select DEFAULT profile

# Deploy
./deployment/create_schema.sh
./deployment/deploy.sh
```

#### Deploy to e2demofieldeng Workspace

```bash
# Create separate config
cp config/workspace.yaml config/e2demofieldeng_workspace.yaml

# Edit config for e2demofieldeng
nano config/e2demofieldeng_workspace.yaml
# Update:
#   - profile: "e2demofieldeng"
#   - host: "https://e2-demo-field-eng.cloud.databricks.com"
#   - catalog: appropriate catalog for this workspace
#   - warehouse_id: warehouse in this workspace
#   - etc.

# Deploy to e2demofieldeng
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/create_schema.sh
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/deploy.sh
```

## Post-Deployment Setup

### Create AI/BI Dashboard

1. Navigate to Databricks SQL in your workspace
2. Create new dashboard
3. Add visualizations using queries from `sql/queries.sql`
4. Note the dashboard ID from URL
5. Update `config/workspace.yaml`:
   ```yaml
   app:
     dashboard_id: "your-dashboard-id"
   ```
6. Update `src/app.yaml`:
   ```yaml
   - name: "DASHBOARD_URL"
     value: "https://your-workspace.com/embed/dashboardsv3/your-dashboard-id"
   ```
7. Redeploy: `./deployment/deploy.sh`

### Create Genie Space

1. Navigate to Genie in Databricks
2. Create new space
3. Add tables from your catalog.schema
4. Configure instructions and sample questions
5. Note the space ID from URL
6. Update `config/workspace.yaml`:
   ```yaml
   app:
     genie_space_id: "your-genie-space-id"
   ```
7. Redeploy: `./deployment/deploy.sh`

### Setup Daily Refresh Job

1. Create Databricks Job:
   ```bash
   databricks --profile YOUR_PROFILE jobs create --json '{
     "name": "HLS Telemetry - Daily Refresh",
     "schedule": {
       "quartz_cron_expression": "0 0 0 * * ?",
       "timezone_id": "UTC"
     },
     "tasks": [{
       "task_key": "refresh_data",
       "sql_task": {
         "warehouse_id": "YOUR_WAREHOUSE_ID",
         "file": {
           "path": "/Workspace/Users/your@email.com/databricks_apps/hls-demo-telemetry-app/sql/refresh.sql"
         }
       }
     }]
   }'
   ```

2. Note the job ID
3. Update `config/workspace.yaml`:
   ```yaml
   app:
     data_refresh_job_id: "your-job-id"
   ```
4. Redeploy

## Updating the Application

When you make code changes:

```bash
# Make your changes in src/
# Then redeploy
./deployment/deploy.sh
```

The app will be updated with zero downtime.

## Rollback

To rollback to a previous version:

```bash
# List deployments
databricks --profile YOUR_PROFILE apps list-deployments hls-demo-telemetry-app

# Activate a previous deployment
databricks --profile YOUR_PROFILE apps activate-deployment hls-demo-telemetry-app DEPLOYMENT_ID
```

## Troubleshooting

### Issue: "App crashed after deployment"

**Solution:**
1. Check logs: `databricks apps get hls-demo-telemetry-app`
2. Common causes:
   - Invalid environment variables
   - Missing dependencies
   - Incorrect warehouse ID
3. Fix the issue and redeploy

### Issue: "Cannot connect to workspace"

**Solution:**
1. Verify ~/.databrickscfg has correct settings
2. Test connection: `databricks workspace list /`
3. Regenerate PAT token if needed
4. Run setup again: `./deployment/setup.sh`

### Issue: "Schema creation failed"

**Solution:**
1. Verify catalog exists: `databricks catalogs list`
2. Check permissions: User needs CREATE SCHEMA permission
3. Verify warehouse is running

### Issue: "SQL queries failing"

**Solution:**
1. Check warehouse status
2. Verify catalog.schema exists
3. Test query manually in SQL Editor
4. Check warehouse permissions

## Best Practices

1. **Version Control**: Always commit changes before deploying
2. **Testing**: Test in DEFAULT workspace before e2demofieldeng
3. **Backups**: Keep backups of workspace.yaml for each workspace
4. **Secrets**: Use Databricks secrets for production
5. **Monitoring**: Set up alerts for app status
6. **Documentation**: Update docs when making changes

## Maintenance

### Regular Tasks

- **Weekly**: Check app logs and performance
- **Monthly**: Review and rotate PAT tokens
- **Quarterly**: Update dependencies in requirements.txt

### Updating Dependencies

```bash
# Update requirements.txt
nano src/requirements.txt

# Redeploy
./deployment/deploy.sh
```

## Support

For issues:
1. Check troubleshooting section
2. Review app logs
3. Contact: suryasai.turaga@databricks.com

---

**Deployment Ready**: Follow these steps to deploy to any workspace in minutes!
