# Sven Mallach (2026)

import sys
import numpy as np
import math

from LayoutData import LayoutData
from SolveHLP import HLPSolver

def parse(input_filename):

    U = 0
    Rlen = 0
    Rwid = 0

    # Read sizes from the first line of the file
    with open(input_filename, "r") as infile:
        U, Rlen, Rwid = map(int, infile.readline().strip().split()) 

    minX = [None for u in range(U)]
    maxX = [None for u in range(U)]
    minY = [None for u in range(U)]
    maxY = [None for u in range(U)]
    minLen = [None for u in range(U)]
    maxLen = [None for u in range(U)]
    minWid = [None for u in range(U)]
    maxWid = [None for u in range(U)]
    minPeri = [None for u in range(U)]
    maxPeri = [None for u in range(U)]
    minArea = [None for u in range(U)]
    maxArea = [None for u in range(U)]

    cost = []
    flow = []
    space = []

    with open(input_filename, "r") as infile:
        # skip the first line now
        infile.readline()  # Skip the first line
        infile.readline()  # Skip the second (empty) line

        for u in range(U):
            minX[u], maxX[u], minY[u], maxY[u], minLen[u], maxLen[u], minWid[u], maxWid[u], minPeri[u], maxPeri[u], minArea[u], maxArea[u] = map(float, infile.readline().strip().split()) 

        infile.readline()  # Skip the empty line

        for u in range(U):
            row = list(map(float, infile.readline().strip().split()))
            print(row)
            cost.append(row)

        infile.readline()  # Skip the empty line

        for u in range(U):
            row = list(map(float, infile.readline().strip().split()))
            flow.append(row)

        infile.readline()  # Skip the empty line

        for u in range(U):
            row = list(map(float, infile.readline().strip().split()))
            space.append(row)

    has_lenwid = sum(minLen) != 0
    has_peri = sum(minPeri) != 0
    has_area = sum(minArea) != 0

    rect_factor = 0.4

    # expand data

    if not has_lenwid:
        if has_area:
            for u in range(U):
                minsqrt = math.sqrt(minArea[u])
                maxsqrt = math.sqrt(maxArea[u])
                low = math.floor(minsqrt - rect_factor * minsqrt)
                high = math.ceil(maxsqrt + rect_factor * maxsqrt)
                print(f"{u}: Approximating lower and upper bounds on length / width as {low} / {high} from area [{minArea[u]}, {maxArea[u]}]\n")
                minLen[u] = minWid[u] = low
                maxLen[u] = maxWid[u] = high
        else:
            print("Error: File has no length/width information but also no area data")
            exit(1)

    if not has_peri:
        if has_area:
            for u in range(U):
                minsqrt = math.sqrt(minArea[u])
                maxsqrt = math.sqrt(maxArea[u])
                low = math.floor(minsqrt - rect_factor * minsqrt)
                high = math.ceil(maxsqrt + rect_factor * maxsqrt)
                minPeri[u] = 4 * math.floor(minsqrt)
                maxPeri[u] = 2 * low + 2 * high
                print(f"{u}: Approximating lower and upper bounds on perimeter as {minPeri[u]} / {maxPeri[u]} from area [{minArea[u]}, {maxArea[u]}]\n")
        else:
            for u in range(U):
                minPeri[u] = 2 * (minLen[u] + minWid[u])
                maxPeri[u] = 2 * (maxLen[u] + maxWid[u])
                print(f"{u}: Approximating lower and upper bounds on perimeter as {minPeri[u]} / {maxPeri[u]} from length / width\n")

    if not has_area:
        if has_lenwid:
            for u in range(U):
                minArea[u] = minLen[u] * minWid[u]
                maxArea[u] = maxLen[u] * maxWid[u]
                print(f"{u}: Setting area bounds to [{minArea[u]}, {maxArea[u]}] due to length [{minLen[u]},{maxLen[u]}] and width [{minWid[u]}, {maxWid[u]}]\n")
        else:
            print("Error: File has no area information but also no length/width data")
            exit(1)


    # plausability check

    for u in range(U):
        maxDiffX = maxX[u] - minX[u]
        if (minX[u] > maxX[u] or minLen[u] > maxLen[u] or maxDiffX < maxLen[u]):
           print(f"Error: min/max length and min/max X data not plausible for unit {u}")
           exit(1)

        maxDiffY = maxY[u] - minY[u]
        if (minY[u] > maxY[u] or minWid[u] > maxWid[u] or maxDiffY < maxWid[u]):
           print(f"Error: min/max width and min/max Y data not plausible for unit {u}")
           exit(1)

    data = LayoutData(U, minX, maxX, minY, maxY, minLen, maxLen, minWid, maxWid, minPeri, maxPeri, minArea, maxArea, cost, flow, space, Rlen, Rwid)

    return data

if __name__ == "__main__":

    # Ensure an input filename is provided via command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python3 HLPMain.py <input_file>")
        sys.exit(1)

    input_filename = sys.argv[1]

    data = parse(input_filename)

    solver = HLPSolver(data)
    objval = solver.buildAndSolveModel(LP=False,strengthen=True,separate=False)

    if (objval >= 0.0):
        xdata, ydata, lens, wids, peris, areas = solver.getLayout()
        print(xdata)
        print(ydata)
        print(lens)
        print(wids)
        print(peris)
        print(areas)
