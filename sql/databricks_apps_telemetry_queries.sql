-- ====================================================================
-- DATABRICKS APPS TELEMETRY - SQL QUERIES LIBRARY
-- ====================================================================
-- Purpose: Comprehensive telemetry tracking for Databricks Apps usage
-- Created: 2025-11-08
-- ====================================================================

-- ====================================================================
-- SECTION 1: CORE TELEMETRY QUERIES
-- ====================================================================

-- Query 1.1: Apps Click Tracking - Per User Metrics
-- Purpose: Track all Apps interactions by user with comprehensive click counts
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.user_click_metrics AS
SELECT
  user_identity.email AS user_email,
  COALESCE(request_params.app_name, 'Unknown App') AS app_name,
  COALESCE(request_params.app_id, 'N/A') AS app_id,
  action_name,
  COUNT(*) AS total_clicks,
  COUNT(DISTINCT DATE(event_time)) AS days_active,
  MIN(event_time) AS first_interaction,
  MAX(event_time) AS last_interaction,
  DATEDIFF(DAY, MIN(event_time), MAX(event_time)) + 1 AS engagement_span_days,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT DATE(event_time)), 0), 2) AS avg_clicks_per_day
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY
  user_identity.email,
  request_params.app_name,
  request_params.app_id,
  action_name
ORDER BY
  total_clicks DESC;

-- Query 1.2: Detailed App URL Access Log
-- Purpose: Comprehensive view of App URL access patterns with full context
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.detailed_access_log AS
SELECT
  event_time,
  event_date,
  user_identity.email AS user_email,
  COALESCE(request_params.app_name, 'Unknown App') AS app_name,
  COALESCE(request_params.app_id, 'N/A') AS app_id,
  request_params.url AS app_url,
  action_name,
  source_ip_address,
  user_agent,
  request_id,
  response.status_code,
  response.error_message,
  workspace_id,
  account_id,
  CASE
    WHEN response.status_code BETWEEN 200 AND 299 THEN 'Success'
    WHEN response.status_code BETWEEN 400 AND 499 THEN 'Client Error'
    WHEN response.status_code BETWEEN 500 AND 599 THEN 'Server Error'
    ELSE 'Unknown'
  END AS request_status_category
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '90' DAY
ORDER BY
  event_time DESC;

-- Query 1.3: App Popularity & Adoption Metrics
-- Purpose: Identify top apps by usage with comprehensive adoption metrics
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.app_popularity_metrics AS
SELECT
  COALESCE(request_params.app_name, 'Unknown App') AS app_name,
  COALESCE(request_params.app_id, 'N/A') AS app_id,
  COUNT(DISTINCT user_identity.email) AS unique_users,
  COUNT(*) AS total_interactions,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_clicks_per_user,
  COUNT(DISTINCT DATE(event_time)) AS days_with_activity,
  MIN(event_time) AS first_seen,
  MAX(event_time) AS last_seen,
  DATEDIFF(DAY, MIN(event_time), MAX(event_time)) + 1 AS app_lifespan_days,
  ROUND(COUNT(DISTINCT user_identity.email) * 100.0 / 
    (SELECT COUNT(DISTINCT user_identity.email) 
     FROM system.access.audit 
     WHERE service_name = 'apps' 
     AND event_date >= CURRENT_DATE - INTERVAL '30' DAY), 2) AS user_penetration_rate
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY
  request_params.app_name,
  request_params.app_id
ORDER BY
  total_interactions DESC;

-- ====================================================================
-- SECTION 2: DASHBOARD WIDGET QUERIES
-- ====================================================================

-- Widget 2.1: Daily Active Users Trend (Line Chart)
-- Purpose: Track DAU over time for Apps
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_dau_trend AS
SELECT
  DATE(event_time) AS activity_date,
  COUNT(DISTINCT user_identity.email) AS daily_active_users,
  COUNT(*) AS total_clicks,
  COUNT(DISTINCT request_params.app_id) AS apps_accessed,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_clicks_per_user
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '90' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  DATE(event_time)
ORDER BY
  activity_date ASC;

-- Widget 2.2: Top 10 Apps by Clicks (Bar Chart)
-- Purpose: Identify most popular apps
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_top_apps AS
SELECT
  COALESCE(request_params.app_name, 'Unknown App') AS app_name,
  COUNT(*) AS click_count,
  COUNT(DISTINCT user_identity.email) AS unique_users,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total,
  MAX(event_time) AS last_accessed
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  request_params.app_name
ORDER BY
  click_count DESC
