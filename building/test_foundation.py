from building import foundation
from math import isclose


def test_calculate_foundation():
    fd = foundation.Foundation(
        label = 'test foundation',
        pile_grid_x = 1500,
        pile_grid_y = 1500,
        pile_no_x = 2,
        pile_no_y = 3,
        pile_stiffness = 100000,
    )

    fd = foundation.calculate_foundation(fd)
    assert fd.foundation_stiffness == 900000




