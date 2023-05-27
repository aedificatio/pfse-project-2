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
        st.header(sw.label)
        bd.shearwalls[idx].top_flange_width = tab.number_input("Top Flange Width (mm)", value=1400, step=50, key=f'{sw.label}_tf_w')
        bd.shearwalls[idx].top_flange_height = tab.number_input("Top Flange Height (mm)", value=250, step=50, key=f'{sw.label}_tf_h')
        bd.shearwalls[idx].web_width = tab.number_input("Web Width (mm)", value=250, step=50, key=f'{sw.label}_web_w')
        bd.shearwalls[idx].web_height = tab.number_input("Web Width (mm)", value=5000, step=50, key=f'{sw.label}_web_h')
        bd.shearwalls[idx].bot_flange_width = tab.number_input("Bottom Flange Width (mm)", value=1400, step=50, key=f'{sw.label}_bf_w')
        bd.shearwalls[idx].bot_flange_height = tab.number_input("Bottom Flange Height (mm)", value=250, step=50, key=f'{sw.label}_bf_h')
        # bd.initialize_data()
        st.plotly_chart(bd.shearwalls[idx].plot, use_container_width=True)
        st.write("Hello", )

st.write(bd.shearwalls[0])
st.write(bd.shearwalls[1])
# st.write(bd.shearwalls[1])

# for sw in bd.shearwalls:
#     Shearwall_1, Shearwall_2 = st.tabs(bd.shearwall_labels)
#     st.write(type(Shearwall_1[0]))
#     with Shearwall_1:
#         st.header("A cat")
#         st.plotly_chart(sw.plot, use_container_width=True)

