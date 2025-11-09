# 🚀 Databricks Apps Telemetry - Quick Start Guide

## What You've Received

A complete telemetry solution for tracking Databricks Apps usage with two dashboard options:

### 📦 Files Included

1. **SQL Files**
   - `databricks_apps_telemetry_queries.sql` - All SQL queries and views
   - `setup_database.sql` - Database initialization script

2. **Dashboard Files**
   - `dash_app.py` - Interactive Python web dashboard
   - `aibi_dashboard_config.yaml` - AI/BI dashboard configuration

3. **Configuration**
   - `requirements.txt` - Python dependencies
   - `.env.template` - Environment variables template

4. **Documentation**
   - `README.md` - Complete project documentation
   - `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
   - `CLAUDE_CODE_PROMPT_DASH.md` - Dash app build guide
   - `CLAUDE_CODE_PROMPT_AIBI.md` - AI/BI dashboard build guide

---

## ⚡ 5-Minute Quick Start

### For Dash Web Dashboard:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure credentials
cp .env.template .env
nano .env  # Add your Databricks credentials

# 3. Initialize database
# Run setup_database.sql in Databricks SQL Editor

# 4. Start dashboard
python dash_app.py

# 5. Open browser
# Navigate to http://localhost:8050
```

### For AI/BI Dashboard:

```
1. Run setup_database.sql in Databricks SQL Editor
2. Go to Databricks → AI/BI → Dashboards
3. Click "Create Dashboard"
4. Follow instructions in CLAUDE_CODE_PROMPT_AIBI.md
5. Use queries from databricks_apps_telemetry_queries.sql
```

---

## 📊 What You Can Track

### Key Metrics (KPIs)
- ✅ Total unique users accessing apps
- ✅ Number of active apps
- ✅ Total app interactions/clicks
- ✅ Overall error rate

### Visualizations
1. **Daily Active Users Trend** - Line chart showing DAU over time
2. **Top 10 Apps** - Bar chart of most popular apps
3. **Usage Heatmap** - Hour-by-hour, day-by-day activity patterns
4. **New vs Returning Users** - User acquisition and retention
5. **Error Monitoring** - Success vs failure rates
6. **User Segmentation** - Power users, active users, casual users

### Advanced Analytics
- Weekly retention cohort analysis
- Session duration analysis
- User journey patterns
- Anomaly detection
- Time-to-first-action metrics

---

## 🎯 Use Cases

### Executive Dashboard
- Monitor overall app adoption
- Track usage trends
- Identify top-performing apps
- Review error rates

### Product Team
- Understand user engagement
- Identify at-risk users
- Measure retention rates
- Track feature adoption

### Engineering Team
- Monitor app health
- Debug error patterns
- Optimize performance
- Capacity planning

### Data Analytics Team
- Deep-dive into usage patterns
- Build custom reports
- Export data for analysis
- Create predictive models

---

## 🔧 Customization Guide

### Modify Time Ranges
```python
# In dash_app.py, change default:
DEFAULT_DAYS_BACK = 30  # Change to 7, 60, 90, etc.
```

### Add New KPIs
```sql
-- In databricks_apps_telemetry_queries.sql, add:
SELECT 
  COUNT(DISTINCT your_metric) AS new_kpi
FROM system.access.audit
WHERE service_name = 'apps'
```

### Change Refresh Intervals
```python
# Dash app (in milliseconds)
REFRESH_INTERVAL = 300000  # 5 minutes
```

```yaml
# AI/BI dashboard
refresh_schedule: "0 */6 * * *"  # Every 6 hours
```

### Add Custom Alerts
```yaml
# In aibi_dashboard_config.yaml
alerts:
  - name: "your_custom_alert"
    condition: "your_sql_condition"
    schedule: "cron_schedule"
    recipients: ["team@company.com"]
```

---

## 📖 Next Steps

