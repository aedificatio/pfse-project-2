import math
import streamlit as st
from building import building

st.header("Designcalculation of shearwalls.")
st.write("NOT for use in real-life, as this is NOT a full implementation")

# Building Geometry Parameters
st.sidebar.header("Building Geometry Parameters")
bd_geom = building.Building_geometry()
bd_geom.width = st.sidebar.number_input("Building Width (m)", value=40, step=1)
bd_geom.depth = st.sidebar.number_input("Building Depth (m)", value=15, step=1)
bd_geom.height = st.sidebar.number_input("Building Height (m)", value=25, step=1)
bd_geom.no_stories = st.sidebar.slider(
    "Number of stories: ", 
    min_value=1, 
    max_value=int(bd_geom.height / 2.5), 
    value=5
)
bd_geom.N_vd = st.sidebar.number_input("Building Weight N'vd (kN)", value=250000, step=1000)
bd_geom.pd_wind = st.sidebar.number_input("Windforce (kN/m2)", value=1.0, step=0.05)
bd_geom.no_shearwalls = st.sidebar.slider(
    "Number of shearwalls: ", 
    min_value=1, 
    max_value=4, 
    value=1
)
st.sidebar.write("")

# create list with shearwall objects
shearwalls = [building.Shearwall() for _ in range(bd_geom.no_shearwalls)]
    
fig = building.plot_building(bd_geom, shearwalls)

# fig
st.plotly_chart(fig, use_container_width=True)


















# for idx in range(1, building_geometry.no_shearwalls + 1):
#     rw_geometry.spans[idx] = st.sidebar.slider(
#         f"Span {idx} - Length in (mm):",
#         min_value=250, 
#         max_value=9000, 
#         value=5000,
#         step = 250
#     )


# # Bridge Crane Parameters
# st.sidebar.write("")
# st.sidebar.header("Bridge Crane Parameters")

# rw_crane = section.Crane()
# rw_crane.crane_load = st.sidebar.number_input("Max Crane Load (kN)", value=350, step=10)
# st.sidebar.write("(This includes self-weight of the bridge crane)")
# rw_crane.no_cranewheels = st.sidebar.slider(
#     "Number of crane wheels: ", 
#     min_value=1, 
#     max_value=4, 
#     value=2
# )
# rw_crane.dist_between_cranewheels = st.sidebar.slider(
#     "Distance between crane wheels - Length in (mm):",
#     min_value=250, 
#     max_value=1500, 
#     value=1000,
#     step = 250
# )


# # Steel Properties
# steel_properties = st.expander(label="Steel Properties")
# with steel_properties:
#     st.header("Steel Properties")
#     rw_material = section.Material()
#     rw_material.fy = st.number_input("Yield strength (MPa)", value=235)
#     rw_material.E_mod = st.number_input("Elastic modulus (MPa)", value=200e3)
#     rw_material.rho = st.number_input("Density ($kg/m^3$)", value = 7850)


# # Section Properties
# section_properties = st.expander(label="Section Properties")
# with section_properties:
#     st.header("Section Properties")
#     rw_section = section.Runway_section()
#     rw_section.top_flange_width = st.number_input("Width top flange (mm)", value = 300)
#     rw_section.top_flange_height = st.number_input("Height top flange (mm)", value = 15)
#     rw_section.web_width = st.number_input("Width of the web (mm)", value = 12)
#     rw_section.web_height = st.number_input("Height of the web (mm)", value = 500)
#     rw_section.bot_flange_width = st.number_input("Width bottom flange (mm)", value = 150)
#     rw_section.bot_flange_height = st.number_input("Height bottom flange (mm)", value = 15)

#     rw_section.section = cr.calc_sectionproperties(
#         material=rw_material,
#         runway_section=rw_section
#     )

#     st.write(f"The current section has the following properties:")
#     st.write(f"- Mass of {rw_section.mass():.3f} ($kg/m^1$)")
#     st.write(f"- A =  {rw_section.area():.0f} ($mm^2$)")
#     st.write(f"- $I_y$ = {rw_section.ixx()/10000:.0f} ($10^4 mm^4$)")
    
