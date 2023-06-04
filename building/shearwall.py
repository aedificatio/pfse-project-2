"""
A module for calculating a steel beam as a crane runway beam steel stresses.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Optional
from plotly import graph_objects as go
from building.building_plot import expand_geom_data
from building.foundation import Foundation


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
    insert_point: Optional[float] = None
    A: Optional[float] = None
    Iy: Optional[float] = None
    h: Optional[float] = None
    e_top: Optional[float] = None
    e_bot: Optional[float] = None
    plot_section: Optional[go.Figure] = None
    foundation: Optional[Foundation] = None
    windshare: Optional[float] = None
    results: Optional[dict] = None


def calc_geom_data(sw: Shearwall):
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

    h = (sw.top_flange_height / 2 + sw.web_height + sw.bot_flange_height / 2) / 1000

    if sw.aligned == 'center':
        nodes_floor = [[-(sw.top_flange_width / 2) / 1000, h], [0, h], [(sw.top_flange_width / 2) / 1000, h]]
        nodes_floor += [[-(sw.bot_flange_width / 2) / 1000, 0], [0, 0], [(sw.bot_flange_width / 2) / 1000, 0]]
        edges_floor = [[0, 1], [1, 2], [3, 4], [4, 5], [1, 4]]
    elif sw.aligned == 'left':
        nodes_floor = [[0, h], [sw.top_flange_width / 1000, h]]
        nodes_floor += [[0, 0], [sw.bot_flange_width / 1000, 0]]
        edges_floor = [[0, 1], [2, 3], [0, 2]]
    elif sw.aligned == 'right':
        nodes_floor = [[-sw.top_flange_width / 1000, h], [0, h]]
        nodes_floor += [[-sw.bot_flange_width / 1000, 0], [0, 0]]
        edges_floor = [[0, 1], [2, 3], [1, 3]]
    else:
        print("Error. No valid alignment given")
    
    for node_floor in nodes_floor:
        node_floor[0] += sw.insert_point
        
    nodes, edges, faces = expand_geom_data(nodes_floor, edges_floor, sw.height)
    
    sw.nodes = nodes
    sw.edges = edges
    sw.faces = faces
    return sw


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