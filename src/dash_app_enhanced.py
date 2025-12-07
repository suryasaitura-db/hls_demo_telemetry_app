"""
====================================================================
DATABRICKS APPS TELEMETRY - ENHANCED EXECUTIVE DASHBOARD
====================================================================
Purpose: Multi-tab executive dashboard for Databricks Apps telemetry
         with leadership-focused metrics, modern UI, and embedded
         Databricks AI/BI dashboards
Framework: Plotly Dash with Databricks SQL connector
Version: 2.1.0
Created: 2025-11-08
Updated: 2025-12-07
====================================================================
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from databricks import sql
from databricks.sdk.core import Config as DBConfig
import os
import yaml
from pathlib import Path

# ====================================================================
# ENVIRONMENT VALIDATION (same as original working app)
# ====================================================================
# Ensure required environment variables are set
assert os.getenv('DATABRICKS_WAREHOUSE_ID'), "DATABRICKS_WAREHOUSE_ID must be set in app.yaml"

# Get catalog and schema from environment (with defaults)
CATALOG = os.getenv('ANALYTICS_CATALOG', 'hls_amer_catalog')
SCHEMA = os.getenv('ANALYTICS_SCHEMA', 'apps_telemetry')

print(f"Starting HLS Apps Analytics Hub...")
print(f"  Warehouse ID: {os.getenv('DATABRICKS_WAREHOUSE_ID')}")
print(f"  Catalog: {CATALOG}")
print(f"  Schema: {SCHEMA}")

# ====================================================================
# CONFIGURATION
# ====================================================================

def load_dashboard_config():
    """Load dashboard configuration from YAML file"""
    config_paths = [
        Path(__file__).parent / 'dashboard_config.yaml',
        Path('/Workspace') / 'dashboard_config.yaml',
        Path.cwd() / 'dashboard_config.yaml',
    ]

    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")

    # Return default config if file not found
    return {
        'dashboards': {},
        'tab_order': ['apps_usage', 'cost_roi', 'security', 'weekly_trends'],
        'theme': {},
        'refresh': {'interval_ms': 300000, 'auto_refresh_enabled': True},
        'workspace': {'workspace_id': '1602460480284688', 'warehouse_id': '4b28691c780d9875'}
    }

# Load configuration at startup
DASHBOARD_CONFIG = load_dashboard_config()


class AppConfig:
    """Dashboard configuration with enhanced theming"""

    # Databricks connection settings
    DATABRICKS_SERVER_HOSTNAME = os.getenv('DATABRICKS_SERVER_HOSTNAME')
    DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')
    DATABRICKS_TOKEN = os.getenv('DATABRICKS_ACCESS_TOKEN')
    WAREHOUSE_ID = os.getenv('DATABRICKS_WAREHOUSE_ID',
                             DASHBOARD_CONFIG.get('workspace', {}).get('warehouse_id', ''))

    # Catalog/Schema for analytics
    ANALYTICS_CATALOG = os.getenv('ANALYTICS_CATALOG', 'hls_amer_catalog')
    ANALYTICS_SCHEMA = os.getenv('ANALYTICS_SCHEMA', 'apps_telemetry')

    # Workspace filter
    WORKSPACE_ID = DASHBOARD_CONFIG.get('workspace', {}).get('workspace_id', '1602460480284688')

    # Default date ranges
    DEFAULT_DAYS_BACK = 30

    # Refresh intervals (in milliseconds)
    REFRESH_INTERVAL = DASHBOARD_CONFIG.get('refresh', {}).get('interval_ms', 300000)

    # Dashboard URLs from config or environment
    LOGFOOD_DASHBOARD_URL = os.getenv('LOGFOOD_DASHBOARD_URL',
        DASHBOARD_CONFIG.get('dashboards', {}).get('logfood_analytics', {}).get('url', ''))
    INFRASTRUCTURE_DASHBOARD_URL = os.getenv('INFRASTRUCTURE_DASHBOARD_URL',
        DASHBOARD_CONFIG.get('dashboards', {}).get('infrastructure_metrics', {}).get('url', ''))
    EXECUTIVE_DASHBOARD_URL = os.getenv('EXECUTIVE_DASHBOARD_URL',
        DASHBOARD_CONFIG.get('dashboards', {}).get('executive_summary', {}).get('url', ''))

    # ================================================================
    # ENHANCED COLOR SCHEME - Databricks Professional Theme
    # ================================================================
    COLORS = {
        # Primary palette (Databricks-inspired)
        'primary': '#FF3621',        # Databricks Orange-Red
        'primary_dark': '#CC2B1A',   # Darker variant
        'primary_light': '#FF6B5C',  # Lighter variant

        # Secondary palette
        'secondary': '#1B3A57',      # Deep Navy (executive feel)
        'secondary_light': '#2E5780',

        # Semantic colors
        'success': '#00A67E',        # Teal green (modern)
        'warning': '#F5A623',        # Warm amber
        'danger': '#DC3545',         # Standard danger red
        'info': '#0EA5E9',           # Sky blue

        # Neutrals
        'background': '#F8FAFC',     # Slightly cooler gray
        'surface': '#FFFFFF',
        'border': '#E2E8F0',
        'text_primary': '#0F172A',   # Almost black
        'text_secondary': '#64748B', # Muted gray

        # Legacy support (keeping old names for compatibility)
        'text': '#0F172A',
    }

    # Chart color palette for consistent visualizations
    CHART_PALETTE = [
        '#FF3621',  # Databricks red
        '#1B3A57',  # Navy
        '#00A67E',  # Teal
        '#F5A623',  # Amber
        '#0EA5E9',  # Sky blue
        '#8B5CF6',  # Purple
        '#EC4899',  # Pink
        '#14B8A6',  # Cyan
        '#F97316',  # Orange
        '#6366F1',  # Indigo
    ]

    # DBU Cost rate (adjust based on your pricing)
    DBU_COST_RATE = 0.15  # USD per DBU


# ====================================================================
# CUSTOM CSS STYLES
# ====================================================================

CUSTOM_CSS = """
/* ================================================================
   HLS EXECUTIVE DASHBOARD THEME
   ================================================================ */

/* Global Styles */
body {
    background-color: #F8FAFC;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Navbar Styling */
.navbar-executive {
    background: linear-gradient(135deg, #1B3A57 0%, #2E5780 100%) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    padding: 0.75rem 1rem;
}

.navbar-brand-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: #FFFFFF !important;
    letter-spacing: -0.5px;
}

.navbar-subtitle {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.7);
    margin-left: 1rem;
}

/* Tab Navigation */
.nav-tabs-executive {
    border-bottom: 2px solid #E2E8F0;
    background: #FFFFFF;
    padding: 0 1rem;
    border-radius: 12px 12px 0 0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.03);
}

