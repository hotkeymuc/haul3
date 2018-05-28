# HAUL IO

#import sys

def put(data):
	#sys.stdout.write(data)
	print(data)

def put_direct(data):
	#sys.stdout.write(data)
	print(data),

def shout(data):
	print('!! ' + str(data))

def get():
	# PY3
	#return input()
	
	data = raw_input()
	return data

def int_str(i):
	return str(i)