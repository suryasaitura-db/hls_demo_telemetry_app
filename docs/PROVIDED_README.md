# Databricks Apps Telemetry Dashboard

> **Comprehensive monitoring and analytics for Databricks Apps usage, adoption, and performance**

[![Databricks](https://img.shields.io/badge/Databricks-System%20Tables-FF3621?logo=databricks)](https://docs.databricks.com/admin/system-tables/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-Interactive%20Dashboard-00D9FF)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Dashboard Options](#dashboard-options)
  - [Dash Web Application](#option-1-dash-web-application)
  - [AI/BI Dashboard](#option-2-aibi-dashboard)
- [Configuration](#configuration)
- [Usage](#usage)
- [Data Model](#data-model)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project provides two comprehensive dashboard solutions for tracking and analyzing Databricks Apps telemetry data:

1. **Interactive Dash Web Application**: A self-hosted, Python-based dashboard with real-time updates
2. **AI/BI Native Dashboard**: A Databricks-native dashboard with natural language querying capabilities

Both dashboards answer critical questions about your Databricks Apps usage:
- 📊 Which apps are most popular?
- 👥 Who are your power users?
- ⏰ When do users engage with apps?
- 🐛 What's the error rate and health status?
- 📈 How are adoption trends evolving?

---

## ✨ Features

### Core Analytics
- **User Engagement Metrics**: Track DAU, MAU, and user segmentation
- **App Performance**: Monitor click-through rates, session duration, and usage patterns
- **Error Monitoring**: Real-time error rate tracking with alerting
- **Retention Analysis**: Cohort-based retention and churn metrics
- **Usage Patterns**: Heatmaps showing hour-by-hour and day-by-day activity

### Advanced Features
- **Natural Language Queries** (AI/BI only): Ask questions in plain English
- **Anomaly Detection**: Automatic detection of unusual patterns
- **Predictive Insights**: Trend forecasting and recommendations
- **Automated Alerts**: Email and Slack notifications for critical events
- **Scheduled Exports**: Automated report delivery (weekly/monthly)
- **User Segmentation**: Automatically classify users by engagement level

### Visualizations
- 📈 Line charts for trends
- 📊 Bar charts for comparisons
- 🌈 Heatmaps for patterns
- 🥧 Area charts for compositions
- 📉 Combo charts for correlations
- 📋 Interactive tables with filtering

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Data Source Layer                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │      system.access.audit (Databricks System Table)  │    │
│  │      Filtered by: service_name = 'apps'            │    │
│  └────────────────────────────────────────────────────┘    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Processing Layer                            │
│  ┌──────────────────────────────────────────────────┐      │
│  │  apps_telemetry Schema                            │      │
│  │  ├── Views (Pre-computed queries)                │      │
│  │  ├── Materialized tables (Performance)           │      │
│  │  └── Alert tables (Monitoring)                   │      │
│  └──────────────────────────────────────────────────┘      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                Presentation Layer                            │
│  ┌──────────────────┐      ┌──────────────────────┐        │
│  │  Dash Web App     │      │  AI/BI Dashboard     │        │
│  │  ├── Python/Plotly│      │  ├── Native UI       │        │
│  │  ├── Self-hosted  │      │  ├── AI Features     │        │
│  │  └── Port 8050    │      │  └── Cloud-hosted    │        │
│  └──────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### For Dash Web Application
- Python 3.9 or higher
- Databricks SQL Warehouse (running)
- Databricks Personal Access Token
- Network access to Databricks workspace

### For AI/BI Dashboard
- Databricks Workspace with AI/BI enabled
- SQL Warehouse (Pro or higher recommended)
- Permission to create dashboards
- Access to `system.access.audit` table

### System Requirements
- 4GB RAM minimum (8GB recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for Databricks access

---

## 🚀 Installation

### 1. Clone or Download Files

```bash
# If using git
git clone <repository-url>
cd databricks-apps-telemetry

# Or download files manually and extract
```

### 2. Install Python Dependencies (for Dash app)

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy template
cp .env.template .env

# Edit .env file with your Databricks credentials
nano .env  # or use your preferred editor
```

**Required environment variables:**
```env
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=dapi_your_token_here
```

### 4. Initialize Database Schema

```bash
# In Databricks SQL Editor, run:
databricks-sql -f setup_database.sql

# Or copy/paste the contents of setup_database.sql
# into Databricks SQL Editor and execute
```

---

## ⚡ Quick Start

### Run the Dash Web Application

```bash
# Start the dashboard
python dash_app.py

# Dashboard will be available at:
# http://localhost:8050
```

### Create the AI/BI Dashboard

1. Log into your Databricks workspace
2. Navigate to **AI/BI** → **Dashboards**
3. Click **Create Dashboard**
4. Follow the step-by-step guide in `CLAUDE_CODE_PROMPT_AIBI.md`
5. Or use the configuration in `aibi_dashboard_config.yaml`

---

## 📊 Dashboard Options

### Option 1: Dash Web Application

**Best for:**
- Custom deployments and branding
- Integration with existing Python infrastructure
- Full control over hosting and security
- Offline or air-gapped environments

**Features:**
- Self-hosted on your infrastructure
- Real-time data updates (5-minute refresh)
- Fully customizable Python code
- No additional Databricks costs
- Requires server maintenance

**Access:**
```
http://your-server:8050
```

**Deployment:**
```bash
# Development
python dash_app.py

# Production (with Gunicorn)
gunicorn dash_app:server -b 0.0.0.0:8050 --workers 4
```

### Option 2: AI/BI Dashboard

**Best for:**
- Databricks-native experience
- Natural language querying
- Executive-level reporting
- Quick setup with no coding
- Managed hosting and maintenance

**Features:**
- Hosted by Databricks (no server needed)
- AI-powered insights and anomaly detection
- Natural language queries ("Show me top apps this month")
- Automatic scaling and performance
- Integrated with Databricks security

**Access:**
```
https://your-workspace.cloud.databricks.com/sql/dashboards/your-dashboard-id
```

---

## ⚙️ Configuration

### Dash App Settings (`dash_app.py`)

```python
class Config:
    # Refresh interval in milliseconds
    REFRESH_INTERVAL = 300000  # 5 minutes
    
    # Default date range
    DEFAULT_DAYS_BACK = 30
    
    # Color scheme
    COLORS = {
        'primary': '#4A90E2',
        'success': '#50C878',
        'warning': '#FFA500',
        'danger': '#FF6B6B',
        # ...
    }
```

### AI/BI Dashboard Settings (`aibi_dashboard_config.yaml`)

```yaml
dashboard:
  refresh_schedule: "0 */6 * * *"  # Every 6 hours
  
filters:
  - name: date_range
    default: "Last 30 Days"
  # ...

alerts:
  - name: high_error_rate_alert
    schedule: "*/30 * * * *"  # Every 30 minutes
  # ...
```

---

## 📖 Usage

### Dash Web Application

#### Viewing Metrics
1. Open http://localhost:8050
2. View KPI cards at the top for summary metrics
3. Scroll down to see detailed charts
4. Use filters to adjust date range

#### Filtering Data
- **Date Range**: Use dropdown to select 7/30/90 days
- **Auto Refresh**: Toggle to enable/disable automatic updates
- **Manual Refresh**: Click "Refresh Now" button

#### Exporting Data
- Tables support sorting by clicking column headers
- Charts can be downloaded as PNG using Plotly toolbar
- Use browser print to save entire dashboard as PDF

### AI/BI Dashboard

#### Natural Language Queries
Type questions like:
- "Show me the top 5 apps this month"
- "What's the error rate trend?"
- "Which users are at risk of churning?"
- "Compare this week to last week"

#### Viewing Insights
- **Auto-Insights Panel**: Review automatically detected patterns
- **Chart Narratives**: Read AI-generated summaries below each chart
- **Anomaly Alerts**: Check notifications for unusual patterns

#### Setting Up Alerts
1. Click **Alerts** tab
2. Create new alert with conditions
3. Configure recipients and schedule
4. Test alert to verify delivery

---

## 📊 Data Model

### Source Table
```sql
system.access.audit
├── event_time (TIMESTAMP)
├── event_date (DATE) -- Partition key
├── service_name (STRING) -- Filter: 'apps'
├── action_name (STRING) -- e.g., 'openApp', 'viewApp'
├── user_identity.email (STRING)
├── request_params.app_name (STRING)
├── request_params.app_id (STRING)
├── request_params.url (STRING)
├── response.status_code (INT)
├── response.error_message (STRING)
└── ...
```

### Key Metrics Calculated
- **Daily Active Users (DAU)**: `COUNT(DISTINCT user_identity.email) per day`
- **Total Interactions**: `COUNT(*) WHERE action_name IN (...)`
- **Error Rate**: `(failed_requests / total_requests) * 100`
- **User Segment**: Based on total_clicks thresholds
- **Retention**: `users active in week N+1 / users active in week N`

### Views Created
```sql
apps_telemetry.user_click_metrics
apps_telemetry.detailed_access_log
apps_telemetry.app_popularity_metrics
apps_telemetry.widget_dau_trend
apps_telemetry.widget_top_apps
apps_telemetry.widget_user_segmentation
apps_telemetry.widget_usage_heatmap
apps_telemetry.widget_error_monitoring
apps_telemetry.widget_user_cohorts
apps_telemetry.user_retention_cohorts
apps_telemetry.app_session_analysis
```

---

## 🐛 Troubleshooting

### Common Issues

#### "Cannot connect to Databricks"
```
Error: Unable to establish connection
```
**Solution:**
1. Verify `DATABRICKS_SERVER_HOSTNAME` is correct (no https://)
2. Check `DATABRICKS_HTTP_PATH` matches your warehouse
3. Ensure Personal Access Token is valid
4. Confirm SQL Warehouse is running
5. Check network/firewall settings

#### "No data in dashboard"
```
All charts showing "No data available"
```
**Solution:**
1. Verify apps have been deployed and accessed
2. Check date range filter (may be too narrow)
3. Run data quality checks from `setup_database.sql`
4. Ensure `service_name = 'apps'` has events in audit log

#### "Views not found"
```
Error: Table or view 'apps_telemetry.widget_dau_trend' not found
```
**Solution:**
1. Run `setup_database.sql` to create schema
2. Execute all CREATE VIEW statements from queries file
3. Verify permissions on `system.access.audit`
4. Check schema exists: `SHOW SCHEMAS LIKE 'apps_telemetry'`

#### "Dashboard slow to load"
```
Charts taking >10 seconds to load
```
**Solution:**
1. Increase SQL Warehouse cluster size
2. Enable query result caching
3. Reduce date range (use 30 days instead of 90)
4. Create materialized views for KPIs
5. Partition audit table if very large

### Performance Optimization

```sql
-- Optimize audit table
OPTIMIZE system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '90' DAY;

-- Analyze table statistics
ANALYZE TABLE system.access.audit COMPUTE STATISTICS;

-- Create materialized view for KPIs
CREATE MATERIALIZED VIEW apps_telemetry.kpi_summary_mv AS
SELECT * FROM apps_telemetry.widget_kpi_summary;

-- Refresh materialized view
REFRESH MATERIALIZED VIEW apps_telemetry.kpi_summary_mv;
```

### Getting Help

- 📚 **Documentation**: See `CLAUDE_CODE_PROMPT_DASH.md` and `CLAUDE_CODE_PROMPT_AIBI.md`
- 🐛 **Bug Reports**: Create an issue with error logs and steps to reproduce
- 💬 **Questions**: Check existing issues or start a discussion
- 📧 **Email**: Contact your Databricks account team

---

## 📁 Project Structure

```
databricks-apps-telemetry/
├── README.md                              # This file
├── requirements.txt                       # Python dependencies
├── .env.template                          # Environment variables template
├── setup_database.sql                     # Database initialization
├── databricks_apps_telemetry_queries.sql  # All SQL queries library
├── aibi_dashboard_config.yaml             # AI/BI dashboard configuration
├── dash_app.py                            # Dash web application
├── CLAUDE_CODE_PROMPT_DASH.md            # Dash app build instructions
├── CLAUDE_CODE_PROMPT_AIBI.md            # AI/BI dashboard instructions
└── LICENSE                                # MIT License
```

---

## 🔐 Security Considerations

- **Never commit `.env` file** to version control
- **Rotate access tokens** regularly (every 90 days recommended)
- **Use service principals** for production deployments
- **Restrict permissions** to apps_telemetry schema as needed
- **Enable SSL/TLS** for Dash app in production
- **Implement authentication** for Dash app (not included by default)
- **Audit dashboard access** through Databricks logs

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Add docstrings to all functions
- Test changes with sample data
- Update README if adding features
- Include screenshots for UI changes

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built on [Dash by Plotly](https://dash.plotly.com/)
- Uses [Databricks System Tables](https://docs.databricks.com/admin/system-tables/)
- Inspired by best practices in data observability and monitoring

---

## 📞 Support

For Databricks-specific questions:
- 📖 [Databricks Documentation](https://docs.databricks.com/)
- 💬 [Databricks Community](https://community.databricks.com/)
- 🎓 [Databricks Academy](https://academy.databricks.com/)

For dashboard issues:
- 🐛 [Report a Bug](../../issues)
- 💡 [Request a Feature](../../issues)
- 📚 [View Documentation](./CLAUDE_CODE_PROMPT_DASH.md)

---

**Made with ❤️ for the Databricks community**

*Last updated: 2025-11-08*
