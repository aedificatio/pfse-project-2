"""
A module for designing a pile foundation
"""

from plotly import graph_objects as go
from dataclasses import dataclass
from typing import Optional


@dataclass
class Foundation:
    """
    Represents data from a pile foundation.
    """
    label: str = 'name'
    plot_foundation: Optional[go.Figure] = None
    pile_stiffness: Optional[float] = None
    pile_size: Optional[int] = None
    pile_grid_x: Optional[int] = None
    pile_grid_y: Optional[int] = None
    pile_no_x: Optional[int] = None
    pile_no_y: Optional[int] = None
    foundation_stiffness: Optional[float] = None


def calculate_foundation(foundation: Foundation) -> Foundation:
    """
    Takes a Foundation object and calculates the rotational stiffness.
    Returns the Foundation with added "foundation_stiffness" variable.
    """
    x_NA = 0.5 * (foundation.pile_no_y - 1) * foundation.pile_grid_y / 1000
    y_s = [-x_NA + foundation.pile_grid_y /1000 * i for i in range(foundation.pile_no_y)]
    k_pile = foundation.pile_stiffness # kN/m1
    C_RotPerRow = [foundation.pile_stiffness * foundation.pile_no_x * i**2 for i in y_s]
    foundation.foundation_stiffness = sum(C_RotPerRow)
    return foundation


def plot_foundation(foundation: Foundation) -> Foundation:
    """
    Takes a Foundation object and plots the foundation.
    Returns the Foundation with added "plot_foundation" variable.
    """
    go.Figure()
    fig = go.Figure()

    h_2_x = 0.5 * (foundation.pile_no_x - 1) * foundation.pile_grid_x
    h_2_y = 0.5 * (foundation.pile_no_y - 1) * foundation.pile_grid_y
    rows = [x * foundation.pile_grid_x - h_2_x for x in range(foundation.pile_no_x)]
    cols = [y * foundation.pile_grid_y - h_2_y for y in range(foundation.pile_no_y)]

    coords = []
    for row in rows:
        for col in cols:
            coords.append((row, col))

    for coord in coords:
        x = coord[0]
        y = coord[1]
        delta = foundation.pile_size / 2
        corners_x = [x - delta, x - delta, x + delta, x + delta]
        corners_y = [y - delta, y + delta, y + delta, y - delta]
        fig.add_trace(go.Scatter(
            x=corners_x,
            y=corners_y,
            fill="toself",
            fillcolor='goldenrod',
            line_color='goldenrod',
            )
        )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    fig.update_layout(
        title = foundation.label,
        showlegend=False,
        width=500,
        height=600,
    )

    foundation.plot_foundation = fig
    return foundation