LIMIT 10;

-- Widget 2.3: User Engagement Segmentation (Table)
-- Purpose: Categorize users by engagement level
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_user_segmentation AS
SELECT
  user_identity.email AS user_email,
  COUNT(DISTINCT request_params.app_id) AS apps_accessed,
  COUNT(*) AS total_clicks,
  COUNT(DISTINCT DATE(event_time)) AS days_active,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT DATE(event_time)), 0), 2) AS avg_clicks_per_day,
  MIN(event_time) AS first_interaction,
  MAX(event_time) AS last_interaction,
  CASE
    WHEN COUNT(*) >= 100 THEN 'Power User'
    WHEN COUNT(*) >= 50 THEN 'Active User'
    WHEN COUNT(*) >= 10 THEN 'Regular User'
    ELSE 'Casual User'
  END AS user_segment,
  CASE
    WHEN DATEDIFF(DAY, MAX(event_time), CURRENT_DATE) <= 7 THEN 'Active'
    WHEN DATEDIFF(DAY, MAX(event_time), CURRENT_DATE) <= 30 THEN 'At Risk'
    ELSE 'Inactive'
  END AS activity_status
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  user_identity.email
ORDER BY
  total_clicks DESC;

-- Widget 2.4: Usage Patterns by Hour and Day (Heatmap)
-- Purpose: Identify peak usage times
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_usage_heatmap AS
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
  COUNT(*) AS click_count,
  COUNT(DISTINCT user_identity.email) AS unique_users
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  DAYOFWEEK(event_time),
  day_name,
  HOUR(event_time)
ORDER BY
  day_of_week,
  hour_of_day;

-- Widget 2.5: App Error Rate Monitor (Combo Chart)
-- Purpose: Track success vs error rates
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_error_monitoring AS
SELECT
  DATE(event_time) AS activity_date,
  COUNT(*) AS total_requests,
  SUM(CASE WHEN response.status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) AS successful_requests,
  SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) AS failed_requests,
  ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percentage,
  COUNT(DISTINCT CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN user_identity.email END) AS users_with_errors
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY
  DATE(event_time)
ORDER BY
  activity_date ASC;

-- Widget 2.6: New vs Returning Users (Area Chart)
-- Purpose: Track user cohorts
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_user_cohorts AS
WITH user_first_interaction AS (
  SELECT
    user_identity.email,
    MIN(DATE(event_time)) AS first_interaction_date
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  GROUP BY
    user_identity.email
)
SELECT
  DATE(a.event_time) AS activity_date,
  COUNT(DISTINCT CASE WHEN DATE(a.event_time) = ufi.first_interaction_date THEN a.user_identity.email END) AS new_users,
  COUNT(DISTINCT CASE WHEN DATE(a.event_time) > ufi.first_interaction_date THEN a.user_identity.email END) AS returning_users,
  COUNT(DISTINCT a.user_identity.email) AS total_users
FROM
  system.access.audit a
  JOIN user_first_interaction ufi ON a.user_identity.email = ufi.email
WHERE
  a.service_name = 'apps'
  AND a.event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND a.action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  DATE(a.event_time)
ORDER BY
  activity_date ASC;

-- Widget 2.7: KPI Summary Metrics (Counter Cards)
-- Purpose: Executive summary metrics
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.widget_kpi_summary AS
SELECT
  COUNT(DISTINCT user_identity.email) AS total_unique_users,
  COUNT(DISTINCT request_params.app_id) AS total_unique_apps,
  COUNT(*) AS total_interactions,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_interactions_per_user,
  COUNT(DISTINCT DATE(event_time)) AS days_with_activity,
  ROUND(COUNT(DISTINCT user_identity.email) * 100.0 / 
    (SELECT COUNT(DISTINCT email) 
     FROM system.access.audit 
     WHERE event_date >= CURRENT_DATE - INTERVAL '30' DAY), 2) AS apps_adoption_rate,
  ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS overall_error_rate
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp');

-- ====================================================================
-- SECTION 3: ADVANCED ANALYTICS QUERIES
-- ====================================================================

