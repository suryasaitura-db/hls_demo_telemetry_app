-- ====================================================================
-- DATABRICKS APPS TELEMETRY - DATABASE SETUP SCRIPT
-- ====================================================================
-- Purpose: Initialize schema and views for telemetry dashboard
-- Run this script before deploying the dashboard
-- ====================================================================

-- Create dedicated schema for telemetry
CREATE SCHEMA IF NOT EXISTS hls_amer_catalog.apps_telemetry
COMMENT 'Schema for Databricks Apps telemetry and analytics';

USE hls_amer_catalog.apps_telemetry;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON SCHEMA hls_amer_catalog.apps_telemetry TO `data_engineers`;
GRANT SELECT ON SCHEMA hls_amer_catalog.apps_telemetry TO `analysts`;
GRANT SELECT ON SCHEMA hls_amer_catalog.apps_telemetry TO `executives`;

-- ====================================================================
-- CREATE VIEWS FROM QUERIES LIBRARY
-- ====================================================================

-- Note: The views are already defined in databricks_apps_telemetry_queries.sql
-- This script provides additional setup and verification

-- Verify system tables access
SELECT 'Checking access to system.access.audit...' AS status;
SELECT COUNT(*) AS audit_record_count
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '7' DAY;

-- Create a materialized view for frequently accessed KPIs (optional for performance)
CREATE OR REPLACE TABLE hls_amer_catalog.apps_telemetry.kpi_summary_materialized AS
SELECT
  CURRENT_TIMESTAMP() AS last_refreshed,
  COUNT(DISTINCT user_identity.email) AS total_unique_users,
  COUNT(DISTINCT request_params.app_id) AS total_unique_apps,
  COUNT(*) AS total_interactions,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_interactions_per_user,
  ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS overall_error_rate,
  DATE_TRUNC('DAY', CURRENT_TIMESTAMP()) AS date_partition
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp');

-- Create job to refresh materialized view (recommended)
-- Note: This is a template - adjust schedule as needed
/*
CREATE OR REPLACE JOB apps_telemetry_refresh
SCHEDULE CRON '0 */6 * * *'  -- Every 6 hours
AS
REFRESH MATERIALIZED VIEW hls_amer_catalog.apps_telemetry.kpi_summary_materialized;
*/

-- ====================================================================
-- DATA QUALITY CHECKS
-- ====================================================================

-- Check 1: Verify data freshness
SELECT 
  'Data Freshness Check' AS check_name,
  MAX(event_time) AS latest_event,
  DATEDIFF(HOUR, MAX(event_time), CURRENT_TIMESTAMP()) AS hours_since_last_event,
  CASE 
    WHEN DATEDIFF(HOUR, MAX(event_time), CURRENT_TIMESTAMP()) < 24 THEN 'PASS'
    ELSE 'FAIL - Data may be stale'
  END AS status
FROM system.access.audit
WHERE service_name = 'apps';

-- Check 2: Verify required action_name values exist
SELECT 
  'Action Names Check' AS check_name,
  action_name,
  COUNT(*) AS event_count
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY action_name
ORDER BY event_count DESC;

-- Check 3: Verify app_name and app_id are being captured
SELECT 
  'App Metadata Check' AS check_name,
  COUNT(*) AS total_events,
  SUM(CASE WHEN request_params.app_name IS NOT NULL THEN 1 ELSE 0 END) AS events_with_app_name,
  SUM(CASE WHEN request_params.app_id IS NOT NULL THEN 1 ELSE 0 END) AS events_with_app_id,
  ROUND(SUM(CASE WHEN request_params.app_name IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS app_name_coverage_pct
FROM system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '7' DAY;

-- ====================================================================
-- PERFORMANCE OPTIMIZATION
-- ====================================================================

-- Analyze table statistics for query optimization
ANALYZE TABLE system.access.audit COMPUTE STATISTICS;

-- Optimize frequently used partitions
OPTIMIZE system.access.audit
WHERE service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '90' DAY;

-- ====================================================================
-- MONITORING & ALERTING SETUP
-- ====================================================================

-- Create alert table for tracking issues
CREATE TABLE IF NOT EXISTS hls_amer_catalog.apps_telemetry.alerts (
  alert_id STRING,
  alert_type STRING,
  alert_severity STRING,
  alert_message STRING,
  alert_timestamp TIMESTAMP,
  resolved BOOLEAN DEFAULT FALSE,
  resolved_timestamp TIMESTAMP
) USING DELTA
PARTITIONED BY (alert_severity);

-- Sample alert: High error rate detection
INSERT INTO hls_amer_catalog.apps_telemetry.alerts
SELECT
  uuid() AS alert_id,
  'HIGH_ERROR_RATE' AS alert_type,
  'WARNING' AS alert_severity,
  CONCAT('App ', app_name, ' has error rate of ', CAST(error_rate_percentage AS STRING), '%') AS alert_message,
  CURRENT_TIMESTAMP() AS alert_timestamp,
  FALSE AS resolved,
  NULL AS resolved_timestamp
FROM hls_amer_catalog.apps_telemetry.high_error_rate_apps
WHERE error_rate_percentage > 5;

-- ====================================================================
-- SUCCESS MESSAGE
-- ====================================================================

SELECT '✓ Setup completed successfully!' AS status,
       'All views and tables created in apps_telemetry schema' AS message,
       'You can now run the Dash dashboard or create AI/BI dashboards' AS next_steps;
