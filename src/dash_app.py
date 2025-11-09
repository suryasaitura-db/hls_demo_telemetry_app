"""
====================================================================
DATABRICKS APPS TELEMETRY - INTERACTIVE DASH DASHBOARD
====================================================================
Purpose: Interactive web dashboard for Databricks Apps telemetry
Framework: Plotly Dash with Databricks SQL connector
Created: 2025-11-08
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
import os

# ====================================================================
# CONFIGURATION
# ====================================================================

class Config:
    """Dashboard configuration"""
    DATABRICKS_SERVER_HOSTNAME = os.getenv('DATABRICKS_SERVER_HOSTNAME')
    DATABRICKS_HTTP_PATH = os.getenv('DATABRICKS_HTTP_PATH')
    DATABRICKS_TOKEN = os.getenv('DATABRICKS_ACCESS_TOKEN')
    
    # Default date ranges
    DEFAULT_DAYS_BACK = 30
    
    # Refresh intervals (in milliseconds)
    REFRESH_INTERVAL = 300000  # 5 minutes
    
    # Color scheme
    COLORS = {
        'primary': '#4A90E2',
        'success': '#50C878',
        'warning': '#FFA500',
        'danger': '#FF6B6B',
        'info': '#7B68EE',
        'background': '#F8F9FA',
        'text': '#212529'
    }

# ====================================================================
# DATABASE CONNECTION
# ====================================================================

class DatabricksConnection:
    """Manages Databricks SQL connection"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish connection to Databricks"""
        try:
            self.connection = sql.connect(
                server_hostname=Config.DATABRICKS_SERVER_HOSTNAME,
                http_path=Config.DATABRICKS_HTTP_PATH,
                access_token=Config.DATABRICKS_TOKEN
            )
            return self.connection
        except Exception as e:
            print(f"Error connecting to Databricks: {e}")
            return None
    
    def execute_query(self, query):
        """Execute SQL query and return DataFrame"""
        try:
            if not self.connection:
                self.connect()
            
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Fetch results and convert to DataFrame
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            
            cursor.close()
            return df
        
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()

# Initialize connection
db_conn = DatabricksConnection()

# ====================================================================
# DATA QUERIES
# ====================================================================

class DataQueries:
    """SQL queries for dashboard data"""
    
    @staticmethod
    def get_kpi_summary(days_back=30):
        return f"""
        SELECT
          COUNT(DISTINCT user_identity.email) AS total_unique_users,
          COUNT(DISTINCT request_params.app_id) AS total_unique_apps,
          COUNT(*) AS total_interactions,
          ROUND(COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT user_identity.email), 0), 2) AS avg_interactions_per_user,
          ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS overall_error_rate
        FROM system.access.audit
        WHERE service_name = 'apps'
          AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
          AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
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
          AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
        GROUP BY DATE(event_time)
        ORDER BY activity_date ASC
        """
    
    @staticmethod
    def get_top_apps(days_back=30, limit=10):
        return f"""
        SELECT
          COALESCE(request_params.app_name, 'Unknown App') AS app_name,
          COUNT(*) AS click_count,
          COUNT(DISTINCT user_identity.email) AS unique_users,
          ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage_of_total
        FROM system.access.audit
        WHERE service_name = 'apps'
          AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
          AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
        GROUP BY request_params.app_name
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
          AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
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
            AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
          GROUP BY user_identity.email
        )
        SELECT
          DATE(a.event_time) AS activity_date,
          COUNT(DISTINCT CASE WHEN DATE(a.event_time) = ufi.first_interaction_date THEN a.user_identity.email END) AS new_users,
          COUNT(DISTINCT CASE WHEN DATE(a.event_time) > ufi.first_interaction_date THEN a.user_identity.email END) AS returning_users
        FROM system.access.audit a
        JOIN user_first_interaction ufi ON a.user_identity.email = ufi.email
        WHERE a.service_name = 'apps'
          AND a.event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
          AND a.action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
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
          ROUND(SUM(CASE WHEN response.status_code >= 400 OR response.error_message IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS error_rate_percentage
        FROM system.access.audit
        WHERE service_name = 'apps'
          AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
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
          CASE
            WHEN COUNT(*) >= 100 THEN 'Power User'
            WHEN COUNT(*) >= 50 THEN 'Active User'
            WHEN COUNT(*) >= 10 THEN 'Regular User'
            ELSE 'Casual User'
          END AS user_segment
        FROM system.access.audit
        WHERE service_name = 'apps'
          AND event_date >= CURRENT_DATE - INTERVAL '{days_back}' DAY
          AND action_name IN ('openApp', 'startApp', 'accessApp', 'viewApp', 'executeApp')
        GROUP BY user_identity.email
        ORDER BY total_clicks DESC
        LIMIT {limit}
        """

