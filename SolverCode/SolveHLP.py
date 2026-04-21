# Sven Mallach (2026)

from LayoutData import LayoutData

import gurobipy as gp
from gurobipy import GRB

class HLPSolver:

    def __init__(self, instance):
        self.__inst = instance
        self.__l = [None for i in range(self.__inst.getNumUnits())] # length
        self.__xc = [None for i in range(self.__inst.getNumUnits())] # center coordinate (horizontal)
        self.__yc = [None for i in range(self.__inst.getNumUnits())] # center coordinate (vertical)
        self.__w = [None for i in range(self.__inst.getNumUnits())] # width
        self.__alphal = [ [ None for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # only strict upper triangle needed
        self.__alphar = [ [ None for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # only strict upper triangle needed
        self.__betab = [ [ None for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # only strict upper triangle needed
        self.__betat = [ [ None for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # only strict upper triangle needed
        self.__zx = [None for j in range(self.__inst.getNumUnits() * self.__inst.getNumUnits())] # Variables for horizontal separation (number is dynamic)
        self.__zy = [None for j in range(self.__inst.getNumUnits() * self.__inst.getNumUnits())] # Variables for vertical separation (number is dynamic)
        self.__zxmap = [ [ -1 for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # Map
        self.__zymap = [ [ -1 for j in range(self.__inst.getNumUnits()) ] for i in range(self.__inst.getNumUnits()) ] # Map
        self.__xdata = None # Container for solution
        self.__ydata = None # Container for solution
        self.__lengths = None # Container for solution
        self.__widths = None # Container for solution
        self.__peris = None # Container for solution
        self.__areas = None # Container for solution

    def buildAndSolveModel(self, LP = False, strengthen = False, separate = False):

        model = gp.Model("HLPModel")
        model.setAttr("ModelSense", 1)

        model.setParam("OutputFlag", 1)
        #model.setParam("OutputFlag", 0)
#        model.setParam("Threads", 1)

        nU = self.__inst.getNumUnits()

        numvars = 4 * nU + 6 * nU * (nU - 1)

        obj = [ 0.0 for i in range(numvars) ]
        lb = [ 0.0 for i in range(numvars) ]
        ub = [ gp.GRB.INFINITY for i in range(numvars) ]
        vtype = [ None for i in range(numvars) ]
        varname = [ "" for i in range(numvars) ]

        # Define the variables
        idx = 0

        for i in range(nU):
            lb[idx] = self.__inst.getMinLength(i)
            ub[idx] = self.__inst.getMaxLength(i)
            vtype[idx] = GRB.CONTINUOUS
            varname[idx] = f"l_{i}"
            self.__l[i] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
            idx += 1

        for i in range(nU):
            lb[idx] = max(self.__inst.getMinX(i), (self.__inst.getMinLength(i) / 2.0))
            ub[idx] = min(self.__inst.getMaxX(i), self.__inst.getRoomLength() - (self.__inst.getMinLength(i) / 2.0))
            vtype[idx] = GRB.CONTINUOUS
            varname[idx] = f"x_c_{i}"
            self.__xc[i] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
            idx += 1

        for i in range(nU):
            lb[idx] = max(self.__inst.getMinY(i), (self.__inst.getMinWidth(i) / 2.0))
            ub[idx] = min(self.__inst.getMaxY(i), self.__inst.getRoomWidth() - (self.__inst.getMinWidth(i) / 2.0))
            vtype[idx] = GRB.CONTINUOUS
            varname[idx] = f"y_c_{i}"
            self.__yc[i] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
            idx += 1

        for i in range(nU):
            lb[idx] = self.__inst.getMinWidth(i)
            ub[idx] = self.__inst.getMaxWidth(i)
            vtype[idx] = GRB.CONTINUOUS
            varname[idx] = f"w_{i}"
            self.__w[i] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
            idx += 1

        for i in range(nU):
            for j in range(i+1, nU):
                obj[idx] = self.__inst.getCost(i,j) * self.__inst.getFlow(i,j)
                vtype[idx] = GRB.CONTINUOUS
                varname[idx] = f"alpha_l_{i}_{j}"
                self.__alphal[i][j] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                idx += 1

        for i in range(nU):
            for j in range(i+1, nU):
                obj[idx] = self.__inst.getCost(i,j) * self.__inst.getFlow(i,j)
                vtype[idx] = GRB.CONTINUOUS
                varname[idx] = f"alpha_r_{i}_{j}"
                self.__alphar[i][j] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                idx += 1

        for i in range(nU):
            for j in range(i+1, nU):
                obj[idx] = self.__inst.getCost(i,j) * self.__inst.getFlow(i,j)
                vtype[idx] = GRB.CONTINUOUS
                varname[idx] = f"beta_b_{i}_{j}"
                self.__betab[i][j] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                idx += 1

        for i in range(nU):
            for j in range(i+1, nU):
                obj[idx] = self.__inst.getCost(i,j) * self.__inst.getFlow(i,j)
                vtype[idx] = GRB.CONTINUOUS
                varname[idx] = f"beta_t_{i}_{j}"
                self.__betat[i][j] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                idx += 1

        zxc = 0
        for i in range(nU):
            for j in range(nU):
                if i != j:
                    if LP:
                        vtype[idx] = GRB.CONTINUOUS
                    else:
                        vtype[idx] = GRB.BINARY
                    ub[idx] = 1.0
                    varname[idx] = f"z_x_{i}_{j}"
                    self.__zx[zxc] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                    self.__zxmap[i][j] = zxc
                    idx += 1
                    zxc += 1

        zyc = 0
        for i in range(nU):
            for j in range(nU):
                if i != j:
                    if LP:
                        vtype[idx] = GRB.CONTINUOUS
                    else:
                        vtype[idx] = GRB.BINARY
                    ub[idx] = 1.0
                    varname[idx] = f"z_y_{i}_{j}"
                    self.__zy[zyc] = model.addVar(lb[idx], ub[idx], obj[idx], vtype[idx], varname[idx])
                    self.__zymap[i][j] = zyc
                    idx += 1
                    zyc += 1

        model.update()

        # Define Constraints

        for i in range(nU):
            conname = f"minPeri_{i}"
            model.addConstr(2.0 * (self.__l[i] + self.__w[i]) >= self.__inst.getMinPerimeter(i), conname)
            conname = f"maxPeri_{i}"
            model.addConstr(2.0 * (self.__l[i] + self.__w[i]) <= self.__inst.getMaxPerimeter(i), conname)

        for i in range(nU):
            for j in range(i+1, nU):
                conname = f"LinHor_{i}_{j}"
                model.addConstr(self.__xc[i] - self.__xc[j] == self.__alphar[i][j] - self.__alphal[i][j], conname)
                conname = f"LinVer_{i}_{j}"
                model.addConstr(self.__yc[i] - self.__yc[j] == self.__betat[i][j] - self.__betab[i][j], conname)


        Mlen = 0.0
        Mwid = 0.0

        for i in range(nU):
            Mlen += self.__inst.getMaxLength(i)
            Mwid += self.__inst.getMaxWidth(i)

        #print(f"{Mlen} / {self.__inst.getRoomLength()}, {Mwid} / {self.__inst.getRoomWidth()}")

        Mlen = min(Mlen, self.__inst.getRoomLength())
        Mwid = min(Mwid, self.__inst.getRoomWidth())

        for i in range(nU):
            for j in range(nU):
                if i != j:
                    conname = f"OrdHor_{i}_{j}"
                    model.addConstr(self.__inst.getClearance(i,j) + (self.__xc[j] + (0.5 * self.__l[j])) - (self.__xc[i] - (0.5 * self.__l[i])) <= Mlen * (1.0 - self.__zx[self.__zxmap[i][j]]), conname)
                    conname = f"OrdVer_{i}_{j}"
                    model.addConstr(self.__inst.getClearance(i,j) + (self.__yc[j] + (0.5 * self.__w[j])) - (self.__yc[i] - (0.5 * self.__w[i])) <= Mwid * (1.0 - self.__zy[self.__zymap[i][j]]), conname)


        for i in range(nU):
            for j in range(i+1, nU):
                conname = f"NoOverlap_{i}_{j}"
                model.addConstr(self.__zx[self.__zxmap[i][j]] + self.__zy[self.__zymap[i][j]] + self.__zx[self.__zxmap[j][i]] + self.__zy[self.__zymap[j][i]] >= 1, conname)

        if strengthen and not separate:
            # These contraints are valid and strengthen the bound, but they do not enforce the z-variables to be one in the right situations, i.e. they do not replace the big-M constraints
            for i in range(nU):
                for j in range(i+1, nU):
                    conname = f"OrdHorStr_{i}_{j}_3"
                    model.addConstr(self.__alphar[i][j] >= ((self.__inst.getMinLength(j) + self.__inst.getMinLength(i)) / 2.0) * self.__zx[self.__zxmap[i][j]], conname)
                    conname = f"OrdHorStr_{j}_{i}_3"
                    model.addConstr(self.__alphal[i][j] >= ((self.__inst.getMinLength(j) + self.__inst.getMinLength(i)) / 2.0) * self.__zx[self.__zxmap[j][i]], conname)

                    conname = f"OrdVerStr_{i}_{j}_3"
                    model.addConstr(self.__betat[i][j] >= ((self.__inst.getMinWidth(i) + self.__inst.getMinWidth(j)) / 2.0) * self.__zy[self.__zymap[i][j]], conname)
                    conname = f"OrdVerStr_{j}_{i}_3"
                    model.addConstr(self.__betab[i][j] >= ((self.__inst.getMinWidth(j) + self.__inst.getMinWidth(i)) / 2.0) * self.__zy[self.__zymap[j][i]], conname)


        # Set Node Limit
        #model.setParam("NodeLimit", nodelimitforMIP)

        # Set aggressive symmetry detection
        #model.setParam("Symmetry", 2)

        model.update()

        model.write("model.lp")

        model._slv = self

        # === Callback for Separation ===
        def separation_callback(model, where):
            nU = model._slv.__inst.getNumUnits()
            eps = 1e-6

            # -------------------------
            # USER CUTS (optional)
            # -------------------------
            if where == GRB.Callback.MIPNODE:
                status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
                if status != GRB.OPTIMAL:
                    return

                #nodecnt = int(model.cbGet(GRB.Callback.MIPNODE_NODCNT))
                #if nodecnt != 0:
                #    return  # nur root

                cuts_added = 0

                if strengthen and separate:
                    for i in range(nU):
                        for j in range(i+1, nU):
                            lhs1 = 0.0
                            lhs1 += model.cbGetNodeRel(model._slv.__alphar[i][j])
                            lhs1 -= ((model._slv.__inst.getMinLength(j) + model._slv.__inst.getMinLength(i)) / 2.0) * model.cbGetNodeRel(model._slv.__zx[model._slv.__zxmap[i][j]])
                            if lhs1 + eps < 0.0:
                                model.cbCut(model._slv.__alphar[i][j] >= ((model._slv.__inst.getMinLength(j) + model._slv.__inst.getMinLength(i)) / 2.0) * model._slv.__zx[model._slv.__zxmap[i][j]])
                                cuts_added += 1

                            lhs2 = 0.0
                            lhs2 += model.cbGetNodeRel(model._slv.__alphal[i][j])
                            lhs2 -= ((model._slv.__inst.getMinLength(j) + model._slv.__inst.getMinLength(i)) / 2.0) * model.cbGetNodeRel(model._slv.__zx[model._slv.__zxmap[j][i]])
                            if lhs2 + eps < 0.0:
                                model.cbCut(model._slv.__alphal[i][j] >= ((model._slv.__inst.getMinLength(j) + model._slv.__inst.getMinLength(i)) / 2.0) * model._slv.__zx[model._slv.__zxmap[j][i]])
                                cuts_added += 1

                            lhs3 = 0.0
                            lhs3 += model.cbGetNodeRel(model._slv.__betat[i][j])
                            lhs3 -= ((model._slv.__inst.getMinWidth(j) + model._slv.__inst.getMinWidth(i)) / 2.0) * model.cbGetNodeRel(model._slv.__zy[model._slv.__zymap[i][j]])
                            if lhs3 + eps < 0.0:
                                model.cbCut(model._slv.__betat[i][j] >= ((model._slv.__inst.getMinWidth(i) + model._slv.__inst.getMinWidth(j)) / 2.0) * model._slv.__zy[model._slv.__zymap[i][j]])
                                cuts_added += 1

                            lhs4 = 0.0
                            lhs4 += model.cbGetNodeRel(model._slv.__betab[i][j])
                            lhs4 -= ((model._slv.__inst.getMinWidth(j) + model._slv.__inst.getMinWidth(i)) / 2.0) * model.cbGetNodeRel(model._slv.__zy[model._slv.__zymap[j][i]])
                            if lhs4 + eps < 0.0:
                                model.cbCut(model._slv.__betab[i][j] >= ((model._slv.__inst.getMinWidth(j) + model._slv.__inst.getMinWidth(i)) / 2.0) * model._slv.__zy[model._slv.__zymap[j][i]])
                                cuts_added += 1

                #print("Cuts: ", cuts_added)

        if separate:
            model.optimize(separation_callback)
            model.setParam("PreCrush", 1)
        else:
            model.optimize()

        objval = -1.0

        print("Optimization ended with status " + str(model.status) + "\n");

        if model.status == GRB.NODE_LIMIT:
            print("Optimization interrupted due to node limit\n");
            objval = model.ObjVal
        elif model.status == GRB.OPTIMAL:
            print("Solved to optimality\n");
            objval = model.ObjVal
        else:
            print(f"Abnormal termination with status {model.status}\n");

        if (objval <= 1e-6):
            print(f"Warning: Turning objective value {objval} to zero.")
            objval = 0.0

        print("Objective: ", objval)

        if (model.SolCount > 0):

            # Retrieve solution
            for i in range(nU):
                print(f"Unit {i} ({self.__xc[i].X}), ({self.__yc[i].X}), {self.__l[i].X}, {self.__w[i].X}, {2.0 * (self.__w[i].X + self.__l[i].X)}, {(self.__l[i].X) * (self.__w[i].X)}, [{self.__inst.getMinArea(i)}, {self.__inst.getMaxArea(i)}]")

            # Store solution to be queried later via getLayout()
            self.__xdata = list(self.__xc[i].X for i in range(self.__inst.getNumUnits()))
            self.__ydata = list(self.__yc[i].X for i in range(self.__inst.getNumUnits()))
            self.__lengths = list(self.__l[i].X for i in range(self.__inst.getNumUnits()))
            self.__widths = list(self.__w[i].X for i in range(self.__inst.getNumUnits()))
            self.__peris = list(2.0 * (self.__l[i].X + self.__w[i].X) for i in range(self.__inst.getNumUnits()))
            self.__areas = list((self.__l[i].X) * (self.__w[i].X) for i in range(self.__inst.getNumUnits()))


        return objval

    # Be sure to have run the solver before calling this method
    # Also make sure that the model has found a solution / terminated with an appropriate status.
    def getLayout(self):
        return self.__xdata, self.__ydata, self.__lengths, self.__widths, self.__peris, self.__areas
