#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import datetime

from haul.haul import *

def put(t):
	print('HAULWriter_opl:\t' + str(t))


PAT_INFIX = [
	'+', '-', '/', '*', '%',
	'&', 'and', 'or', '|', '||', '^'
	'>', '<', '==', '>=', '<=',
]

DIALECT_OPL3 = 0

class HAULWriter_opl(HAULWriter):
	"Writes BASIC code"
	
	def __init__(self, stream_out, dialect=DIALECT_OPL3):
		HAULWriter.__init__(self, stream_out)
		self.default_extension = 'opl'
		
		#OPL needs proc name in first line, so we can not add this comment
		#	self.write_comment('Translated from HAUL3 to OPL on ' + str(datetime.datetime.now()) )
		
		self.dialect = dialect
		
	def write_comment(self, t):
		"Add a comment to the file"
		#self.stream_out.put('REM ' + t + '\n')
		self.stream_out.put('REM ' + t + '\n')
		
	def write_indent(self, num):
		r = ''
		for i in xrange(num):
			r += '  '
		self.write(r)
		
	def write_namespace(self, ns, indent=0):
		if (ns is None): return
		if (len(ns.ids) == 0): return
		
		self.write_indent(indent)
		self.write_comment('Namespace "' + str(ns) + '"')
		
		# Count all vars that need to be declared. OPL does not allow empty LOCAL instruction
		i = 0
		for id in ns.ids:
			if (id.kind == 'var'):
				i += 1
		
		if (i == 0): return
		
		self.write_indent(indent)
		self.write('LOCAL ')
		
		i = 0
		for id in ns.ids:
			#self.write('# id: "' + str(id.name) + '" (' + str(id.kind) + ') = ' + str(id.data_type))
			
			if (id.name == 'res'): continue	# Do not (re-)declare result
			if (id.kind == 'var'):
				if (i > 0): self.write(', ')
				self.write(str(id.name))
				self.write_type(id.data_type)
				i += 1
		self.write('\n')
		
		
	def write_function(self, f, indent=0):
		#self.write_namespace(f.namespace, indent)
		f.destination = self.stream_out.size	# Record offset in output stream
		
		self.write_indent(indent)
		
		if self.dialect == DIALECT_OPL3:
			self.write(f.id.name.upper())
		else:
			self.write('PROC ')
			self.write(f.id.name)
		
		#@FIXME: in OPL functions have their return type indicator added (%, $, ...)
		#self.write_type(f.returnType)
		
		self.write(': ')
		
		if (len(f.args) > 0):
			self.write('(')
			for i in xrange(len(f.args)):
				if (i > 0): self.write(', ')
				#self.write_expression(args[i])
				self.write_var(f.args[i])
				"""
				id = f.namespace.findId(f.args[i].name)
				if (id == None):
					#self.write_comment('UnknownType')
					pass
				else:
					self.write(' AS ')
					self.write_type(id.data_type)
				"""
			self.write(')')
			
		self.write('\n')
		
		#if self.dialect == DIALECT_OPL:
		#	self.write_namespace(f.namespace, indent+1)
		self.write_block(f.block, indent+1)
		
		if self.dialect != DIALECT_OPL3:
			self.write('ENDP\n')
			self.write_indent(indent)
			self.write('\n')
		
	def write_module(self, m, indent=0):
		m.destination = self.stream_out.size	# Record offset in output stream
		
		wait_before_exit = True	# Add a wait statement (so you can read the output)
		
		# Name must be pre-pended
		self.write(m.name.upper() + ':')
		# Add main parameters, e.g. (A$)
		self.write('\n')
		
		self.write_indent(indent+1)
		self.write_comment('### Module "' + m.name + '"')
		
		for im in m.imports:
			self.write_indent(indent+1)
			"""
			self.write('\'INCLUDE ')
			self.write(str(im))
			self.write('\n')
			"""
			#@FIXME: How to import external libraries? Merge them inside this file?
			#self.write('LOADM "' + str(im) + '"\n')	# Not compatible with old OPL, gives error
			
		#self.write('### Module namespace...\n')
		self.write_namespace(m.namespace, indent+1)
		
		self.write_indent(indent+1)
		self.write_comment('### Root Block (main function):')
		
		if (m.block):
			self.write_block(m.block, indent+1)
			
			if wait_before_exit: self.write('GET\n')	# Wait for key
			#self.write('PAUSE 40\n')
		
		if self.dialect == DIALECT_OPL3:
			# Old OPL needs to have each PROC in its own file. Newer OPL can have "PROC xxx:" in source
			self.write_indent(indent+1)
			self.write_comment('Functions and classes are in separate files')
		else:
			self.write_indent(indent)
			self.write_comment('### Classes...')
			for typ in m.classes:
				self.write_class(typ, indent)
			
			self.write_indent(indent)
			self.write_comment('### Funcs...')
			for func in m.funcs:
				self.write_function(func, indent)
		
		
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
		
		if BLOCKS_HAVE_LOCAL_NAMESPACE:
			if (b.namespace and len(b.namespace.ids) > 0):
				#self.write_indent(indent)
				#self.write_comment('### Block namespace...')
				self.write_namespace(b.namespace, indent)
		
		for instr in b.instrs:
			if (instr.control) or (instr.call):
				self.write_indent(indent)
				self.write_instruction(instr, indent)	#, namespace=b.namespace)
				self.write('\n')
			
	def write_instruction(self, i, indent, namespace=None):
		i.destination = self.stream_out.size	# Record offset in output stream
		#put(' writing instruction: ' + str(i))
		
		if (i.control):
			self.write_control(i.control, indent)
		if (i.call):
			self.write_call(i.call, namespace=namespace)
		
	def write_control(self, c, indent=0):
		if (c.controlType == C_IF):
			j = 0
			while j < len(c.exprs):
				if (j > 0): self.write('ELSE')	# "ELSEIF" in OPL
				self.write('IF (')
				
				self.write_expression(c.exprs[j])
				self.write(')')
				#self.write(' THEN')
				self.write('\n')
				self.write_block(c.blocks[j], indent+1)
				j += 1
			
			if (j < len(c.blocks)):
				self.write_indent(indent)
				self.write('ELSE\n')
				self.write_block(c.blocks[j], indent+1)
			
			self.write_indent(indent)
			self.write('ENDIF\n')
		
		elif (c.controlType == C_FOR):
			self.write('FOR ')
			self.write_expression(c.exprs[0])
			self.write(' in ')
			self.write_expression(c.exprs[1])
			self.write('\n')
			self.write_block(c.blocks[0], indent+1)
			
			self.write_indent(indent)
			self.write('NEXT ')
			self.write_expression(c.exprs[0])
			
		elif (c.controlType == C_RETURN):
			self.write('RETURN ')
			self.write_expression(c.exprs[0])
			#self.write('\n')
		else:
			self.write('CONTROL "' + str(c.controlType) + '"\n')
		
	def write_call(self, c, level=0, namespace=None):
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
			if (i == 'str'):
				#i = '""+'
				i = 'STR$'
			
			if (i == 'int_str'):
				i = ''
			
			if (level == 0):
				
				# Internals
				if (i == 'put'):
					self.write('PRINT ')
					self.write_expression_list(c.args, 0, level)
				
				elif (i == 'shout'):
					self.write('PRINT ')
					self.write_expression_list(c.args, 0, level)
					
					# Beep and wait for key
					self.write(' : ')
					self.write('BEEP 250,440')
					self.write(' : ')
					self.write('GET')	# Beep and wait for key
				
				elif (i == 'put_direct'):
					self.write('PRINT ')
					self.write_expression_list(c.args, 0, level)
					self.write(',')
					
				else:
					
					self.write(i.upper())
					
					#@FIXME: in OPL functions have their return type indicator added (%, $, ...)
					#f = namespace.findId(i)
					#self.write_type(f.data)
					
					self.write(':')
					
					if (len(c.args) > 0):
						self.write('(')
						self.write_expression_list(c.args, 0, level)
						self.write(')')
			else:
				self.write(i)
				if (len(c.args) > 0):
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
			t = v.data_str
			t = t.replace('\\', '\\\\')
			t = t.replace('"', '\\"')
			t = t.replace('\r', '\\r')
			t = t.replace('\n', '\\n')
			t = t.replace('\'', '\\\'')
			self.write('"' + t + '"')
		elif (v.type == T_BOOLEAN):
			if (v.data_bool): self.write('TRUE')
			else: self.write('FALSE')
		elif (v.type == T_INTEGER):
			self.write(str(v.data_int))
		elif (v.type == T_FLOAT):
			self.write(str(v.data_float))
		else:
			self.write('[type=' + str(v.type) + ']')
	
	def write_type(self, v):
		if (v == T_INTEGER):	self.write('%')
		elif (v == T_FLOAT):	pass
		elif (v ==T_STRING):	self.write('$')
		else:
			self.write(str(v))
			
		
	def write_var(self, v):
		self.write(v.name)
		
		# Add type identifier
		#self.write('[' + v.parentNamespace.name + ':' + v.name + ']')
		#id = v.parentNamespace.findId(v)
		self.write_type(v.data_type)


