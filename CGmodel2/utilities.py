import numpy as np
import random
from pulp import *

def createResourceLink(nodes):
    n = len(nodes)
    resource_link = np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            resource_link[i][j] = random.randint(0,100)
            resource_link[j][i] = resource_link[i][j]
    return resource_link


def addPattern(allRCk,ptallk,patterns) :
    RCmin = min(allRCk)
    patterns.append(ptallk(ptallk.index(RCmin)))
    return patterns
            
    