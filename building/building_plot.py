"""
A module for calculating a steel beam as a crane runway beam steel stresses.
"""

from plotly import graph_objects as go
# import streamlit as st


# import pycba as cba
# import numpy as np
# import matplotlib
# import matplotlib.pyplot as plt
# import matplotlib.markers as markers
# import plotly.express as px
# from rich import print as rprint
# from dataclasses import dataclass, field
# from typing import Dict, Optional, Tuple
# from handcalcs.decorator import handcalc
# import pandas as pd


def plot_building(building):
    """
    """
    layout = go.Layout(
        autosize=False, width=1200, height=800,
        title = 'Simplified Building Viewport',
        scene = dict(
            aspectmode='data',
            aspectratio=go.layout.scene.Aspectratio(x=0.4, y=0.4, z=0.4)
        ),
        # xaxis = dict(
        #     scaleratio = 1,
        # ),
        # yaxis = dict(
        #     # scaleratio = 1,
        #     scaleanchor = 'x'
        # )
    )
    fig = go.Figure(layout=layout)
    
    # plot building contour & faces
    # building.calc_geom_data()
    plot_item_contour(fig, building.nodes, building.edges, color='rgb(0, 0, 255)', line_width=2, marker_size=2)
    plot_item_faces(fig, building.nodes, building.faces, opacity=0.25, color='rgb(0, 0, 255)')

    # plot cores contour & faces
    for shearwall in building.shearwalls:
        plot_item_contour(fig, shearwall.nodes, shearwall.edges, color='rgb(255, 0, 0)', line_width=2, marker_size=2)
        plot_item_faces(fig, shearwall.nodes, shearwall.faces, opacity=0.25, color='rgb(255, 0, 0)')
    
    fig.layout.height = 1000
    fig.layout.width = 1000

    fig.layout.scene.xaxis.range = (0, building.width * 2.2)
    fig.layout.scene.yaxis.range = (0, building.depth * 2.2)
    # fig.layout.xaxis.scaleratio = 1
    # fig.layout.yaxis.scaleratio = 1
    # fig.update_scenes(Aspectratio(x=2, y=2, z=2))
    fig.update_scenes(xaxis_autorange="reversed")
        
    return fig


def plot_item_faces(fig, nodes, faces, opacity=0.25, color: str = 'rgb(0, 0, 255)'):
    """
    """
    # Add building_faces
    x, y, z = zip(*nodes)
    i, j, k = zip(*faces)

    fig.add_trace(
        go.Mesh3d(
            x = x,
            y = y,
            z = z,
            i = i,
            j = j,
            k = k,
            opacity = opacity,
            color = color
        )
    )
    return fig


def plot_item_contour(fig, nodes, edges, color: str='rgb(0, 0, 255)', line_width: int=2, marker_size: int =2):
    """
    """
    for i_node, j_node in edges:
        x_coord_i, y_coord_i, z_coord_i = nodes[i_node]
        x_coord_j, y_coord_j, z_coord_j = nodes[j_node]

        trace = go.Scatter3d(
            x = [x_coord_i, x_coord_j],
            y = [y_coord_i, y_coord_j],
            z = [z_coord_i, z_coord_j],
            line = {
                'color': color,
                'width': line_width,
            },
            marker = {
                'size': marker_size
            },
            showlegend = False
        )
        fig.add_trace(trace)
    return fig


def expand_geom_data(nodes_floor, edges_floor, height):
    """
    """
    # Add height to node coordinates
    nodes = [node_floor + [0] for node_floor in nodes_floor]
    nodes += [node_floor + [height] for node_floor in nodes_floor]
    
    # Define edges 3d
    start_roof_idx = int(len(nodes) / 2)
    # Horizontal edges
    edges = edges_floor + [[x + start_roof_idx, y + start_roof_idx] for x, y in edges_floor]
    # Vertical edges
    edges += [[idx, idx + start_roof_idx] for idx, node in enumerate(nodes_floor)]
    
    faces = []
    for edge in edges_floor:
        faces.append(edge + [edge[0] + start_roof_idx])
        faces.append([edge[0] + start_roof_idx, edge[1] + start_roof_idx, edge[1]])
    return (nodes, edges, faces)