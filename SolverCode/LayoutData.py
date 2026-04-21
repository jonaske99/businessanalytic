# Sven Mallach (2026)

class LayoutData:

    def __init__(self, nU, minX, maxX, minY, maxY, minL, maxL, minW, maxW, minP, maxP, minA, maxA, C, F, S, rL, rW):
        self.__nUnits = nU # Number of Organizational Units
        self.__minX = minX # lower bound on the horizontal center position of a unit
        self.__maxX = maxX # upper bound on the horizontal center position of a unit
        self.__minY = minY # lower bound on the vertical center position of a unit
        self.__maxY = maxY # upper bound on the vertical center position of a unit
        self.__minLength = minL # lower bound on the length of a unit
        self.__maxLength = maxL # upper bound on the length of a unit
        self.__minWidth = minW # lower bound on the width of a unit
        self.__maxWidth = maxW # upper bound on the width of a unit
        self.__minPerimeter = minP # lower bound on the perimeter of a unit
        self.__maxPerimeter = maxP # upper bound on the perimeter of a unit
        self.__minArea = minA # lower bound on area of unit
        self.__maxArea = maxA # upper bound on area of unit
        self.__cost = C # Cost Matrix
        self.__flow = F # Flow Matrix
        self.__space = S # Clearance Matrix
        self.__roomLength = rL # Horizontal Space
        self.__roomWidth = rW  # Vertical Space

    def getNumUnits(self):
        return self.__nUnits

    def getMinX(self, u):
        return self.__minX[u]

    def getMaxX(self, u):
        return self.__maxX[u]

    def getMinY(self, u):
        return self.__minY[u]

    def getMaxY(self, u):
        return self.__maxY[u]

    def getMinLength(self, u):
        return self.__minLength[u]

    def getMaxLength(self, u):
        return self.__maxLength[u]

    def getMinWidth(self, u):
        return self.__minWidth[u]

    def getMaxWidth(self, u):
        return self.__maxWidth[u]

    def getMinPerimeter(self, u):
        return self.__minPerimeter[u]

    def getMaxPerimeter(self, u):
        return self.__maxPerimeter[u]

    def getMinArea(self, u):
        return self.__minArea[u]

    def getMaxArea(self, u):
        return self.__maxArea[u]

    def getCost(self, u1, u2):
        return self.__cost[u1][u2]

    def getFlow(self, u1, u2):
        return self.__flow[u1][u2]

    def getClearance(self, u1, u2):
        return self.__space[u1][u2]

    def getRoomLength(self):
        return self.__roomLength

    def getRoomWidth(self):
        return self.__roomWidth

