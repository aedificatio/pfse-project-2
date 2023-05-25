from building.building import Shearwall
import pandas as pd

def calculate_section(wall: Shearwall):
    """
    """
    wall.top_flange_width
    wall.top_flange_height
    wall.web_height
    wall.web_width
    wall.bot_flange_width
    wall.bot_flange_height

    df = pd.DataFrame(layers, columns=["b", "h"])
    df['A'] = df['b'] * df['h']
    df['Iy_eigen'] = 1/12 * df['b'] * df['h']**3
    df['center_top'] = df['h'].cumsum() - df['h'] / 2
    df['S'] = df['A'] * df['center_top']

    e_top_el = df['S'].sum() / df['A'].sum()
    e_bot_el = df['h'].sum() - e_top_el

    df['zwp_center_el'] = e_top_el - df['center_top']
    df['Aaa'] = df['A'] * df['zwp_center_el']**2

    h_tot = df['h'].sum() 
    A_tot = df['A'].sum()
    Iy = df['Iy_eigen'].sum() + df['Aaa'].sum()
    section = 4
    return section