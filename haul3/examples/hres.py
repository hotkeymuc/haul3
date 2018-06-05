# HAUL Resources

# Load the real file, overwriting this module instance (same name!)
import imp
hres1 = imp.load_source('hres2', '../data/langs/py/hres.py')

def use(uri):
	return hres1.use(uri)

def get(i):
	return hres1.get(i)


"""
hio = imp.load_source('hio', '../data/langs/py/hio.py')

def put(t):
	hio.put(t)


def hres_get(i):
	return _data[i]
hres.get = hres_get


# Used for testing: This loads a resource at runtime.
_data = []
def hres_use(filename):
	i = len(_data)
	put('Loading file "%s" (%d) at run-time...' % (filename, i))
	with open(filename, 'rb') as h:
		data = h.read()
	_data.append(data)
	return i
hres.use = hres_use

"""