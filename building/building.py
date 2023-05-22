"""
A module for calculating a steel beam as a crane runway beam steel stresses.
"""

import streamlit as st
import pycba as cba
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from plotly import graph_objects as go
import plotly.express as px
from rich import print as rprint
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from handcalcs.decorator import handcalc


@dataclass
class Building_geometry:
    """
    Datatype represents the geometry of a building.
    """
    width: float = 40.0  # m
    depth: float = 15.0  # m
    height: float = 25.0  # m
    no_stories: int = 5  # amount
    no_shearwalls: int = Optional
    N_vd: int = Optional  # kN
    pd_wind: float = Optional[float]  # kN/m2

    def calc_geom_data(self):
        """
        Returns a dictionary with nodes, edges and faces, 
        representing the 3d geometry of the building.
        'nodes' # [[x, y, z],...] nodes in x, y, z
        'edges' # [[i, j],...] meaning node numbers
        'faces' # [[i, j, k],...] meaning node numbers

        N.B.:
        'nodes_floor' # [[x, y],...] nodes in x, y on ground level
        'edges_floor' # [[i, j],...] meaning nodes numbers on ground level
        """
        nodes_floor = [[0, 0], [self.width, 0], [self.width, self.depth], [0, self.depth]]
        edges_floor = [[0, 1], [1, 2], [2, 3], [3, 0]]

        nodes, edges, faces = convert_geom_data(nodes_floor, edges_floor, self.height)

        faces += add_roof_faces(nodes, edges)

        self.nodes = nodes
        self.edges = edges
        self.faces = faces
        return


@dataclass
class Shearwall:
    """
    Datatype represents shearwall.
    """
    label: str = 'name'
    top_flange_width: int = 1400  # mm
    top_flange_height: int = 250  # mm
    web_width: int = 2500  # mm
    web_height: int = 5000  # mm
    bot_flange_width: int = 1400  # mm
    bot_flange_height: int = 250  # mm
    aligned: str = 'left'  # 'left', 'center' or 'right'
    height: float = 25.0  # m
    insert_point: list = field(default_factory=list)


    def calc_geom_data(self):
        """
        Returns a dictionary with nodes, edges and faces, 
        representing the 3d geometry of a shearwall.
        'nodes' # [[x, y, z],...] nodes in x, y, z
        'edges' # [[i, j],...] meaning node numbers
        'faces' # [[i, j, k],...] meaning node numbers

        N.B.:
        'nodes_floor' # [[x, y],...] nodes in x, y on ground level
        'edges_floor' # [[i, j],...] meaning nodes numbers on ground level
        """
        
        h = (self.top_flange_height / 2 + self.web_height + self.bot_flange_height / 2) / 1000

        if self.aligned == 'center':
            nodes_floor = [[-(self.top_flange_width / 2) / 1000, h], [0, h], [(self.top_flange_width / 2) / 1000, h]]
            nodes_floor += [[-(self.bot_flange_width / 2) / 1000, 0], [0, 0], [(self.bot_flange_width / 2) / 1000, 0]]
            edges_floor = [[0, 1], [1, 2], [3, 4], [4, 5], [1, 4]]
        elif self.aligned == 'left':
            nodes_floor = [[0, h], [self.top_flange_width / 1000, h]]
            nodes_floor += [[0, 0], [self.bot_flange_width / 1000, 0]]
            edges_floor = [[0, 1], [2, 3], [0, 2]]
        elif self.aligned == 'right':
            nodes_floor = [[-self.top_flange_width / 1000, h], [0, h]]
            nodes_floor += [[-self.bot_flange_width / 1000, 0], [0, 0]]
            edges_floor = [[0, 1], [2, 3], [1, 3]]
        else:
            print("Error. No valid alignment given")

        for node_floor in nodes_floor:
            node_floor[0] += self.insert_point[0]
            node_floor[1] += self.insert_point[1]

        nodes, edges, faces = convert_geom_data(nodes_floor, edges_floor, self.height)

        self.nodes = nodes
        self.edges = edges
        self.faces = faces
        return

    
def convert_geom_data(nodes_floor, edges_floor, height):
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


def add_roof_faces(nodes, edges):
    """
    """
    start_roof_idx = int(len(nodes) / 2)
    roof_faces = [[edges[0][0] + start_roof_idx, edges[1][0] + start_roof_idx, edges[2][0] + start_roof_idx]]
    roof_faces.append([edges[0][0] + start_roof_idx, edges[2][0] + start_roof_idx, edges[3][0] + start_roof_idx])
    return roof_faces


def plot_building(building, shearwalls: Optional= None):
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
    for shearwall in shearwalls:
        # shearwall.calc_geom_data()
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


