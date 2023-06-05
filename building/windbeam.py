import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.markers as markers
from typing import Dict, Tuple
from PyNite import FEModel3D
from building.building import Building


def floor(bd: Building) -> Building:
    """
    Function takes a Building object calculates the windbeam and plots the results. 
    Returns Building with add variables: 

    'floor_reactions'   : dict with Support reaction forces for each shearwall
    'floor_data_My'     : list with My data
    'floor_data_Vz'     : list with Vz data
    'floor_plot_My'     : plot of My as matplotlib fig
    'floor_plot_Vz'     : plot of Vz as matplotlib fig
    """
    supports = {}
    for idx, sw in enumerate(bd.shearwalls):
        supports[idx] = sw.insert_point
        
    nodes = list(supports.values())
    if 0.0 not in nodes:
            nodes.append(0.0)
    length = bd.width
    if length not in nodes:
        nodes.append(length)
    nodes = sorted(nodes)

    UDL_floor = bd.pd_wind * (bd.height / bd.no_stories) # kN/m1

    support_reactions, data_My, data_Vz = calculate_windbeam(supports, nodes, UDL_floor)
    fig_M, fig_V = plot_MV_results(data_My, data_Vz, nodes, supports)

    bd.floor_reactions = support_reactions
    bd.floor_data_My = data_My
    bd.floor_data_Vz = data_Vz
    bd.floor_plot_My = fig_M
    bd.floor_plot_Vz = fig_V
    for idx, sw in enumerate(bd.shearwalls):
        sw.windshare = support_reactions[idx] / bd.width / UDL_floor

    return bd

@st.cache_data
def calculate_windbeam(
    supports: dict[int, float], 
    nodes: list[list], 
    UDL_floor: float
    ) -> Tuple[dict[int,float], list[list], list[list]]:
    """
    Function calculates the forces on a windbeam (floorlevel).
    Returns a tuple containing:

    - support_reactions : dict with support_reactions for each shearwall
    - data_My           : list[list] with x, My data
    - data_Vz           : list[list] with x, Vz data
    """
    supports = list(supports.values())
    beam_model = FEModel3D()

    beamname = "Windbeam"
    udl = UDL_floor

    node_labels = []
    for idx, node_x_coord in enumerate(nodes):
        node_label = f"N{idx + 1}"
        node_labels.append(node_label)
        beam_model.add_node(node_label, node_x_coord, 0, 0)

    restricted_first_pin = False
    for support in supports:
        node_label = node_labels[nodes.index(support)]
        
        if len(supports) == 1:
            beam_model.def_support(node_label, support_DX=True, support_DY=True, support_DZ=True, 
                                support_RX=True, support_RY=True, support_RZ=True)
        elif not restricted_first_pin:
            beam_model.def_support(node_label, support_DX=True, support_DY=True, support_DZ=True, support_RX=True)
            restricted_first_pin = True
        else:
            beam_model.def_support(node_label, support_DY=True, support_DZ=True)

    beam_model.add_material(name = 'Concrete', E = 20000, G = 11200, nu = 0.3, rho = 2500)

    beam_model.add_member(
        name = beamname,
        i_node = node_labels[0],
        j_node = node_labels[-1],
        material = 'Concrete',
        # E = 10000,
        # G = 1,
        Iy = 1e+10,
        Iz = 1e+10,
        J = 1,
        A = 10000
    )

    beam_model.add_load_combo('LC1', {'WindLoad': 1.0})

    beam_model.add_member_dist_load(
        Member = beamname,
        Direction = 'Fz',
        w1 = -udl,
        w2 = -udl,
        x1 = 0,
        x2 = nodes[-1],
        case = "WindLoad"
    )

    beam_model.analyze()

    support_reactions = {}
    for idx, support in enumerate(supports):
        node_label = node_labels[nodes.index(support)]
        
        Fz = beam_model.Nodes[node_label].RxnFZ['LC1']
        support_reactions[idx] = Fz

    data_My = beam_model.Members[beamname].moment_array(Direction="My", combo_name="LC1", n_points=1000)
    data_Vz = beam_model.Members[beamname].shear_array(Direction="Fz", combo_name="LC1", n_points=1000)
    data_ez = beam_model.Members[beamname].deflection_array(Direction="Fz", combo_name="LC1", n_points=1000)
    return (support_reactions, data_My, data_Vz)


# Nocache
def plot_MV_results(
        data_My,
        data_Vz,
        nodes, 
        supports
    ) -> Tuple[matplotlib.figure.Figure]:
    
    """
    Function plots the forces on a windbeam (floorlevel).
    Returns the Figure objects of the bendingmoments and shearforces.
    
    """
    plot_M = {
        'title': "Bending moment",
        'y_label':'kNm',
        'max': 'green',
        'min': 'blue',
        'selected_pos': 'red'
    }
    plot_V = {
        'title': "Shearforce",
        'y_label': 'kN',
        'max': 'red',
        'min': 'orange',
        'selected_pos': 'red'
    }
    fig_M, ax_M = plot_results(plot_M, data_My, nodes, supports)
    fig_M.set_size_inches(7,5)
    
    fig_V, ax_V = plot_results(plot_V, data_Vz, nodes, supports)
    fig_V.set_size_inches(7,5)
    return (fig_M, fig_V)


@st.cache_data
def plot_results(
    plot_info: Dict[str,str], 
    data: list[list[int]], 
    nodes: list[int],
    supports: list[int],
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes._axes.Axes]:
    """
    Plots the data and returns a Matplotlib Figure and Axes object.
    """
    fig, ax = plt.subplots()
    ax.set_title(plot_info['title'])
    ax.set_xlabel("m")
    ax.set_ylabel(plot_info['y_label'])
    ax.plot(data[0], data[1], plot_info['max'])
    
    ax.fill_between(data[0], data[1], color=plot_info['max'], alpha=0.3)
    ax.plot([0,nodes[-1]],[0,0], color='gray', linewidth=3)
    for support in supports:
        ax.plot(supports[support], 0, marker=markers.CARETUP, color='gray', markersize=9)
    return fig, ax


