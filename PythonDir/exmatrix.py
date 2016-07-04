import matrix

print "\n"

n = int(raw_input("Matrix size: "))
mat = matrix.create(n)
matrix.mprint(mat, n)
print "\n"
matrix.diagonal(mat, n)

print "\n"