# ====================================================================
# DASH APP INITIALIZATION
# ====================================================================

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Apps Telemetry Dashboard"
)

# ====================================================================
# LAYOUT COMPONENTS
# ====================================================================

def create_kpi_card(title, value, icon, color, percentage_change=None):
    """Create a KPI card component"""
    
    change_badge = html.Div()
    if percentage_change is not None:
        badge_color = "success" if percentage_change >= 0 else "danger"
        change_badge = dbc.Badge(
            f"{'+' if percentage_change >= 0 else ''}{percentage_change}%",
            color=badge_color,
            className="ms-2"
        )
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi bi-{icon} fs-2", style={'color': color}),
            ], className="text-center mb-2"),
            html.H3(value, className="text-center mb-0"),
            html.P([title, change_badge], className="text-center text-muted mb-0")
        ])
    ], className="h-100 shadow-sm")

def create_header():
    """Create dashboard header"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.I(className="bi bi-bar-chart-fill me-2"),
                        html.Span("Databricks Apps Telemetry Dashboard", 
                                 className="navbar-brand mb-0 h1")
                    ])
                ]),
            ], align="center", className="g-0"),
            dbc.Row([
                dbc.Col([
                    html.Div(id='last-update-time', className="text-muted small")
                ])
            ], align="center")
        ], fluid=True),
        color="dark",
        dark=True,
        className="mb-4"
    )

def create_filters():
    """Create filter controls"""
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range:", className="fw-bold"),
                    dcc.Dropdown(
                        id='date-range-dropdown',
                        options=[
                            {'label': 'Last 7 Days', 'value': 7},
                            {'label': 'Last 30 Days', 'value': 30},
                            {'label': 'Last 90 Days', 'value': 90},
                        ],
                        value=30,
                        clearable=False
                    )
                ], md=3),
                dbc.Col([
                    html.Label("Auto Refresh:", className="fw-bold"),
                    dbc.Switch(
                        id='auto-refresh-switch',
                        label="Enable",
                        value=True
                    )
                ], md=2),
                dbc.Col([
                    html.Label("\u00A0", className="fw-bold"),  # Non-breaking space for alignment
                    html.Div([
                        dbc.Button(
                            [html.I(className="bi bi-arrow-clockwise me-2"), "Refresh Now"],
                            id='refresh-button',
                            color="primary",
                            className="w-100"
                        )
                    ])
                ], md=2)
            ])
        ])
    ], className="mb-4 shadow-sm")

# ====================================================================
# MAIN LAYOUT
# ====================================================================

app.layout = dbc.Container([
    # Header
    create_header(),
    
    # Filters
    create_filters(),
    
    # Hidden div to store data
    dcc.Store(id='kpi-data-store'),
    dcc.Store(id='charts-data-store'),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=Config.REFRESH_INTERVAL,
        n_intervals=0
    ),
    
    # KPI Cards Row
    html.H4("Key Performance Indicators", className="mb-3"),
    dbc.Row([
        dbc.Col(html.Div(id='kpi-card-1'), md=3),
        dbc.Col(html.Div(id='kpi-card-2'), md=3),
        dbc.Col(html.Div(id='kpi-card-3'), md=3),
        dbc.Col(html.Div(id='kpi-card-4'), md=3),
    ], className="mb-4"),
    
    # Charts Row 1
    html.H4("Usage Trends & Patterns", className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Daily Active Users Trend", className="card-title"),
                    dcc.Loading(
                        dcc.Graph(id='dau-trend-chart'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm h-100")
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Top 10 Apps by Engagement", className="card-title"),
                    dcc.Loading(
                        dcc.Graph(id='top-apps-chart'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm h-100")
        ], md=6),
    ], className="mb-4"),
    
    # Heatmap Row
    html.H4("Usage Patterns Analysis", className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("Usage Patterns by Day and Hour", className="card-title"),
                    dcc.Loading(
                        dcc.Graph(id='usage-heatmap'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm")
        ], md=12),
    ], className="mb-4"),
    
    # Charts Row 2
    html.H4("User Behavior & Health", className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("New vs Returning Users", className="card-title"),
                    dcc.Loading(
                        dcc.Graph(id='user-cohorts-chart'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm h-100")
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("App Health Monitor", className="card-title"),
                    dcc.Loading(
                        dcc.Graph(id='error-monitoring-chart'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm h-100")
        ], md=6),
    ], className="mb-4"),
    
    # User Segmentation Table
    html.H4("User Engagement Details", className="mb-3"),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("User Segmentation", className="card-title"),
                    dcc.Loading(
                        html.Div(id='user-segmentation-table'),
                        type="circle"
                    )
                ])
            ], className="shadow-sm")
        ], md=12),
    ], className="mb-4"),
    
    # Footer
    html.Hr(),
    html.Footer([
        html.P([
            "Databricks Apps Telemetry Dashboard | ",
            html.A("Documentation", href="#", className="text-decoration-none"),
            " | Data refreshes every 5 minutes"
        ], className="text-center text-muted")
    ])
    
], fluid=True, className="py-3")

# ====================================================================
# CALLBACKS
# ====================================================================

@app.callback(
    Output('last-update-time', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('refresh-button', 'n_clicks'),
    State('auto-refresh-switch', 'value')
)
def update_timestamp(n_intervals, n_clicks, auto_refresh):
    """Update last refresh timestamp"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Last updated: {now}"