-- Query 3.1: User Retention Analysis (Weekly Cohorts)
-- Purpose: Track user retention over time
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.user_retention_cohorts AS
WITH weekly_cohorts AS (
  SELECT
    user_identity.email,
    DATE_TRUNC('WEEK', MIN(event_time)) AS cohort_week,
    DATE_TRUNC('WEEK', event_time) AS activity_week
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '90' DAY
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  GROUP BY
    user_identity.email,
    DATE_TRUNC('WEEK', event_time)
)
SELECT
  cohort_week,
  COUNT(DISTINCT CASE WHEN activity_week = cohort_week THEN email END) AS week_0_users,
  COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '1' WEEK THEN email END) AS week_1_users,
  COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '2' WEEK THEN email END) AS week_2_users,
  COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '3' WEEK THEN email END) AS week_3_users,
  COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '4' WEEK THEN email END) AS week_4_users,
  ROUND(COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '1' WEEK THEN email END) * 100.0 / 
    NULLIF(COUNT(DISTINCT CASE WHEN activity_week = cohort_week THEN email END), 0), 2) AS retention_week_1_pct,
  ROUND(COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '2' WEEK THEN email END) * 100.0 / 
    NULLIF(COUNT(DISTINCT CASE WHEN activity_week = cohort_week THEN email END), 0), 2) AS retention_week_2_pct,
  ROUND(COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '3' WEEK THEN email END) * 100.0 / 
    NULLIF(COUNT(DISTINCT CASE WHEN activity_week = cohort_week THEN email END), 0), 2) AS retention_week_3_pct,
  ROUND(COUNT(DISTINCT CASE WHEN activity_week = cohort_week + INTERVAL '4' WEEK THEN email END) * 100.0 / 
    NULLIF(COUNT(DISTINCT CASE WHEN activity_week = cohort_week THEN email END), 0), 2) AS retention_week_4_pct
FROM
  weekly_cohorts
GROUP BY
  cohort_week
ORDER BY
  cohort_week DESC;

-- Query 3.2: App Session Duration Analysis
-- Purpose: Calculate session durations and engagement time
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.app_session_analysis AS
WITH app_sessions AS (
  SELECT
    user_identity.email,
    request_params.app_id,
    COALESCE(request_params.app_name, 'Unknown App') AS app_name,
    event_time,
    LEAD(event_time) OVER (PARTITION BY user_identity.email, request_params.app_id ORDER BY event_time) AS next_event_time,
    TIMESTAMPDIFF(MINUTE, event_time, LEAD(event_time) OVER (PARTITION BY user_identity.email, request_params.app_id ORDER BY event_time)) AS time_to_next_action
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
)
SELECT
  app_name,
  app_id,
  COUNT(*) AS total_sessions,
  ROUND(AVG(CASE WHEN time_to_next_action <= 60 THEN time_to_next_action END), 2) AS avg_session_duration_minutes,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY CASE WHEN time_to_next_action <= 60 THEN time_to_next_action END), 2) AS median_session_duration_minutes,
  ROUND(PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY CASE WHEN time_to_next_action <= 60 THEN time_to_next_action END), 2) AS p90_session_duration_minutes,
  MIN(CASE WHEN time_to_next_action <= 60 THEN time_to_next_action END) AS min_session_duration_minutes,
  MAX(CASE WHEN time_to_next_action <= 60 THEN time_to_next_action END) AS max_session_duration_minutes
FROM
  app_sessions
WHERE
  time_to_next_action IS NOT NULL
GROUP BY
  app_name,
  app_id
ORDER BY
  total_sessions DESC;

-- Query 3.3: App Performance by User Segment
-- Purpose: Compare app usage across user segments
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.app_usage_by_segment AS
WITH user_segments AS (
  SELECT
    user_identity.email,
    CASE
      WHEN COUNT(*) >= 100 THEN 'Power User'
      WHEN COUNT(*) >= 50 THEN 'Active User'
      WHEN COUNT(*) >= 10 THEN 'Regular User'
      ELSE 'Casual User'
    END AS user_segment
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  GROUP BY
    user_identity.email
)
SELECT
  us.user_segment,
  COALESCE(a.request_params.app_name, 'Unknown App') AS app_name,
  COUNT(DISTINCT a.user_identity.email) AS unique_users,
  COUNT(*) AS total_clicks,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT a.user_identity.email), 0), 2) AS avg_clicks_per_user
FROM
  system.access.audit a
  JOIN user_segments us ON a.user_identity.email = us.email
WHERE
  a.service_name = 'apps'
  AND a.event_date >= CURRENT_DATE - INTERVAL '30' DAY
  AND a.action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  us.user_segment,
  a.request_params.app_name
