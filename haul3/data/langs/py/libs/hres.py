# HAUL Resources

def get(i):
	return _data[i]


# Used for testing: This loads a resource at runtime.
_data = []
def use(filename):
	i = len(_data)
	print('Loading file "%s" (%d) at run-time...' % (filename, i))
	with open(filename, 'rb') as h:
		data = h.read()
	_data.append(data)
	return i
