from building import windbeam

def test_calculate_windbeam():
    # test data
    supports = {'0': 10, '1': 40}
    nodes = [0, 10, 40, 50]
    UDL_floor = 1.2
    x = windbeam.calculate_windbeam(supports, nodes, UDL_floor)
    
    assert x[0][0] == 30