@app.callback(
    [Output('kpi-data-store', 'data'),
     Output('charts-data-store', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('refresh-button', 'n_clicks'),
     Input('date-range-dropdown', 'value')],
    State('auto-refresh-switch', 'value')
)
def fetch_data(n_intervals, n_clicks, days_back, auto_refresh):
    """Fetch all data from Databricks"""
    
    # Only refresh if auto-refresh is enabled or manual refresh clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return {}, {}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'interval-component' and not auto_refresh:
        return dash.no_update, dash.no_update
    
    # Fetch KPI data
    kpi_df = db_conn.execute_query(DataQueries.get_kpi_summary(days_back))
    kpi_data = kpi_df.to_dict('records')[0] if not kpi_df.empty else {}
    
    # Fetch charts data
    charts_data = {
        'dau_trend': db_conn.execute_query(DataQueries.get_dau_trend(days_back)).to_dict('records'),
        'top_apps': db_conn.execute_query(DataQueries.get_top_apps(days_back)).to_dict('records'),
        'usage_heatmap': db_conn.execute_query(DataQueries.get_usage_heatmap(days_back)).to_dict('records'),
        'user_cohorts': db_conn.execute_query(DataQueries.get_user_cohorts(days_back)).to_dict('records'),
        'error_monitoring': db_conn.execute_query(DataQueries.get_error_monitoring(days_back)).to_dict('records'),
        'user_segmentation': db_conn.execute_query(DataQueries.get_user_segmentation(days_back)).to_dict('records')
    }
    
    return kpi_data, charts_data

@app.callback(
    [Output('kpi-card-1', 'children'),
     Output('kpi-card-2', 'children'),
     Output('kpi-card-3', 'children'),
     Output('kpi-card-4', 'children')],
    Input('kpi-data-store', 'data')
)
def update_kpi_cards(kpi_data):
    """Update KPI cards"""
    if not kpi_data:
        return [html.Div("Loading...")] * 4
    
    card1 = create_kpi_card(
        "Total Unique Users",
        f"{kpi_data.get('total_unique_users', 0):,}",
        "people-fill",
        Config.COLORS['primary']
    )
    
    card2 = create_kpi_card(
        "Active Apps",
        f"{kpi_data.get('total_unique_apps', 0):,}",
        "app-indicator",
        Config.COLORS['info']
    )
    
    card3 = create_kpi_card(
        "Total Interactions",
        f"{kpi_data.get('total_interactions', 0):,}",
        "activity",
        Config.COLORS['success']
    )
    
    card4 = create_kpi_card(
        "Error Rate",
        f"{kpi_data.get('overall_error_rate', 0):.2f}%",
        "exclamation-triangle-fill",
        Config.COLORS['danger'] if kpi_data.get('overall_error_rate', 0) > 5 else Config.COLORS['success']
    )
    
    return card1, card2, card3, card4

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
            line=dict(color=Config.COLORS['primary'], width=3),
            mode='lines+markers'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['activity_date'],
            y=df['total_clicks'],
            name='Total Clicks',
            line=dict(color=Config.COLORS['danger'], width=2, dash='dash'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Daily Active Users", secondary_y=False)
    fig.update_yaxes(title_text="Total Clicks", secondary_y=True)
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20)
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
    
    fig = px.bar(
        df,
        y='app_name',
        x='click_count',
        color='unique_users',
        orientation='h',
        title='',
        color_continuous_scale='Blues',
        labels={'click_count': 'Total Clicks', 'app_name': 'App Name', 'unique_users': 'Unique Users'}
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis={'categoryorder': 'total ascending'}
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
    heatmap_data = df.pivot(index='day_name', columns='hour_of_day', values='click_count')
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(day_order)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        hovertemplate='Day: %{y}<br>Hour: %{x}<br>Clicks: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20)
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
        fillcolor=Config.COLORS['primary'],
        line=dict(width=0)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['activity_date'],
        y=df['returning_users'],
        name='Returning Users',
        stackgroup='one',
        fillcolor=Config.COLORS['success'],
        line=dict(width=0)
    ))
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title='Date',
        yaxis_title='User Count'
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
            name='Successful Requests',
            marker_color=Config.COLORS['success']
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            x=df['activity_date'],
            y=df['failed_requests'],
            name='Failed Requests',
            marker_color=Config.COLORS['danger']
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['activity_date'],
            y=df['error_rate_percentage'],
            name='Error Rate %',
            line=dict(color='#FF4500', width=3),
            mode='lines+markers'
        ),
        secondary_y=True
    )
    
    # Add threshold line
    fig.add_hline(
        y=5,
        line_dash="dash",
        line_color="orange",
        annotation_text="5% Threshold",
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Request Count", secondary_y=False)
    fig.update_yaxes(title_text="Error Rate (%)", secondary_y=True)
    
    fig.update_layout(
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        barmode='stack'
    )
    
    return fig

@app.callback(
    Output('user-segmentation-table', 'children'),
    Input('charts-data-store', 'data')
)
def update_user_segmentation_table(charts_data):
    """Update user segmentation table"""
    if not charts_data or 'user_segmentation' not in charts_data:
        return html.Div("No data available")
    
    df = pd.DataFrame(charts_data['user_segmentation'])
    if df.empty:
        return html.Div("No data available")
    
    # Create table with conditional formatting
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("User Email"),
            html.Th("Segment"),
            html.Th("Total Clicks"),
            html.Th("Apps Accessed"),
            html.Th("Days Active"),
            html.Th("Avg Clicks/Day")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row['user_email']),
                html.Td(
                    dbc.Badge(
                        row['user_segment'],
                        color={
                            'Power User': 'primary',
                            'Active User': 'success',
                            'Regular User': 'warning',
                            'Casual User': 'secondary'
                        }.get(row['user_segment'], 'secondary')
                    )
                ),
                html.Td(f"{row['total_clicks']:,}"),
                html.Td(f"{row['apps_accessed']}"),
                html.Td(f"{row['days_active']}"),
                html.Td(f"{row['avg_clicks_per_day']:.2f}")
            ]) for _, row in df.head(25).iterrows()
        ])
    ], striped=True, bordered=True, hover=True, responsive=True, size='sm')
    
    return table

# ====================================================================
# RUN APP
# ====================================================================

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
