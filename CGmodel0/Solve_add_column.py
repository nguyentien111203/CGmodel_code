from pulp import *
import Tryna_run_it as mds
import old_variables as md

initial_columns = [['0','V1','V2','V3','0','0'],
                 ['0','0','V1','V2','V3','0'],
                 ['V4','V5','V6','0','0','0'],
                 ['0','0','V4','V5','V6','0']]  # Initialize an empty list to store valid columns

exit_condition = 1
while exit_condition < 3:
    
    
    e = LpVariable.dicts("e_c_i",[(initial_columns.index(c),i) for c in initial_columns for i in md.N],cat='Binary')
    for c in initial_columns:
        for i in md.N:
            if c[md.N.index(i)]=='0':
                e[(initial_columns.index(c),i)]= 0
            else:
                e[(initial_columns.index(c),i)] = 1


    #Constant g[c,k,v] : do it used vnf v of sfc k in c
    g = LpVariable.dicts("g_c_k_v",[(initial_columns.index(c),k,v) for c in initial_columns for k in md.K for v in md.Nk[k]],cat='Binary')
    for c in initial_columns:
        for k in md.K:
            for v in md.Ns:
                if v in md.Nk[k] and v in c:
                    g[(initial_columns.index(c),k,v)] = 1
                else:
                    g[(initial_columns.index(c),k,v)] = 0

    #Constant m[c,k] : whether column c can be used for sfc k
    m = LpVariable.dicts("m_c_k",[(initial_columns.index(c),k) for c in initial_columns for k in md.K],cat='Binary')
    for c in initial_columns:
        for k in md.K:
            if all(g[(initial_columns.index(c),k,v)]==1 for v in md.Nk[k]):
                m[(initial_columns.index(c),k)] = 1
            else:
                m[(initial_columns.index(c),k)] = 0

    #Constant h[c,i] : resources costed in node i of column c
    h = LpVariable.dicts("h_c_i",[(initial_columns.index(c),i) for c in initial_columns for i in md.N],cat='Integer')
    for c in initial_columns:
        for i in md.N:
            if c[md.N.index(i)] == '0':
                h[(initial_columns.index(c),i)] = 0
            else :
                h[initial_columns.index(c),i] = md.r[c[md.N.index(i)]]

    #Constant b[c,ij] : resources costed in link ij of column c
    b = LpVariable.dicts("b_c_ij",[(initial_columns.index(c),i,j) for c in initial_columns for (i,j) in md.L],cat='Integer')
    for c in initial_columns:
        for i in md.N:
            for j in md.N:
                if i!=j:
                    if ((c[md.N.index(i)] == '0') or (c[md.N.index(j)] == '0')):
                        b[(initial_columns.index(c),i,j)] = 0
                    else :
                        b[(initial_columns.index(c),i,j)] = md.r_vw[(c[md.N.index(i)],c[md.N.index(j)])]


    RMPmodel = LpProblem(name='MP_Mapping Sfc',sense=LpMaximize)
    lamda = LpVariable.dict('lamda',[initial_columns.index(c) for c in initial_columns],cat='Binary')  # Initialize an empty dictionary to store lambda values
    tolerance = 0
    for i in md.N:
        RMPmodel += lpSum(h[(initial_columns.index(c),i)]*lamda[initial_columns.index(c)] for c in initial_columns) - md.ai[i] <= tolerance #Add resource constraints on nodes
    for (i,j) in md.L:
        RMPmodel += lpSum(lamda[initial_columns.index(c)]*b[(initial_columns.index(c),i,j)] for c in initial_columns) <= md.aij[(i,j)] # Add resource constraints on edges
    for k in md.K:       
        RMPmodel += lpSum(lamda[initial_columns.index(c)*m[(initial_columns.index(c),k)]] for c in initial_columns) <= 1 # Ensure each SFC is placed at most once
    for i in md.N:
        for k in md.K: 
            for v in md.Nk[k]:
                RMPmodel += lpSum(lamda[initial_columns.index(c)]*e[(initial_columns.index(c),i)]*g[(initial_columns.index(c),k,v)] for c in initial_columns) - 1 <= tolerance  # Ensure each node has at most one vNF       
    RMPmodel += lpSum(lamda[initial_columns.index(c)] for c in initial_columns) <= len(md.K) # Ensure the number of placed SFCs does not exceed the initial number

    RMPmodel += lpSum(lamda[initial_columns.index(c)])
    RMPmodel.solve()
    #Create a dual RMP
    #Model for dual variables
    #phi-i
    phi_i = LpVariable.dict(name="phi_i",indices=md.N,lowBound=0,cat = 'Continuous')
    modelphi_i = LpProblem(sense=LpMinimize)
    for c in initial_columns:
        modelphi_i += lpSum(h[(initial_columns.index(c),i)]*phi_i[i] for i in md.N) - 1.0 >= tolerance 
    modelphi_i += lpSum(md.ai[i]*phi_i[i] for i in md.N)

    #te_ij
    te_ij = {(i, j): LpVariable(name=f"te_{i}_{j}", lowBound=0, cat='Continuous') for i in md.N for j in md.N if (i, j) in md.L}
    modelte_ij = LpProblem(sense=LpMinimize)
    for i in md.N:
        for j in md.N:
            if i!=j and (i,j) in md.L:
                modelte_ij += lpSum(b[(initial_columns.index(c),i,j)]*te_ij[(i,j)] for i in md.N for j in md.N if (i,j) in md.L for c in initial_columns) >= 1.0
    modelte_ij += lpSum(md.aij[(i,j)]*te_ij[(i,j)] for i in md.N for j in md.N if (i,j) in md.L) 
    for i in md.N:
        for j in md.N:
            if (i,j) in md.L:
                if te_ij[(i,j)] == None:
                    te_ij[(i,j)] = 0
    #theta_k
    theta_k = LpVariable.dict(name="theta_k",indices=md.K,lowBound=0,cat = 'Continuous')
    modeltheta_k = LpProblem(sense=LpMinimize)
    for k in md.K:
        modeltheta_k += lpSum(m[(initial_columns.index(c),k)]*theta_k[k] for k in md.K for c in initial_columns) - 1.0 >= tolerance
    modeltheta_k += lpSum(theta_k[k] for k in md.K) 
    for k in md.K:
        if theta_k[k] == None:
            theta_k[k] = 0

    #beta_i_v
    beta_i_v = {(i, v): LpVariable(name=f"beta_i_{i}_v_{v}", lowBound=0, cat='Continuous') for i in md.N for v in md.Ns}
    modelbeta_i_v = LpProblem(sense=LpMinimize)
    for i in md.N:
        for k in md.K:
            for v in md.Nk[k]:
                modelbeta_i_v += lpSum(e[(initial_columns.index(c),i)]*g[(initial_columns.index(c),k,v)]*beta_i_v[(i,v)] for i in md.N for k in md.K for v in md.Nk[k] for c in initial_columns) - 1 >= tolerance
    modelbeta_i_v += lpSum(beta_i_v[(i,v)] for i in md.N for v in md.Nk[k])

    #Solve RMP
    RMPmodel.solve()
    #SOlve PP
    modelphi_i.solve()
    modelbeta_i_v.solve()
    modelte_ij.solve()
    modeltheta_k.solve()
    c_allk = []
    RC_allk = []
    for k in md.K: #Solve the problem with every sfc
        modelk = LpProblem(name=f"Solve with {k}",sense=LpMinimize)
        RC1 = 1.0 - lpSum(lpSum(md.r[v]*md.x_vk_i[(v,k,i)] for v in md.Nk[k])*mds.phi_i[md.N.index(i)].value() for i in md.N) 
        RC2 = tolerance - lpSum(md.r_vw[(v,w)]*md.z_ij_vw_k[(v,w,k,i,j)]*mds.te_ij[md.N.index(i)*len(md.N) + md.N.index(j)].value() for i in md.N for j in md.N for v in md.Nk[k] for w in md.Nk[k] if (i,j) in md.L if v!=w)
        RC3 = tolerance - mds.theta_k[md.K.index(k)].value() 
        RC4 = tolerance - lpSum(lpSum(md.x_vk_i[(v,k,i)] for v in md.Nk[k])*mds.beta_i_v[md.N.index(i)*len(md.N) + md.Ns.index(v)].value() for i in md.N for v in md.Nk[k] if mds.beta_i_v[md.N.index(i)*len(md.N) + md.Ns.index(v)].value()!=None)
        RC_sum = RC1 + RC2 + RC3 + RC4
        modelk += RC_sum
        print(modelk)
        #Add constraint from the old model
        #Resources on node 
        for i in md.N :
            modelk += lpSum(md.x_vk_i[(v,k,i)]*md.r[v] for v in md.Nk[k]) <= md.ai[i]  

        #Resource on link
        for i in md.N:
            for j in md.N:
                if i!=j and (i,j) in md.L:
                    modelk += lpSum(md.z_ij_vw_k[(v,w,k,i,j)]*md.r_vw[(v,w)] for v in md.Nk[k] for w in md.Nk[k] if w!=v) <= md.aij[(i,j)]
                #Constraint for variables z
                    for v in md.Nk[k]:
                        for w in md.Nk[k]:
                            if w!=v:
                                modelk += md.z_ij_vw_k[(v,w,k,i,j)] - md.x_vw_k_ij[(v,w,k,i,j)] >= 0
                                modelk += md.z_ij_vw_k[(v,w,k,i,j)] - md.y_vw_k[(v,w,k)] >= 0
                                modelk += md.x_vw_k_ij[(v,w,k,i,j)] + md.y_vw_k[(v,w,k)] - 1 - md.z_ij_vw_k[(v,w,k,i,j)] >= 0
        #All node can be put only one vNF
        for i in md.N :
            modelk += lpSum(md.x_vk_i[(v,k,i)] for v in md.Nk[k]) <= 1 
        #Every vnf of that sfc have to be put on the physical network
        for v in md.Nk[k] :
            modelk += lpSum(md.x_vk_i[(v,k,i)] for i in md.N) == 1 
        #Flow conservation
        M = 1000
        for i in md.N :
            for v in md.Nk[k]:
                for w in md.Nk[k]:
                    if v!=w :
                        modelk += (lpSum(md.x_vw_k_ij[(v,w,k,i,j)] for j in md.N if j!=i)-lpSum(md.x_vw_k_ij[(v,w,k,j,i)] for j in md.N if j!=i))
                        - (md.x_vk_i[(v,k,i)]-md.x_vk_i[(w,k,i)]) >= -M*(1-md.y_vw_k[(v,w,k)]) 
         
                        modelk += (lpSum(md.x_vw_k_ij[(v,w,k,i,j)] for j in md.N if j!=i)-lpSum(md.x_vw_k_ij[(v,w,k,j,i)] for j in md.N if j!=i))
                        - (md.x_vk_i[(v,k,i)]-md.x_vk_i[(w,k,i)]) <= M*(1-md.y_vw_k[(v,w,k)]) 
            
        #Remove reduntdancy variables
        for v in md.Nk[k] :
            for w in md.Nk[k]:
                if v!=w :
                    modelk += lpSum(md.x_vw_k_ij[(v,w,k,i,j)] for i in md.N for j in md.N if i!=j) == md.y_vw_k[(v,w,k)] 
        #VNF orders
        #modelk += lpSum(md.y_vw_k[(v,w)] for w in md.Nk[k]) == len(md.Nk[k])
        #modelk += lpSum()
        #Partially fixed order
    #Build a column based on the result
        modelk.solve()
        for i in md.N:
            for v in md.Nk[k]:
                print(f'x_{v}_{k}_{i} = {md.x_vk_i[(v,k,i)].value()}')
        print("RC1 Value:", RC1.value())
        print("RC2 Value:", RC2.value())
        print("RC3 Value:", RC3)
        print("RC4 Value:", RC4.value())
        print("RC_sum:", RC_sum.value())
        column = []
        for i in md.N:
            column.append('0')
        for i in md.N:
            for v in md.Nk[k]:
                if (value(md.x_vk_i[(v,k,i)])==1):
                    column[md.N.index(i)] = v
        print(column)
        c_allk.append(column)
        RC_allk.append(RC_sum.value())
    RCmin = RC_allk[0]
    for i in RC_allk:
        if RCmin - i >= tolerance:
            RCmin = i
    if RCmin - 0 >= tolerance:
        exit_condition = 4
    else:
        initial_columns.append(c_allk[RC_allk.index(RCmin)])
    print(initial_columns)
    print(RC_allk)
    exit_condition+=1
    print('exit_condition = ' + str(exit_condition))
    
RMPmodel.solve()
print(lamda.values)
