# Small test file

#import hio
from hio import *
#import sys
#from sys import *


#@fun parse int
#@arg cmd str
def parse(cmd):
	put_('parse: "')
	put_(cmd)
	put('"')
	
	if (cmd == 'help'):
		put('This is help dummy.')
		
	elif (cmd == 'exit'):
		put('Exiting...')
		
	elif (cmd == 'ver'):
		put('1.0')	# BANNER
		
	else:
		shout('Unknown command')
	return 0

### Main:
pass	# The main block must start with an instruction, or else the first annotation could be skipped or interpreted in "module" scope (instead of "block" scope)

#@var BANNER str
BANNER = 'shellmini 1.0'

#@var PROMPT str
PROMPT = '>'

put(BANNER)

#@var cmd str
cmd = ''
#@var running bool
running = True

while (running):
	put_(PROMPT)
	cmd = fetch()
	parse(cmd)
	if (cmd == 'exit'): running = False

put('End of shellmini')
#return 0
