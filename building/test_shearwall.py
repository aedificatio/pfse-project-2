from building import shearwall
from math import isclose


def test_calculate_section():
    sw = shearwall.Shearwall(
        label = 'name',
        E_wall = 10000,
        top_flange_width = 1400,
        top_flange_height = 250,
        web_width = 250,
        web_height = 5000,
        bot_flange_width = 1400,
        bot_flange_height = 250,
    )
    sw = shearwall.calculate_section(sw)
    assert sw.Iy == 7431250000000
    assert sw.A == 1950000