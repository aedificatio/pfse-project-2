"""
A module for calculating a steel beam as a crane runway beam steel stresses.
"""

import streamlit as st
import pycba as cba
import numpy as np
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.markers as markers
import matplotlib.patches as patches
from plotly import graph_objects as go
import plotly.express as px
from rich import print as rprint
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
from handcalcs.decorator import handcalc
import pandas as pd
from building.plot_geometry import convert_geom_data


@dataclass
class Building:
    """
    Datatype represents the geometry of a building.
    """
    width: float = 40.0  # m
    depth: float = 15.0  # m
    height: float = 25.0  # m
    no_stories: int = 5  # amount
    no_shearwalls: Optional[int] = None
    N_vd: Optional[int] = None  # kN
    pd_wind: Optional[float] = None # kN/m2
    
    def initialize_data(self):
        """
        """
        self.calc_geom_data()
        self.sw_insert_points()
        self.create_shearwalls()
        return

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
    
    def sw_insert_points(self):
        """
        """
        insertion_points = []
        if self.no_shearwalls == 1:
            insertion_points.append(self.width / 2)
        else:
            for i in range(self.no_shearwalls):
                insertion_points.append(i * self.width / (self.no_shearwalls - 1))
        self.sw_insert_points = insertion_points
        return
    
    def create_shearwalls(self):
        """
        """
        shearwalls = []
        shearwall_labels = []
        for idx in range(self.no_shearwalls):
            x = Shearwall()
            x.label = f"Shearwall {idx + 1}"
            x.height = self.height
            if idx == 0:
                x.aligned = "left"
            elif idx == self.no_shearwalls - 1:
                x.aligned = "right"
            else:
                x.aligned = "center"
            x.insert_point = [self.sw_insert_points[idx],0]
            x.calc_geom_data()
            x = calculate_section(x)
            x = plot_section(x)
            shearwalls.append(x)
            shearwall_labels.append(x.label)
        self.shearwalls = shearwalls
        self.shearwall_labels = shearwall_labels
        return
    



@dataclass
class Shearwall:
    """
    Datatype represents shearwall.
    """
    label: str = 'name'
    E_wall: int = 10000  # MPa
    top_flange_width: int = 1400  # mm
    top_flange_height: int = 250  # mm
    web_width: int = 250  # mm
    web_height: int = 5000  # mm
    bot_flange_width: int = 1400  # mm
    bot_flange_height: int = 250  # mm
    aligned: str = 'left'  # 'left', 'center' or 'right'
    height: float = 25.0  # m
    insert_point: list = field(default_factory=list)
    A: Optional[float] = None
    Iy: Optional[float] = None
    h: Optional[float] = None
    e_top: Optional[float] = None
    e_bot: Optional[float] = None
    plot_section: Optional[go.Figure] = None
    plot_foundation: Optional[go.Figure] = None
    pile_stiffness: Optional[float] = None
    pile_size: Optional[int] = None
    pile_grid_x: Optional[int] = None
    pile_grid_y: Optional[int] = None
    pile_no_x: Optional[int] = None
    pile_no_y: Optional[int] = None
    foundation_stiffness: Optional[float] = None
    



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

def add_roof_faces(nodes, edges):
    """
    """
    start_roof_idx = int(len(nodes) / 2)
    roof_faces = [[edges[0][0] + start_roof_idx, edges[1][0] + start_roof_idx, edges[2][0] + start_roof_idx]]
    roof_faces.append([edges[0][0] + start_roof_idx, edges[2][0] + start_roof_idx, edges[3][0] + start_roof_idx])
    return roof_faces

