# HLS Demo Telemetry App

Comprehensive Databricks Apps telemetry monitoring solution with interactive dashboards, AI-powered insights, and automated alerting.

## 🚀 Quick Deploy

Deploy to any Databricks workspace in 3 commands:

```bash
./deployment/setup.sh          # Configure workspace
./deployment/create_schema.sh  # Create database
./deployment/deploy.sh         # Deploy app
```

## 📊 Features

- **Interactive Dash Web Dashboard** - Real-time monitoring with auto-refresh
- **AI/BI Native Dashboard** - Natural language querying with Databricks AI/BI
- **Executive KPI Cards** - Total users, active apps, interactions, error rates
- **Advanced Analytics** - DAU trends, top apps, usage heatmaps, user segmentation
- **Error Monitoring** - Real-time error tracking with 5% threshold alerts
- **User Cohort Analysis** - New vs returning users, retention tracking
- **SQL Serverless** - All queries execute via SQL Serverless warehouse

## 📁 Project Structure

```
hls_demo_telemetry_app/
├── src/                    # Application source code
│   ├── app.py             # Dash web dashboard
│   ├── app.yaml           # Databricks App configuration
│   └── requirements.txt   # Python dependencies
├── sql/                    # SQL scripts
│   ├── setup_database.sql # Database initialization
│   ├── databricks_apps_telemetry_queries.sql  # All views
│   ├── create_tables.sql  # Table DDL templates
│   └── queries.sql        # Analytical queries
├── deployment/             # Deployment automation
│   ├── setup.sh           # Interactive workspace configuration
│   ├── create_schema.sh   # Create database schema
│   ├── deploy.sh          # Deploy application
│   ├── test_sql_queries.sh # Test SQL queries
│   └── utils.sh           # Utility functions
├── dashboards/             # Dashboard configurations
│   └── aibi_dashboard_config.yaml
├── docs/                   # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── CLAUDE_CODE_PROMPT_AIBI.md
│   └── CLAUDE_CODE_PROMPT_DASH.md
└── config/                 # Configuration templates
    └── workspace.yaml.template
```

## 🎯 What's Deployed

### ✅ SQL Queries Tested
- All core telemetry queries verified with SQL Serverless
- KPI summary, DAU trends, top apps, error rates
- Usage heatmaps, user cohorts, segmentation
- Schema: `hls_amer_catalog.apps_telemetry`

### ✅ Database Views (To be created)
- 15+ pre-built views for dashboard widgets
- User click metrics, access logs, popularity metrics
- Daily active users, top apps, user segmentation
- Error monitoring, retention cohorts, session analysis

### ✅ Ready for Deployment
- Dash web application (interactive Python dashboard)
- AI/BI dashboard configuration (native Databricks)
- Automated deployment scripts
- Multi-workspace support

## 📖 Documentation

- **Quick Start**: `docs/PROVIDED_QUICK_START.md`
- **Deployment Guide**: `docs/PROVIDED_DEPLOYMENT_GUIDE.md`
- **Dash App Guide**: `docs/CLAUDE_CODE_PROMPT_DASH.md`
- **AI/BI Guide**: `docs/CLAUDE_CODE_PROMPT_AIBI.md`

## 🔧 Configuration

### Workspace Setup

Run interactive setup:
```bash
./deployment/setup.sh
```

Or manually create `config/workspace.yaml`:
```yaml
workspace:
  profile: "DEFAULT"
  host: "https://your-workspace.cloud.databricks.com"
  catalog: "hls_amer_catalog"
  schema: "apps_telemetry"
  warehouse_id: "your-warehouse-id"
  serving_endpoint: "databricks-claude-sonnet-4-5"
```

### Environment Variables

Copy `.env.template` to `.env` and configure:
```env
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=dapi_your_token_here
```

## ✅ Testing Status

All SQL queries tested and verified:
- ✅ System audit table access
- ✅ Schema creation (hls_amer_catalog.apps_telemetry)
- ✅ KPI summary query
- ✅ DAU trend query
- ✅ Top apps query
- ✅ Error rate monitoring
- ✅ Usage heatmap query

## 🚢 Deployment

### Deploy to DEFAULT Workspace
```bash
./deployment/setup.sh          # Select DEFAULT profile
./deployment/create_schema.sh  # Create schema
./deployment/deploy.sh         # Deploy app
```

### Deploy to Another Workspace
```bash
# Create separate config
cp config/workspace.yaml config/e2demofieldeng_workspace.yaml

# Edit for new workspace
nano config/e2demofieldeng_workspace.yaml

# Deploy
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/create_schema.sh
CONFIG_FILE=config/e2demofieldeng_workspace.yaml ./deployment/deploy.sh
```

## 📊 Dashboard Options

### Option 1: Dash Web App
```bash
python src/dash_app.py
# Access at http://localhost:8050
```

### Option 2: AI/BI Dashboard
1. Run `sql/databricks_apps_telemetry_queries.sql` in Databricks SQL Editor
2. Create dashboard in AI/BI
3. Use configuration from `dashboards/aibi_dashboard_config.yaml`

## 🎯 Next Steps

1. Create database views (run SQL file in Databricks SQL Editor)
2. Deploy Dash app or create AI/BI dashboard
3. Configure alerts and scheduled exports
4. Customize for your use case

## 📞 Support

- **GitHub**: https://github.com/suryasaitura-db/hls_demo_telemetry_app
- **Issues**: Create an issue on GitHub
- **Contact**: suryasai.turaga@databricks.com

## 📝 License

Databricks Internal Use

---

**Status**: ✅ SQL Queries Tested | ⏳ Views Creation Pending | 🚀 Ready for Deployment

**Last Updated:** 2025-11-08
