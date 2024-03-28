# HAUL IO glue

# Load the real file, overwriting this module instance (same name!)
import imp
#hio = imp.load_source('hio', '../haul/langs/py/lib/sys.py')
hio = imp.load_source('hio', '../data/langs/py/libs/sys.py')

#hio.put('tests/hio.py is correctly re-directing')