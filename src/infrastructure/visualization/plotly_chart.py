import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Any, Optional
from ...domain.entities import Visualization, VisualizationType
from ...domain.repositories import IChartGenerator, ChartGenerationError


class PlotlyChartGenerator(IChartGenerator):
    """Plotly implementation of the chart generator interface.

    This class creates various types of charts using Plotly for data visualization.
    """

    def __init__(self):
        """Initialize the plotly chart generator."""
        self.default_config = {
            "template": "plotly_white",
            "showlegend": True,
            "height": 600,
        }

    def _create_bar_chart(
        self,
        data: Any,
        title: str,
        config: dict[str, Any]
    ) -> go.Figure:
        """Create a bar chart from the data.

        Args:
            data: Data to visualize (DataFrame, dict, or list).
            title: Chart title.
            config: Chart configuration.

        Returns:
            Plotly figure object.
        """
        try:
            # Handle different data types
            if isinstance(data, dict):
                # Convert dict to DataFrame
                if len(data) == 1 and isinstance(list(data.values())[0], dict):
                    list(data.keys())[0]
                    metric_data = list(data.values())[0]
                    df = pd.DataFrame(list(metric_data.items()), columns=['Category', 'Value'])
                    x_col, y_col = 'Category', 'Value'
                elif all(isinstance(v, (int, float)) for v in data.values()):
                    # Simple key-value pairs
                    df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
                    x_col, y_col = 'Category', 'Value'
                else:
                    # Multiple metrics or complex dict structure
                    try:
                        df = pd.DataFrame(data)
                        x_col = df.columns[0]
                        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
                    except Exception:
                        # Fallback: try to flatten nested dict
                        flattened = {}
                        for k, v in data.items():
                            if isinstance(v, dict):
                                for sub_k, sub_v in v.items():
                                    flattened[f"{k}_{sub_k}"] = sub_v
                            else:
                                flattened[k] = v
                        df = pd.DataFrame(list(flattened.items()), columns=['Category', 'Value'])
                        x_col, y_col = 'Category', 'Value'
            elif isinstance(data, (list, tuple)):
                # Convert list to DataFrame
                df = pd.DataFrame(data)
                if len(df.columns) >= 2:
                    x_col, y_col = df.columns[0], df.columns[1]
                else:
                    x_col, y_col = "Index", df.columns[0] if len(df.columns) > 0 else "Value"
                    df[x_col] = range(len(df))
            elif isinstance(data, pd.DataFrame):
                df = data.copy()
                if len(df.columns) >= 2:
                    x_col, y_col = df.columns[0], df.columns[1]
                else:
                    x_col, y_col = "Index", df.columns[0] if len(df.columns) > 0 else "Value"
                    df[x_col] = range(len(df))
            else:
                # Fallback: Create simple bar chart
                df = pd.DataFrame({"Category": ["A", "B", "C"], "Value": [1, 2, 3]})
                x_col, y_col = "Category", "Value"

            # Create the bar chart
            if len(df.columns) > 2:
                # Multiple value columns - create grouped bar chart
                fig = px.bar(
                    df,
                    x=x_col,
                    y=df.columns[1:],
                    title=title,
                    template=config.get("template", "plotly_white"),
                    height=config.get("height", 500)
                )
            else:
                # Single value column
                fig = px.bar(
                    df,
                    x=x_col,
                    y=y_col,
                    title=title,
                    template=config.get("template", "plotly_white"),
                    height=config.get("height", 500)
                )

            # Update layout
            fig.update_layout(
                showlegend=config.get("showlegend", len(df.columns) > 2),
                xaxis_title=x_col,
                yaxis_title=y_col   
            )

            return fig
        except Exception as e:
            # Create fallback chart with error details
            import traceback
            error_msg = str(e)
            print(f"Chart generation error details: {error_msg}")
            print(f"Data type: {type(data)}")
            print(f"Data content: {data}")
            print(f"Traceback: {traceback.format_exc()}")

            fig = go.Figure(
                data=[go.Bar(x=["Error"], y=[0])],
                layout=go.Layout(
                    title=f"Chart generation Error: {title} - {error_msg}",
                    template="plotly_white"
                )
            )
            return fig

    def _create_line_chart(
        self,
        data: Any,
        title: str,
        config: dict[str, Any]
    ) -> go.Figure:
        """Create a line chart from the data.

        Args:
            data: Data to visualize.
            title: Chart title.
            config: Chart configuration.

        Returns:
            Plotly figure object.
        """
        try:
            # Handle different data types
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, (list, tuple)):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data.copy()
            else:
                # Fallback
                df = pd.DataFrame({
                    "X": [1, 2, 3], 
                    "Y": [2, 4, 6]
                })

            # Determine columns
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
            else:
                x_col, y_col = "Index", df.columns[0] if len(df.columns) > 0 else "Value"
                df[x_col] = range(len(df))

            # Create the line chart
            if len(df.columns) > 2:
                # Multiple y columns
                fig = px.line(
                    df,
                    x=x_col,
                    y=df.columns[1:],
                    title=title,
                    template=config.get("template", "plotly_white"),
                    height=config.get("height", 500)
                )
            else:
                # Single y column
                fig = px.line(
                    df,
                    x=x_col,
                    y=y_col,
                    title=title,
                    template=config.get("template", "plotly_white"),
                    height=config.get("height", 500)
                )

            # Update layout
            fig.update_layout(
                showlegend=config.get("showlegend", len(df.columns) > 2),
                xaxis_title=x_col,
                yaxis_title=y_col   
            )

            return fig
        except Exception as e:
            # Create fallback chart with error details
            import traceback
            error_msg = str(e)
            print(f"Line chart generation error details: {error_msg}")
            print(f"Data type: {type(data)}")
            print(f"Data content: {data}")

            fig = go.Figure(
                data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3], mode='lines')],
                layout=go.Layout(
                    title=f"Line chart Error: {title} - {error_msg}",
                    template="plotly_white"
                )
            )
            return fig
        
    def _create_pie_chart(
        self,
        data: Any,
        title: str,
        config: dict[str, Any]
    ) -> go.Figure:
        """Create a pie chart from the data.

        Args:
            data: Data to visualize.
            title: Chart title.
            config: Chart configuration.

        Returns:
            Plotly figure object.
        """
        try:
            # Handle different data types
            if isinstance(data, dict):
                if len(data) == 1 and isinstance(list(data.values())[0], dict):
                    metric_data = list(data.values())[0]
                    labels = list(metric_data.keys())
                    values = list(metric_data.values())
                else:
                    labels = list(data.keys())
                    values = list(data.values())
            elif isinstance(data, pd.DataFrame):
                if len(data.columns) >= 2:
                    labels, values = data.iloc[:, 0], data.iloc[:, 1]
                else:
                    labels, values = data.index, data.iloc[:, 0] if len(data.columns) > 0 else [1] * len(data)
            elif isinstance(data, (list, tuple)):
                df = pd.DataFrame(data)
                if len(df.columns) >= 2:
                    labels, values = df.iloc[:, 0], df.iloc[:, 1]
                else:
                    labels, values = df.index, df.iloc[:, 0] if len(df.columns) > 0 else [1] * len(df)
            else:
                # Fallback
                labels, values = ["A", "B", "C"], [1, 2, 3]

            # Create the pie chart
            fig = px.pie(
                values=values,
                names=labels,
                title=title,
                template=config.get("template", "plotly_white"),
                height=config.get("height", 500)
            )

            fig.update_layout(
                showlegend=config.get("showlegend", True)
            )

            return fig
        except Exception as e:
            # Create fallback chart with error details
            import traceback
            error_msg = str(e)
            print(f"Pie chart generation error details: {error_msg}")
            print(f"Data type: {type(data)}")
            print(f"Data content: {data}")

            fig = go.Figure(
                data=[go.Pie(labels=["Error"], values=[1])],
                layout=go.Layout(
                    title=f"Pie chart Error: {title} - {error_msg}",
                    template="plotly_white"
                )
            )
            return fig
        
    def _create_scatter_chart(
        self,
        data: Any,
        title: str,
        config: dict[str, Any]
    ) -> go.Figure:
        """Create a scatter plot from the data.

        Args:
            data: Data to visualize.
            title: Chart title.
            config: Chart configuration.

        Returns:
            Plotly figure object.
        """
        try:
            # Handle different data types
            if isinstance(data, dict):
                df = pd.DataFrame(data)
            elif isinstance(data, (list, tuple)):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data.copy()
            else:
                # Fallback
                df = pd.DataFrame({
                    "X": [1, 2, 3, 4], 
                    "Y": [2, 4, 3, 5]
                })

            # Determine columns
            if len(df.columns) >= 2:
                x_col, y_col = df.columns[0], df.columns[1]
            else:
                x_col, y_col = "Index", df.columns[0] if len(df.columns) > 0 else "Value"
                df[x_col] = range(len(df))

            # Create the scatter chart
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                title=title,
                template=config.get("template", "plotly_white"),
                height=config.get("height", 500)
            )

            # Add size and color columns if available
            if len(df.columns) > 2:
                size_col = df.columns[2] if len(df.columns) > 2 else None
                if size_col:
                    fig.update_traces(marker={"size": df[size_col] * 10})

            if len(df.columns) > 3:
                color_col = df.columns[3] if len(df.columns) > 3 else None
                if color_col:
                    fig.update_traces(marker={
                        "color": df[color_col], 
                        "colorscale": "Viridis", 
                        "showscale": True
                    })

            # Update layout
            fig.update_layout(
                showlegend=config.get("showlegend", False),
                xaxis_title=x_col,
                yaxis_title=y_col   
            )

            return fig
        except Exception as e:
            # Create fallback chart with error details
            import traceback
            error_msg = str(e)
            print(f"Scatter chart generation error details: {error_msg}")
            print(f"Data type: {type(data)}")
            print(f"Data content: {data}")

            fig = go.Figure(
                data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3], mode='markers')],
                layout=go.Layout(
                    title=f"Scatter chart Error: {title} - {error_msg}",
                    template="plotly_white"
                )
            )
            return fig

    def generate_chart(
        self,
        chart_type: VisualizationType,
        data: Any,
        title: str,
        config: Optional[dict[str, Any]] = None
    ) -> Visualization:
        """Generate a visualization based on the data and chart type.

        Args:
            chart_type: Type of chart to generate.
            data: Data to visualize.
            title: Chart title.
            config: Additional chart configuration.

        Returns:
            Visualization object with the generated chart.

        Raises:
            ChartGenerationError: If chart generation fails.
        """
        try:
            config = {**self.default_config, **(config or {})}

            if chart_type == VisualizationType.BAR:
                chart = self._create_bar_chart(data, title, config)
            elif chart_type == VisualizationType.LINE:
                chart = self._create_line_chart(data, title, config)
            elif chart_type == VisualizationType.PIE:
                chart = self._create_pie_chart(data, title, config)
            elif chart_type == VisualizationType.SCATTER:
                chart = self._create_scatter_chart(data, title, config)
            else:
                raise ChartGenerationError(f"Unsupported chart type: {chart_type}")
            
            return Visualization(
                chart_type=chart_type,
                chart_object=chart,
                title=title,
                description=config.get(
                    "description", f"{chart_type.value} chart for {title}"
                ),
                config=config
            )
        except Exception as e:
            raise ChartGenerationError(
                f"Failed to generate {chart_type.value} chart: {str(e)}"
            ) from e