.nav-tabs-executive .nav-link {
    color: #64748B;
    border: none;
    border-bottom: 3px solid transparent;
    padding: 1rem 1.5rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: all 0.2s ease;
    margin-bottom: -2px;
}

.nav-tabs-executive .nav-link:hover {
    color: #1B3A57;
    border-bottom-color: #E2E8F0;
    background: transparent;
}

.nav-tabs-executive .nav-link.active {
    color: #FF3621 !important;
    border-bottom-color: #FF3621 !important;
    background: transparent !important;
}

/* Executive KPI Cards */
.kpi-card-executive {
    border: none;
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    overflow: hidden;
    background: #FFFFFF;
}

.kpi-card-executive:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12), 0 8px 24px rgba(0,0,0,0.08);
}

.kpi-card-executive .card-body {
    padding: 1.25rem;
}

.kpi-icon-container {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.75rem;
}

.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}

.kpi-label {
    font-size: 0.8rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 500;
}

.kpi-change {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    margin-top: 0.5rem;
    display: inline-block;
}

.kpi-change-positive {
    background: rgba(0, 166, 126, 0.1);
    color: #00A67E;
}

.kpi-change-negative {
    background: rgba(220, 53, 69, 0.1);
    color: #DC3545;
}

.kpi-change-neutral {
    background: rgba(100, 116, 139, 0.1);
    color: #64748B;
}

/* Section Headers */
.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1B3A57;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
}

.section-header::before {
    content: '';
    width: 4px;
    height: 20px;
    background: #FF3621;
    border-radius: 2px;
    margin-right: 0.75rem;
}

/* Chart Cards */
.chart-card {
    background: #FFFFFF;
    border: none;
    border-radius: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 2px 8px rgba(0,0,0,0.04);
    overflow: hidden;
}

.chart-card .card-header {
    background: transparent;
    border-bottom: 1px solid #E2E8F0;
    padding: 1rem 1.25rem;
}

.chart-card .card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #1B3A57;
    margin-bottom: 0;
}

.chart-card .card-subtitle {
    font-size: 0.8rem;
    color: #64748B;
}

/* Data Tables */
.table-executive {
    font-size: 0.875rem;
}

.table-executive thead th {
    background: #F8FAFC;
    color: #1B3A57;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    padding: 0.875rem 1rem;
    border-bottom: 2px solid #E2E8F0;
}

.table-executive tbody td {
    padding: 0.75rem 1rem;
    vertical-align: middle;
    border-bottom: 1px solid #F1F5F9;
}

.table-executive tbody tr:hover {
    background: #F8FAFC;
}

