# HAUL string glue

# Load the real file, overwriting this module instance (same name!)
import imp
strings = imp.load_source('strings', '../haul/langs/py/lib/strings.py')

#print(str(strings.startsWith('abcd', 'a')))