def calculate_section(wall: Shearwall):
    """
    """
    layers = [
        [wall.top_flange_width, wall.top_flange_height],
        [wall.web_width, wall.web_height],
        [wall.bot_flange_width, wall.bot_flange_height]
    ]

    df = pd.DataFrame(layers, columns=["b", "h"])
    df['A'] = df['b'] * df['h']
    df['Iy_eigen'] = 1/12 * df['b'] * df['h']**3
    df['center_top'] = df['h'].cumsum() - df['h'] / 2
    df['S'] = df['A'] * df['center_top']

    e_top = df['S'].sum() / df['A'].sum()
    e_bot = df['h'].sum() - e_top

    df['zwp_center_el'] = e_top - df['center_top']
    df['Aaa'] = df['A'] * df['zwp_center_el']**2
    
    wall.A = df['A'].sum()
    wall.Iy = df['Iy_eigen'].sum() + df['Aaa'].sum()
    wall.h = df['h'].sum() 
    wall.e_top = e_top
    wall.e_bot = e_bot
    return wall

def calculate_foundation(wall: Shearwall):
    """
    """
    pile_stiffness = wall.pile_stiffness
    pile_grid_x = wall.pile_grid_x / 1000
    pile_grid_y = wall.pile_grid_y / 1000
    pile_no_x = wall.pile_no_x
    pile_no_y = wall.pile_no_y

    h_2 = 0.5 * (pile_no_y - 1) * pile_grid_y
    y_s = [-h_2 + pile_grid_y * i for i in range(pile_no_y)]

    
    c_rot = [pile_stiffness * pile_no_x * i**2 for i in y_s]
    wall.foundation_stiffness = sum(c_rot)
    return wall

def plot_section(wall: Shearwall):
    """
    """
    go.Figure()
    fig = go.Figure()
    tf_w = wall.top_flange_width
    tf_h = wall.top_flange_height
    web_w = wall.web_width
    bf_w = wall.bot_flange_width
    bf_h = wall.bot_flange_height

    e_top = wall.e_top
    e_bot = wall.e_bot

    if wall.aligned == 'left':
        tf_x = [0, tf_w, tf_w, 0]
        web_x = [0, web_w, web_w, 0]
        bf_x = [0, bf_w, bf_w, 0]
    elif wall.aligned == 'center':
        tf_x = [-tf_w / 2, tf_w / 2, tf_w / 2, -tf_w / 2]
        web_x = [-web_w / 2, web_w / 2, web_w / 2, -web_w / 2]
        bf_x = [-bf_w / 2, bf_w / 2, bf_w / 2, -bf_w / 2]
    else:
        tf_x = [-bf_w, 0, 0, -bf_w]
        web_x = [-web_w, 0, 0, -web_w]
        bf_x = [-bf_w, 0, 0, -bf_w]

    tf = {'x': tf_x, 'y': [e_top, e_top, e_top - tf_h, e_top - tf_h]}
    web = {'x': web_x, 'y': [-e_bot + bf_h, -e_bot + bf_h, e_top - tf_h, e_top - tf_h]}
    bf = {'x': bf_x, 'y': [-e_bot, -e_bot, -e_bot + bf_h, -e_bot + bf_h]}

    items = [tf, web, bf]

    for item in items:
        fig.add_trace(go.Scatter(
            x=item['x'],
            y=item['y'],
            fill="toself",
            fillcolor='royalblue',
            line_color='royalblue',
            )
        )

    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    fig.update_layout(
        title = wall.label,
        showlegend=False,
        width=500,
        height=600,
    )

    wall.plot_section = fig
    return wall

def plot_foundation(wall: Shearwall):
    """
    """
    go.Figure()
    fig = go.Figure()

    h_2_x = 0.5 * (wall.pile_no_x - 1) * wall.pile_grid_x
    h_2_y = 0.5 * (wall.pile_no_y - 1) * wall.pile_grid_y
    rows = [x * wall.pile_grid_x - h_2_x for x in range(wall.pile_no_x)]
    cols = [y * wall.pile_grid_y - h_2_y for y in range(wall.pile_no_y)]

    coords = []
    for row in rows:
        for col in cols:
            coords.append((row, col))

    for coord in coords:
        x = coord[0]
        y = coord[1]
        delta = wall.pile_size / 2
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
        title = wall.label,
        showlegend=False,
        width=500,
        height=600,
    )

    wall.plot_foundation = fig
    return wall