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
        for idx in range(self.no_shearwalls):
            x = Shearwall()
            x.label = f"Shearwall_{idx + 1}"
            x.height = self.height
            if idx == 0:
                x.aligned = "left"
            elif idx == self.no_shearwalls - 1:
                x.aligned = "right"
            else:
                x.aligned = "center"
            x.insert_point = [self.sw_insert_points[idx],0]
            x.calc_geom_data()
            # x.section = building.calculate_section(x)
            shearwalls.append(x)
        self.shearwalls = shearwalls
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
    section: Optional[float] = None


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


