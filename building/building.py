"""
A module for calculating a steel beam as a crane runway beam steel stresses.
"""
from dataclasses import dataclass
from typing import Optional
from building.building_plot import expand_geom_data
from building.foundation import Foundation
from building.shearwall import Shearwall, calc_geom_data, calculate_section, plot_section


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
    floor_reactions: Optional[list] = None
    floor_data_My: Optional[list] = None
    floor_data_Vz: Optional[list] = None
    floor_plot_My: Optional[list] = None
    floor_plot_Vz: Optional[list] = None
    

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

        nodes, edges, faces = expand_geom_data(nodes_floor, edges_floor, self.height)

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
            sw = Shearwall()
            sw.label = f"Shearwall {idx + 1}"
            sw.height = self.height
            if idx == 0:
                sw.aligned = "left"
            elif idx == self.no_shearwalls - 1:
                sw.aligned = "right"
            else:
                sw.aligned = "center"
            sw.insert_point = self.sw_insert_points[idx]
            sw = calc_geom_data(sw)
            sw = calculate_section(sw)
            sw = plot_section(sw)
            sw.foundation = Foundation(label=f'Foundation {idx + 1}')
            shearwalls.append(sw)
            shearwall_labels.append(sw.label)
        self.shearwalls = shearwalls
        self.shearwall_labels = shearwall_labels
        return
    

def add_roof_faces(nodes, edges):
    """
    """
    start_roof_idx = int(len(nodes) / 2)
    roof_faces = [[edges[0][0] + start_roof_idx, edges[1][0] + start_roof_idx, edges[2][0] + start_roof_idx]]
    roof_faces.append([edges[0][0] + start_roof_idx, edges[2][0] + start_roof_idx, edges[3][0] + start_roof_idx])
    return roof_faces


