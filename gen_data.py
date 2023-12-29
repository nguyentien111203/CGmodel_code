import networkx as nx

def gen_phy() -> nx.DiGraph():
    PHY = nx.DiGraph()
    PHY.add_node(0, weight = 10)
    PHY.add_node(0, weight = 10)
    PHY.add_node(0, weight = 10)
    # add edge
    return PHY

def gen_sfc() -> nx.DiGraph():
    sfc = nx.DiGraph()
    sfc.add_node(0, weight = 10)
    sfc.add_node(0, weight = 10)
    sfc.add_node(0, weight = 10)
    # add edge
    return sfc