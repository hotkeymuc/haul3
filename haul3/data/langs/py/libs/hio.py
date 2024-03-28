# HAUL IO

#import sys

def put(data):
	#sys.stdout.write(data)
	print(data)

def put_(data):
	#sys.stdout.write(data)
	print(data),

def shout(data):
	print('!! ' + str(data))

def fetch():
	# PY3
	#return input()
	
	data = raw_input()
	return data

def int_str(i):
	return str(i)
def float_str(i):
	return str(i)