# ====================================================================
# CLAUDE CODE PROMPT: DATABRICKS AI/BI DASHBOARD FOR APPS TELEMETRY
# ====================================================================

## Project Overview

Create a comprehensive Databricks AI/BI Dashboard for monitoring Databricks Apps telemetry. This dashboard leverages Databricks' native AI/BI capabilities to provide executive-level insights into app usage, adoption, and performance metrics with natural language querying capabilities.

## Context

We are tracking telemetry data for Databricks Apps to understand:
- **Usage Patterns**: When and how users interact with apps
- **Adoption Metrics**: Which apps are most popular and user penetration rates
- **Performance Health**: Error rates, success rates, and system reliability
- **User Behavior**: Segmentation, retention, and engagement levels

Data is sourced from `system.access.audit` table, filtered for `service_name = 'apps'`.

## AI/BI Dashboard Advantages

Unlike traditional dashboards, Databricks AI/BI provides:
- **Natural Language Queries**: Users can ask questions in plain English
- **AI-Powered Insights**: Automatic anomaly detection and trend analysis
- **Intelligent Recommendations**: Suggested visualizations and filters
- **Predictive Analytics**: Forecasting and trend predictions
- **Auto-Generated Narratives**: Explains what the data shows

## Technical Architecture

```
AI/BI Dashboard Structure
├── Data Layer
│   ├── Source: system.access.audit
│   ├── Schema: apps_telemetry
│   └── Views: Pre-computed metrics
│
├── Presentation Layer
│   ├── KPI Cards (4)
│   ├── Charts (6 types)
│   ├── Tables (1)
│   └── Filters (Global)
│
├── AI Features
│   ├── Natural Language Queries
│   ├── Auto Insights
│   ├── Anomaly Detection
│   └── Trend Analysis
│
└── Alerting & Scheduling
    ├── High Error Rate Alerts
    ├── Anomaly Alerts
    └── Scheduled Exports
```

## Dashboard Specifications

### Section 1: Executive KPI Summary (Top Row)

Create 4 large KPI counter widgets in a 4-column grid:

