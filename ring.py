#!/usr/bin/python
import sys
import math
import csv
import numpy as np
import random as rnd
import time

from log import *
from gurobipy import *


def createmodel(u,v):
    n = len(u)
    idx = range(0,n)

    # Create model
    model = Model("ringloading")

    # Create variables
    b = model.addVars(idx, name="b", vtype=GRB.BINARY)
    z = model.addVars(idx, name="z", lb=-1, ub=1)
    t = model.addVar(name="t")

    # Add constraints
    for k in idx:
        model.addConstr(z[k], GRB.EQUAL, -u[k]*(1-b[k]) + v[k]*b[k], "Z"+str(k))

        lexp = LinExpr()

        for i in range(0,k+1):
            lexp.add(z[i])
        for i in range(k+1,n):
            lexp.add(-z[i])
        model.addConstr(lexp, GRB.LESS_EQUAL, t, "M"+str(k)+"_1")
        model.addConstr(lexp, GRB.GREATER_EQUAL, -t, "M"+str(k)+"_2")

    model.setObjective(t, GRB.MINIMIZE)

    return model

if __name__ == '__main__':
    t0 = time.time()
    if len(sys.argv)>2 or len(sys.argv)<1:
        print "Usage: ring.py size"
        exit(0)

    mylogfile = "ring.log"
    log = Logger(mylogfile)

    n = int(sys.argv[1])

    u = []
    v = []
    for k in range(0,n):
        u.append(rnd.random())
        v.append(rnd.uniform(0,1-u[k]))

    #log.joint("u: " + str(u) + "\n")
    #log.joint("v: " + str(v) + "\n")

    model = createmodel(u,v)
    model.write("model.lp")
    model.setParam(GRB.Param.Presolve, 0)
    model.optimize()
    model.write("model.sol")
    x = model.getAttr('X', model.getVars())
    b = x[0:n]
    z = x[n:2*n]
    t = x[2*n]

    log.joint("-------------------------------------------------------\n" )
    log.joint("      u        v         z\n")
    for i in range(0,n):
        log.joint("%2d"%i + "   %0.4f"%u[i] + "   %0.4f"%v[i] + "   %7.4f"%z[i] )
        if np.abs(z[i]-v[i])<1e-6:
            log.joint("= v")
        else:
            log.joint("=-u")

        log.joint("\n")
    log.joint("Objective value:  " + str(t)+"\n")
    log.joint("-------------------------------------------------------\n" )
    log.joint("Time: %0.2f"%(time.time()-t0)+" [s]\n" )
    log.closelog()