#     st.header("Plot Section")
#     plot_centroids = rw_section.section.plot_centroids()
#     st.pyplot(fig=plot_centroids.figure)


# # Calculate Runway
# calculate_runway = st.expander(label="Calculate Crane Runway")
# with calculate_runway:

#     stepsize: float = 0.05
#     results_envelope, results_critical_values, bridge_model = cr.calculate_envelopes(
#         rw_material.E_mod, 
#         rw_geometry.spans, 
#         rw_section.ixx(), 
#         rw_section.mass(), 
#         rw_crane, 
#         stepsize
#     )

#     pos_x_all = results_envelope.x # Numpy array with x values

#     pos_x_selected = st.slider(
#         "Select position of beam crane", 
#         min_value = float(min(pos_x_all)),
#         max_value = float(max(pos_x_all)),
#         value=float(math.floor(pos_x_all.mean())),
#         step=stepsize
#     )
#     # RESULT AT SELECTED POS
#     result_at_pos = bridge_model.static_vehicle(pos=pos_x_selected)

#     fig_M, fig_V = section.plot_MV_results(
#         results_envelope, 
#         pos_x_selected, 
#         result_at_pos, 
#         rw_geometry, 
#         rw_crane
#     )
#     st.pyplot(fig=fig_M)
#     st.pyplot(fig=fig_V)

#     st.subheader("Max & Min Bendingmoments")
#     st.write(
#         f"{-results_critical_values['Mmax']['val']:.3f} kNm \
#         at {results_critical_values['Mmax']['at']:.3f} m \
#         with crane position {results_critical_values['Mmax']['pos']}"
#     )
#     st.write(
#         f"{-results_critical_values['Mmin']['val']:.3f} kNm \
#         at {results_critical_values['Mmin']['at']:.3f} m \
#         with crane position {results_critical_values['Mmin']['pos']}"
#     )
#     st.subheader("Max & Min Shearforces")
#     st.write(
#         f"{results_critical_values['Vmax']['val']:.3f} kN \
#         at {results_critical_values['Vmax']['at']:.3f} m \
#         with crane position {results_critical_values['Vmax']['pos']}"
#     )
#     st.write(
#         f"{results_critical_values['Vmin']['val']:.3f} kN \
#         at {results_critical_values['Vmin']['at']:.3f} m \
#         with crane position {results_critical_values['Vmin']['pos']}"
#     )


# # Show Hand Calculation for runway stresses
# show_handcalcs = st.expander(label="Show Hand Calculation For Runway Stresses")
# with show_handcalcs:
#     st.header("Show Hand Calculation For Runway Stresses")

#     st.write(f"The section height is {rw_section.height():.3f} mm")
#     st.write(f"e_top is {rw_section.ex_top():.3f} mm and Wx_top is {rw_section.Wx_top()/1000:.3f} $10^3 mm^3$")
#     st.write(f"e_bot is {rw_section.ex_bot():.3f} mm and Wx_bot is {rw_section.Wx_bot()/1000:.3f} $10^3 mm^3$")

#     absolute_max_moment = section.calculate_abs_max_bendingmoment(results_critical_values)
#     Mxx=absolute_max_moment*1e+6 # Nmm

#     st.write(f"The absolute maximum bendingmoment is {absolute_max_moment:.3f} kNm")
    
#     calcs_latex, calcs_values = section.handcalculations(rw_section, Mxx)

#     for calc in calcs_latex:
#         st.latex(calc)

#     st.subheader("Calculated stress by sectionproperties.")
#     stress_post = rw_section.section.calculate_stress(Mxx=Mxx)
#     plot_stress = stress_post.plot_stress_m_zz()
#     fig_plot_bendingstress = plot_stress.figure
#     st.pyplot(fig=fig_plot_bendingstress)