#### KPI 1: Total Unique Users
- **Type**: Counter
- **Query**: `SELECT COUNT(DISTINCT user_identity.email) FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '30' DAY`
- **Format**: Number with thousand separators
- **Icon**: User group icon
- **Color**: Blue (#4A90E2)
- **Comparison**: Show % change vs previous 30 days
- **Trend**: Up/down arrow indicator

#### KPI 2: Total Active Apps
- **Type**: Counter
- **Query**: `SELECT COUNT(DISTINCT request_params.app_id) FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '30' DAY`
- **Format**: Number
- **Icon**: Application icon
- **Color**: Purple (#7B68EE)
- **Description**: "Apps with at least 1 interaction"

#### KPI 3: Total Interactions
- **Type**: Counter
- **Query**: `SELECT COUNT(*) FROM system.access.audit WHERE service_name = 'apps' AND event_date >= CURRENT_DATE - INTERVAL '30' DAY`
- **Format**: Number with thousand separators
- **Icon**: Activity/chart icon
- **Color**: Green (#50C878)
- **Comparison**: Show % change vs previous period

#### KPI 4: Apps Adoption Rate
- **Type**: Counter
- **Query**: Calculate percentage of all users who have used apps
- **Format**: Percentage with 2 decimal places
- **Icon**: Trending up icon
- **Color**: Red (#FF6B6B) if <50%, Orange if 50-75%, Green if >75%
- **Threshold Indicators**: Color-coded based on adoption level

### Section 2: Usage Trends (Second Row, 2 Columns)

#### Widget A: Daily Active Users Trend
- **Type**: Line Chart
- **Title**: "Daily Active Users Trend - Last 90 Days"
- **Query**: Reference `apps_telemetry.widget_dau_trend`
- **X-Axis**: activity_date (Date format)
- **Y-Axis (Primary)**: daily_active_users (Line, #4A90E2, width=2)
- **Y-Axis (Secondary)**: total_clicks (Dashed line, #FF6B6B)
- **Features**:
  - Smooth line interpolation
  - Data point markers on hover
  - Zoom/pan enabled
  - Legend positioned top-right
  - Tooltip shows both metrics
- **AI Insight**: Enable "Explain this trend" feature
- **Grid Lines**: Horizontal only

#### Widget B: Top 10 Apps by Engagement
- **Type**: Horizontal Bar Chart
- **Title**: "Most Popular Apps (Last 30 Days)"
- **Query**: Reference `apps_telemetry.widget_top_apps`
- **Y-Axis**: app_name (categorical)
- **X-Axis**: click_count (numeric)
- **Color Encoding**: unique_users (sequential blue palette)
- **Sorting**: Descending by click_count
- **Features**:
  - Show exact values on bars
  - Click-through to app details (if available)
  - Tooltip: App name, clicks, unique users, % of total
- **Layout**: Sort bars from highest to lowest (top to bottom)

### Section 3: Usage Patterns (Full Width)

#### Widget: Usage Heatmap
- **Type**: Heatmap
- **Title**: "Usage Patterns by Day and Hour"
- **Subtitle**: "Darker colors indicate higher activity levels"
- **Query**: Reference `apps_telemetry.widget_usage_heatmap`
- **X-Axis**: hour_of_day (0-23, labeled as "12 AM", "1 AM", etc.)
- **Y-Axis**: day_name (Mon-Sun, in order)
- **Color Palette**: Red-Yellow-Green (RdYlGn)
  - Red: Low activity
  - Yellow: Medium activity
  - Green: High activity
- **Color Scale**: Logarithmic (to handle outliers)
- **Features**:
  - Cell size: Auto-adjust
  - Show values: Optional (toggle)
  - Tooltip: Day, Hour, Click count, Unique users
  - Interactive: Click cell to filter other charts
- **AI Insight**: "When are apps most actively used?"

### Section 4: User Analysis (Fourth Row, 2 Columns)

#### Widget A: New vs Returning Users
- **Type**: Stacked Area Chart
- **Title**: "User Acquisition & Retention"
- **Query**: Reference `apps_telemetry.widget_user_cohorts`
- **X-Axis**: activity_date
- **Y-Axis**: User count
- **Series**:
  1. new_users (Blue #4A90E2, bottom layer)
  2. returning_users (Green #50C878, top layer)
- **Stack Mode**: Normal (not percentage)
- **Features**:
  - Smooth area interpolation
  - Legend with totals
  - Zoom enabled
  - Tooltip shows both segments
- **AI Question**: "What's our user retention rate?"

#### Widget B: App Health Monitor
- **Type**: Combo Chart (Bars + Line)
- **Title**: "Request Success vs Error Rates"
- **Query**: Reference `apps_telemetry.widget_error_monitoring`
- **X-Axis**: activity_date
- **Y-Axis (Left)**: Request count
  - successful_requests (Green bars)
  - failed_requests (Red bars)
  - Stack mode: Stacked
- **Y-Axis (Right)**: error_rate_percentage (Red line, width=3)
- **Reference Lines**:
  - Horizontal line at 5% (Orange dashed) labeled "Threshold"
- **Features**:
  - Dual Y-axes
  - Different scales for count vs percentage
  - Tooltip shows all metrics
  - Alert badge if any day exceeds 5% error rate
- **AI Alert**: "Notify me if error rate exceeds 5%"

### Section 5: User Segmentation (Full Width)

#### Widget: User Engagement Table
- **Type**: Interactive Table
- **Title**: "Top 100 Users by Engagement"
- **Query**: Reference `apps_telemetry.widget_user_segmentation` (LIMIT 100)
- **Columns**:
  1. **user_email** (250px, left-aligned, sortable)
  2. **user_segment** (120px, center-aligned, sortable)
     - Conditional formatting:
       * "Power User": Blue background, white text
       * "Active User": Green background, white text
       * "Regular User": Orange background, white text
       * "Casual User": Gray background, dark text
  3. **activity_status** (100px, center-aligned)
     - Conditional formatting:
       * "Active": Green badge
       * "At Risk": Orange badge
       * "Inactive": Red badge
  4. **total_clicks** (120px, right-aligned, number format, sortable)
  5. **apps_accessed** (120px, right-aligned, number format, sortable)
  6. **days_active** (120px, right-aligned, number format, sortable)
  7. **avg_clicks_per_day** (140px, right-aligned, decimal format (2 places), sortable)
  8. **last_interaction** (180px, datetime format, sortable)

- **Features**:
  - Default sort: total_clicks DESC
  - Page size: 25 rows
  - Search box (filter by user email)
  - Export to CSV/Excel button
  - Pagination controls
  - Click row for user drill-down (future)
- **AI Question**: "Who are our power users?"

### Section 6: Advanced Analytics (Sixth Row, 2 Columns)

#### Widget A: Weekly Retention Cohorts
- **Type**: Cohort Heatmap
- **Title**: "Weekly User Retention Analysis"
- **Query**: Reference `apps_telemetry.user_retention_cohorts`
- **Layout**:
  - Rows: cohort_week (cohort start date)
  - Columns: Week 0, Week 1, Week 2, Week 3, Week 4
  - Values: Retention percentage (0-100%)
- **Color Palette**: Red (0%) → Yellow (50%) → Green (100%)
- **Display**: Show percentages in cells
- **Tooltip**: Shows actual user counts
- **Features**:
  - Latest cohorts at top
  - Highlight declining retention
  - Click to see user list
- **AI Insight**: "What's our week-1 retention rate trend?"

#### Widget B: Session Duration Distribution
- **Type**: Box Plot (or Violin Plot)
- **Title**: "App Session Duration Distribution (Top 10 Apps)"
- **Query**: Reference `apps_telemetry.app_session_analysis`
- **X-Axis**: app_name
- **Y-Axis**: Session duration in minutes
- **Box Plot Elements**:
  - Min: min_session_duration_minutes
  - Q1: 25th percentile
  - Median: median_session_duration_minutes
  - Q3: 75th percentile (p90_session_duration_minutes)
  - Max: max_session_duration_minutes
  - Outliers: Show as individual points
- **Features**:
  - Show only top 10 apps by session count
  - Color code by app
  - Tooltip shows all statistics
- **AI Question**: "Which apps have the longest sessions?"

## Global Filters

All widgets should respond to these global filters:

### Filter 1: Date Range
- **Type**: Date Range Picker
- **Label**: "Analysis Period"
- **Default**: Last 30 Days
- **Preset Options**:
  - Last 7 Days
  - Last 30 Days
  - Last 90 Days
  - Last 12 Months
  - Custom Range (date picker)
- **Behavior**: Updates all queries when changed

### Filter 2: App Name
- **Type**: Multi-select Dropdown
- **Label**: "Filter by App"
- **Source**: `SELECT DISTINCT COALESCE(request_params.app_name, 'Unknown') FROM system.access.audit WHERE service_name = 'apps'`
- **Default**: "All Apps"
- **Behavior**: Filters all charts to show only selected apps

### Filter 3: User Segment
- **Type**: Single-select Dropdown
- **Label**: "User Segment"
- **Options**:
  - All Segments (default)
  - Power User
  - Active User
  - Regular User
  - Casual User
- **Behavior**: Filters data to show only users in selected segment

## AI/BI Specific Features

### Natural Language Queries

Enable these sample questions for users:

1. "What was our peak usage time last week?"
2. "Which app has the highest error rate?"
3. "Show me users who haven't logged in for 30 days"
4. "What's the trend in daily active users?"
5. "Which apps are growing fastest in adoption?"
6. "Compare this month's usage to last month"
7. "List all apps with >10% error rate"
8. "Who are the top 5 power users?"
9. "What percentage of users are at risk of churning?"
10. "Show me anomalies in usage patterns"

### Auto-Insights Panel

Configure automatic insights to detect:
- Sudden spikes or drops in DAU (>20% change)
- Apps with increasing error rates
- Declining user retention trends
- Anomalous usage patterns (unusual times/days)
- New apps gaining traction quickly
- Users becoming inactive (at-risk)

Display insights in a collapsible panel at the top of dashboard with:
- Icon indicating insight type (warning, info, success)
- Summary text of the insight
- Link to relevant chart
- Timestamp of detection
- "Dismiss" or "Act on this" buttons

### AI-Powered Narratives

For each major chart, generate a brief narrative summary:

**Example for DAU Chart**:
"Daily active users have increased by 23% over the past month, from an average of 145 users to 178 users. Peak usage occurred on Wednesday, November 6th with 234 active users. This represents strong growth in app adoption."

Place narratives below each chart in a light gray box.

## Alerting Configuration

Set up automated alerts:

### Alert 1: High Error Rate
- **Name**: "High Error Rate Detected"
- **Condition**: `error_rate_percentage > 5%` for any app
- **Query**: `SELECT * FROM apps_telemetry.high_error_rate_apps`
- **Schedule**: Every 30 minutes
- **Channels**: Email + Slack
- **Recipients**: data-platform-team@company.com
- **Template**: "⚠️ High error rate detected for {app_name}: {error_rate_percentage}%"
- **Severity**: Warning

### Alert 2: Usage Anomaly
- **Name**: "Unusual Usage Pattern"
- **Condition**: Z-score > 2 for DAU or clicks
- **Query**: `SELECT * FROM apps_telemetry.anomaly_detection WHERE anomaly_status = 'Anomaly Detected'`
- **Schedule**: Daily at 8:00 AM
- **Channels**: Email
- **Recipients**: analytics-team@company.com
- **Template**: "📊 Anomaly detected on {activity_date}: {clicks_z_score} standard deviations from normal"
- **Severity**: Info

### Alert 3: Inactive User Warning
- **Name**: "Previously Active Users Becoming Inactive"
- **Condition**: Users with >10 historical clicks, no activity in 30+ days
- **Query**: `SELECT * FROM apps_telemetry.inactive_users_alert WHERE inactivity_level = 'Critical - 30+ days'`
- **Schedule**: Weekly on Monday at 9:00 AM
- **Channels**: Email
- **Recipients**: product-team@company.com
- **Template**: "👥 {count} previously active users have been inactive for 30+ days"
- **Severity**: Warning

## Scheduled Exports

### Export 1: Weekly Executive Report
- **Name**: "Apps Telemetry Weekly Summary"
- **Query**: `SELECT * FROM apps_telemetry.weekly_executive_summary`
- **Format**: Excel (.xlsx) with formatted table
- **Schedule**: Every Monday at 7:00 AM
- **Recipients**: executives@company.com, product-leads@company.com
- **Includes**:
  - Week-over-week metrics
  - Top apps this week
  - Key insights summary
  - Charts as images

### Export 2: Monthly Detailed Report
- **Name**: "Monthly Apps Usage Report"
- **Query**: `SELECT * FROM apps_telemetry.monthly_trends_report`
- **Format**: CSV
- **Schedule**: First day of month at 8:00 AM
- **Destination**: DBFS path `/dbfs/analytics/exports/apps_telemetry/monthly/`
- **Retention**: Keep 24 months

## Dashboard Settings

### Refresh Configuration
- **Auto-refresh**: Enabled
- **Refresh interval**: Every 6 hours
- **Cache TTL**: 
  - KPIs: 1 hour
  - Charts: 1-2 hours
  - Tables: 1 hour
  - Heatmap: 2 hours (slower changing)

### Performance Optimization
- Use Delta Lake caching for frequent queries
- Partition audit data by event_date
- Create materialized views for KPIs
- Use query result caching
- Limit historical data to 90 days for detailed views
- Aggregate older data for long-term trends

### Permissions
- **Viewers**: all-employees@company.com (read-only)
- **Editors**: analytics-team@company.com, data-platform-team@company.com
- **Admins**: data-engineering-leads@company.com

## Implementation Steps

### Step 1: Prepare Data Layer
```sql
-- Run in Databricks SQL
CREATE SCHEMA IF NOT EXISTS apps_telemetry;

-- Run all view creation queries from databricks_apps_telemetry_queries.sql
source databricks_apps_telemetry_queries.sql;

-- Verify views
SHOW VIEWS IN apps_telemetry;
```

### Step 2: Create AI/BI Dashboard
```
1. Navigate to Databricks AI/BI in your workspace
2. Click "Create Dashboard"
3. Name: "Apps Telemetry Executive Dashboard"
4. Description: "Comprehensive analytics for Databricks Apps usage and adoption"
5. Choose Warehouse: Select your SQL Warehouse
```

### Step 3: Add Global Filters
```
1. Click "Add Filter"
2. Create each of the 3 filters defined above
3. Set default values
4. Apply to all widgets
```

### Step 4: Build KPI Section
```
For each KPI:
1. Click "Add Visualization"
2. Select "Counter" type
3. Write or paste the query
4. Configure formatting (number/percentage)
5. Set color and icon
6. Enable comparison if applicable
7. Position in grid (1x4 layout)
```

### Step 5: Build Charts Section
```
For each chart:
1. Click "Add Visualization"
2. Select appropriate chart type
3. Reference the pre-built view (e.g., apps_telemetry.widget_dau_trend)
4. Configure axes, colors, and formatting
5. Add titles and subtitles
6. Enable interactive features
7. Position in grid
```

### Step 6: Build Table Section
```
1. Click "Add Visualization"
2. Select "Table" type
3. Query: SELECT * FROM apps_telemetry.widget_user_segmentation
4. Configure column formatting and conditional rules
5. Set page size to 25
6. Enable sorting and search
```

### Step 7: Configure AI Features
```
1. Click "AI Settings"
2. Enable natural language queries
3. Add suggested questions
4. Configure auto-insights:
   - Enable anomaly detection
   - Set thresholds
   - Choose metrics to monitor
5. Enable AI narratives for key charts
```

### Step 8: Set Up Alerts
```
1. Click "Alerts" tab
2. For each alert:
   - Click "Create Alert"
   - Name and describe
   - Select query
   - Set condition
   - Configure schedule
   - Add recipients
   - Customize message template
   - Set severity level
```

### Step 9: Configure Exports
```
1. Click "Schedules" tab
2. For each export:
   - Click "Create Schedule"
   - Select query/dashboard
   - Choose format (Excel/CSV)
   - Set frequency (weekly/monthly)
   - Add recipients or destination
   - Configure filename template
```

### Step 10: Test and Publish
```
1. Click "Refresh" to load data
2. Test all filters
3. Verify all charts render correctly
4. Test natural language queries
5. Trigger test alerts
6. Review on mobile view
7. Click "Publish" when ready
8. Share link with stakeholders
```

## Quality Checklist

- [ ] All 4 KPI cards display correctly with proper formatting
- [ ] All 6 chart types render without errors
- [ ] User segmentation table has conditional formatting
- [ ] All global filters update all widgets
- [ ] Natural language queries return correct results
- [ ] Auto-insights panel shows relevant insights
- [ ] Alerts trigger correctly based on conditions
- [ ] Scheduled exports deliver on time
- [ ] Mobile view is responsive
- [ ] Permissions are configured correctly
- [ ] Dashboard auto-refreshes every 6 hours
- [ ] AI narratives provide useful summaries
- [ ] Performance meets <5 second load time
- [ ] All tooltips display relevant information
- [ ] Color coding is consistent and meaningful

## Configuration File Usage

The dashboard configuration is defined in `aibi_dashboard_config.yaml`. This file can be used to:

1. **Document** the dashboard structure
2. **Version control** dashboard changes
3. **Replicate** dashboard in different environments
4. **Automate** dashboard creation via Databricks API

To use the configuration programmatically:

```python
import yaml
from databricks.sdk import WorkspaceClient

# Load configuration
with open('aibi_dashboard_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize Databricks client
client = WorkspaceClient()

# Create dashboard programmatically using the config
# (Implement based on Databricks API documentation)
```

## Claude Code Execution

To build this AI/BI dashboard with Claude Code, run:

```bash
claude code "Create a Databricks AI/BI Dashboard for Apps Telemetry following the detailed specifications in CLAUDE_CODE_PROMPT_AIBI.md. The dashboard should include all KPI cards, charts, tables, global filters, AI features, alerts, and scheduled exports as specified. Ensure the dashboard is production-ready and follows best practices for AI/BI dashboards."
```

Since AI/BI dashboards are created through the Databricks UI, Claude Code should:
1. Generate all necessary SQL queries and views
2. Create a detailed implementation guide
3. Provide step-by-step UI instructions
4. Generate alert and export configurations
5. Create testing scripts to validate data
6. Document the dashboard structure

## Additional Resources

- **Databricks AI/BI Documentation**: https://docs.databricks.com/ai-bi/index.html
- **SQL Warehouse Setup**: https://docs.databricks.com/sql/admin/sql-endpoints.html
- **Dashboard Best Practices**: https://docs.databricks.com/dashboards/index.html
- **Natural Language Queries**: https://docs.databricks.com/ai-bi/genie.html
- **System Tables Reference**: https://docs.databricks.com/admin/system-tables/index.html

## Success Indicators

The dashboard is successful when:
1. ✅ Executives can answer key business questions at a glance
2. ✅ Natural language queries work intuitively
3. ✅ Alerts catch issues before they become critical
4. ✅ Auto-insights surface actionable patterns
5. ✅ Mobile access works seamlessly
6. ✅ Scheduled exports arrive reliably
7. ✅ Dashboard loads in <5 seconds
8. ✅ All stakeholders can self-serve analytics
9. ✅ Data quality is trusted and validated
10. ✅ Dashboard drives actual business decisions

Good luck building your AI/BI dashboard! 🚀📊
