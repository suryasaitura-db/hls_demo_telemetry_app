# ====================================================================
# CLAUDE CODE PROMPT: DATABRICKS APPS TELEMETRY DASH DASHBOARD
# ====================================================================

## Project Overview

Build a comprehensive, production-ready Dash web application for monitoring Databricks Apps telemetry data. The dashboard should provide real-time insights into app usage, user engagement, error rates, and adoption metrics.

## Context

We need to track how users interact with Databricks Apps deployed in our workspace. Specifically:
- Which apps are being accessed most frequently
- Which users are clicking on app URLs
- Usage patterns (time of day, day of week)
- Error rates and health monitoring
- User segmentation and retention

The data source is the `system.access.audit` table in Databricks, filtered for `service_name = 'apps'`.

## Technical Requirements

### 1. Technology Stack
- **Framework**: Dash with dash-bootstrap-components
- **Visualization**: Plotly Express and Plotly Graph Objects
- **Database**: Databricks SQL Warehouse via databricks-sql-connector
- **Data Processing**: Pandas and NumPy
- **Styling**: Bootstrap 5 theme

### 2. Architecture
```
dash_app.py (main application)
├── Configuration (Config class)
├── Database Connection (DatabricksConnection class)
├── Data Queries (DataQueries class)
├── Layout Components
│   ├── Header
│   ├── Filters
│   ├── KPI Cards
│   ├── Charts
│   └── Tables
└── Callbacks (reactive updates)
```

### 3. Core Features Required

#### A. KPI Summary Cards (Top Row)
Create 4 prominent KPI cards showing:
1. **Total Unique Users** - Count of distinct users accessing apps
2. **Active Apps** - Count of distinct apps being used
3. **Total Interactions** - Total number of app clicks/accesses
4. **Error Rate** - Percentage of failed requests (color-coded: green <5%, red ≥5%)

Each card should:
- Display large, prominent numbers
- Include relevant icon (using Bootstrap Icons)
- Use color coding based on thresholds
- Show trend indicators if possible (up/down arrows)

#### B. Interactive Charts

1. **Daily Active Users Trend (Line Chart)**
   - X-axis: Date
   - Y-axis (primary): Daily Active Users (solid line)
   - Y-axis (secondary): Total Clicks (dashed line)
   - Features: Zoom, pan, hover tooltips
   - Time range: Configurable (7/30/90 days)

2. **Top 10 Apps by Engagement (Horizontal Bar Chart)**
   - Y-axis: App names
   - X-axis: Click count
   - Color: By unique users (gradient)
   - Sorted: Descending by clicks
   - Show values on bars

3. **Usage Patterns Heatmap**
   - X-axis: Hour of day (0-23)
   - Y-axis: Day of week (Mon-Sun)
   - Color intensity: Click volume
   - Color scale: Red-Yellow-Green
   - Tooltip: Shows exact click count

4. **New vs Returning Users (Stacked Area Chart)**
   - X-axis: Date
   - Y-axis: User count
   - Two areas: New users (blue) and Returning users (green)
   - Stacked to show total

5. **App Health Monitor (Combo Chart)**
   - X-axis: Date
   - Y-axis (left): Stacked bars for successful/failed requests
   - Y-axis (right): Error rate % (line)
   - Reference line at 5% error threshold

#### C. User Segmentation Table
Display top 100 users with:
- User email
- Segment badge (Power/Active/Regular/Casual) with color coding
- Activity status (Active/At Risk/Inactive) with color coding
- Total clicks (formatted with commas)
- Apps accessed count
- Days active
- Average clicks per day

Features:
- Sortable columns
- Conditional formatting
- Responsive design
- Pagination (25 rows per page)

#### D. Filters & Controls

1. **Date Range Dropdown**
   - Options: Last 7 Days, Last 30 Days, Last 90 Days
   - Default: Last 30 Days
   - Triggers data refresh on change

2. **Auto-Refresh Toggle**
   - Switch to enable/disable auto-refresh
   - Default: Enabled
   - Interval: 5 minutes

3. **Manual Refresh Button**
   - Button to trigger immediate data refresh
   - Shows loading spinner during refresh

4. **Last Update Timestamp**
   - Display in header
   - Format: YYYY-MM-DD HH:MM:SS

### 4. Database Queries

Use the pre-defined queries in `DataQueries` class:
- `get_kpi_summary(days_back)` - KPI metrics
- `get_dau_trend(days_back)` - Daily active users over time
- `get_top_apps(days_back, limit)` - Top apps by usage
- `get_usage_heatmap(days_back)` - Hour/day usage patterns
- `get_user_cohorts(days_back)` - New vs returning users
- `get_error_monitoring(days_back)` - Error rates over time
- `get_user_segmentation(days_back, limit)` - User engagement levels

All queries should:
- Use parameterized date ranges
- Filter for `service_name = 'apps'`
- Include relevant action_names: openApp, startApp, accessApp, viewApp, executeApp
- Handle null values gracefully
- Return empty DataFrames on errors (no crashes)

### 5. User Experience Requirements

#### Performance
- Initial load: <5 seconds
- Chart updates: <2 seconds
- Use data stores (dcc.Store) for caching
- Lazy loading with dcc.Loading components

