# HAUL Platform Capabilities

# Load the real file, overwriting this module instance (same name!)
import imp
hcaps = imp.load_source('hio', '../haul/langs/py/lib/hcaps.py')

# Augment
hcaps.PLATFORM = 'Python (simulated)'

