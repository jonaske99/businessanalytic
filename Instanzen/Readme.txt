# File Format Description

1st line: n hdim vdim

where n is the number of units, and hdim (vdim) are the horizontal (vertical) dimensions of the available space.

The 1st line is followed by a blank line.

Then, n lines (i.e. one per unit) follow with the following data:

xlb xub ylb yub llb lub wlb wub plb pub alb aub

where the meaning is as follows:

xlb, xub: Lower and upper bound on the center x-coordinate of the unit
ylb, yub: Lower and upper bound on the center y-coordinate of the unit
llb, lub: Lower and upper bound on the length of the unit
wlb, wub: Lower and upper bound on the width of the unit
plb, pub: Lower and upper bound on the perimeter of the unit
alb, aub: Lower and upper bound on the area of the unit

Typically, either alb, aub are given, *or* llb, lub, wlb, wub, plb, and pub. The respective other values are then left zero (but reasonably approximated within the solver program).

The n lines are followed by a blank line.

Then, there is an n-by-n matrix describing the flows f_ij between units i and j. Due to symmetry, the value will always be written in the strict upper triangle, i.e., at the position (i,j) where i < j.

Again a blank line follows.

Then, there is an n-by-n matrix describing the costs c_ij to be paid for each unit of flow transported between i and j. Again, only the strict upper triangle is used.

Another separating blank line follows.

Finally, there is an n-by-n matrix describing a minimum (horizontal or vertical) separation s_ij to be established between units i and j. Again, only the strict upper triangle is used.
