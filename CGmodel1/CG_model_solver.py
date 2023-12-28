from pulp import *
import Define_a_column as Dac
import math

#This is for generating initial columns
def generate_Initial_Column(myp:Dac.Mypattern) :
    patterns = []
    column1 = {'N1':'V1','N2':'V2','N3':'V3','N4':'0','N5':'0','N6':'0'}
    pattern1 = myp(myp.sfc,myp.sfcs,myp.vnfs,myp.vnfs_resource,myp.vnfs_link_resource,myp.nodes,myp.nodes_resource,myp.links,myp.links_resource,column1)
    patterns.append(pattern1)

    column2 = {'N1':'0','N2':'V1','N3':'V2','N4':'V3','N5':'0','N6':'0'}
    pattern2 = myp(myp.sfc,myp.sfcs,myp.vnfs,myp.vnfs_resource,myp.vnfs_link_resource,myp.nodes,myp.nodes_resource,myp.links,myp.links_resource,column2)    
    patterns.append(pattern2)

    column3 = {'N1':'V4','N2':'V5','N3':'V6','N4':'0','N5':'0','N6':'0'}
    pattern3 = myp(myp.sfc,myp.sfcs,myp.vnfs,myp.vnfs_resource,myp.vnfs_link_resource,myp.nodes,myp.nodes_resource,myp.links,myp.links_resource,column3)
    patterns.append(pattern3)

    column4 = {'N1':'0','N2':'0','N3':'0','N4':'V4','N5':'V5','N6':'V6'}
    pattern4 = myp(myp.sfc,myp.sfcs,myp.vnfs,myp.vnfs_resource,myp.vnfs_link_resource,myp.nodes,myp.nodes_resource,myp.links,myp.links_resource,column4)
    patterns.append(pattern4)

    return patterns


#This is for master problem
def master_problem(myp:Dac.Mypattern,patterns) :
    #Create problem
    master_prob = LpProblem(name='Putting_VNFs',sense=LpMaximize)

    #Define decision variables
    lamda = LpVariable.dict(name='Putting_column',indices=range(0,len(patterns)),lowBound=0,upBound=1,cat='Continuous')

    #Define constraints
    #Constraint 1 : Resource on node 
    for i in myp.nodes:
        master_prob += lpSum(pattern.h(i)*lamda[patterns.index(pattern)] for pattern in patterns) <= myp.nodes_resource[i],f'Resource_node_{i}'
    
    #Constraint 2 : Resource on link
    for i in myp.nodes:
        for j in myp.nodes:
            if (i,j) in myp.links:
                master_prob += lpSum(pattern.b(i,j)*lamda[patterns.index(pattern)] for pattern in patterns) <= myp.links_resource[(i,j)],f'Resource_link_{i}_{j}'

    #Constraint 3 : Every sfc can use only one column at max
    for k in myp.sfcs:
        master_prob += lpSum(pattern.m(k)*lamda[patterns.index(pattern)] for pattern in patterns) <= 1,f'{k}_max_1_column'

    #Constraint 4 : Every nodes can be put only one vnf at max
    for i in myp.nodes:
        master_prob += lpSum(pattern.e(i)*lamda[patterns.index(pattern)] for pattern in patterns) <= 1,f'{i}_can_be_put_one'
    
    #Constraint 5 : Not exceed the initial number of sfc
    master_prob += lpSum(lamda[patterns.index(pattern)] for pattern in patterns) <= len(myp.sfcs),f'Not_exceed'

    #Objective : Maximize the number of sfcs can be put
    master_prob += lpSum(lamda[patterns.index(pattern)] for pattern in patterns)


    return master_prob


