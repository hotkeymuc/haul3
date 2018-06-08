# HAUL Resources for testing

# Load the real run-time file for Python
import imp
hres1 = imp.load_source('hres2', '../data/langs/py/libs/hres.py')

def use(uri):
	return hres1.use(uri)

def get(i):
	return hres1.get(i)


"""
hio = imp.load_source('hio', '../data/langs/py/hio.py')
def put(t):
	hio.put(t)


_data = []
def use(filename):
	i = len(_data)
	put('Loading file "%s" (%d) at run-time...' % (filename, i))
	with open(filename, 'rb') as h:
		data = h.read()
	_data.append(data)
	return i

def get(i):
	return _data[i]

"""