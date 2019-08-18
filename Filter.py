array = range(-4, 5)

#filtering all positive values
def filterPositive(value):
	if value > 0:
		return value
		
filtered = list(filter(filterPositive, array)) #that is inexplicably filthy
print(filtered)

#summing all values in the filtered array
def reduceSumm(val1, val2):
	return val1+val2
	
reduced = reduce(reduceSumm, filtered)
print(reduced)

#incrementing all filtered values by 10
def mapIncrement(value):
	return value + 10
	
incremented = list(map(mapIncrement, filtered))
print(incremented)