#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""

Idea:
Parsing complexity can be minimized/eliminated if the source is read using Python's reflections.

"""

def put(t):
	print(str(t))

### Load Python source file...
put('-------------------- Loading --------------------')

filename = 'complex'
#filename = 'vm'
#filename = 'bastest'

# Python pre 3.12: Use imp
#import imp
#m = imp.load_source('src', '../../../examples/' + filename + '.py')

# Python post 3.12: Use importlib
import importlib
import sys
sys.path.append('../../../examples')
m = importlib.import_module(filename)	#, 'some_package')


### Now inspect it
put('-------------------- Inspection --------------------')
#put('m=%s' % str(m))
#put(str(m.__file__))	# The full filename
#put(str(m.__spec__))	# ModuleSpec(name='complex', loader=<_frozen_importlib_external.SourceFileLoader object at 0x7f33be24e980>, origin='/z/data/_code/_python/_compilers/haul/haul3.git/haul3/./examples/complex.py')
#for o in dir(m): put('* %s: %s' % (str(o), dir(o)))

import inspect	# For getmembers(module)
#put(inspect.getmembers(m))
#put(inspect.getsource(m))

import dis	# For disassembly

# See https://docs.python.org/3/library/inspect.html
for o in inspect.getmembers(m):
	#put('* %s' % str(o))
	#put('* %s: %s' % (str(o), dir(o)))
	
	name, value = o
	put('* %s (%s)' % (name, type(value).__name__))
	if callable(value):
		put('\tcallable!')
		#put(dir(value))
		
		# __code__, __call__, __dict__, __dir__, __sizeof__, __defaults__
		if '__code__' in dir(value):
			#put('__code__: %s' % str(value.__code__))
			#'co_argcount', 'co_cellvars', 'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags', 'co_freevars', 'co_kwonlyargcount', 'co_lines', 'co_linetable', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals', 'co_posonlyargcount', 'co_stacksize', 'co_varnames'
			#put('__code__: %s' % dir(value.__code__))
			
			put('\tsource: %s' % str(inspect.getsource(value)))
			
			put('\tco_lines:')
			for l in value.__code__.co_lines():
				put('\t\t%s' % str(l))
				#put('\t%s (%s)' % (str(l), str(type(l))))
			#put('\tBytecode: %s' % str(value.__code__.co_code))
			put('\tco_code (bytecode): %s' % (', '.join([ '0x%02x'%op for op in value.__code__.co_code ])))
			
			# Disassemble
			# See https://docs.python.org/3/library/dis.html
			#dis.disco(value.__code__)	# Outputs disassembly to stdout
			#dis.disassemble(value.__code__)	# Outputs disassembly to stdout
			put('\tinstructions:')
			for ins in dis.get_instructions(value.__code__):
				put('\t\t%s' % str(ins))
			
		

