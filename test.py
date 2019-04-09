
a = [1,0]
b = [1,0,-1]
c = [1,0,-1]
d = [1,0,-1]

from itertools import product as prd


# aa = permutations(a)
# bb = permutations(b)
# cc = permutations(c)
# dd = permutations(d)
#
# gg = permutations([aa,bb,cc,dd])
#
# for al, bl, cl, dl in zip(aa,bb,cc,dd):
#     print(al, bl, cl, dl)

print(prd(b, repeat=3))

for x in prd(b, repeat=3):
    print(x)