#### Responsiveness
- Mobile-friendly layout
- Collapsible sections on small screens
- Responsive grid system (Bootstrap)
- Touch-friendly controls

#### Visual Design
- Clean, professional appearance
- Consistent color scheme (defined in Config.COLORS)
- Adequate whitespace
- Clear hierarchy
- Accessible (WCAG AA compliant)

#### Error Handling
- Graceful degradation on query failures
- User-friendly error messages
- Loading states for all data operations
- Connection retry logic

### 6. Code Quality Standards

- **Type hints**: Use for function parameters and returns
- **Docstrings**: For all classes and functions
- **Comments**: Explain complex logic
- **Error handling**: Try-catch blocks for database operations
- **Logging**: Log errors and important events
- **Constants**: Use Config class, no magic numbers
- **DRY principle**: Reusable components and functions
- **PEP 8**: Follow Python style guide

### 7. Configuration

Environment variables (from .env file):
```
DATABRICKS_SERVER_HOSTNAME=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
DATABRICKS_ACCESS_TOKEN=dapi_your_token_here
```

Application settings:
- Auto-refresh interval: 5 minutes (300000 ms)
- Default date range: 30 days
- Chart height: 400px
- Page size for tables: 25 rows
- Top apps limit: 10

### 8. Deployment

The app should:
- Run on host 0.0.0.0, port 8050
- Support both development (debug=True) and production modes
- Work with gunicorn for production deployment
- Include proper error pages

## Step-by-Step Implementation Guide

### Step 1: Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.template .env

# Edit .env with your Databricks credentials
nano .env
```

### Step 2: Initialize Database
```bash
# Run setup script in Databricks SQL
databricks-sql -f setup_database.sql
```

### Step 3: Test Database Connection
```python
# Verify connection
python -c "from dash_app import db_conn; print(db_conn.connect())"
```

### Step 4: Run Application
```bash
# Development mode
python dash_app.py

# Production mode
gunicorn dash_app:server -b 0.0.0.0:8050 --workers 4
```

### Step 5: Access Dashboard
Navigate to: http://localhost:8050

## Testing Checklist

- [ ] All KPI cards display correct values
- [ ] Charts render without errors
- [ ] Date range filter works correctly
- [ ] Auto-refresh toggles properly
- [ ] Manual refresh updates data
- [ ] Heatmap displays correct day/hour patterns
- [ ] User segmentation table sorts correctly
- [ ] Conditional formatting applies properly
- [ ] Mobile responsive layout works
- [ ] Error handling displays user-friendly messages
- [ ] Loading states show during data fetch
- [ ] Tooltips display on hover
- [ ] All links and buttons function correctly

## Success Criteria

The dashboard is complete when:
1. All visualizations load without errors
2. Data refreshes automatically every 5 minutes
3. Filters update all charts simultaneously
4. Performance meets <5 second load time
5. Layout is responsive on mobile devices
6. Error states are handled gracefully
7. All 6 chart types display correctly
8. User segmentation table is interactive
9. Code follows quality standards
10. Documentation is complete

## Common Pitfalls to Avoid

1. **Database Connection**: Don't create new connections for each query; reuse the connection
2. **Date Handling**: Ensure date columns are properly formatted for Plotly
3. **Empty Data**: Always check for empty DataFrames before rendering charts
4. **Memory Leaks**: Close cursors and clean up resources
5. **Callback Loops**: Be careful with circular dependencies in callbacks
6. **Performance**: Use data stores to avoid redundant queries
7. **Security**: Never commit .env file or credentials to git

## Additional Enhancements (Optional)

If time permits, consider adding:
- Export to CSV/Excel functionality
- Email alerts for high error rates
- Custom date range picker
- User search functionality
- App-specific deep dive pages
- Drill-down capabilities
- Dark mode toggle
- Bookmark/save filter state
- Compare time periods
- Real-time streaming updates

## Files Provided

1. `dash_app.py` - Main application code
2. `requirements.txt` - Python dependencies
3. `.env.template` - Environment variables template
4. `setup_database.sql` - Database initialization script
5. `databricks_apps_telemetry_queries.sql` - SQL query library

## Support & Documentation

- Dash Documentation: https://dash.plotly.com/
- Plotly Documentation: https://plotly.com/python/
- Databricks SQL Connector: https://docs.databricks.com/dev-tools/python-sql-connector.html
- Bootstrap Components: https://dash-bootstrap-components.opensource.faculty.ai/

## Claude Code Execution

To implement this project with Claude Code, run:

```bash
claude code "Build the Databricks Apps Telemetry Dash dashboard following the specifications in CLAUDE_CODE_PROMPT_DASH.md. Start by setting up the environment, then implement the dashboard with all required features including KPI cards, interactive charts, heatmap, and user segmentation table. Ensure all callbacks work correctly and the dashboard is production-ready."
```

The implementation should be iterative:
1. First, set up the basic structure and database connection
2. Then, implement one chart at a time
3. Add interactivity and filters
4. Polish the UI and add error handling
5. Test thoroughly and optimize performance

Good luck! 🚀
