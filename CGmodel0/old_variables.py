from pulp import LpProblem, LpVariable, lpSum, LpMaximize, value

# Define the updated input parameters based on your adjustment
N = ["N1", "N2", "N3", "N4", "N5", "N6"]  # Updated physical nodes
L = [("N1", "N2"), ("N2", "N3"), ("N3", "N4"), ("N4", "N5"), ("N5", "N6"), ("N6", "N1"),
     ("N2", "N1"), ("N3", "N2"), ("N4", "N3"), ("N4", "N5"), ("N6", "N5"), ("N1", "N6")]  # Updated physical links
K = ["SFC1", "SFC2"]  # Service Function Chains
Ns = ["V1", "V2", "V3","V4", "V5", "V6"]  # Updated nodes in each SFC
Nk = {"SFC1": ["V1", "V2", "V3"], "SFC2": ["V4", "V5", "V6"]}  # Updated nodes in each SFC
Nk_pairs = {k: [(v, w) for v in Nk[k] for w in Nk[k] if v != w] for k in K}  # Node pairs in each SFC

# Updated resource requirements
r = {"V1": 50, "V2": 30, "V3": 30, "V4": 40, "V5": 45, "V6": 35}  # Updated node resource requirements
r_vw = {("V1","V2"): 20,("V2","V1"): 20,("V2","V3") : 20,("V3","V2"): 20,("V1","V3"): 20,("V3","V1") : 20, 
        ("V4","V5"): 25,("V5","V4"): 25, ("V5","V6"): 25,("V6","V5"): 25, ("V4","V6"): 25,("V6","V4"): 25}  # Updated link resource requirements for each SFC
ai = {"N1": 100, "N2": 80, "N3": 30, "N4": 40, "N5": 45, "N6": 35}  # Updated available resources at each node
aij = {
    ("N1", "N2"): 60, ("N2", "N1") : 60,    
    ("N2", "N3"): 60, ("N3", "N2") : 60,
    ("N3", "N4"): 60, ("N4", "N3") : 60,
    ("N4", "N5"): 60, ("N5", "N4") : 60,
    ("N5", "N6"): 60, ("N6", "N5") : 60,
    ("N6", "N1"): 60, ("N1", "N6") : 60
}  # Updated available resources on each link
for i in N:
    for j in N:
        if i!=j and (i,j) not in L:
            aij[(i,j)] = 0