ORDER BY
  us.user_segment,
  total_clicks DESC;

-- Query 3.4: Time-to-First-Action Analysis
-- Purpose: Measure how quickly users engage with apps after deployment
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.time_to_first_action AS
WITH app_first_seen AS (
  SELECT
    request_params.app_id,
    COALESCE(request_params.app_name, 'Unknown App') AS app_name,
    MIN(event_time) AS app_created_at
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
  GROUP BY
    request_params.app_id,
    request_params.app_name
),
user_first_action AS (
  SELECT
    user_identity.email,
    request_params.app_id,
    MIN(event_time) AS first_action_time
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  GROUP BY
    user_identity.email,
    request_params.app_id
)
SELECT
  afs.app_name,
  afs.app_id,
  COUNT(DISTINCT ufa.email) AS total_users,
  ROUND(AVG(TIMESTAMPDIFF(HOUR, afs.app_created_at, ufa.first_action_time)), 2) AS avg_hours_to_first_action,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY TIMESTAMPDIFF(HOUR, afs.app_created_at, ufa.first_action_time)), 2) AS median_hours_to_first_action
FROM
  app_first_seen afs
  JOIN user_first_action ufa ON afs.app_id = ufa.app_id
WHERE
  TIMESTAMPDIFF(HOUR, afs.app_created_at, ufa.first_action_time) >= 0
  AND TIMESTAMPDIFF(HOUR, afs.app_created_at, ufa.first_action_time) <= 720  -- Within 30 days
GROUP BY
  afs.app_name,
  afs.app_id
ORDER BY
  total_users DESC;

-- Query 3.5: User Journey Analysis
-- Purpose: Track typical user paths through apps
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.user_journey_patterns AS
WITH user_actions AS (
  SELECT
    user_identity.email,
    action_name,
    COALESCE(request_params.app_name, 'Unknown App') AS app_name,
    event_time,
    ROW_NUMBER() OVER (PARTITION BY user_identity.email, DATE(event_time) ORDER BY event_time) AS action_sequence
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '7' DAY
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
)
SELECT
  action_sequence,
  action_name,
  app_name,
  COUNT(*) AS occurrence_count,
  COUNT(DISTINCT email) AS unique_users,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY action_sequence), 2) AS percentage_at_step
FROM
  user_actions
WHERE
  action_sequence <= 5  -- First 5 actions
GROUP BY
  action_sequence,
  action_name,
  app_name
ORDER BY
  action_sequence,
  occurrence_count DESC;

-- ====================================================================
-- SECTION 4: ALERTING & MONITORING QUERIES
-- ====================================================================

-- Query 4.1: Anomaly Detection - Unusual Activity Patterns
-- Purpose: Identify unusual spikes or drops in app usage
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.anomaly_detection AS
WITH daily_metrics AS (
  SELECT
    DATE(event_time) AS activity_date,
    COUNT(*) AS daily_clicks,
    COUNT(DISTINCT user_identity.email) AS daily_users
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '30' DAY
  GROUP BY
    DATE(event_time)
),
stats AS (
  SELECT
    AVG(daily_clicks) AS avg_clicks,
    STDDEV(daily_clicks) AS stddev_clicks,
    AVG(daily_users) AS avg_users,
    STDDEV(daily_users) AS stddev_users
  FROM
    daily_metrics
)
SELECT
  dm.activity_date,
  dm.daily_clicks,
  dm.daily_users,
  s.avg_clicks,
  s.avg_users,
  ROUND((dm.daily_clicks - s.avg_clicks) / NULLIF(s.stddev_clicks, 0), 2) AS clicks_z_score,
  ROUND((dm.daily_users - s.avg_users) / NULLIF(s.stddev_users, 0), 2) AS users_z_score,
  CASE
    WHEN ABS((dm.daily_clicks - s.avg_clicks) / NULLIF(s.stddev_clicks, 0)) > 2 THEN 'Anomaly Detected'
    WHEN ABS((dm.daily_users - s.avg_users) / NULLIF(s.stddev_users, 0)) > 2 THEN 'Anomaly Detected'
    ELSE 'Normal'
  END AS anomaly_status
FROM
  daily_metrics dm
  CROSS JOIN stats s
ORDER BY
  dm.activity_date DESC;

