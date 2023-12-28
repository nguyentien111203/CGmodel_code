import Define_a_column as Dac
import CG_model_solver 



# Define the updated input parameters based on your adjustment
Dac.Mypattern.nodes = ["N1", "N2", "N3", "N4", "N5", "N6"]  # Updated physical nodes
Dac.Mypattern.links = [("N1", "N2"), ("N2", "N3"), ("N3", "N4"), ("N4", "N5"), ("N5", "N6"), ("N6", "N1"),
                      ("N2", "N1"), ("N3", "N2"), ("N4", "N3"), ("N5", "N4"), ("N6", "N5"), ("N1", "N6")]  # Updated physical links
Dac.Mypattern.sfcs = ["SFC1", "SFC2"]  # Service Function Chains
Dac.Mypattern.sfc = {"SFC1": ["V1", "V2", "V3"], "SFC2": ["V4", "V5", "V6"]}  # Updated nodes in each SFC
Dac.Mypattern.vnfs = ["V1", "V2", "V3","V4", "V5", "V6"]

# Updated resource requirements
Dac.Mypattern.vnfs_resource = {"V1": 50, "V2": 30, "V3": 30, "V4": 40, "V5": 45, "V6": 35}  # Updated node resource requirements
Dac.Mypattern.vnfs_link_resource = {("V1","V2"): 20,("V2","V1"): 20,("V2","V3") : 20,("V3","V2"): 20,("V1","V3"): 20,("V3","V1") : 20, 
        ("V4","V5"): 25,("V5","V4"): 25, ("V5","V6"): 25,("V6","V5"): 25, ("V4","V6"): 25,("V6","V4"): 25}  # Updated link resource requirements for each SFC
Dac.Mypattern.nodes_resource = {"N1": 100, "N2": 80, "N3": 30, "N4": 40, "N5": 45, "N6": 35}  # Updated available resources at each node
Dac.Mypattern.links_resource = {
    ("N1", "N2"): 60, ("N2", "N1"): 60,
    ("N2", "N3"): 60, ("N3", "N2"): 60,
    ("N3", "N4"): 60, ("N4", "N3"): 60,
    ("N4", "N5"): 60, ("N5", "N4"): 60,
    ("N5", "N6"): 60, ("N6", "N5"): 60,
    ("N6", "N1"): 60, ("N1", "N6"): 60
}  # Updated available resources on each link

CG_model_solver.column_generation(Dac.Mypattern)