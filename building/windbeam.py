from building.building import Building
import streamlit as st

def floor(bd: Building):
    """
    """
    sw_ins = []
    for sw in bd.shearwalls:
        sw_ins.append(sw.insert_point)
    
    windbeam_nodes = sw_ins.copy()
    
    if 0.0 not in windbeam_nodes:
            windbeam_nodes.append(0.0)

    length = bd.width
    if length not in windbeam_nodes:
        windbeam_nodes.append(length)

    # sw_ins = sorted(sw_ins)
    windbeam_nodes = sorted(windbeam_nodes)
    # st.write('sw_ins', sw_ins)
    # st.write('windbeam_nodes', windbeam_nodes)
    spans = {}
    
    for idx, node in enumerate(windbeam_nodes[:-1]):
        spans[idx] = windbeam_nodes[idx + 1] - windbeam_nodes[idx]
    

    supports = {}
    for idx, support in enumerate(sw_ins):
        supports[idx] = support

    forces = calculate_windbeam(sw_ins, windbeam_nodes)
    st.write('forces', forces)
    for idx, sw in enumerate(bd.shearwalls):
        st.write('PPP', idx, bd.width, forces[idx])
        # st.write('>>>', idx, sw, forces[idx])
        # sw.windshare = forces[idx] / bd.width
        # st.write(sw.windshare)

    # st.write('forces', forces)
    return bd
    
    
def calculate_windbeam(sw_ins, windbeam_nodes):
    """
    """
    wind = {}
    support = False
    remainder = 0
    for idx, node in enumerate(windbeam_nodes):
        if node in sw_ins: 
            support=True 
        else: 
            support=False
        
        if support and idx == 0:
            wind[idx] = windbeam_nodes[idx + 1] / 2

        elif support and idx == len(windbeam_nodes) - 1:
            wind[idx] = (windbeam_nodes[-1] - windbeam_nodes[-2]) / 2

        elif not support and idx == 0:
            remainder = windbeam_nodes[1] / 2

        elif not support and idx == len(windbeam_nodes) - 1:
            remainder = (windbeam_nodes[-1] - windbeam_nodes[-2]) / 2
            wind[idx - 1] += remainder

        elif support and not idx == len(windbeam_nodes) - 1:
        
            wind[idx] = (windbeam_nodes[idx + 1] - windbeam_nodes[idx - 1]) / 2 + remainder
            remainder = 0
    return wind