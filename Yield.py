#def gensquares(N): <--- creates the entire array
#	array = []
#	for i in range(N):
#		array.append( i ** 2)
#	return array

def gensquares(N): #<--- can be iterated, so we can 
	for i in range(N): #       create only the values we want
		yield i ** 2
		
for i in gensquares(5):
	print(i)