#This is for subproblem
def subProblem(myp:Dac.Mypattern,duals_nodes,duals_links,duals_node_vnf,duals_sfc,duals_exceed,k) :
    #Create the subproblem
    subprob = LpProblem(name='Subproblem',sense=LpMinimize)

    #Define the decision variables
    x_vk_i = LpVariable.dicts("x_vk_i", [(v, k, i) for k in myp.sfcs for v in myp.sfc[k] for i in myp.nodes],cat='Binary')
    x_vw_k_ij = LpVariable.dicts("x_vw_k_ij", [(v, w, k, i, j) for k in myp.sfcs for v in myp.vnfs for w in myp.vnfs for i in myp.nodes for j in myp.nodes if (i,j) in myp.links],cat='Binary')
    y_vw_k = LpVariable.dicts("y_vw_k", [(v, w, k) for k in myp.sfcs for v in myp.sfc[k] for w in myp.sfc[k]], cat="Binary")
    z_vw_k_ij = LpVariable.dicts("z_vw_k_ij", [(v, w, k, i, j) for k in myp.sfcs for v in myp.vnfs for w in myp.vnfs for i in myp.nodes for j in myp.nodes if (i,j) in myp.links],cat='Binary')

    #Define the constraint
    
    #Resources on node 
    for i in myp.nodes :
        subprob += lpSum(x_vk_i[(v,k,i)]*myp.vnfs_resource[v] for v in myp.sfc[k]) <= myp.nodes_resource[i]  

    #Resource on link
    for i in myp.nodes:
        for j in myp.nodes:
            if (i,j) in myp.links:
                subprob += lpSum(z_vw_k_ij[(v,w,k,i,j)]*myp.vnfs_link_resource[(v,w)] for v in myp.sfc[k] for w in myp.sfc[k] if w!=v) <= myp.links_resource[(i,j)]
            #Constraint for variables z
                for v in myp.sfc[k]:
                    for w in myp.sfc[k]:
                        if w!=v:
                            subprob += z_vw_k_ij[(v,w,k,i,j)] - x_vw_k_ij[(v,w,k,i,j)] >= 0
                            subprob += z_vw_k_ij[(v,w,k,i,j)] - y_vw_k[(v,w,k)] >= 0
                            subprob += x_vw_k_ij[(v,w,k,i,j)] + y_vw_k[(v,w,k)] - 1 >= z_vw_k_ij[(v,w,k,i,j)]
    #All node can be put only one vNF
    for i in myp.nodes :
        subprob += lpSum(x_vk_i[(v,k,i)] for v in myp.sfc[k]) <= 1 
    #Every vnf of that sfc have to be put on the physical network
    for v in myp.sfc[k] :
        subprob += lpSum(x_vk_i[(v,k,i)] for i in myp.nodes) == 1 
    #Flow conservation
    M = 1000
    for i in myp.nodes :
        for v in myp.sfc[k]:
            for w in myp.sfc[k]:
                if v!=w :
                    subprob += (lpSum(x_vw_k_ij[(v,w,k,i,j)] for j in myp.nodes if (i,j) in myp.links)-lpSum(x_vw_k_ij[(v,w,k,j,i)] for j in myp.nodes if (j,i) in myp.links))
                    - (x_vk_i[(v,k,i)]-x_vk_i[(w,k,i)]) >= -M*(1-y_vw_k[(v,w,k)]) 
       
                    subprob += (lpSum(x_vw_k_ij[(v,w,k,i,j)] for j in myp.nodes if (i,j) in myp.links)-lpSum(x_vw_k_ij[(v,w,k,j,i)] for j in myp.nodes if (j,i) in myp.links))
                    - (x_vk_i[(v,k,i)]-x_vk_i[(w,k,i)]) <= M*(1-y_vw_k[(v,w,k)]) 
            
    #Remove reduntdancy variables
    for v in myp.sfc[k] :
        for w in myp.sfc[k]:
            if v!=w :
                subprob += lpSum(x_vw_k_ij[(v,w,k,i,j)] for i in myp.nodes for j in myp.nodes if (i,j) in myp.links) == y_vw_k[(v,w,k)] 

    #Objective : Minimize this reduced cost 
    subprob += (1.0 - lpSum(lpSum(myp.vnfs_resource[v]*x_vk_i[(v,k,i)] for v in myp.sfc[k])*duals_nodes[i] for i in myp.nodes) 
                    - lpSum(myp.vnfs_link_resource[(v,w)]*z_vw_k_ij[(v,w,k,i,j)]*duals_links[(i,j)] for i in myp.nodes for j in myp.nodes for v in myp.sfc[k] for w in myp.sfc[k] if (i,j) in myp.links if v!=w)
                    - duals_sfc[k] 
                    - (lpSum(lpSum(x_vk_i[(v,k,i)] for v in myp.sfc[k])*duals_node_vnf[i] for i in myp.nodes for v in myp.vnfs)
                    - duals_exceed),f'Reduced_cost_{k}')
        
    return subprob
    
#Print the final solution
def print_solution(master, patterns):
    use = []
    for i in master.variables():
        use.append(math.ceil(i.value()))
    for i in range(0,len(patterns)):
        if use[i] > 0:
            print('Choose column ',patterns[i].column)
            print('------------------')
    print()

#This is for column generation
def column_generation(myp:Dac.Mypattern) :
    patterns = generate_Initial_Column(myp)
    for pattern in patterns :
        print(type(pattern))
    print(type(patterns))
    while True :
        master = master_problem(myp,patterns)
        print(master)
        master.solve()
        duals_nodes = {}
        for i in myp.nodes :
            duals_nodes[i] = master.constraints[f'Resource_node_{i}'].pi
        duals_links = {}
        for i in myp.nodes :
            for j in myp.nodes :
                if (i,j) in myp.links :
                    duals_links[(i,j)] = master.constraints[f'Resource_link_{i}_{j}'].pi
        duals_sfcs = {}
        for k in myp.sfcs :
            duals_sfcs[k] = master.constraints[f'{k}_max_1_column'].pi
        duals_node_vnf = {}
        for i in myp.nodes :
            duals_node_vnf[(i)] = master.constraints[f'{i}_can_be_put_one'].pi
        duals_exceed = master.constraints[f'Not_exceed'].pi
        print(duals_nodes)
        print(duals_links)
        print(duals_node_vnf)
        print(duals_sfcs)
        print(duals_exceed)
        your_subproblems_list = []
        allcols = []
        for k in myp.sfcs:
            subproblem = subProblem(myp,duals_nodes,duals_links,duals_node_vnf,duals_sfcs,duals_exceed,k)
            your_subproblems_list.append(subproblem)
            subproblem.solve()
            column = {}
            for var in subproblem.variables():
                if var.name == 'x_vk_i' :
                    if var.varValue == 0:
                        column[i] = '0'
                    else :
                        (v,k,i) = var.indice()
                        column[i] = v
            allcols.append(column)
        RCk_values = [value(subproblem.objective) for subproblem in your_subproblems_list]
        for result in RCk_values:
            print(RCk_values.index(result),' : ',type(result))
        print(allcols)
        if min(RCk_values) - 0 > 1e-10:
            break
        patterns.append(allcols[RCk_values.index(min(RCk_values))])

    print_solution(master,patterns)
    final_result = master.objective.value()
    print('Total number of sfcs : ',int(final_result))
        