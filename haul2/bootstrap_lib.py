# This is bootstrap_lib.py, it contains the translation of lib.hal which is not available in the bootstrap context...
# Don't confuse it with htk/py/lib.py which contains all platform specific definitions - this is just for the platform independent helpers.
CR = chr(10)
LF = chr(13)

def arr_set_int(l):
    return [0]*l
