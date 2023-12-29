from pulp import *
import numpy as np
import math

notMapIn = '0'
class Mypattern(object) :

    #Define a column with information :
    # sfc : which sfc 
    # sfcs : all sfc
    # vnfs : all vnf in that sfc
    # vnfs_resource : resources of each vnf
    # vnfs_link_resources : resources of each connection between two vnf of that sfc
    # nodes/links : nodes/links given by the problem
    # column : the way we arrange vnfs in physical network
    def __init__(self, sfc, sfcs, vnfs, vnfs_resource,
                 vnfs_link_resource,
                 nodes,
                 nodes_resource,
                 links,
                 links_resource,
                 column):
        self.sfc = sfc
        self.sfcs = sfcs
        self.vnfs = vnfs
        self.vnfs_resource = vnfs_resource
        self.vnfs_link_resource = vnfs_link_resource
        self.nodes = nodes
        self.nodes_resource = nodes_resource
        self.links = links
        self.links_resource = links_resource
        self.column = column

    #[vnf1 vnf2 vnf3 '0']
    # h: resource require of c on i?
    # Calculate h(c,i)
    def h(self,i) :
        if self.column[i] == notMapIn :
            return 0
        else:
            return self.vnfs_resource[self.column[i]]

    #Calculate g(c,k,v)
    def g(self,k,v) :
        if self.sfc != k:
            return 0
        elif v not in k:
            return 0
        else :
            return 1
        
    #Calculate b(c,i,j)
    def b(self,i,j):
        if (i,j) not in self.links:
            return 0
        elif ((self.column[i] == '0') or self.column[j] == '0'):
            return 0
        else:
            return self.vnfs_link_resource[(self.column[i],self.column[j])]
        
    #Calculate e(c,i)
    def e(self,i) :
        if self.column[i] == '0':
            return 0
        else :
            return 1
        
    #Calculate m(c,k)
    def m(self,k) :
        if self.sfc == k:
            return 1
        else :
            return 0
              
    