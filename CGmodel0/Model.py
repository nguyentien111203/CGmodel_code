from pulp import LpProblem, LpVariable, lpSum, LpMaximize, value

# Define the updated input parameters based on your adjustment
N = ["N1", "N2", "N3", "N4", "N5", "N6"]  # Updated physical nodes
L = [("N1", "N2"), ("N2", "N3"), ("N3", "N4"), ("N4", "N5"), ("N5", "N6"), ("N6", "N1")]  # Updated physical links
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
    ("N1", "N2"): 60,
    ("N2", "N3"): 60,
    ("N3", "N4"): 60,
    ("N4", "N5"): 60,
    ("N5", "N6"): 60,
    ("N6", "N1"): 60,
}  # Updated available resources on each link
for i in N:
    for j in N:
        if i!=j and (i,j) not in L:
            aij[(i,j)] = 0
# Define variables
x_vk_i = LpVariable.dicts("x_vk_i", [(v, k, i) for v in N for k in K for i in N], cat="Binary")
x_vw_k_ij = LpVariable.dicts("x_vw_k_ij", [(v, w, k, i, j) for v in N for w in N for k in K for i in N for j in N], cat="Binary")
pi_k = LpVariable.dicts("pi_k", K, cat="Binary")
y_vw_k = LpVariable.dicts("y_vw_k", [(v, w, k) for v in N for w in N for k in K], cat="Binary")

# Define the objective function
pi_k['SFC1'] = 1
pi_k['SFC2'] = 1

for i in N:
    for k in K:
        for v in Ns:
            x_vk_i[(v,k,i)] = 0
x_vk_i[('V1','SFC1','N1')] = 1
x_vk_i[('V2','SFC1','N2')] = 1
x_vk_i[('V3','SFC1','N3')] = 1
x_vk_i[('V4','SFC2','N4')] = 1
x_vk_i[('V5','SFC2','N5')] = 1
x_vk_i[('V6','SFC2','N6')] = 1

for i in N:
    for j in N:
        for k in K:
            for v in Ns:
                for w in Ns:
                    x_vw_k_ij[(v,w,k,i,j)] = 0
x_vw_k_ij[('V1', 'V2', 'SFC1', 'N1', 'N2')] = 1
x_vw_k_ij[('V2', 'V3', 'SFC1', 'N2', 'N3')] = 1
x_vw_k_ij[('V3', 'V1', 'SFC1', 'N3', 'N1')] = 1
x_vw_k_ij[('V4', 'V5', 'SFC2', 'N4', 'N5')] = 1
x_vw_k_ij[('V5', 'V6', 'SFC2', 'N5', 'N6')] = 1
x_vw_k_ij[('V6', 'V4', 'SFC2', 'N6', 'N4')] = 1

for k in K:
    for w in Ns:
        for v in Ns:
            y_vw_k[(v,w,k)] = 0
y_vw_k[('V1','V2','SFC1')] = 1
y_vw_k[('V2','V3','SFC1')] = 1
y_vw_k[('V3','V1','SFC1')] = 1
y_vw_k[('V4','V5','SFC2')] = 1
y_vw_k[('V5','V6','SFC2')] = 1
y_vw_k[('V6','V4','SFC2')] = 1

