#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.haul import *

def put(t):
	print('HAULWriter_vbs:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=',
]


class HAULWriter_vbs(HAULWriter):
	"Writes Visual BASIC code"
	
	def __init__(self, stream_out):
		HAULWriter.__init__(self, stream_out)
		#self.default_extension = 'bas'
		self.default_extension = 'vbs'
		self.write_comment('Translated from HAUL3 to Visual BASIC on ' + str(datetime.datetime.now()) )
		
	def write_comment(self, t):
		"Add a comment to the file"
		#self.stream_out.put('REM ' + t + '\n')
		self.stream_out.put('\' ' + t + '\n')
		
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '\t'
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns and len(ns.ids) > 0):
			self.write_indent(indent)
			self.write_comment('Namespace "' + str(ns) + '"')
			for id in ns.ids:
				#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
				if (id.name == 'res'): continue	# Do not (re-)declare result
				if (id.kind == 'var'):
					self.write_indent(indent)
					#self.write('#@' + str(id.kind) + ' ' + str(id.name) + ' ' + str(id.data_type) + '\n')
					#self.write('DIM ' + str(id.name))
					self.write('DIM ' + str(id.name))
					self.write('	\' AS ')
					self.write_type(id.data_type)
					self.write('\n')
		
	def write_function(self, f, indent=0):
		f.destination = self.stream_out.size	# Record offset in output stream
		
		#self.write_namespace(f.namespace, indent)
		
		self.write_indent(indent)
		self.write('FUNCTION ')
		self.write(f.id.name)
		self.write('(')
		for i in xrange(len(f.args)):
			if (i > 0): self.write(', ')
			#self.write_expression(args[i])
			self.write_var(f.args[i])
			"""
			id = f.namespace.find_id(f.args[i].name)
			if (id == None):
				#self.write_comment('UnknownType')
				pass
			else:
				self.write(' AS ')
				self.write_type(id.data_type)
			"""
		self.write(')')
		
		self.write('\n')
		
		#self.write_namespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		self.write_indent(indent)
		self.write('END FUNCTION\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.size	# Record offset in output stream
		
		self.write_comment('### Module "' + m.name + '"')
		for im in m.imports:
			self.write('\'INCLUDE ')
			self.write(str(im))
			self.write('\n')
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent)
		
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
		
	def write_block(self, b, indent=0):
		b.destination = self.stream_out.size	# Record offset in output stream
		
		#self.write("# Block \"" + b.name + "\"\n")
		"""
		if (b.namespace and len(b.namespace.ids) > 0):
			#self.write_indent(indent)
			#self.write('### Block namespace...\n')
			self.write_namespace(b.namespace, indent)
		"""
		
		for instr in b.instrs:
			self.write_indent(indent)
			self.write_instruction(instr, indent)
			self.write('\n')
			
	def write_instruction(self, i, indent):
		i.destination = self.stream_out.size	# Record offset in output stream
		
		#put(' writing instruction: ' + str(i))
		if (i.control): self.write_control(i.control, indent)
		if (i.call):
			self.write_call(i.call)
		
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0):
					self.write_indent(indent)
					self.write('ELSE ')	#elif
				self.write('IF (')
				
				self.write_expression(c.exprs[j])
				self.write(') THEN\n')
				self.write_block(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('ELSE\n')
				self.write_block(c.blocks[j], indent+1)
			self.write_indent(indent)
			self.write('END IF\n')
		
		elif (c.controlType == C_FOR):
			self.write('FOR ')
			self.write_expression(c.exprs[0])
			self.write(' in ')
			self.write_expression(c.exprs[1])
			self.write('\n')
			self.write_block(c.blocks[0], indent+1)
			
			self.write('NEXT ')
			self.write_expression(c.exprs[0])
			
		elif (c.controlType == C_RETURN):
			self.write('RETURN ')
			self.write_expression(c.exprs[0])
			self.write('\n')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, level=0):
		i = c.id.name
		
		# Set-variable-instruction
		if i == I_VAR_SET.name:
			
			## Annotate type if available
			# if (c.args[0].var) and (not c.args[0].var.type == None): self.write('#@' + c.args[0].var.type.name + '\n')
			
			#self.write_var(c.args[0].var)
			self.write_expression(c.args[0], level)
			self.write(' = ')
			self.write_expression(c.args[1], level)
		
		elif i == I_ARRAY_LOOKUP.name:
			self.write_expression(c.args[0], level)
			self.write('(')
			self.write_expression_list(c.args, 1, level)
			self.write(')')
			
		elif i == I_ARRAY_CONSTRUCTOR.name:
			self.write('(')
			self.write_expression_list(c.args, 0, level)
			self.write(')')
			
		elif i == I_OBJECT_CALL.name:
			self.write_expression(c.args[0], level)
			self.write('(')
			self.write_expression_list(c.args, 1, level)
			self.write(')')
			
		elif i == I_OBJECT_LOOKUP.name:
			self.write_expression(c.args[0], level)
			self.write('.')
			self.write_expression(c.args[1], level)
		
		elif any(i in p for p in PAT_INFIX):
			self.write_expression(c.args[0], level)	# level-1
			
			self.write(' ' + i + ' ')
			
			self.write_expression(c.args[1], level)	# level-1
		
		else:
			# Write a standard call
			# Internals
			if i == I_PRINT.name:
				i = 'PRINT'
			if (i == I_STR.name):
				i = 'STR$'
			
			if (level == 0):
				self.write('CALL ')
				self.write(i)
				self.write('(')
				self.write_expression_list(c.args, 0, level)
				self.write(')')
			else:
				self.write(i)
				self.write('(')
				self.write_expression_list(c.args, 0, level)
				self.write(')')
			
	def write_expression_list(self, es, start, level):
		i = 0
		for i in xrange(len(es)-start):
			if (i > 0): self.write(', ')
			self.write_expression(es[start+i], level=level)
	
	def write_expression(self, e, level=0):
		if (e.value): self.write_value(e.value)
		if (e.var): self.write_var(e.var)
		if (e.call):
			if (level > 0): self.write('(')
			self.write_call(e.call, level+1)
			if (level > 0): self.write(')')
			
	def write_value(self, v):
		if (v.type == T_STRING):
			self.write('"' + v.data_str.replace('"', '"+CHR$(34)+"') + '"')	#@TODO: Escaping!
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		elif (v.type == T_BOOLEAN):
			if (v.data_bool == True):
				self.write('TRUE')
			else:
				self.write('FALSE')
		else:
			self.write('[type=' + v.type + '?]')
	
	def write_type(self, v):
		if (v == T_INTEGER):	v = 'INTEGER';
		elif (v == T_FLOAT):	v = 'SINGLE';
		elif (v == T_STRING):	v = 'STRING';
		self.write(str(v))
	
	def write_var(self, v):
		self.write(v.name)
		
		#self.write('[' + v.id.namespace.name + ':' + v.id.name + ']')