/* Segment Badges */
.segment-badge {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.segment-power {
    background: linear-gradient(135deg, #FF3621 0%, #FF6B5C 100%);
    color: white;
}

.segment-active {
    background: linear-gradient(135deg, #00A67E 0%, #14B8A6 100%);
    color: white;
}

.segment-regular {
    background: linear-gradient(135deg, #F5A623 0%, #F97316 100%);
    color: white;
}

.segment-casual {
    background: #E2E8F0;
    color: #64748B;
}

/* Filter Controls */
.filter-card {
    background: #FFFFFF;
    border: none;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
}

.filter-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}

/* Status Indicators */
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.status-healthy { background: #00A67E; }
.status-warning { background: #F5A623; }
.status-critical { background: #DC3545; }

/* Loading Spinner */
.dash-spinner {
    color: #FF3621 !important;
}

/* Footer */
.dashboard-footer {
    background: #F8FAFC;
    border-top: 1px solid #E2E8F0;
    padding: 1rem 0;
    margin-top: 2rem;
    font-size: 0.8rem;
    color: #64748B;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .kpi-value {
        font-size: 1.5rem;
    }

    .nav-tabs-executive .nav-link {
        padding: 0.75rem 1rem;
        font-size: 0.8rem;
    }
}
"""

# ====================================================================
# DATABASE CONNECTION - Using same pattern as working original app
# ====================================================================

# Initialize Databricks SDK config (same as original working app)
cfg = DBConfig()

def sql_query(query: str) -> pd.DataFrame:
    """Execute a SQL query and return result as pandas DataFrame.
    Uses the exact same pattern as the original working app.
    """
    try:
        with sql.connect(
            server_hostname=cfg.host,
            http_path=f"/sql/1.0/warehouses/{os.getenv('DATABRICKS_WAREHOUSE_ID')}",
            credentials_provider=lambda: cfg.authenticate
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall_arrow().to_pandas()
    except Exception as e:
        print(f"Query failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


class DatabricksConnection:
    """Wrapper class for backward compatibility with enhanced app structure"""

    def __init__(self):
        self.connection = None

    def execute_query(self, query):
        """Execute SQL query using the simple sql_query function"""
        return sql_query(query)

    def connect(self):
        """Connection is handled per-query in sql_query function"""
        return True

    def close(self):
        """Connection is handled per-query, nothing to close"""
        pass

# Initialize connection wrapper
db_conn = DatabricksConnection()

# ====================================================================
# DATA QUERIES - Enhanced with Leadership Metrics
# ====================================================================

class DataQueries:
    """SQL queries for dashboard data including executive metrics"""

    WORKSPACE_FILTER = f"AND workspace_id = '{AppConfig.WORKSPACE_ID}'"

    # ================================================================
    # CORE TELEMETRY QUERIES
    # ================================================================

    @staticmethod
    def get_kpi_summary(days_back=30):
        return f"""
        WITH current_period AS (
            SELECT
                COUNT(DISTINCT user_identity.email) AS total_unique_users,
                COUNT(DISTINCT request_params.app_id) AS total_unique_apps,
                COUNT(*) AS total_interactions,
                ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_interactions_per_user,
                ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS overall_error_rate
            FROM system.access.audit
            WHERE service_name = 'apps'
                AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
                AND event_date < CURRENT_DATE
                {DataQueries.WORKSPACE_FILTER}
        ),
        previous_period AS (
            SELECT
                COUNT(DISTINCT user_identity.email) AS prev_users,
                COUNT(*) AS prev_interactions
            FROM system.access.audit
            WHERE service_name = 'apps'
                AND event_date >= CURRENT_DATE - INTERVAL '{days_back * 2}' DAY
                AND event_date < CURRENT_DATE - INTERVAL '{days_back}' DAY
                {DataQueries.WORKSPACE_FILTER}
        )
        SELECT
            c.*,
            p.prev_users,
            p.prev_interactions,
            ROUND((c.total_unique_users - p.prev_users) * 100.0 / NULLIF(p.prev_users, 0), 1) AS user_growth_pct,
            ROUND((c.total_interactions - p.prev_interactions) * 100.0 / NULLIF(p.prev_interactions, 0), 1) AS interaction_growth_pct
        FROM current_period c
        CROSS JOIN previous_period p
        """

    @staticmethod
    def get_dau_trend(days_back=90):
        return f"""
        SELECT
            DATE(event_time) AS activity_date,
            COUNT(DISTINCT user_identity.email) AS daily_active_users,
            COUNT(*) AS total_clicks,
            COUNT(DISTINCT request_params.app_id) AS apps_accessed
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY DATE(event_time)
        ORDER BY activity_date ASC
        """

    @staticmethod
    def get_top_apps(days_back=30, limit=10):
        return f"""
        SELECT
            COALESCE(request_params.app_name, request_params.app_id, 'Unknown App') AS app_name,
            COUNT(*) AS click_count,
            COUNT(DISTINCT user_identity.email) AS unique_users,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total,
            COUNT(DISTINCT DATE(event_time)) AS active_days
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY COALESCE(request_params.app_name, request_params.app_id, 'Unknown App')
        ORDER BY click_count DESC
        LIMIT {limit}
        """

    @staticmethod
    def get_usage_heatmap(days_back=30):
        return f"""
        SELECT
            DAYOFWEEK(event_time) AS day_of_week,
            CASE DAYOFWEEK(event_time)
                WHEN 1 THEN 'Sunday'
                WHEN 2 THEN 'Monday'
                WHEN 3 THEN 'Tuesday'
                WHEN 4 THEN 'Wednesday'
                WHEN 5 THEN 'Thursday'
                WHEN 6 THEN 'Friday'
                WHEN 7 THEN 'Saturday'
            END AS day_name,
            HOUR(event_time) AS hour_of_day,
            COUNT(*) AS click_count
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY DAYOFWEEK(event_time), day_name, HOUR(event_time)
        ORDER BY day_of_week, hour_of_day
        """

    @staticmethod
    def get_user_cohorts(days_back=30):
        return f"""
        WITH user_first_interaction AS (
            SELECT
                user_identity.email,
                MIN(DATE(event_time)) AS first_interaction_date
            FROM system.access.audit
            WHERE service_name = 'apps'
                {DataQueries.WORKSPACE_FILTER}
            GROUP BY user_identity.email
        )
        SELECT
            DATE(a.event_time) AS activity_date,
            COUNT(DISTINCT CASE WHEN DATE(a.event_time) = ufi.first_interaction_date THEN a.user_identity.email END) AS new_users,
            COUNT(DISTINCT CASE WHEN DATE(a.event_time) > ufi.first_interaction_date THEN a.user_identity.email END) AS returning_users,
            COUNT(DISTINCT a.user_identity.email) AS total_users
        FROM system.access.audit a
        JOIN user_first_interaction ufi ON a.user_identity.email = ufi.email
        WHERE a.service_name = 'apps'
            AND a.event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER.replace('AND', 'AND a.')}
        GROUP BY DATE(a.event_time)
        ORDER BY activity_date ASC
        """

    @staticmethod
    def get_error_monitoring(days_back=30):
        return f"""
        SELECT
            DATE(event_time) AS activity_date,
            COUNT(*) AS total_requests,
            SUM(CASE WHEN response.status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) AS successful_requests,
            SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) AS failed_requests,
            ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS error_rate_percentage
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY DATE(event_time)
        ORDER BY activity_date ASC
        """

    @staticmethod
    def get_user_segmentation(days_back=30, limit=100):
        return f"""
        SELECT
            user_identity.email AS user_email,
            COUNT(DISTINCT request_params.app_id) AS apps_accessed,
            COUNT(*) AS total_clicks,
            COUNT(DISTINCT DATE(event_time)) AS days_active,
            ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT DATE(event_time)), 0), 2) AS avg_clicks_per_day,
            MAX(event_time) AS last_interaction,
            CASE
                WHEN COUNT(*) >= 100 THEN 'Power User'
                WHEN COUNT(*) >= 50 THEN 'Active User'
                WHEN COUNT(*) >= 10 THEN 'Regular User'
                ELSE 'Casual User'
            END AS user_segment
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY user_identity.email
        ORDER BY total_clicks DESC
        LIMIT {limit}
        """

    # ================================================================
    # EXECUTIVE/LEADERSHIP METRICS QUERIES
    # ================================================================

    @staticmethod
    def get_executive_summary(days_back=30):
        """High-level metrics for executive view"""
        return f"""
        WITH metrics AS (
            SELECT
                COUNT(DISTINCT user_identity.email) AS total_users,
                COUNT(DISTINCT request_params.app_id) AS total_apps,
                COUNT(*) AS total_interactions,
                SUM(CASE WHEN response.status_code >= 400 THEN 1 ELSE 0 END) AS total_errors,
                COUNT(DISTINCT DATE(event_time)) AS active_days
            FROM system.access.audit
            WHERE service_name = 'apps'
                AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
                {DataQueries.WORKSPACE_FILTER}
        ),
        power_users AS (
            SELECT COUNT(DISTINCT user_identity.email) AS power_user_count
            FROM system.access.audit
            WHERE service_name = 'apps'
                AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
                {DataQueries.WORKSPACE_FILTER}
            GROUP BY user_identity.email
            HAVING COUNT(*) >= 100
        )
        SELECT
            m.*,
            ROUND((m.active_days * 100.0 / {days_back}), 1) AS uptime_percentage,
            ROUND(100.0 - (m.total_errors * 100.0 / NULLIF(m.total_interactions, 0)), 2) AS success_rate,
            COALESCE((SELECT COUNT(*) FROM power_users), 0) AS power_user_count,
            ROUND(COALESCE((SELECT COUNT(*) FROM power_users), 0) * 100.0 / NULLIF(m.total_users, 0), 1) AS power_user_ratio
        FROM metrics m
        """

    @staticmethod
    def get_cost_metrics(days_back=30):
        """Cost and DBU tracking from billing table"""
        return f"""
        SELECT
            DATE(usage_date) AS date,
            COALESCE(usage_metadata.app_name, 'Unknown') AS app_name,
            sku_name,
            SUM(usage_quantity) AS total_dbus,
            ROUND(SUM(usage_quantity) * {AppConfig.DBU_COST_RATE}, 2) AS estimated_cost_usd
        FROM system.billing.usage
        WHERE usage_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            AND (usage_metadata.app_name IS NOT NULL OR sku_name LIKE '%APP%')
        GROUP BY DATE(usage_date), COALESCE(usage_metadata.app_name, 'Unknown'), sku_name
        ORDER BY date DESC, total_dbus DESC
        """

    @staticmethod
    def get_cost_summary(days_back=30):
        """Aggregated cost summary"""
        return f"""
        SELECT
            SUM(usage_quantity) AS total_dbus,
            ROUND(SUM(usage_quantity) * {AppConfig.DBU_COST_RATE}, 2) AS total_cost_usd,
            COUNT(DISTINCT usage_metadata.app_name) AS apps_with_cost,
            ROUND(AVG(usage_quantity), 2) AS avg_daily_dbus
        FROM system.billing.usage
        WHERE usage_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            AND (usage_metadata.app_name IS NOT NULL OR sku_name LIKE '%APP%')
        """

    @staticmethod
    def get_security_events(days_back=30):
        """Security-relevant events from audit log"""
        return f"""
        SELECT
            DATE(event_time) AS date,
            action_name,
            COUNT(*) AS event_count,
            COUNT(DISTINCT user_identity.email) AS unique_users,
            SUM(CASE WHEN response.status_code >= 400 THEN 1 ELSE 0 END) AS failed_count
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            AND action_name IN ('loginApp', 'updateAppPermissions', 'deleteApp', 'createApp', 'deployApp')
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY DATE(event_time), action_name
        ORDER BY date DESC, event_count DESC
        """

    @staticmethod
    def get_app_lifecycle_events(days_back=30):
        """App creation, deployment, deletion events"""
        return f"""
        SELECT
            DATE(event_time) AS date,
            action_name,
            COALESCE(request_params.app_name, request_params.app_id) AS app_name,
            user_identity.email AS performed_by,
            response.status_code,
            event_time
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
            AND action_name IN ('createApp', 'deleteApp', 'deployApp', 'startApp', 'stopApp')
            {DataQueries.WORKSPACE_FILTER}
        ORDER BY event_time DESC
        LIMIT 50
        """

    @staticmethod
    def get_weekly_trends(weeks_back=12):
        """Week-over-week trends for leadership reporting"""
        return f"""
        SELECT
            DATE_TRUNC('week', event_time) AS week_start,
            COUNT(DISTINCT user_identity.email) AS weekly_users,
            COUNT(*) AS weekly_interactions,
            COUNT(DISTINCT request_params.app_id) AS weekly_active_apps,
            ROUND(SUM(CASE WHEN response.status_code >= 400 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS weekly_error_rate
        FROM system.access.audit
        WHERE service_name = 'apps'
            AND event_date >= CURRENT_DATE - INTERVAL '{weeks_back * 7}' DAY
            {DataQueries.WORKSPACE_FILTER}
        GROUP BY DATE_TRUNC('week', event_time)
        ORDER BY week_start ASC
        """


# ====================================================================
# DASH APP INITIALIZATION
# ====================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="HLS Apps Analytics Hub",
    update_title="Loading..."
)

# Inject custom CSS
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
        {CUSTOM_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# ====================================================================
# LAYOUT COMPONENTS
# ====================================================================

def create_executive_kpi_card(title, value, change=None, icon="graph-up", color=None):
    """Create an executive-style KPI card"""

    if color is None:
        color = AppConfig.COLORS['primary']

    # Determine change styling
    change_element = html.Div()
    if change is not None:
        if isinstance(change, (int, float)):
            change_class = "kpi-change-positive" if change >= 0 else "kpi-change-negative"
            change_text = f"+{change}%" if change >= 0 else f"{change}%"
        else:
            change_class = "kpi-change-neutral"
            change_text = str(change)

        change_element = html.Span(change_text, className=f"kpi-change {change_class}")

    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi bi-{icon}", style={'fontSize': '1.5rem', 'color': color})
            ], className="kpi-icon-container", style={'backgroundColor': f"{color}15"}),
            html.Div(value, className="kpi-value"),
            html.Div(title, className="kpi-label"),
            change_element
        ])
    ], className="kpi-card-executive h-100")


def create_header():
    """Create executive dashboard header"""
    return dbc.Navbar([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-bar-chart-line-fill me-3",
                               style={'fontSize': '1.75rem', 'color': '#FF3621'}),
                        html.Span("HLS Apps Analytics Hub", className="navbar-brand-text"),
                        html.Span("Executive Dashboard", className="navbar-subtitle d-none d-md-inline")
                    ], className="d-flex align-items-center")
                ], width="auto"),
            ], align="center", className="g-0 flex-grow-1"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span(id='connection-status', className="me-3"),
                        html.I(className="bi bi-clock me-1", style={'color': 'rgba(255,255,255,0.6)'}),
                        html.Span(id='last-update-time', className="small",
                                  style={'color': 'rgba(255,255,255,0.8)'})
                    ], className="d-flex align-items-center")
                ], width="auto")
            ], align="center", className="g-0")
        ], fluid=True, className="d-flex justify-content-between")
    ], className="navbar-executive mb-4", dark=True)


def create_filters():
    """Create filter controls"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div("Date Range", className="filter-label"),
                dcc.Dropdown(
                    id='date-range-dropdown',
                    options=[
                        {'label': 'Last 7 Days', 'value': 7},
                        {'label': 'Last 30 Days', 'value': 30},
                        {'label': 'Last 90 Days', 'value': 90},
                        {'label': 'Last 6 Months', 'value': 180},
                    ],
                    value=30,
                    clearable=False,
                    className="filter-dropdown"
                )
            ], md=2),
            dbc.Col([
                html.Div("Auto Refresh", className="filter-label"),
                dbc.Switch(
                    id='auto-refresh-switch',
                    label="Enabled",
                    value=True,
                    className="mt-2"
                )
            ], md=2),
            dbc.Col([
                html.Div("\u00A0", className="filter-label"),
                dbc.Button([
                    html.I(className="bi bi-arrow-clockwise me-2"),
                    "Refresh"
                ], id='refresh-button', color="primary", className="w-100")
            ], md=2),
            dbc.Col([
                html.Div("\u00A0", className="filter-label"),
                dbc.Button([
                    html.I(className="bi bi-download me-2"),
                    "Export"
                ], id='export-button', color="secondary", outline=True, className="w-100")
            ], md=2),
        ], className="align-items-end")
    ], className="filter-card")