-- Query 4.2: High Error Rate Apps
-- Purpose: Identify apps with concerning error rates
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.high_error_rate_apps AS
SELECT
  COALESCE(request_params.app_name, 'Unknown App') AS app_name,
  COALESCE(request_params.app_id, 'N/A') AS app_id,
  COUNT(*) AS total_requests,
  SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) AS error_count,
  ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percentage,
  COUNT(DISTINCT user_identity.email) AS affected_users,
  MAX(event_time) AS last_error_time
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY
  request_params.app_name,
  request_params.app_id
HAVING
  error_rate_percentage > 5  -- Apps with >5% error rate
ORDER BY
  error_rate_percentage DESC;

-- Query 4.3: Inactive Users Alert
-- Purpose: Identify previously active users who haven't used apps recently
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.inactive_users_alert AS
WITH user_activity AS (
  SELECT
    user_identity.email,
    MAX(event_time) AS last_activity,
    COUNT(*) AS total_historical_clicks,
    DATEDIFF(DAY, MAX(event_time), CURRENT_DATE) AS days_inactive
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  GROUP BY
    user_identity.email
)
SELECT
  email,
  last_activity,
  total_historical_clicks,
  days_inactive,
  CASE
    WHEN days_inactive > 30 THEN 'Critical - 30+ days'
    WHEN days_inactive > 14 THEN 'Warning - 14+ days'
    WHEN days_inactive > 7 THEN 'At Risk - 7+ days'
    ELSE 'Active'
  END AS inactivity_level
FROM
  user_activity
WHERE
  total_historical_clicks >= 10  -- Only users who were previously active
  AND days_inactive > 7
ORDER BY
  days_inactive DESC,
  total_historical_clicks DESC;

-- ====================================================================
-- SECTION 5: EXECUTIVE REPORTING QUERIES
-- ====================================================================

-- Query 5.1: Weekly Executive Summary
-- Purpose: Week-over-week comparison for executive reporting
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.weekly_executive_summary AS
WITH weekly_metrics AS (
  SELECT
    DATE_TRUNC('WEEK', event_time) AS week_start,
    COUNT(DISTINCT user_identity.email) AS weekly_active_users,
    COUNT(*) AS total_clicks,
    COUNT(DISTINCT request_params.app_id) AS apps_used,
    SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) AS errors
  FROM
    system.access.audit
  WHERE
    service_name = 'apps'
    AND event_date >= CURRENT_DATE - INTERVAL '60' DAY
    AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
  GROUP BY
    DATE_TRUNC('WEEK', event_time)
)
SELECT
  week_start,
  weekly_active_users,
  total_clicks,
  apps_used,
  errors,
  ROUND(errors * 100.0 / NULLIF(total_clicks, 0), 2) AS error_rate_pct,
  LAG(weekly_active_users) OVER (ORDER BY week_start) AS prev_week_users,
  ROUND((weekly_active_users - LAG(weekly_active_users) OVER (ORDER BY week_start)) * 100.0 / 
    NULLIF(LAG(weekly_active_users) OVER (ORDER BY week_start), 0), 2) AS user_growth_pct,
  LAG(total_clicks) OVER (ORDER BY week_start) AS prev_week_clicks,
  ROUND((total_clicks - LAG(total_clicks) OVER (ORDER BY week_start)) * 100.0 / 
    NULLIF(LAG(total_clicks) OVER (ORDER BY week_start), 0), 2) AS click_growth_pct
FROM
  weekly_metrics
ORDER BY
  week_start DESC;

-- Query 5.2: Monthly Trends Report
-- Purpose: Month-over-month analysis
CREATE OR REPLACE VIEW hls_amer_catalog.apps_telemetry.monthly_trends_report AS
SELECT
  DATE_TRUNC('MONTH', event_time) AS month_start,
  COUNT(DISTINCT user_identity.email) AS monthly_active_users,
  COUNT(*) AS total_interactions,
  COUNT(DISTINCT request_params.app_id) AS unique_apps_used,
  COUNT(DISTINCT DATE(event_time)) AS active_days,
  ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_interactions_per_user,
  ROUND(COUNT(DISTINCT user_identity.email) * 1.0 / NULLIF(COUNT(DISTINCT DATE(event_time)), 0), 2) AS avg_users_per_day
FROM
  system.access.audit
WHERE
  service_name = 'apps'
  AND event_date >= CURRENT_DATE - INTERVAL '12' MONTH
  AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
GROUP BY
  DATE_TRUNC('MONTH', event_time)
ORDER BY
  month_start DESC;

-- ====================================================================
-- END OF SQL QUERIES LIBRARY
-- ====================================================================
