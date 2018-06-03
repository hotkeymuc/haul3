#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""

The HAUL General Assembly
=========================

This writer is something different.
It doesn't just translate the AST into a new structure, but it actually compiles stuff.
Since it is not clear, yet, whether the output is x86, MIPS, AVR, JavaByteCode etc. it takes a general approach of gathering heap and register/stack use.
Maybe, later on, the actual HAULWriters will extend this to allow simple compilation of all kinds of machine code.


TODO:
 OK	* get rid of usage=USAGE_... -- figure that out when writing out the atom! Just keep symbolic track of temp. results
 * ExpressionLists are actually separate atoms that just need to coordinate on which USE-positions they use. They can be merged in a smart way to work out the optimal USE
 * Start Atom by specifying where to put the result later on
    * Keep track of re-used USE() positions
 * Table of calls determines in advance which value should go where (e.g. bare-metal calls need EAX,EBX, function calls might expect them on the stack)


This is still highly experimental:
* Calling conventions are not clear, yet (caller or callee argument reversal)
* Comparisons are not yet handled with CMP/JMP
* Handling of for/while is missing
* ...

"""

import datetime

from haul.haul import *

def put(t):
	print('HAULWriter_asm:\t' + str(t))


INSTR_INTERNAL = [
	'+', '-', '*', '/',
	#'>', '>=', '==', '<', '<=',
	#'and', 'or', 'xor',
]
INSTR_INTERNAL_TRANS = {
	'+': 'ADD',
	'-': 'SUB',
	'*': 'MUL',
	'/': 'DIV',
	
	'>': 'GT',
	'>=': 'GE',
	'==': 'EQ',
	'<': 'LT',
	'<=': 'LE',
	
	'and': 'AND',
	'or': 'OR',
	'xor': 'XOR',
}

REF_VALUE = 0
REF_ADDR = 1

class Atom:
	"Atomic set of instructions. Registers/stack use takes place within one atom."
	def __init__(self):
		self.stack = []
		self.useStack = 0	# Current USE stack usage
		
	def pushVar(self, var):
		#self.stack.append(var)
		self.stack.append('[%04X %s' % (int(var.user), var.name) + ']')
	
	def pushAddr(self, id):
		#self.stack.append(var)
		addr = id.user
		if (addr == None): addr = 0
		self.stack.append('ADDR [@%04X %s]' % (int(addr), id.name))
	
	def pushResult(self):
		self.stack.append('RES')
	
	def pushValue(self, value):
		self.stack.append(value)
	
	def use(self,ref=REF_VALUE):
		r = self.useStack
		
		#self.stack.append('USE(' + str(r) + ')')
		
		if (r == 0):
			t = 'LD	AF, '
		else:
			t = 'USE(' + str(r) + ')'
			t += '\t'
		
		if (ref == REF_VALUE):
			#t += 'REF_VALUE{' + str(self.stack[-1]) + '}'
			t += '' + str(self.stack[-1]) + ''
		else:
			t += 'REF{' + str(self.stack[-1]) + '}'
		self.stack[-1] = t
		
		self.useStack += 1
		return r
	
	def pushInstr(self, instr, consume=[], consumeMore=0):
		r = instr
		
		for i in xrange(consumeMore):
			consume.append(self.useStack - consumeMore + i)
		
		i = 0
		for c in consume:
			if (i > 0): r += ', '
			self.useStack -= 1
			
			if (i == 0):
				r += 'AF'
			else:
				r += 'STACK(' + str(c) + ')'
			i += 1
		
		self.stack.append(r)
	
	
	def write(self, writer, indent=0):
		if len(self.stack) == 0:
			return ''
		
		writer.write('--------------------' + '\n')
		for s in self.stack:
			writer.write_indent(indent)
			writer.write(str(s) + '\n')
			#r += str(s) + '\n'
		writer.write('--------------------' + '\n')
		#return r

class HAULWriter_asm(HAULWriter):
	"Writes some kind of assembly"
	
	def __init__(self, stream_out):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'asm'
		
		self.heap = []
		#self.heapSize = 0
		self.codeSize = 0
		self.entryPoint = 0
		self.write_comment('Translated from HAUL3 to Assembly on ' + str(datetime.datetime.now()))
		
	def write_comment(self, t):
		"Add a comment to the file"
		self.stream_out.put('; ' + t + '\n')
		
	def addToHeap(self, id):
		#@TODO: Use a thread-safe structure
		heapSize = len(self.heap)	# Keep track of global memory usage
		id.user = heapSize	# Store mem in id
		self.heap.append(id)
		#id.user = self.heapSize
		#self.heapSize += 1
	
	def write_post(self, indent=0):
		"Post-processing"
		
		# Write heap section
		self.write('\n')
		self.write('# Global Heap:\n')
		oldNs = None
		for id in self.heap:
			ns = id.namespace
			if not ns == oldNs:
				self.write_indent(indent)
				self.write('# Namespace "' + str(ns) + '"\n')
				oldNs = ns
			
			#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data))
			self.write_indent(indent)
			self.write(('#\t%04X' % int(id.user)) + '\t' + str(id.kind) + '\t' + str(id.name) + '\t' + str(id.data_type) + '\n')
		self.write('\n')
		
		self.write('# Entry point: %04X\n' % self.entryPoint)
		self.write('\n')
		
	
	def write(self, t):
		"Keep track of memory"
		self.codeSize += len(t)
		HAULWriter.write(self, t)
	
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			
			# Pre-process namespace (add all ids to heap)
			for id in ns.ids:
				self.addToHeap(id)
			
			"""
			self.write_indent(indent)
			self.write('# Namespace "' + str(ns) + '"\n')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data))
				self.write_indent(indent)
				self.write(('#\t%04X' % int(id.user)) + '\t' + str(id.kind) + '\t' + str(id.name) + '\t' + str(id.data) + '\n')
			"""
	
	def write_function(self, f, indent=0):
		f.destination = self.stream_out.size	# Record offset in output stream
		
		self.write_indent(indent)
		self.write('# Begin of function ' + f.id.name + '\n')
		
		self.write_namespace(f.namespace, indent)
		
		# Store code address
		f.user = self.codeSize
		f.id.user = self.codeSize
		
		# POP params
		self.write_indent(indent)
		self.write(':' + f.id.name + ('\t# %04X' % self.codeSize) + '\n')
		for i in xrange(len(f.args)):
			self.write_indent(indent+1)
			#self.write_expression(args[i])
			self.write('POP ');
			#self.write_var(f.args[len(len(f.args)) - i - 1])
			self.write_var(f.args[i])
			self.write('\n');
		self.write_indent(indent+1)
		self.write('\n')
		
		#self.write_namespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		self.write_indent(indent+1)
		self.write('# End of function ' + f.id.name + '\n')
		self.write_indent(indent)
		self.write('\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.size	# Record offset in output stream
		
		self.write('### Module "' + m.name + '"\n')
		for im in m.imports:
			self.write('import ')
			self.write(str(im))
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
		self.write('### Classes...\n')
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write('### Funcs...\n')
		for func in m.funcs:
			self.write_function(func, indent)
		
		self.write('### Root Block (main function):\n')
		if (m.block):
			self.entryPoint = self.codeSize
			self.write_block(m.block, indent)
		
		self.write_post(indent=indent)
		
	def write_class(self, c, indent=0):
		c.destination = self.stream_out.size	# Record offset in output stream
		
		#self.write('# Class "' + t.id.name + '"\n')
		self.write_indent(indent)
		self.write('class ')
		self.write(c.id.name)
		self.write(':\n')
		
		if (c.namespace):
			#self.write_indent(indent+1)
			#self.write('### Class namespace...\n')
			self.write_namespace(c.namespace, indent+1)
		
		#@TODO: Initializer?
		for func in c.funcs:
			self.write_function(func, indent+1)
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		self.write_indent(indent)
		self.write('\n')
		
	def write_block(self, b, indent=0):
		b.destination = self.stream_out.size	# Record offset in output stream
		
		self.write('# Block "' + b.name + '"\n')
		
		if (b.name == '__main'):
			self.entryPoint = self.codeSize
		
		self.write(':' + b.name + ('\t# %04X' % self.codeSize) + '\n')
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write('### Block namespace...\n')
				self.write_namespace(b.namespace, indent)
		
		for instr in b.instrs:
			self.write_indent(indent)
			self.write_instruction(instr, indent)
			#self.write('\n')
			
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		atom = Atom()
		
		if (i.comment != None):
			self.write_comment(i.comment)
		
		if (i.control): self.write_control(i.control, atom=atom, indent=indent)
		if (i.call): self.write_call(i.call, atom=atom)
		
		self.write('\n')
		#self.write(str(atom))
		atom.write(writer=self, indent=indent)
		#self.write('\n')
		
		
	def write_control(self, c, atom, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('el')	#elif
				
				#@TODO: atom for the if-expression has to be atom.written out before writing out the block!
				
				self.write('if (')
				self.write_expression(c.exprs[j], atom=atom)
				self.write('):\n')
				self.write_block(c.blocks[j], indent=indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('else:\n')
				self.write_block(c.blocks[j], indent=indent+1)
		
		elif (c.controlType == C_FOR):
			self.write('for ')
			self.write_expression(c.exprs[0], atom=atom)
			self.write(' in ')
			self.write_expression(c.exprs[1], atom=atom)
			self.write(':\n')
			self.write_block(c.blocks[0], atom=atom, indent=indent+1)
		#@TODO: C_WHILE
		#@TODO: C_CONTINUE
		#@TODO: C_BREAK
		#@TODO: C_RAISE
		elif (c.controlType == C_RETURN):
			self.write('return ')
			self.write_expression(c.exprs[0], atom=atom)
			#self.write('\n')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, atom, level=0):
		i = c.id.name
		
		#self.write('/* ' + str(i) + ' */\n')
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			"""
			self.write_expression(c.args[0], atom=atom, level=level)
			storVar = atom.use()
			
			self.write(' = ')
			self.write_expression(c.args[1], atom=atom, level=level)
			storVal = atom.use()
			"""
			
			self.write_comment('Set value of variable ' + str(c.args[0]) + ' to the result of ' + str(c.args[1]) + '\n')
			
			"""
			self.write_expression(c.args[1], atom=atom, level=level)
			storVal = atom.use(ref=REF_VALUE)
			
			self.write_expression(c.args[0], atom=atom, level=level)
			storVar = atom.use(ref=REF_ADDR)
			
			atom.pushInstr('MOV', consume=[storVar, storVal])
			"""
			
			self.write_comment('First: Calculate the primitive result of expression ' + str(c.args[1]))
			self.write_expression(c.args[1], atom=atom, level=level)
			storVal = atom.use(ref=REF_VALUE)
			
			
			self.write_comment('Second: Set value of variable %s to that value' % str(c.args[1]))
			atom.pushInstr('LD	[%04X %s], ' % (c.args[0].var.user, c.args[0].var.name), consume=[storVal])
			
		
		elif i == I_ARRAY_LOOKUP.name:
			self.write_expression(c.args[0], atom=atom, level=level)
			self.write('[')
			self.write_expression_list(c.args, 1, atom=atom, level=level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.write_expression_list(c.args, 0, atom=atom, level=level)
			self.write(']')
			
		elif i == I_OBJECT_CALL.name:
			
			self.write('(')
			self.write_expression_list(c.args, 1, atom=atom, level=level)
			self.write(')')
			
			self.write_expression(c.args[0], atom=atom, level=level)
			storAddr = atom.use()
			
			atom.pushInstr(i + ' ', consume=[storAddr], consumeMore=len(c.args)-1)
			atom.pushResult()
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], atom=atom, level=0)
			storObject = atom.use()
			
			self.write('.')
			self.write_expression(c.args[1], atom=atom, level=0)
			storProp = atom.use()
			
			atom.pushInstr('LOOKUP', consume=[storObject, storProp], consumeMore=0)
			atom.pushResult()
		
		else:
			# Write a standard call
			self.write(i)
			
			if (c.id.name in INSTR_INTERNAL):
				# Bare-metal function
				
				self.write('(')
				self.write_expression_list(c.args, 0, atom=atom, level=level)
				self.write(')')
				
				atom.pushInstr(INSTR_INTERNAL_TRANS[c.id.name], consume=[], consumeMore=len(c.args))
				
			else:
				# Function call
				self.write('(')
				self.write_expression_list(c.args, 0, atom=atom, level=level)
				self.write(')')
				
				"""
				atom.pushAddr(c.id)
				storAddr = atom.use()
				atom.pushInstr('CALL', [storAddr], len(c.args))
				"""
				atom.pushInstr(\
					'CALL [@%04X %s]' % ((int(c.id.user) if not c.id.user == None else 0), i),
					consume=[],
					consumeMore=len(c.args)
					)
				
			atom.pushResult()
			
			
	def write_expression_list(self, es, start, atom, level):
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.write_expression(es[start+i], atom=atom, level=level)
			atom.use()	## Process in reverse order
			
		
	
	def write_expression(self, e, atom, level=0):
		if (e.value):
			self.write('VALUE{')
			self.write_value(e.value)
			self.write('}')
			atom.pushValue(e.value)
			
		if (e.var):
			self.write_var(e.var)
			atom.pushVar(e.var)
			
		if (e.call):
			if (level > 0): self.write('(')
			
			#subAtom = atom.addProcedure()
			self.write_call(e.call, atom=atom, level=level+1)
			#atom.pushResult(subAtom)
			if (level > 0): self.write(')')
			
	def write_value(self, v):
		if (type(v.data) is str):
			self.write("'" + v.data + "'")	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
			
	def write_var(self, v):
		self.write(('[@%04X' % int(v.user)) + ' ' + v.name + ']')
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