def create_chart_card(title, chart_id, subtitle=None, height=400):
    """Create a styled chart card"""
    header_content = [html.H5(title, className="card-title mb-0")]
    if subtitle:
        header_content.append(html.Small(subtitle, className="card-subtitle text-muted"))

    return dbc.Card([
        dbc.CardHeader(html.Div(header_content)),
        dbc.CardBody([
            dcc.Loading(
                dcc.Graph(id=chart_id, style={'height': f'{height}px'}),
                type="circle",
                color=AppConfig.COLORS['primary']
            )
        ])
    ], className="chart-card h-100")


# ====================================================================
# TAB CONTENT LAYOUTS
# ====================================================================

def create_apps_telemetry_tab():
    """Apps Usage Telemetry tab content"""
    return html.Div([
        # KPI Row
        html.Div("Key Performance Indicators", className="section-header"),
        dbc.Row([
            dbc.Col(html.Div(id='kpi-card-users'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-apps'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-interactions'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-error-rate'), lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Charts Row 1
        html.Div("Usage Trends", className="section-header"),
        dbc.Row([
            dbc.Col([
                create_chart_card("Daily Active Users", "dau-trend-chart", "Last 90 days")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_chart_card("Top Apps by Engagement", "top-apps-chart", "By click count")
            ], lg=6, className="mb-4"),
        ]),

        # Heatmap Row
        html.Div("Usage Patterns", className="section-header"),
        dbc.Row([
            dbc.Col([
                create_chart_card("Activity Heatmap", "usage-heatmap", "By day and hour", height=350)
            ], lg=12, className="mb-4"),
        ]),

        # Charts Row 2
        html.Div("User Behavior & Health", className="section-header"),
        dbc.Row([
            dbc.Col([
                create_chart_card("New vs Returning Users", "user-cohorts-chart")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_chart_card("App Health Monitor", "error-monitoring-chart", "Error rate tracking")
            ], lg=6, className="mb-4"),
        ]),

        # User Table
        html.Div("User Engagement Details", className="section-header"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("User Segmentation", className="card-title mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div(id='user-segmentation-table'),
                            type="circle",
                            color=AppConfig.COLORS['primary']
                        )
                    ])
                ], className="chart-card")
            ], lg=12, className="mb-4"),
        ]),
    ])


