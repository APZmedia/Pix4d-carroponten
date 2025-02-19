import plotly.graph_objects as go
from visualization.reference_points import REFERENCE_POINTS
from config import CENTER

def make_plot(calibrated_positions, uncalibrated_positions, adjusted_positions, center, title="Camera Position Visualization"):
    """
    Creates an interactive plot with calibrated, uncalibrated, and adjusted positions.
    """
    fig = go.Figure()

    # Plot adjusted uncalibrated positions in green
    if adjusted_positions:
        fig.add_trace(
            go.Scatter(
                x=[pos[0] for pos in adjusted_positions.values()],
                y=[pos[1] for pos in adjusted_positions.values()],
                mode='markers',
                marker=dict(color='green', symbol='x'),
                name='Uncalibrated (Adjusted)',
                text=[f"ID: {uid}" for uid in adjusted_positions.keys()],
                hoverinfo='text'
            )
        )

    # Plot calibrated anchors in red
    if calibrated_positions:
        fig.add_trace(
            go.Scatter(
                x=[pos[0] for pos in calibrated_positions.values()],
                y=[pos[1] for pos in calibrated_positions.values()],
                mode='markers',
                marker=dict(color='red', symbol='circle'),
                name='Calibrated',
                text=[f"ID: {uid}" for uid in calibrated_positions.keys()],
                hoverinfo='text'
            )
        )

    # Plot reference points (black diamonds)
    if REFERENCE_POINTS:
        fig.add_trace(
            go.Scatter(
                x=[p[0] for p in REFERENCE_POINTS.values()],
                y=[p[1] for p in REFERENCE_POINTS.values()],
                mode='markers',
                marker=dict(color='black', symbol='diamond'),
                name='Reference Points',
                text=[f"Ref: {rid}<br>Z={p[2]:.2f}" for rid, p in REFERENCE_POINTS.items()],
                hoverinfo='text'
            )
        )

    # Plot center (purple star)
    fig.add_trace(
        go.Scatter(
            x=[center[0]],
            y=[center[1]],
            mode='markers',
            marker=dict(color='purple', symbol='star', size=12),
            name='Center',
            text=["Center"],
            hoverinfo='text'
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title='X Position',
        yaxis_title='Y Position',
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )
    return fig
