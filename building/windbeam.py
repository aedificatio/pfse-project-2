from building.building import Building
import streamlit as st

def floor(bd: Building):
    """
    """
    supports = {}
    for idx, sw in enumerate(bd.shearwalls):
        supports[idx] = sw.insert_point

    windbeam_nodes = list(supports.values())
    
    if 0.0 not in windbeam_nodes:
            windbeam_nodes.append(0.0)

    length = bd.width
    if length not in windbeam_nodes:
        windbeam_nodes.append(length)
    
    windbeam_nodes = sorted(windbeam_nodes)
    
    wind = calculate_windbeam(supports, windbeam_nodes)
    for idx, sw in enumerate(bd.shearwalls):
        sw.windshare = wind[idx] / bd.width
    return bd
    
    
def calculate_windbeam(supports, windbeam_nodes):
    """
    """
    wind = {}
    support = False
    remainder = 0
    for idx, node in enumerate(windbeam_nodes):
        if node in supports.values(): 
            support=True 
            support_idx = [k for k, v in supports.items() if v == node][0]
        else: 
            support=False
        
        if support and idx == 0:
            wind[support_idx] = windbeam_nodes[idx + 1] / 2

        elif support and idx == len(windbeam_nodes) - 1:
            if len(supports) == 1:
                wind[support_idx] = (windbeam_nodes[-1] - windbeam_nodes[-2])
            else:
                wind[support_idx] = (windbeam_nodes[-1] - windbeam_nodes[-2]) / 2

        elif not support and idx == 0:
            remainder = windbeam_nodes[1] / 2

        elif not support and idx == len(windbeam_nodes) - 1:
            remainder = (windbeam_nodes[-1] - windbeam_nodes[-2]) / 2
            support_idx = list(supports.keys())[-1]
            wind[support_idx] += remainder
            
        elif support and not idx == len(windbeam_nodes) - 1:
            wind[support_idx] = (windbeam_nodes[idx + 1] - windbeam_nodes[idx - 1]) / 2 + remainder
            remainder = 0
    return wind