def create_cost_roi_tab():
    """Cost & ROI Analysis tab content"""
    return html.Div([
        # Cost KPIs
        html.Div("Cost Overview", className="section-header"),
        dbc.Row([
            dbc.Col(html.Div(id='kpi-card-total-dbus'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-total-cost'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-cost-per-user'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-avg-daily-cost'), lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Cost Charts
        dbc.Row([
            dbc.Col([
                create_chart_card("DBU Consumption Trend", "cost-trend-chart", "Daily DBU usage")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_chart_card("Cost by App", "cost-by-app-chart", "Top consumers")
            ], lg=6, className="mb-4"),
        ]),

        # Cost Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Detailed Cost Breakdown", className="card-title mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div(id='cost-breakdown-table'),
                            type="circle",
                            color=AppConfig.COLORS['primary']
                        )
                    ])
                ], className="chart-card")
            ], lg=12, className="mb-4"),
        ]),
    ])


def create_security_tab():
    """Security & Compliance tab content"""
    return html.Div([
        # Security KPIs
        html.Div("Security Overview", className="section-header"),
        dbc.Row([
            dbc.Col(html.Div(id='kpi-card-login-events'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-permission-changes'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-failed-requests'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-app-deployments'), lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Security Charts
        dbc.Row([
            dbc.Col([
                create_chart_card("Security Events Timeline", "security-timeline-chart")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_chart_card("App Lifecycle Events", "lifecycle-chart")
            ], lg=6, className="mb-4"),
        ]),

        # Recent Events Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Recent App Lifecycle Events", className="card-title mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div(id='lifecycle-events-table'),
                            type="circle",
                            color=AppConfig.COLORS['primary']
                        )
                    ])
                ], className="chart-card")
            ], lg=12, className="mb-4"),
        ]),
    ])


def create_weekly_trends_tab():
    """Weekly Trends & Leadership Report tab"""
    return html.Div([
        # Trend KPIs
        html.Div("Weekly Performance Summary", className="section-header"),
        dbc.Row([
            dbc.Col(html.Div(id='kpi-card-wow-users'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-wow-interactions'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-wow-apps'), lg=3, md=6, className="mb-3"),
            dbc.Col(html.Div(id='kpi-card-wow-error-rate'), lg=3, md=6, className="mb-3"),
        ], className="mb-4"),

        # Trend Charts
        dbc.Row([
            dbc.Col([
                create_chart_card("Weekly User Growth", "weekly-users-chart", "12-week trend", height=350)
            ], lg=12, className="mb-4"),
        ]),

        dbc.Row([
            dbc.Col([
                create_chart_card("Weekly Interactions", "weekly-interactions-chart")
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_chart_card("Weekly Error Rate", "weekly-error-rate-chart")
            ], lg=6, className="mb-4"),
        ]),
    ])


