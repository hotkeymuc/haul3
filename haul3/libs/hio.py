# HAUL I/O

# This file is just used as a "header" to compile against
# HIO is platform specific, so this file is rather abstract

#@fun put
#@arg t str
def put(t):
	print(t)
	

#@fun put_
#@arg t str
def put_(t):
	# put in same line
	print(t)	# comma
	

#@fun shout
#@arg t str
def shout(t):
	# Display
	print(t)
	
	# Wait for input
	#raw_input()
	

#@fun fetch str
def fetch():
	# Get user input (blocking)
	
	# raw_input()
	return ''

#@fun int_str str
#@arg i int
def int_str(i):
	return str(i)
	
