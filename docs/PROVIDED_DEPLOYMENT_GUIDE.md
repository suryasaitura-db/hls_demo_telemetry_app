# Databricks Apps Telemetry - Deployment Guide

## 🚀 Complete Deployment Instructions

This guide covers deploying both the Dash web application and AI/BI dashboard in various environments.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Local Development Deployment](#local-development-deployment)
3. [Production Deployment - Dash App](#production-deployment-dash-app)
4. [AI/BI Dashboard Deployment](#aibi-dashboard-deployment)
5. [Cloud Deployment Options](#cloud-deployment-options)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## 📋 Pre-Deployment Checklist

### Required Access & Permissions

- [ ] Databricks workspace access
- [ ] SQL Warehouse created and running
- [ ] Personal Access Token or Service Principal credentials
- [ ] Permissions to read `system.access.audit` table
- [ ] Permissions to create schema and views
- [ ] (For AI/BI) Permission to create dashboards

### Infrastructure Requirements

#### For Dash App:
- [ ] Server with Python 3.9+ installed
- [ ] 4GB RAM minimum (8GB recommended)
- [ ] Network connectivity to Databricks
- [ ] Port 8050 open (or custom port)
- [ ] SSL certificate (for production HTTPS)

#### For AI/BI Dashboard:
- [ ] Databricks workspace with AI/BI enabled
- [ ] SQL Warehouse (Pro tier recommended)
- [ ] Email/Slack for alerts (optional)

### Files Needed

- [ ] `requirements.txt` - Python dependencies
- [ ] `.env` file - Environment variables (created from template)
- [ ] `setup_database.sql` - Database initialization
- [ ] `databricks_apps_telemetry_queries.sql` - SQL queries
- [ ] `dash_app.py` - Dash application (for web app)
- [ ] `aibi_dashboard_config.yaml` - Dashboard config (for AI/BI)

---

## 🏠 Local Development Deployment

### Step 1: Setup Environment

```bash
# Create project directory
mkdir databricks-apps-telemetry
cd databricks-apps-telemetry

# Copy all project files here
# (Download from repository or use provided files)

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import dash; import databricks.sql; print('✓ Dependencies installed')"
```

### Step 3: Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit .env file
nano .env  # or your preferred editor
```

**Fill in your credentials:**
```env
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456
DATABRICKS_ACCESS_TOKEN=dapiXXXXXXXXXXXXXXXXXXXXXXXX
```

**To get these values:**
1. **Hostname**: Workspace URL without https://
2. **HTTP Path**: SQL Warehouse → Connection Details → HTTP Path
3. **Token**: User Settings → Developer → Access Tokens → Generate New Token

### Step 4: Initialize Database

```bash
# Option A: Using Databricks SQL CLI
databricks-sql -f setup_database.sql

# Option B: Copy/paste in Databricks SQL Editor
# 1. Open Databricks SQL Editor
# 2. Copy contents of setup_database.sql
# 3. Execute in SQL Editor
```

**Verify setup:**
```sql
-- Run in Databricks SQL Editor
USE apps_telemetry;
SHOW VIEWS;

-- Should show all views like:
-- widget_dau_trend
-- widget_top_apps
-- widget_user_segmentation
-- etc.
```

### Step 5: Run Application

```bash
# Start Dash app
python dash_app.py

# You should see:
# Dash is running on http://0.0.0.0:8050/
# * Serving Flask app 'dash_app'
# * Debug mode: on
```

### Step 6: Access Dashboard

Open browser and navigate to:
```
http://localhost:8050
```

You should see:
- ✓ KPI cards at top with metrics
- ✓ Charts loading with data
- ✓ Filters working
- ✓ No error messages

---

## 🌐 Production Deployment - Dash App

### Option 1: Deploy with Gunicorn (Recommended)

#### Step 1: Install Gunicorn

```bash
pip install gunicorn
```

#### Step 2: Test Gunicorn Locally

```bash
# Run with 4 worker processes
gunicorn dash_app:server \
  --bind 0.0.0.0:8050 \
  --workers 4 \
  --threads 2 \
  --timeout 120 \
  --log-level info
```

#### Step 3: Create Systemd Service (Linux)

Create `/etc/systemd/system/databricks-telemetry.service`:

```ini
[Unit]
Description=Databricks Apps Telemetry Dashboard
After=network.target

[Service]
User=dashboarduser
Group=dashboarduser
WorkingDirectory=/opt/databricks-telemetry
Environment="PATH=/opt/databricks-telemetry/venv/bin"
EnvironmentFile=/opt/databricks-telemetry/.env
ExecStart=/opt/databricks-telemetry/venv/bin/gunicorn \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /var/log/databricks-telemetry/access.log \
    --error-logfile /var/log/databricks-telemetry/error.log \
    dash_app:server

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 4: Start Service

```bash
# Create log directory
sudo mkdir -p /var/log/databricks-telemetry
sudo chown dashboarduser:dashboarduser /var/log/databricks-telemetry

# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start databricks-telemetry

# Enable auto-start on boot
sudo systemctl enable databricks-telemetry

# Check status
sudo systemctl status databricks-telemetry

# View logs
sudo journalctl -u databricks-telemetry -f
```

### Option 2: Deploy with Docker

#### Step 1: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY dash_app.py .
COPY .env .

# Expose port
EXPOSE 8050

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "--workers", "4", "--timeout", "120", "dash_app:server"]
```

#### Step 2: Build and Run

```bash
# Build image
docker build -t databricks-telemetry:latest .

# Run container
docker run -d \
  --name databricks-telemetry \
  -p 8050:8050 \
  --env-file .env \
  --restart unless-stopped \
  databricks-telemetry:latest

# Check logs
docker logs -f databricks-telemetry

# Stop container
docker stop databricks-telemetry
```

### Option 3: Deploy with Nginx Reverse Proxy

#### Step 1: Configure Nginx

Create `/etc/nginx/sites-available/databricks-telemetry`:

```nginx
upstream dash_app {
    server 127.0.0.1:8050;
}

server {
    listen 80;
    server_name telemetry.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name telemetry.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/telemetry.crt;
    ssl_certificate_key /etc/ssl/private/telemetry.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/telemetry-access.log;
    error_log /var/log/nginx/telemetry-error.log;

    location / {
        proxy_pass http://dash_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}
```

#### Step 2: Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/databricks-telemetry /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 📊 AI/BI Dashboard Deployment

### Step 1: Prepare Database Views

```bash
# Run all view creation queries in Databricks SQL Editor
# Copy/paste contents of: databricks_apps_telemetry_queries.sql

# Verify views created
USE apps_telemetry;
SHOW VIEWS;
```

### Step 2: Create Dashboard

1. Log into Databricks workspace
2. Navigate to **SQL** → **Dashboards**
3. Click **Create Dashboard**
4. Name: "Apps Telemetry Executive Dashboard"

### Step 3: Add Global Filters

#### Filter 1: Date Range
```
1. Click "Add Filter"
2. Name: "date_range"
3. Type: Date Range
4. Default: Last 30 Days
5. Apply to: All widgets
```

#### Filter 2: App Filter
```
1. Click "Add Filter"
2. Name: "app_filter"
3. Type: Multi-select dropdown
4. Query: SELECT DISTINCT request_params.app_name 
         FROM system.access.audit 
         WHERE service_name = 'apps'
5. Default: All
```

### Step 4: Create KPI Cards

For each KPI (4 total):

```
1. Click "Add Visualization"
2. Type: Counter
3. Enter query (from aibi_dashboard_config.yaml)
4. Configure:
   - Title
   - Format (number/percentage)
   - Icon
   - Color
5. Position in grid (1 row, 4 columns)
```

### Step 5: Create Charts

For each chart (6 total):

```
1. Click "Add Visualization"
2. Select chart type (line/bar/heatmap/area/combo)
3. Query: SELECT * FROM apps_telemetry.widget_[name]
4. Configure axes, colors, formatting
5. Add title and subtitle
6. Position in grid
```

**Chart Configuration Reference:**
- DAU Trend: Line chart, dual Y-axis
- Top Apps: Horizontal bar chart
- Usage Heatmap: Heatmap, RdYlGn palette
- User Cohorts: Stacked area chart
- Error Monitoring: Combo chart (bars + line)

### Step 6: Create User Table

```
1. Click "Add Visualization"
2. Type: Table
3. Query: SELECT * FROM apps_telemetry.widget_user_segmentation
4. Configure columns:
   - Format numbers, dates
   - Add conditional formatting for segments
   - Set column widths
5. Enable:
   - Sorting
   - Search
   - Pagination (25 rows/page)
```

### Step 7: Configure Alerts

#### Alert 1: High Error Rate
```
1. Click "Alerts" tab
2. "Create Alert"
3. Name: "High Error Rate"
4. Query: SELECT * FROM apps_telemetry.high_error_rate_apps 
         WHERE error_rate_percentage > 5
5. Schedule: Every 30 minutes
6. Destination: Email
7. Recipients: platform-team@company.com
8. Template: "⚠️ Error rate {error_rate_percentage}% for {app_name}"
```

#### Alert 2: Usage Anomaly
```
1. "Create Alert"
2. Name: "Usage Anomaly Detected"
3. Query: SELECT * FROM apps_telemetry.anomaly_detection 
         WHERE anomaly_status = 'Anomaly Detected'
4. Schedule: Daily at 8 AM
5. Destination: Email
6. Recipients: analytics-team@company.com
```

### Step 8: Configure Scheduled Exports

#### Weekly Executive Report
```
1. Click "Schedules" tab
2. "Create Schedule"
3. Name: "Weekly Apps Summary"
4. Query: SELECT * FROM apps_telemetry.weekly_executive_summary
5. Format: Excel (.xlsx)
6. Schedule: Every Monday at 7 AM
7. Recipients: executives@company.com
```

### Step 9: Set Permissions

```
1. Click "Share" button
2. Add permissions:
   - Viewers: all-employees@company.com (Can View)
   - Editors: analytics-team@company.com (Can Edit)
   - Admins: data-engineering@company.com (Can Manage)
3. Save
```

### Step 10: Publish Dashboard

```
1. Click "Publish"
2. Review layout on mobile preview
3. Test all filters
4. Verify all charts load
5. Publish
6. Copy shareable link
7. Distribute to stakeholders
```

---

## ☁️ Cloud Deployment Options

### AWS Deployment

#### Option 1: EC2 Instance

```bash
# Launch EC2 instance (t3.medium recommended)
# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clone repository
git clone <repo-url>
cd databricks-apps-telemetry

# Setup as per local deployment steps
# Configure systemd service
# Setup Nginx with Let's Encrypt for SSL
```

#### Option 2: ECS/Fargate

```yaml
# task-definition.json
{
  "family": "databricks-telemetry",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "dashboard",
      "image": "your-account.dkr.ecr.region.amazonaws.com/databricks-telemetry:latest",
      "portMappings": [
        {
          "containerPort": 8050,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABRICKS_SERVER_HOSTNAME", "value": "workspace.cloud.databricks.com"},
        {"name": "DATABRICKS_HTTP_PATH", "value": "/sql/1.0/warehouses/xxx"}
      ],
      "secrets": [
        {"name": "DATABRICKS_ACCESS_TOKEN", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/databricks-telemetry",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Azure Deployment

#### Azure App Service

```bash
# Create App Service
az webapp up \
  --name databricks-telemetry \
  --resource-group myResourceGroup \
  --runtime "PYTHON:3.11" \
  --sku B1

# Configure environment variables
az webapp config appsettings set \
  --name databricks-telemetry \
  --resource-group myResourceGroup \
  --settings \
    DATABRICKS_SERVER_HOSTNAME=workspace.azuredatabricks.net \
    DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxx

# Deploy code
az webapp deployment source config-zip \
  --name databricks-telemetry \
  --resource-group myResourceGroup \
  --src app.zip
```

### GCP Deployment

#### Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/databricks-telemetry

# Deploy to Cloud Run
gcloud run deploy databricks-telemetry \
  --image gcr.io/PROJECT-ID/databricks-telemetry \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABRICKS_SERVER_HOSTNAME=workspace.gcp.databricks.com \
  --set-secrets DATABRICKS_ACCESS_TOKEN=databricks-token:latest
```

---

## 📊 Monitoring & Maintenance

### Application Monitoring

#### Health Checks

```python
# Add to dash_app.py
@app.server.route('/health')
def health_check():
    try:
        # Test database connection
        db_conn.execute_query("SELECT 1")
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503
```

#### Monitoring Metrics

Key metrics to track:
- Response time (target: <2s)
- Error rate (target: <1%)
- Memory usage (alert if >80%)
- CPU usage (alert if >70%)
- Active connections
- Query execution time

#### Logging

```python
# Configure logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/databricks-telemetry/app.log'),
        logging.StreamHandler()
    ]
)
```

### Database Maintenance

#### Regular Tasks (Weekly)

```sql
-- Optimize audit table partitions
OPTIMIZE system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '90' DAY;

-- Update table statistics
ANALYZE TABLE system.access.audit COMPUTE STATISTICS;

-- Refresh materialized views (if using)
REFRESH MATERIALIZED VIEW apps_telemetry.kpi_summary_mv;
```

#### Data Retention

```sql
-- Archive old data (keep 90 days detailed, 2 years aggregated)
CREATE TABLE apps_telemetry.historical_metrics AS
SELECT
  DATE_TRUNC('MONTH', event_time) AS month,
  COUNT(DISTINCT user_identity.email) AS monthly_users,
  COUNT(*) AS total_interactions
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date < CURRENT_DATE - INTERVAL '90' DAY
GROUP BY DATE_TRUNC('MONTH', event_time);
```

### Backup & Recovery

```bash
# Backup configuration files
tar -czf databricks-telemetry-backup-$(date +%Y%m%d).tar.gz \
  dash_app.py \
  .env \
  requirements.txt \
  setup_database.sql

# Backup to S3/Azure Blob/GCS
aws s3 cp databricks-telemetry-backup-*.tar.gz s3://my-backups/
```

### Security Updates

```bash
# Check for security updates monthly
pip list --outdated

# Update dependencies
pip install --upgrade -r requirements.txt

# Audit for vulnerabilities
pip-audit
```

---

## 🔧 Troubleshooting

### Common Production Issues

#### High Memory Usage

**Symptoms:**
- Dashboard becomes slow
- Out of memory errors

**Solutions:**
```python
# Reduce data in memory
# In dash_app.py, limit query results:
query = f"""
SELECT * FROM apps_telemetry.widget_user_segmentation
LIMIT 100  -- Add limit
"""

# Clear caches periodically
# Restart service if memory exceeds threshold
```

#### Slow Query Performance

**Symptoms:**
- Charts take >10s to load
- Timeouts

**Solutions:**
```sql
-- Create materialized views
CREATE MATERIALIZED VIEW apps_telemetry.kpi_summary_mv AS
SELECT * FROM apps_telemetry.widget_kpi_summary;

-- Schedule refresh
CREATE JOB refresh_kpi_mv
SCHEDULE CRON '0 */6 * * *'
AS REFRESH MATERIALIZED VIEW apps_telemetry.kpi_summary_mv;
```

#### Connection Timeouts

**Symptoms:**
- "Connection timed out" errors
- Intermittent failures

**Solutions:**
```python
# Implement retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def execute_query_with_retry(query):
    return db_conn.execute_query(query)
```

---

## ✅ Post-Deployment Checklist

### Functional Testing

- [ ] All KPI cards display correct values
- [ ] All charts render without errors
- [ ] Filters update all visualizations
- [ ] Tables sort correctly
- [ ] Auto-refresh works
- [ ] Manual refresh button works
- [ ] Tooltips display on hover
- [ ] Export functionality works

### Performance Testing

- [ ] Initial load time <5 seconds
- [ ] Chart refresh time <2 seconds
- [ ] Memory usage stable over 24 hours
- [ ] No memory leaks detected
- [ ] Concurrent user testing (10+ users)

### Security Testing

- [ ] HTTPS enabled (production)
- [ ] Credentials not in source code
- [ ] Access tokens secure
- [ ] Network access restricted
- [ ] Audit logging enabled
- [ ] Error messages don't leak sensitive info

### Monitoring Setup

- [ ] Health check endpoint configured
- [ ] Logging to centralized system
- [ ] Alerts configured for errors
- [ ] Performance metrics tracked
- [ ] Uptime monitoring enabled

### Documentation

- [ ] Deployment notes recorded
- [ ] Configuration documented
- [ ] Runbook created
- [ ] Team trained on usage
- [ ] Support contacts defined

---

## 📞 Support & Escalation

### Issue Severity Levels

**Critical (P0):**
- Dashboard completely down
- Security breach
- Data corruption

**High (P1):**
- Major features broken
- Performance severely degraded
- Alerts not working

**Medium (P2):**
- Minor features broken
- Some visualizations incorrect
- Slow performance

**Low (P3):**
- Cosmetic issues
- Enhancement requests

### Contact Information

- **Dashboard Issues**: your-team@company.com
- **Databricks Support**: Databricks customer success team
- **On-Call**: Check PagerDuty rotation

---

## 🎉 Success Criteria

Deployment is successful when:

1. ✅ Dashboard accessible to all users
2. ✅ All visualizations display correctly
3. ✅ Performance meets SLA (<5s load time)
4. ✅ Alerts delivering successfully
5. ✅ Scheduled exports running
6. ✅ Zero critical errors in 24 hours
7. ✅ Positive user feedback
8. ✅ Documentation complete
9. ✅ Team trained
10. ✅ Monitoring in place

**Congratulations on your successful deployment! 🚀**

---

*For additional help, refer to README.md or contact the data platform team.*