def create_embedded_dashboard_tab(dashboard_key):
    """
    Create an embedded dashboard tab with iframe support.

    Args:
        dashboard_key: Key from dashboard_config.yaml (e.g., 'logfood_analytics')

    Returns:
        Dash HTML component with either iframe or placeholder
    """
    # Get dashboard config
    dashboard_config = DASHBOARD_CONFIG.get('dashboards', {}).get(dashboard_key, {})

    name = dashboard_config.get('name', dashboard_key.replace('_', ' ').title())
    description = dashboard_config.get('description', '')
    icon = dashboard_config.get('icon', 'bar-chart-line')
    url = dashboard_config.get('url', '')
    external_url = dashboard_config.get('external_url', url)
    height = dashboard_config.get('height', 800)
    background = dashboard_config.get('background', '#FFFFFF')
    enabled = dashboard_config.get('enabled', False)

    # Also check environment variables as override
    env_key = f"{dashboard_key.upper()}_URL"
    url = os.getenv(env_key, url)

    if url and enabled:
        # Render iframe with dashboard
        return dbc.Container([
            # Dashboard Header
            html.Div([
                html.I(className=f"bi bi-{icon} me-3",
                       style={'fontSize': '2rem', 'color': AppConfig.COLORS['primary']}),
                html.H2(name, className="mb-1",
                       style={'color': AppConfig.COLORS['secondary'], 'fontSize': '1.8rem', 'fontWeight': '700'}),
                html.P(description,
                       style={'color': AppConfig.COLORS['text_secondary'], 'fontSize': '1rem'})
            ], style={'textAlign': 'center', 'marginBottom': '1.5rem'}),

            # Main Dashboard Container
            dbc.Row([
                dbc.Col([
                    html.Div([
                        # Dashboard Header with controls
                        html.Div([
                            html.Div([
                                html.I(className="bi bi-speedometer2 me-2"),
                                html.H5(name, className="mb-0 d-inline"),
                                dbc.Badge("LIVE", color="success", className="ms-2")
                            ], className="d-flex align-items-center"),
                            html.Div([
                                dbc.Button([
                                    html.I(className="bi bi-arrow-clockwise me-1"),
                                    "Refresh"
                                ], size="sm", color="light", outline=True, className="me-2",
                                id=f"refresh-{dashboard_key}"),
                                dbc.Button([
                                    html.I(className="bi bi-box-arrow-up-right me-1"),
                                    "Open in Databricks"
                                ], size="sm", color="light", outline=True,
                                href=external_url, target="_blank") if external_url else None
                            ], className="d-flex")
                        ], className="d-flex align-items-center justify-content-between p-3",
                        style={
                            'background': f'linear-gradient(135deg, {AppConfig.COLORS["secondary"]} 0%, {AppConfig.COLORS["secondary_light"]} 100%)',
                            'color': 'white',
                            'borderRadius': '12px 12px 0 0'
                        }),

                        # Dashboard iframe
                        html.Iframe(
                            id=f"dashboard-iframe-{dashboard_key}",
                            src=url,
                            style={
                                'width': '100%',
                                'height': f'calc(100vh - 280px)',
                                'border': 'none',
                                'minHeight': f'{height}px',
                                'background': background,
                                'borderRadius': '0 0 12px 12px'
                            }
                        )
                    ], className="dashboard-container",
                    style={
                        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.1)',
                        'borderRadius': '12px',
                        'overflow': 'hidden'
                    })
                ], md=12)
            ])
        ], fluid=True, className="px-4 py-3")

    else:
        # Render placeholder when dashboard not configured
        return html.Div([
            dbc.Container([
                html.Div([
                    html.Div([
                        html.I(className=f"bi bi-{icon}",
                               style={'fontSize': '4rem', 'color': AppConfig.COLORS['border']}),
                        html.H3(f"{name}", className="mt-4 mb-2",
                               style={'color': AppConfig.COLORS['secondary']}),
                        html.P(description or "Dashboard not yet configured",
                               className="text-muted mb-4"),

                        html.Hr(style={'width': '100px', 'margin': '1.5rem auto'}),

                        html.Div([
                            html.H5("Configuration Required", className="mb-3",
                                   style={'color': AppConfig.COLORS['text_primary']}),
                            html.P([
                                "To enable this dashboard, update ",
                                html.Code("dashboard_config.yaml"),
                                " with:"
                            ], className="text-muted"),

                            html.Div([
                                html.Pre(f"""dashboards:
  {dashboard_key}:
    enabled: true
    url: "https://your-workspace.databricks.com/embed/dashboardsv3/YOUR_DASHBOARD_ID"
    external_url: "https://your-workspace.databricks.com/dashboardsv3/YOUR_DASHBOARD_ID"
""", style={
                                    'background': '#F8FAFC',
                                    'padding': '1rem',
                                    'borderRadius': '8px',
                                    'fontSize': '0.85rem',
                                    'textAlign': 'left',
                                    'border': f'1px solid {AppConfig.COLORS["border"]}'
                                })
                            ], style={'maxWidth': '600px', 'margin': '0 auto'}),

                            html.P([
                                html.Strong("Or "),
                                "set the environment variable: ",
                                html.Code(f"{dashboard_key.upper()}_URL")
                            ], className="text-muted mt-3"),
                        ]),

                        html.Div([
                            html.H6("How to get Dashboard Embed URL:", className="mt-4 mb-3",
                                   style={'color': AppConfig.COLORS['secondary']}),
                            html.Ol([
                                html.Li("Open your dashboard in Databricks"),
                                html.Li("Click the 'Share' button (top right)"),
                                html.Li("Select 'Embed' tab"),
                                html.Li("Copy the embed URL"),
                                html.Li("Update the config file and redeploy")
                            ], style={'textAlign': 'left', 'maxWidth': '400px', 'margin': '0 auto'},
                               className="text-muted")
                        ])

                    ], style={
                        'textAlign': 'center',
                        'padding': '4rem 2rem',
                        'background': 'white',
                        'borderRadius': '16px',
                        'boxShadow': '0 2px 8px rgba(0,0,0,0.06)',
                        'border': f'2px dashed {AppConfig.COLORS["border"]}'
                    })
                ], style={'maxWidth': '800px', 'margin': '2rem auto'})
            ], fluid=True)
        ])


def create_logfood_placeholder_tab(tab_name):
    """Legacy placeholder function - redirects to embedded dashboard"""
    if tab_name == "Logfood Analytics":
        return create_embedded_dashboard_tab('logfood_analytics')
    elif tab_name == "Infrastructure Metrics":
        return create_embedded_dashboard_tab('infrastructure_metrics')
    else:
        return create_embedded_dashboard_tab('custom_dashboard_1')


# ====================================================================
# MAIN LAYOUT
# ====================================================================

app.layout = dbc.Container([
    # Data Stores
    dcc.Store(id='kpi-data-store'),
    dcc.Store(id='charts-data-store'),
    dcc.Store(id='cost-data-store'),
    dcc.Store(id='security-data-store'),
    dcc.Store(id='weekly-data-store'),

    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=AppConfig.REFRESH_INTERVAL,
        n_intervals=0
    ),

    # Header
    create_header(),

    # Filters
    create_filters(),

    # Main Tabs
    dbc.Tabs([
        dbc.Tab(
            label="Apps Usage",
            tab_id="tab-apps-usage",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
        dbc.Tab(
            label="Cost & ROI",
            tab_id="tab-cost-roi",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
        dbc.Tab(
            label="Security & Compliance",
            tab_id="tab-security",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
        dbc.Tab(
            label="Weekly Trends",
            tab_id="tab-weekly",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
        dbc.Tab(
            label="Logfood Analytics",
            tab_id="tab-logfood-1",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
        dbc.Tab(
            label="Infrastructure",
            tab_id="tab-logfood-2",
            label_style={"fontWeight": "600"},
            active_label_style={"color": AppConfig.COLORS['primary']}
        ),
    ], id="main-tabs", active_tab="tab-apps-usage", className="nav-tabs-executive mb-4"),

    # Tab Content Container
    html.Div(id="tab-content"),

    # Footer
    html.Footer([
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("HLS Apps Analytics Hub", className="fw-bold me-3"),
                    html.Span("|", className="mx-2 text-muted"),
                    html.Span(f"Workspace: {AppConfig.WORKSPACE_ID}", className="text-muted"),
                    html.Span("|", className="mx-2 text-muted"),
                    html.Span("Data refreshes every 5 minutes", className="text-muted")
                ])
            ], md=8),
            dbc.Col([
                html.Div([
                    html.A("Documentation", href="#", className="text-decoration-none me-3"),
                    html.A("Support", href="#", className="text-decoration-none")
                ], className="text-end")
            ], md=4)
        ])
    ], className="dashboard-footer")

], fluid=True, className="py-3", style={'backgroundColor': AppConfig.COLORS['background']})


# ====================================================================
# CALLBACKS
# ====================================================================

