from handcalcs.decorator import handcalc
from typing import Dict, Optional, Tuple
from building.foundation import Foundation, calculate_foundation
from building.shearwall import Shearwall
from building.building import Building
import streamlit as st

hc_renderer = handcalc(override='long', decimal_separator=',')

def F_k1(E, I_y, l):
    """
    """
    EI = (E * I_y) / 10**9 # kNm2
    F_k1 = (7.83 * EI) / l**2 # kN
    return F_k1

def F_k2(C_rot, l):
    """
    """
    F_k2 = (2 * C_rot) / l # kN
    return F_k2

def F_ktot(F_k1, F_k2):
    """
    """
    F_ktot = 1 / (1 / F_k1 + 1 / F_k2) # kN
    return F_ktot

def UDL_wind(pd_wind, height, width, no_stories, pct_wind):
    """

    """
    UDL_wind = pct_wind * width * pd_wind * (height / no_stories) # kN/m1
    return UDL_wind

def UDL_lean(height, N_vd):
    """
    """
    theta_lean = 1 / 400
    UDL_lean = theta_lean * (N_vd / height) # kN/m1
    return UDL_lean

def UDL_tot(UDL_wind, UDL_lean):
    """
    """
    UDL_tot = UDL_wind + UDL_lean # kN/m1
    return UDL_tot

def N_vd(pct_wind, N_vdTot):
    """
    """
    N_vd = pct_wind * N_vdTot # kN
    return N_vd

def second_order_effect(F_ktot, N_vd):
    """
    """
    n = F_ktot / N_vd
    SecondOrderEffect = n / (n - 1)
    return n

def calculate_moment(UDL_tot, l, n):
    """
    """
    M_FirstOrder = (1/2) * UDL_tot * l**2 # kNm
    M_SecondOrder = n / (n - 1) * M_FirstOrder # kNm
    return M_SecondOrder


hc_calculate_foundation = hc_renderer(calculate_foundation)
hc_F_k1 = hc_renderer(F_k1)
hc_F_k2 = hc_renderer(F_k2)
hc_F_ktot = hc_renderer(F_ktot)
hc_UDL_wind = hc_renderer(UDL_wind)
hc_UDL_lean = hc_renderer(UDL_lean)
hc_UDL_tot = hc_renderer(UDL_tot)
hc_N_vd = hc_renderer(N_vd)
hc_second_order_effect = hc_renderer(second_order_effect)
hc_calculate_moment = hc_renderer(calculate_moment)


def sw_calculation(sw: Shearwall, bd: Building):
    """
    """

    # st.subheader('Pile foundation')

    # pile_foundation, _ = hc_calculate_foundation(sw.foundation)
    # st.latex(pile_foundation)
    # st.write(f'The rotational stiffness of the pile foundation is: {sw.foundation.foundation_stiffness:.4e} $kNm/rad$')
    # st.divider()
    
    st.subheader('Wall load')
    st.write(f'This shearwall takes {sw.windshare * 100:.2f}% of the windload and the stability of the building weight')
    
    st.write('\nBuilding weight to stabilize:')
    N_vd_wall_latex, N_vd_wall = hc_N_vd(sw.windshare, bd.N_vd)
    st.latex(N_vd_wall_latex)

    st.write('\nWindload on shearwall:')
    UDL_wind_latex, UDL_wind = hc_UDL_wind(bd.pd_wind, bd.height, bd.width, bd.no_stories, sw.windshare)
    st.latex(UDL_wind_latex)
    
    st.write('\nLoad on shearwall by $\\theta_{lean}$:')
    UDL_lean_latex, UDL_lean = hc_UDL_lean(bd.height, bd.N_vd)
    st.latex(UDL_lean_latex)

    st.write('\nTotal load on shearwall:')
    UDL_tot_latex, UDL_tot = hc_UDL_tot(UDL_wind, UDL_lean)
    st.latex(UDL_tot_latex)
    st.divider()

    st.subheader('Wall capacity')
    F_k1_latex, F_k1 = hc_F_k1(sw.E_wall, sw.Iy, bd.height)
    st.latex(F_k1_latex)

    F_k2_latex, F_k2 = hc_F_k2(sw.foundation.foundation_stiffness, bd.height)
    st.latex(F_k2_latex)

    # Can we put this latex line in the function?
    st.latex('\\frac{1}{F_{ktot}} = \\frac{1}{F_{k1}} + \\frac{1}{F_{k2}}')
    F_ktot_latex, F_ktot = hc_F_ktot(F_k1, F_k2)
    st.latex(F_ktot_latex)
    st.divider()

    st.subheader('Second order effects')
    n_latex, n_value = hc_second_order_effect(F_ktot, N_vd_wall)
    st.latex(n_latex)
    st.divider()

    st.subheader('Moments at groundfloor level')
    M_SecondOrder_latex, M_SecondOrder = hc_calculate_moment(UDL_tot, bd.height, n_value)
    st.latex(M_SecondOrder_latex)

    results = {
        'C_rot': f'{sw.foundation.foundation_stiffness:.3e} kNm/rad',
        'N_vd_wall': f'{N_vd_wall:.0f} kN',
        'UDL_wind': f'{UDL_wind:.2f} kN/m1',
        'UDL_lean': f'{UDL_lean:.2f} kN/m1',
        'UDL_tot': f'{UDL_tot:.2f} kN/m1',
        'F_k1': f'{F_k1:.0f} kN',
        'F_k2': f'{F_k2:.0f} kN',
        'F_ktot': f'{F_ktot:.0f} kN',
        'n_value': f'{n_value:.3f}',
        'SecondOrderEffect': f'{(n_value / (n_value - 1) - 1) * 100:.2f}%',
        'M_SecondOrder': f'{M_SecondOrder:.0f} kNm',
    }
    sw.results = results
    return sw






    


    
