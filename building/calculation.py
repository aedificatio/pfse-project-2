from handcalcs.decorator import handcalc
from typing import Dict, Optional, Tuple
from building.foundation import Foundation, calculate_foundation
from building.shearwall import Shearwall
from building.building import Building
import streamlit as st

hc_renderer = handcalc(override='long', decimal_separator=',')

def F_k1(E: float, I_y: float, l: float) -> float:
    """
    Function calculates the critical load of a fixed cantilever section.
    """
    EI = (E * I_y) / 10**9 # kNm2
    F_k1 = (7.83 * EI) / l**2 # kN
    return F_k1

def F_k2(C_rot: float, l: float) -> float:
    """
    Function calculates the critical load of a stiff section with a springrotation support.
    """
    F_k2 = (2 * C_rot) / l # kN
    return F_k2

def F_ktot(F_k1: float, F_k2: float) -> float:
    """
    Function calculates the critical load of a section with a springrotation support.
    """
    F_ktot = 1 / (1 / F_k1 + 1 / F_k2) # kN
    return F_ktot

def UDL_wind(pd_wind: float, width: float, pct_wind: float) -> float:
    """
    Function calculates the UDL windload on a shearwall.
    """
    UDL_wind = pct_wind * width * pd_wind # kN/m1
    return UDL_wind

def UDL_lean(height: float, N_vd: float, pct_wind: float) -> float:
    """
    Function calculates the UDL load on the shearwall due to the lean.
    """
    theta_lean = 1 / 400
    UDL_lean = theta_lean * ((pct_wind * N_vd) / height) # kN/m1
    return UDL_lean

def UDL_tot(UDL_wind: float, UDL_lean: float) -> float:
    """
    Function calculates the total UDL load on a shearwall.
    """
    UDL_tot = UDL_wind + UDL_lean # kN/m1
    return UDL_tot

def N_vd(pct_wind: float, N_vdTot: float) -> float:
    """
    Function calculates the building mass assings to a shearwall.
    """
    N_vd = pct_wind * N_vdTot # kN
    return N_vd

def second_order_effect(F_ktot: float, N_vd: float) -> float:
    """
    Function calculates the secondorder effects of a shearwall.
    """
    n = F_ktot / N_vd
    SecondOrderEffect = n / (n - 1)
    return n

def calculate_moment(UDL_tot: float, l: float, n: float) -> float:
    """
    Function calculates the bending moment at groundlevel including secondorder effects.
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

# No Cache
def sw_calculation(sw: Shearwall, bd: Building) -> Shearwall:
    """
    Function makes handcalculation of a shearwall.
    Returns the shearwall with added dict variables 
    
    'results'           : Nicely formatted values from the calculation
    'results_latex'     : Latex epresentation of the calculation
    """
    N_vd_wall_latex, N_vd_wall = hc_N_vd(sw.windshare, bd.N_vd)
    UDL_wind_latex, UDL_wind = hc_UDL_wind(bd.pd_wind, bd.width, sw.windshare)
    UDL_lean_latex, UDL_lean = hc_UDL_lean(bd.height, bd.N_vd, sw.windshare)
    UDL_tot_latex, UDL_tot = hc_UDL_tot(UDL_wind, UDL_lean)
    F_k1_latex, F_k1 = hc_F_k1(sw.E_wall, sw.Iy, bd.height)
    F_k2_latex, F_k2 = hc_F_k2(sw.foundation.foundation_stiffness, bd.height)
    F_ktot_latex, F_ktot = hc_F_ktot(F_k1, F_k2)
    n_latex, n_value = hc_second_order_effect(F_ktot, N_vd_wall)
    M_SecondOrder_latex, M_SecondOrder = hc_calculate_moment(UDL_tot, bd.height, n_value)

    results = {
        'Windshare': f'{sw.windshare * 100:.2f}%',
        'UDL_wind': f'{UDL_wind:.2f} kN/m1',
        'UDL_lean': f'{UDL_lean:.2f} kN/m1',
        'UDL_tot': f'{UDL_tot:.2f} kN/m1',
        'C_rot': f'{sw.foundation.foundation_stiffness:.3e} kNm/rad',
        'N_vd_wall': f'{N_vd_wall:.0f} kN',
        'F_k1': f'{F_k1:.0f} kN',
        'F_k2': f'{F_k2:.0f} kN',
        'F_ktot': f'{F_ktot:.0f} kN',
        'n_value': f'{n_value:.3f}',
        'SecondOrderEffect': f'{(n_value / (n_value - 1) - 1) * 100:.2f}%',
        'M_SecondOrder': f'{M_SecondOrder:.0f} kNm',
    }
    results_latex = {
        'UDL_wind': UDL_wind_latex,
        'UDL_lean': UDL_lean_latex,
        'UDL_tot': UDL_tot_latex,
        'N_vd_wall': N_vd_wall_latex,
        'F_k1': F_k1_latex,
        'F_k2': F_k2_latex,
        'F_ktot': F_ktot_latex,
        'n_latex': n_latex,
        'M_SecondOrder': M_SecondOrder_latex
    }
    sw.results = results
    sw.results_latex = results_latex
    return sw


def display_sw_calculation(sw: Shearwall) -> None:
    """
    Function displays the latex handcalculation of a shearwall.
    """
    st.subheader('Wall load')
    st.write(f'This shearwall takes {sw.windshare * 100:.2f}% of the windload and the stability of the building weight')
    
    st.write('\nBuilding weight to stabilize:')
    st.latex(sw.results_latex["N_vd_wall"])

    st.write('\nWindload on shearwall:')
    st.latex(sw.results_latex["UDL_wind"])
    
    st.write('\nLoad on shearwall by $\\theta_{lean}$:')
    st.latex(sw.results_latex["UDL_lean"])

    st.write('\nTotal load on shearwall:')
    st.latex(sw.results_latex["UDL_tot"])
    st.divider()

    st.subheader('Wall capacity')
    st.latex(sw.results_latex["F_k1"])

    st.latex(sw.results_latex["F_k2"])

    # Can we put this latex line in the function?
    st.latex('\\frac{1}{F_{ktot}} = \\frac{1}{F_{k1}} + \\frac{1}{F_{k2}}')
    st.latex(sw.results_latex["F_ktot"])
    st.divider()

    st.subheader('Second order effects')
    st.latex(sw.results_latex["n_latex"])
    st.divider()

    st.subheader('Moments at groundfloor level')
    st.latex(sw.results_latex["M_SecondOrder"])







    


    