@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'active_tab')
)
def render_tab_content(active_tab):
    """Render content based on active tab"""
    if active_tab == "tab-apps-usage":
        return create_apps_telemetry_tab()
    elif active_tab == "tab-cost-roi":
        return create_cost_roi_tab()
    elif active_tab == "tab-security":
        return create_security_tab()
    elif active_tab == "tab-weekly":
        return create_weekly_trends_tab()
    elif active_tab == "tab-logfood-1":
        return create_embedded_dashboard_tab("logfood_analytics")
    elif active_tab == "tab-logfood-2":
        return create_embedded_dashboard_tab("infrastructure_metrics")
    elif active_tab == "tab-executive":
        return create_embedded_dashboard_tab("executive_summary")
    return html.Div("Select a tab")


@app.callback(
    Output('last-update-time', 'children'),
    Output('connection-status', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks')
)
def update_timestamp(n_intervals, n_clicks):
    """Update last refresh timestamp and connection status"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check connection
    try:
        if db_conn.connection or db_conn.connect():
            status = html.Span([
                html.I(className="bi bi-circle-fill me-1", style={'color': '#00A67E', 'fontSize': '0.5rem'}),
                "Connected"
            ], style={'color': '#00A67E', 'fontSize': '0.75rem'})
        else:
            status = html.Span([
                html.I(className="bi bi-circle-fill me-1", style={'color': '#DC3545', 'fontSize': '0.5rem'}),
                "Disconnected"
            ], style={'color': '#DC3545', 'fontSize': '0.75rem'})
    except:
        status = html.Span([
            html.I(className="bi bi-circle-fill me-1", style={'color': '#F5A623', 'fontSize': '0.5rem'}),
            "Unknown"
        ], style={'color': '#F5A623', 'fontSize': '0.75rem'})

    return now, status


@app.callback(
    [Output('kpi-data-store', 'data'),
     Output('charts-data-store', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks'),
     Input('date-range-dropdown', 'value'),
     Input('main-tabs', 'active_tab')],
    State('auto-refresh-switch', 'value')
)
def fetch_telemetry_data(n_intervals, n_clicks, days_back, active_tab, auto_refresh):
    """Fetch telemetry data for Apps Usage tab"""

    ctx = dash.callback_context

    # Handle interval-only refresh when auto-refresh is disabled
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'interval-component' and not auto_refresh:
            return dash.no_update, dash.no_update

    # Skip data fetch if not on apps usage tab (but still load on initial)
    if ctx.triggered and active_tab != "tab-apps-usage":
        # Only skip if this is a tab change, not initial load
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'main-tabs':
            return dash.no_update, dash.no_update

    # Default days_back if None
    if days_back is None:
        days_back = 30

    print(f"Fetching telemetry data for {days_back} days...")

    try:
        # Fetch KPI data
        kpi_df = db_conn.execute_query(DataQueries.get_kpi_summary(days_back))
        kpi_data = kpi_df.to_dict('records')[0] if not kpi_df.empty else {}
        print(f"KPI data: {kpi_data}")

        # Fetch charts data
        charts_data = {
            'dau_trend': db_conn.execute_query(DataQueries.get_dau_trend(min(days_back * 3, 90))).to_dict('records'),
            'top_apps': db_conn.execute_query(DataQueries.get_top_apps(days_back)).to_dict('records'),
            'usage_heatmap': db_conn.execute_query(DataQueries.get_usage_heatmap(days_back)).to_dict('records'),
            'user_cohorts': db_conn.execute_query(DataQueries.get_user_cohorts(days_back)).to_dict('records'),
            'error_monitoring': db_conn.execute_query(DataQueries.get_error_monitoring(days_back)).to_dict('records'),
            'user_segmentation': db_conn.execute_query(DataQueries.get_user_segmentation(days_back)).to_dict('records')
        }
        print(f"Charts data loaded: {list(charts_data.keys())}")

        return kpi_data, charts_data
    except Exception as e:
        print(f"Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        return {}, {}


# ================================================================
# KPI CARD CALLBACKS
# ================================================================

@app.callback(
    [Output('kpi-card-users', 'children'),
     Output('kpi-card-apps', 'children'),
     Output('kpi-card-interactions', 'children'),
     Output('kpi-card-error-rate', 'children')],
    Input('kpi-data-store', 'data')
)
def update_kpi_cards(kpi_data):
    """Update main KPI cards"""
    if not kpi_data:
        return [create_executive_kpi_card("Loading...", "-", None, "hourglass")] * 4

    card_users = create_executive_kpi_card(
        "Total Users",
        f"{kpi_data.get('total_unique_users', 0):,}",
        kpi_data.get('user_growth_pct'),
        "people-fill",
        AppConfig.COLORS['primary']
    )

    card_apps = create_executive_kpi_card(
        "Active Apps",
        f"{kpi_data.get('total_unique_apps', 0):,}",
        None,
        "grid-3x3-gap-fill",
        AppConfig.COLORS['info']
    )

    card_interactions = create_executive_kpi_card(
        "Interactions",
        f"{kpi_data.get('total_interactions', 0):,}",
        kpi_data.get('interaction_growth_pct'),
        "cursor-fill",
        AppConfig.COLORS['success']
    )

    error_rate = kpi_data.get('overall_error_rate', 0)
    card_error = create_executive_kpi_card(
        "Error Rate",
        f"{error_rate:.2f}%",
        "Healthy" if error_rate < 5 else "Needs Attention",
        "shield-check" if error_rate < 5 else "exclamation-triangle-fill",
        AppConfig.COLORS['success'] if error_rate < 5 else AppConfig.COLORS['danger']
    )

    return card_users, card_apps, card_interactions, card_error


# ================================================================
# CHART CALLBACKS
# ================================================================

@app.callback(
    Output('dau-trend-chart', 'figure'),
    Input('charts-data-store', 'data')
)
def update_dau_chart(charts_data):
    """Update DAU trend chart"""
    if not charts_data or 'dau_trend' not in charts_data:
        return go.Figure()

    df = pd.DataFrame(charts_data['dau_trend'])
    if df.empty:
        return go.Figure()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df['activity_date'],
            y=df['daily_active_users'],
            name='Daily Active Users',
            line=dict(color=AppConfig.COLORS['primary'], width=3),
            mode='lines+markers',
            marker=dict(size=4)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df['activity_date'],
            y=df['total_clicks'],
            name='Total Clicks',
            line=dict(color=AppConfig.COLORS['secondary_light'], width=2, dash='dash'),
            mode='lines'
        ),
        secondary_y=True
    )

    fig.update_xaxes(title_text="Date", gridcolor='#E2E8F0')
    fig.update_yaxes(title_text="Daily Active Users", secondary_y=False, gridcolor='#E2E8F0')
    fig.update_yaxes(title_text="Total Clicks", secondary_y=True, gridcolor='#E2E8F0')

    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@app.callback(
    Output('top-apps-chart', 'figure'),
    Input('charts-data-store', 'data')
)
def update_top_apps_chart(charts_data):
    """Update top apps chart"""
    if not charts_data or 'top_apps' not in charts_data:
        return go.Figure()

    df = pd.DataFrame(charts_data['top_apps'])
    if df.empty:
        return go.Figure()

    # Sort for display
    df = df.sort_values('click_count', ascending=True)

    fig = go.Figure(go.Bar(
        y=df['app_name'],
        x=df['click_count'],
        orientation='h',
        marker=dict(
            color=df['unique_users'],
            colorscale=[[0, AppConfig.COLORS['secondary_light']], [1, AppConfig.COLORS['primary']]],
            showscale=True,
            colorbar=dict(title="Users", thickness=15)
        ),
        text=df['click_count'],
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Clicks: %{x:,}<br>Users: %{marker.color:,}<extra></extra>"
    ))

    fig.update_layout(
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=80, t=30, b=20),
        xaxis_title="Total Clicks",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@app.callback(
    Output('usage-heatmap', 'figure'),
    Input('charts-data-store', 'data')
)
def update_usage_heatmap(charts_data):
    """Update usage heatmap"""
    if not charts_data or 'usage_heatmap' not in charts_data:
        return go.Figure()

    df = pd.DataFrame(charts_data['usage_heatmap'])
    if df.empty:
        return go.Figure()

    # Pivot data for heatmap
    heatmap_data = df.pivot(index='day_name', columns='hour_of_day', values='click_count').fillna(0)

    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex([d for d in day_order if d in heatmap_data.index])

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=[f"{h:02d}:00" for h in heatmap_data.columns],
        y=heatmap_data.index,
        colorscale=[[0, '#F8FAFC'], [0.5, AppConfig.COLORS['warning']], [1, AppConfig.COLORS['primary']]],
        hovertemplate='<b>%{y}</b> at %{x}<br>Clicks: %{z:,}<extra></extra>',
        showscale=True,
        colorbar=dict(title="Clicks", thickness=15)
    ))

    fig.update_layout(
        template='plotly_white',
        height=330,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Hour of Day",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@app.callback(
    Output('user-cohorts-chart', 'figure'),
    Input('charts-data-store', 'data')
)
def update_user_cohorts_chart(charts_data):
    """Update user cohorts chart"""
    if not charts_data or 'user_cohorts' not in charts_data:
        return go.Figure()

    df = pd.DataFrame(charts_data['user_cohorts'])
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['activity_date'],
        y=df['new_users'],
        name='New Users',
        stackgroup='one',
        fillcolor=AppConfig.COLORS['primary'],
        line=dict(width=0.5, color=AppConfig.COLORS['primary'])
    ))

    fig.add_trace(go.Scatter(
        x=df['activity_date'],
        y=df['returning_users'],
        name='Returning Users',
        stackgroup='one',
        fillcolor=AppConfig.COLORS['success'],
        line=dict(width=0.5, color=AppConfig.COLORS['success'])
    ))

    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title='Date',
        yaxis_title='User Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@app.callback(
    Output('error-monitoring-chart', 'figure'),
    Input('charts-data-store', 'data')
)
def update_error_monitoring_chart(charts_data):
    """Update error monitoring chart"""
    if not charts_data or 'error_monitoring' not in charts_data:
        return go.Figure()

    df = pd.DataFrame(charts_data['error_monitoring'])
    if df.empty:
        return go.Figure()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df['activity_date'],
            y=df['successful_requests'],
            name='Successful',
            marker_color=AppConfig.COLORS['success'],
            opacity=0.8
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Bar(
            x=df['activity_date'],
            y=df['failed_requests'],
            name='Failed',
            marker_color=AppConfig.COLORS['danger'],
            opacity=0.8
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df['activity_date'],
            y=df['error_rate_percentage'],
            name='Error Rate %',
            line=dict(color=AppConfig.COLORS['warning'], width=3),
            mode='lines+markers',
            marker=dict(size=6)
        ),
        secondary_y=True
    )

    # Add threshold line
    fig.add_hline(
        y=5,
        line_dash="dash",
        line_color=AppConfig.COLORS['danger'],
        annotation_text="5% SLA Threshold",
        annotation_position="top right",
        secondary_y=True
    )

    fig.update_xaxes(title_text="Date", gridcolor='#E2E8F0')
    fig.update_yaxes(title_text="Request Count", secondary_y=False, gridcolor='#E2E8F0')
    fig.update_yaxes(title_text="Error Rate (%)", secondary_y=True, gridcolor='#E2E8F0')

    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


@app.callback(
    Output('user-segmentation-table', 'children'),
    Input('charts-data-store', 'data')
)
def update_user_segmentation_table(charts_data):
    """Update user segmentation table with modern styling"""
    if not charts_data or 'user_segmentation' not in charts_data:
        return html.Div("No data available", className="text-muted text-center py-4")

    df = pd.DataFrame(charts_data['user_segmentation'])
    if df.empty:
        return html.Div("No data available", className="text-muted text-center py-4")

    # Create segment badge
    def get_segment_badge(segment):
        badge_class = {
            'Power User': 'segment-power',
            'Active User': 'segment-active',
            'Regular User': 'segment-regular',
            'Casual User': 'segment-casual'
        }.get(segment, 'segment-casual')
        return html.Span(segment, className=f"segment-badge {badge_class}")

    # Create table
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("User Email"),
                html.Th("Segment"),
                html.Th("Total Clicks", className="text-end"),
                html.Th("Apps", className="text-end"),
                html.Th("Days Active", className="text-end"),
                html.Th("Avg/Day", className="text-end"),
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(row['user_email'][:40] + "..." if len(str(row['user_email'])) > 40 else row['user_email']),
                html.Td(get_segment_badge(row['user_segment'])),
                html.Td(f"{row['total_clicks']:,}", className="text-end"),
                html.Td(f"{row['apps_accessed']}", className="text-end"),
                html.Td(f"{row['days_active']}", className="text-end"),
                html.Td(f"{row['avg_clicks_per_day']:.1f}", className="text-end"),
            ]) for _, row in df.head(20).iterrows()
        ])
    ], className="table-executive", striped=False, hover=True, responsive=True)

    return table


# ====================================================================
# RUN APP
# ====================================================================

# Expose server for gunicorn/Databricks Apps (if needed)
server = app.server

if __name__ == '__main__':
    # Run with Dash's built-in server (compatible with Databricks Apps)
    app.run(debug=True)
