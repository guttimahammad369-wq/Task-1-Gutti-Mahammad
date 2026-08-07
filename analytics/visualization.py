from typing import Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.logger import logger


class VisualizationEngine:
    """Dynamic visualization generator producing interactive Plotly charts."""

    def __init__(self):
        # Premium dark/modern color palette matching professional dashboard design
        self.color_palette = px.colors.qualitative.Plotly

    def create_bar_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        color_col: Optional[str] = None,
        orientation: str = "v",
    ) -> go.Figure:
        """Creates an interactive Plotly Bar Chart.

        Args:
            df: Input DataFrame.
            x_col: Column for X axis.
            y_col: Column for Y axis.
            title: Chart title string.
            color_col: Optional column for color encoding.
            orientation: 'v' for vertical, 'h' for horizontal.

        Returns:
            go.Figure: Configured Plotly figure object.
        """
        logger.info(f"Generating Bar Chart: {title}")
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col or x_col,
            title=title,
            text_auto=".2s" if df[y_col].dtype != "object" else None,
            orientation=orientation,
            color_discrete_sequence=self.color_palette,
        )

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Inter, sans-serif", size=13),
            title_font_size=16,
            xaxis_title=x_col,
            yaxis_title=y_col,
            margin=dict(l=40, r=40, t=50, b=40),
            hovermode="x unified",
        )
        return fig

    def create_line_chart(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        markers: bool = True,
    ) -> go.Figure:
        """Creates an interactive Plotly Line Chart for time series trends.

        Args:
            df: Input DataFrame.
            x_col: Time axis column.
            y_col: Metric axis column.
            title: Chart title string.
            markers: Whether to show data points.

        Returns:
            go.Figure: Plotly Line Chart figure.
        """
        logger.info(f"Generating Line Chart: {title}")
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            title=title,
            markers=markers,
            color_discrete_sequence=["#2563EB"],
        )

        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Inter, sans-serif", size=13),
            title_font_size=16,
            xaxis_title=x_col,
            yaxis_title=y_col,
            margin=dict(l=40, r=40, t=50, b=40),
            hovermode="x unified",
        )
        return fig

    def create_pie_chart(
        self,
        df: pd.DataFrame,
        names_col: str,
        values_col: str,
        title: str,
        hole: float = 0.4,
    ) -> go.Figure:
        """Creates an interactive Plotly Pie/Donut Chart.

        Args:
            df: Input DataFrame.
            names_col: Category names column.
            values_col: Metric values column.
            title: Chart title string.
            hole: Inner radius for donut chart styling.

        Returns:
            go.Figure: Plotly Pie/Donut figure.
        """
        logger.info(f"Generating Pie/Donut Chart: {title}")
        fig = px.pie(
            df,
            names=names_col,
            values=values_col,
            title=title,
            hole=hole,
            color_discrete_sequence=self.color_palette,
        )

        fig.update_traces(textinfo="percent+label", pull=[0.02] * len(df))
        fig.update_layout(
            template="plotly_white",
            font=dict(family="Inter, sans-serif", size=13),
            title_font_size=16,
            margin=dict(l=40, r=40, t=50, b=40),
        )
        return fig

    def create_histogram(
        self,
        df: pd.DataFrame,
        column: str,
        title: str,
        nbins: int = 25,
    ) -> go.Figure:
        """Creates an interactive Plotly Histogram distribution plot.

        Args:
            df: Input DataFrame.
            column: Numerical column to plot.
            title: Chart title string.
            nbins: Number of histogram bins.

        Returns:
            go.Figure: Plotly Histogram figure.
        """
        logger.info(f"Generating Histogram: {title}")
        fig = px.histogram(
            df,
            x=column,
            nbins=nbins,
            title=title,
            color_discrete_sequence=["#4F46E5"],
            marginal="box",
        )

        fig.update_layout(
            template="plotly_white",
            font=dict(family="Inter, sans-serif", size=13),
            title_font_size=16,
            xaxis_title=column,
            yaxis_title="Frequency",
            margin=dict(l=40, r=40, t=50, b=40),
        )
        return fig


# Global singleton instance
visualization_engine = VisualizationEngine()
