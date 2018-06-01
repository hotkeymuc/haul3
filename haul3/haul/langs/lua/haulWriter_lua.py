#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime
from haul.haul import *

def put(t):
	print('HAULWriter_lua:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=',
]


class HAULWriter_lua(HAULWriter):
	"Writes Lua code"
	
	def __init__(self, streamOut):
		HAULWriter.__init__(self, streamOut)
		self.defaultExtension = 'lua'
		self.write_comment('Translated from HAUL3 to Lua on ' + str(datetime.datetime.now()) )
		
	def write_comment(self, t):
		"Add a comment to the file"
		self.streamOut.put('-- ' + t + '\n')
		
	def writeIndent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def writeNamespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.writeIndent(indent)
			self.write_comment('# Namespace "' + str(ns) + '"')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				# local NAME = VALUE?
				self.writeIndent(indent)
				self.write_comment(' @' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) )
		
	def write_function(self, f, indent=0):
		f.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeNamespace(f.namespace, indent)
		
		self.writeIndent(indent)
		self.write('function ')
		self.write(f.id.name)
		self.write('(')
		for i in xrange(len(f.args)):
			if (i > 0): self.write(', ')
			#self.writeExpression(args[i])
			self.writeVar(f.args[i])
		self.write(')')
		
		self.write('\n')
		
		#self.writeNamespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		self.write('end')
		self.write('\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.streamOut.size	# Record offset in output stream
		
		self.write_comment('### Module "' + m.name + '"')
		for im in m.imports:
			
			#self.write('local ')
			#self.write(str(im))
			#self.write(' = require "')
			#self.write(str(im))
			#self.write('"')
			self.write('dofile("')
			self.write(str(im))
			self.write('.lua")')
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.writeNamespace(m.namespace, indent)
		
		self.write_comment('### Classes...')
		for typ in m.classes:
			self.write_class(typ, indent)
		
		self.write_comment('### Funcs...')
		for func in m.funcs:
			self.write_function(func, indent)
		
		self.write_comment('### Root Block (main function):')
		if (m.block):
			self.write_block(m.block, indent)
		
	def write_class(self, c, indent=0):
		c.destination = self.streamOut.size	# Record offset in output stream
		
		self.writeIndent(indent)
		self.write_comment('Class "' + c.id.name + '"')
		
		self.writeIndent(indent)
		self.write(c.id.name)
		self.write(' = class(\n')
		
		#@TODO: Initializer!
		self.writeIndent(indent+1)
		self.write('function(self)')	#@TODO: and all the initializer parameters!
		if (c.namespace):
			#self.writeIndent(indent+1)
			#self.write('### Class namespace...\n')
			self.writeNamespace(c.namespace, indent+1)
		
		self.write('end)\n')
		
		
		for func in c.funcs:
			#@TODO: Pre-pend class name with colon
			self.write_comment('pre-pend "' + c.id.name + ':" because it\'s a method')
			self.write_function(func, indent+1)
		
		#self.write('# End-of-Type "' + t.id.name + '"\n')
		
	def write_block(self, b, indent=0):
		b.destination = self.streamOut.size	# Record offset in output stream
		
		#self.write("# Block \"" + b.name + "\"\n")
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.writeIndent(indent)
				#self.write('### Block namespace...\n')
				self.writeNamespace(b.namespace, indent)
		
		for instr in b.instrs:
			self.writeIndent(indent)
			self.writeInstr(instr, indent)
			self.write('\n')
			
	def writeInstr(self, i, indent):
		i.destination = self.streamOut.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.comment): 
			self.write_comment(i.comment)
		
		if (i.control): self.writeControl(i.control, indent)
		if (i.call): self.writeCall(i.call)
		
	def writeControl(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('el')	#elif
				self.write('if (')
				
				self.writeExpression(c.exprs[j])
				self.write(') then\n')
				self.write_block(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.writeIndent(indent)
				self.write('else\n')
				self.write_block(c.blocks[j], indent+1)
			self.writeIndent(indent)
			self.write('end\n')
		
		elif (c.controlType == C_FOR):
			self.write('for ')
			self.writeExpression(c.exprs[0])
			self.write(' in ')
			self.writeExpression(c.exprs[1])
			self.write(':\n')
			self.write_block(c.blocks[0], indent+1)
		elif (c.controlType == C_RETURN):
			self.write('return ')
			self.writeExpression(c.exprs[0])
			self.write('\n')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def writeCall(self, c, level=0):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.writeVar(c.args[0].var)
			self.writeExpression(c.args[0], level)
			self.write(' = ')
			self.writeExpression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			self.write('[')
			self.writeExpressionList(c.args, 1, level)
			self.write(']')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('[')
			self.writeExpressionList(c.args, 0, level)
			self.write(']')
			
		elif i == I_OBJECT_CALL.name:
			self.writeExpression(c.args[0], level)
			self.write('(')
			self.writeExpressionList(c.args, 1, level)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.writeExpression(c.args[0], level)
			#@TODO: Need to know if instance call or simple look-up!
			#self.write('.')
			self.write(':')
			self.writeExpression(c.args[1], level)
		
		elif any(i in p for p in PAT_INFIX):
			self.writeExpression(c.args[0], level)	# level-1
			
			self.write(' ' + i + ' ')
			
			self.writeExpression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			self.write(i)
			self.write('(')
			self.writeExpressionList(c.args, 0, level)
			self.write(')')
			
	def writeExpressionList(self, es, start, level):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.writeExpression(es[start+i], level=level)
	
	def writeExpression(self, e, level=0):
		if (e.value): self.writeValue(e.value)
		if (e.var): self.writeVar(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.writeCall(e.call, level+1)
			if (level > 0): self.write(')')
			
	def writeValue(self, v):
		if (type(v.data) == str):
			self.write("'" + v.data + "'")	#@TODO: Escaping!
		else:
			self.write(str(v))	#.data
			
	def writeVar(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