### Phase 1: Setup (30 minutes)
1. ✅ Review README.md
2. ✅ Run setup_database.sql
3. ✅ Choose dashboard type (Dash or AI/BI)
4. ✅ Follow deployment guide

### Phase 2: Customization (1 hour)
1. Adjust KPI thresholds
2. Modify color schemes
3. Add company branding
4. Configure alerts

### Phase 3: Enhancement (ongoing)
1. Add user authentication (Dash app)
2. Create drill-down pages
3. Integrate with other data sources
4. Build predictive models

---

## 💡 Pro Tips

### Performance
- Use materialized views for frequently accessed data
- Limit historical data to 90 days for real-time queries
- Create aggregate tables for long-term trends
- Enable query result caching in Databricks

### Security
- Rotate access tokens every 90 days
- Use service principals for production
- Implement row-level security if needed
- Enable audit logging for dashboard access

### Best Practices
- Schedule view refreshes during off-peak hours
- Monitor query execution times
- Set up health checks
- Document any customizations

---

## 🆘 Common Issues & Solutions

### "Cannot connect to Databricks"
→ Check DATABRICKS_SERVER_HOSTNAME, HTTP_PATH, and TOKEN in .env

### "No data in dashboard"
→ Verify apps have been accessed and run data quality checks

### "Views not found"
→ Run setup_database.sql to create all views

### "Dashboard is slow"
→ Increase SQL Warehouse size or create materialized views

### "Charts not loading"
→ Check browser console for errors and verify queries work in SQL Editor

---

## 📞 Support Resources

- **Documentation**: See README.md for comprehensive guide
- **Deployment**: See DEPLOYMENT_GUIDE.md for production setup
- **Dash App**: See CLAUDE_CODE_PROMPT_DASH.md for details
- **AI/BI**: See CLAUDE_CODE_PROMPT_AIBI.md for configuration
- **Databricks Docs**: https://docs.databricks.com/admin/system-tables/

---

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Dashboard loads in < 5 seconds
- ✅ All KPIs show data
- ✅ Charts render without errors
- ✅ Filters update visualizations
- ✅ Data refreshes automatically
- ✅ Stakeholders can self-serve analytics

---

## 🚀 Using with Claude Code

### Build Dash Dashboard
```bash
claude code "Build the Databricks Apps Telemetry Dash dashboard following CLAUDE_CODE_PROMPT_DASH.md. Set up the environment, implement all features including KPI cards, charts, heatmap, and user table. Ensure production-ready with error handling."
```

### Build AI/BI Dashboard
```bash
claude code "Create a Databricks AI/BI Dashboard for Apps Telemetry following CLAUDE_CODE_PROMPT_AIBI.md. Include all widgets, filters, alerts, and AI features as specified."
```

---

## 📝 Example Queries

### Top 5 Apps This Month
```sql
SELECT 
  request_params.app_name,
  COUNT(*) as clicks,
  COUNT(DISTINCT user_identity.email) as users
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= DATE_TRUNC('MONTH', CURRENT_DATE)
GROUP BY request_params.app_name
ORDER BY clicks DESC
LIMIT 5
```

### Users Who Haven't Used Apps in 30 Days
```sql
SELECT 
  user_identity.email,
  MAX(event_time) as last_access,
  DATEDIFF(DAY, MAX(event_time), CURRENT_DATE) as days_inactive
FROM system.access.audit
WHERE service_name = 'apps'
GROUP BY user_identity.email
HAVING days_inactive > 30
ORDER BY days_inactive DESC
```

### Error Rate by App
```sql
SELECT 
  request_params.app_name,
  COUNT(*) as total_requests,
  SUM(CASE WHEN response.status_code >= 400 THEN 1 ELSE 0 END) as errors,
  ROUND(SUM(CASE WHEN response.status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as error_rate
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - 7
GROUP BY request_params.app_name
HAVING error_rate > 0
ORDER BY error_rate DESC
```

---

**Happy Monitoring! 📊✨**

*Built with ❤️ for the Databricks community*
