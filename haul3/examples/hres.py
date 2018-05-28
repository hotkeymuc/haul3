# HAUL Resources

# Load the real file, overwriting this module instance (same name!)
import imp
hres = imp.load_source('hio', '../haul/langs/py/lib/hres.py')

hio = imp.load_source('hio', '../haul/langs/py/lib/hio.py')

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

