import streamlit as st
from building import building
from building import plot_geometry

st.header("Designcalculation of shearwalls.")
st.write("NOT for use in real-life, as this is NOT a full implementation")

# Building Parameters
st.sidebar.header("Building Parameters")
bd = building.Building()
bd.width = st.sidebar.number_input("Building Width (m)", value=50, step=1)
bd.depth = st.sidebar.number_input("Building Depth (m)", value=15, step=1)
bd.height = st.sidebar.number_input("Building Height (m)", value=20.0, step=0.5)
bd.no_stories = st.sidebar.slider(
    "Number of stories: ",
    min_value=1,
    max_value=int(bd.height / 2.5),
    value=5
)
bd.N_vd = st.sidebar.number_input("Building Weight N'vd (kN)", value=250000, step=1000)
bd.pd_wind = st.sidebar.number_input("Windforce (kN/m2)", value=1.0, step=0.05)
bd.no_shearwalls = st.sidebar.slider(
    "Number of shearwalls: ",
    min_value=1,
    max_value=4,
    value=2
)
st.sidebar.write("")


bd.initialize_data()

fig = plot_geometry.plot_building(bd)

st.plotly_chart(fig, use_container_width=True)
for idx, tab in enumerate(st.tabs(bd.shearwall_labels)):
    
    with tab:
        
        sw = bd.shearwalls[idx]
        st.header(sw.label)
        sw.E_wall = tab.number_input("Young's Modulus", value=10000, step=100, key=f'E_sw{idx}')
        sw.top_flange_height = tab.number_input("Top Flange Height (mm)", value=250, step=50, key=f'tf_h_sw{idx}')
        sw.web_width = tab.number_input("Web Width (mm)", value=250, step=50, key=f'web_w_sw{idx}')
        sw.web_height = tab.number_input("Web Height (mm)", value=5000, step=50, key=f'web_h_sw{idx}')
        sw.bot_flange_width = tab.number_input("Bottom Flange Width (mm)", value=1400, step=50, key=f'bf_w_sw{idx}')
        sw.bot_flange_height = tab.number_input("Bottom Flange Height (mm)", value=250, step=50, key=f'bf_h_sw{idx}')

        sw = building.calculate_section(sw)
        sw = building.plot_section(sw)
        st.plotly_chart(bd.shearwalls[idx].plot_section, use_container_width=True)

        sw.pile_stiffness = tab.number_input("Pile Stiffness (kN/m)", value=100000, step=500, key=f'p_stiff_sw{idx}')
        sw.pile_size = tab.number_input("Pile Size (mm)", value=250, step=25, key=f'p_size_sw{idx}')
        sw.pile_grid_x = tab.number_input("Pile Grid X (mm)", value=1500, step=50, key=f'grid_x_sw{idx}')
        sw.pile_grid_y = tab.number_input("Pile Grid Y (mm)", value=1500, step=50, key=f'grid_y_sw{idx}')
        sw.pile_no_x = tab.number_input("Piles in X-direction", value=2, step=1, key=f'p_no_x_sw{idx}')
        sw.pile_no_y = tab.number_input("Piles in Y-direction", value=2, step=1, key=f'p_no_y_sw{idx}')

        sw = building.calculate_foundation(sw)
        sw = building.plot_foundation(sw)
        st.plotly_chart(bd.shearwalls[idx].plot_foundation, use_container_width=True)

        st.write(f'$A     $= {sw.A:.0f} $mm^2$')
        st.write(f'$I_y   $= {sw.Iy:.4e} $mm^4$')
        st.write(f'$C_r   $= {sw.foundation_stiffness:.4e} $kN/m$')
        st.write(f'$E_c   $= {sw.E_wall:.0f} $MPa$')

        


