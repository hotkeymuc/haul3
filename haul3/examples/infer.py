# Test type inference (i.e. not declaring a var)

from hio import *

def infer_me(x=3):
	put('Can you guess my returnType?')
	return x+5

def uninferrable(y):
	put('I am difficult.')
	y = 6

put('Testing type inference')

a = 5
put(int_str(a))

b = 2.3
put(float_str(a))

put('End')
#return 0
