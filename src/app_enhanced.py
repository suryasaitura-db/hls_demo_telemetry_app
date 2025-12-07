"""
HLS Demo Telemetry Report - Enhanced Application Entry Point
This is the entry point for the Databricks App deployment
Version: 2.1.0
"""

from dash_app_enhanced import app

# Main execution - runs Dash's built-in server
if __name__ == '__main__':
    app.run(debug=True)
