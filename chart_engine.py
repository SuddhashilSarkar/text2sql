import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Optional

class ChartEngine:
    """Generates charts from SQL results and LLM hints."""
    
    @staticmethod
    def generate_chart(
        sql_results: list,
        chart_params: Optional[Dict] = None,
        column_names: Optional[list] = None
    ) -> Optional[go.Figure]:  # Changed from px.Figure to go.Figure
        """
        Renders a Plotly chart based on SQL data and LLM parameters.
        
        Args:
            sql_results: Raw results from SQL execution (tuples or dicts)
            chart_params: Dict with 'chart_type', 'x', 'y' (from LLM)
            column_names: Column names if sql_results are tuples
        
        Returns:
            Plotly figure or None (if error)
        """
        try:
            # Convert SQL results to DataFrame
            if isinstance(sql_results[0], dict):
                df = pd.DataFrame(sql_results)
            else:
                if not column_names:
                    column_names = [f"col{i}" for i in range(len(sql_results[0]))]
                df = pd.DataFrame(sql_results, columns=column_names)

            # Get chart parameters or use defaults
            chart_type = chart_params.get("chart_type", "bar") if chart_params else "bar"
            x_col = chart_params.get("x") if chart_params else df.columns[0]
            y_col = chart_params.get("y") if chart_params else df.columns[1] if len(df.columns) > 1 else None

            # Validate columns
            if x_col not in df.columns or (y_col and y_col not in df.columns):
                x_col, y_col = df.columns[0], df.columns[1] if len(df.columns) > 1 else None

            # Generate chart
            if chart_type == "bar" and y_col:
                fig = px.bar(df, x=x_col, y=y_col)
            elif chart_type == "line" and y_col:
                fig = px.line(df, x=x_col, y=y_col)
            elif chart_type == "pie":
                fig = px.pie(df, names=x_col, values=y_col if y_col else df.columns[1])
            else:
                fig = px.bar(df, x=x_col, y=y_col)  # Fallback
            
            return fig
        
        except Exception as e:
            print(f"Chart generation failed: {e}")
            return None
        
